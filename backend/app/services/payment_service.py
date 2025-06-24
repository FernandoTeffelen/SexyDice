import mercadopago
from flask import current_app # <-- Importamos o 'current_app'
from app import db
from app.models import Payment

class PaymentService:
    """Gerencia as interações com o serviço de pagamento (Mercado Pago)."""
    
    def __init__(self):
        """Inicializa o SDK do Mercado Pago."""
        
        # --- MUDANÇA AQUI ---
        # Acessa a variável a partir do objeto de configuração do Flask
        access_token = current_app.config.get('MERCADO_PAGO_ACCESS_TOKEN')

        if not access_token:
            # Isso previne que a aplicação tente usar o serviço sem configuração
            raise ValueError("Mercado Pago Access Token não foi configurado nas variáveis de ambiente.")
        
        self.sdk = mercadopago.SDK(access_token)

    def create_pix_payment(self, amount, description, payer_email, user_id, plan_type, duration_days):
        """Cria uma cobrança PIX, salva no DB e retorna os dados para o frontend."""
        payment_data = {
            "transaction_amount": float(amount),
            "description": description,
            "payment_method_id": "pix",
            "payer": {
                "email": payer_email,
            },
            "external_reference": str(user_id) # Vincula o pagamento ao nosso user_id
        }
        try:
            payment_response = self.sdk.payment().create(payment_data)
            payment = payment_response.get("response")

            if payment and payment.get("status") == "pending":
                qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
                qr_code_text = payment["point_of_interaction"]["transaction_data"]["qr_code"]
                
                # Salva o pagamento pendente no nosso banco de dados
                if user_id:
                    new_payment_record = Payment(
                        user_id=user_id,
                        mercado_pago_id=payment.get("id"),
                        amount=amount,
                        status=payment.get("status"),
                        plan_type=plan_type,
                        duration_days=duration_days
                    )
                    db.session.add(new_payment_record)
                    db.session.commit()
                    print(f"Pagamento PIX {payment.get('id')} registrado no DB para user {user_id}")

                return {
                    "success": True, 
                    "qr_code_base64": qr_code_base64, 
                    "qr_code_text": qr_code_text,
                    "mercado_pago_id": payment.get("id")
                }
            else:
                print(f"Erro na criação do PIX, resposta do Mercado Pago: {payment_response}")
                return {"success": False, "error": payment.get("message", "Erro desconhecido na API do Mercado Pago")}

        except Exception as e:
            print(f"Exceção ao criar pagamento PIX: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Erro interno ao processar pagamento: {str(e)}"}

    def get_payment_details(self, payment_id):
        """Busca os detalhes de um pagamento no Mercado Pago."""
        try:
            payment_response = self.sdk.payment().get(payment_id)
            return payment_response.get("response")
        except Exception as e:
            print(f"Erro ao buscar detalhes do pagamento {payment_id}: {e}")
            return None