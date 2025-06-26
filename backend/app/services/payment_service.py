import mercadopago
from flask import current_app
from app import db
from app.models import Payment, User, Donation
from datetime import datetime, timedelta, timezone

class PaymentService:
    """Gerencia as interações com o serviço de pagamento (Mercado Pago)."""
    
    def __init__(self):
        """Inicializa o SDK do Mercado Pago."""
        access_token = current_app.config.get('MERCADO_PAGO_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("Mercado Pago Access Token não foi configurado.")
        self.sdk = mercadopago.SDK(access_token)

    def create_pix_payment(self, amount, description, payer_email, user_id, plan_type, duration_days):
        """Cria uma ordem de pagamento PIX para assinaturas."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "Usuário não encontrado."}

            expiration_time = datetime.now(timezone.utc) + timedelta(minutes=15)
            expiration_time_iso = expiration_time.strftime('%Y-%m-%dT%H:%M:%S.000-03:00')

            payment_data = {
                "transaction_amount": float(amount),
                "description": description,
                "payment_method_id": "pix",
                "date_of_expiration": expiration_time_iso,
                "payer": { "email": user.email },
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
                    "mercado_pago_id": payment["id"],
                    "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
                    "qr_code_text": payment["point_of_interaction"]["transaction_data"]["qr_code"],
                }
            else:
                current_app.logger.error(f"Erro PIX: {payment_response}")
                return {"success": False, "error": payment_response.get("message", "Erro desconhecido.")}

        except Exception as e:
            current_app.logger.error(f"Exceção ao criar PIX: {e}", exc_info=True)
            return {"success": False, "error": "Erro interno do servidor."}
        
    def create_donation_pix(self, amount, payer_email, message):
        """Cria uma ordem de pagamento PIX para doações."""
        try:
            expiration_time = datetime.now(timezone.utc) + timedelta(minutes=30)
            expiration_time_iso = expiration_time.strftime('%Y-%m-%dT%H:%M:%S.000-03:00')

            payment_data = {
                "transaction_amount": float(amount),
                "description": "Doação para o projeto SexyDice",
                "payment_method_id": "pix",
                "date_of_expiration": expiration_time_iso,
                "payer": {"email": payer_email}
            }
            payment_response = self.sdk.payment().create(payment_data)
            payment = payment_response.get("response")

            if payment and payment.get("id"):
                new_donation = Donation(
                    email=payer_email,
                    amount=amount,
                    message=message,
                    mercado_pago_id=payment["id"],
                    status='pending'
                )
                db.session.add(new_donation)
                db.session.commit()
                return {
                    "success": True,
                    "mercado_pago_id": payment["id"],
                    "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
                    # CORREÇÃO ESTAVA AQUI - GARANTINDO QUE O TEXTO SEJA RETORNADO
                    "qr_code_text": payment["point_of_interaction"]["transaction_data"]["qr_code"]
                }
            else:
                return {"success": False, "error": "Falha na API do Mercado Pago."}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Exceção ao criar PIX de doação: {e}", exc_info=True)
            return {"success": False, "error": "Erro interno no servidor."}

    def get_payment_details(self, payment_id):
        """Busca os detalhes de um pagamento no Mercado Pago."""
        try:
            payment_info = self.sdk.payment().get(payment_id)
            if payment_info and payment_info.get("response"):
                return payment_info["response"]
            return None
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar detalhes do pagamento {payment_id} no MP: {e}")
            return None