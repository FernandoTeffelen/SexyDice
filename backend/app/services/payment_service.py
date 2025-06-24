import mercadopago
from flask import current_app
from app import db
from app.models import Payment, User
from datetime import datetime, timedelta, timezone # <-- Importações necessárias

class PaymentService:
    """Gerencia as interações com o serviço de pagamento (Mercado Pago)."""
    
    def __init__(self):
        """Inicializa o SDK do Mercado Pago."""
        access_token = current_app.config.get('MERCADO_PAGO_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("Mercado Pago Access Token não foi configurado nas variáveis de ambiente.")
        self.sdk = mercadopago.SDK(access_token)

    def create_pix_payment(self, user_id, plan_type, amount, duration_days):
        """
        Cria uma ordem de pagamento PIX no Mercado Pago com tempo de expiração.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "Usuário não encontrado."}

            # --- INÍCIO DA LÓGICA DE EXPIRAÇÃO ADICIONADA DE VOLTA ---
            
            # Define o tempo de expiração para 15 minutos a partir de agora
            expiration_time = datetime.now(timezone.utc) + timedelta(minutes=15)
            
            # Converte para o formato de data que a API do Mercado Pago espera
            expiration_time_iso = expiration_time.strftime('%Y-%m-%dT%H:%M:%S.000-03:00')

            # --- FIM DA LÓGICA DE EXPIRAÇÃO ---

            # Monta os dados do pagamento
            payment_data = {
                "transaction_amount": float(amount),
                "description": f"Plano {plan_type.capitalize()} - SexyDice",
                "payment_method_id": "pix",
                "date_of_expiration": expiration_time_iso, # <-- CAMPO ADICIONADO AQUI
                "payer": {
                    "email": user.email,
                    "first_name": user.name.split(' ')[0],
                    "last_name": ' '.join(user.name.split(' ')[1:]) if ' ' in user.name else 'User',
                },
                "external_reference": str(user_id)
            }

            payment_response = self.sdk.payment().create(payment_data)
            payment = payment_response.get("response")

            if payment and payment.get("id"):
                new_payment = Payment(
                    user_id=user.id,
                    mercado_pago_id=payment["id"],
                    plan_type=plan_type,
                    amount=amount,
                    duration_days=duration_days,
                    status='pending'
                )
                db.session.add(new_payment)
                db.session.commit()

                return {
                    "success": True,
                    "payment_id": payment["id"],
                    "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
                    "qr_code_text": payment["point_of_interaction"]["transaction_data"]["qr_code"],
                }
            else:
                current_app.logger.error(f"Erro na criação do PIX, resposta do Mercado Pago: {payment_response}")
                error_message = "Erro desconhecido ao se comunicar com o Mercado Pago."
                if payment and isinstance(payment, dict) and "message" in payment:
                    error_message = payment["message"]
                return {"success": False, "error": error_message}

        except Exception as e:
            current_app.logger.error(f"Exceção ao criar pagamento PIX: {e}", exc_info=True)
            return {"success": False, "error": "Ocorreu um erro interno no servidor."}

    def get_payment_details(self, payment_id):
        """Busca os detalhes de um pagamento no Mercado Pago."""
        try:
            payment_response = self.sdk.payment().get(payment_id)
            return payment_response.get("response")
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar detalhes do pagamento {payment_id}: {e}", exc_info=True)
            return None