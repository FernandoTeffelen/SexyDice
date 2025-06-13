# backend/app/services/payment_service.py
import mercadopago
import os
from app import db # Importe 'db'
from app.models import Payment # Importe o modelo Payment

class PaymentService:
    """Gerencia as interações com o serviço de pagamento (Mercado Pago)."""
    
    def __init__(self):
        access_token = os.environ.get('MERCADO_PAGO_ACCESS_TOKEN') #
        if not access_token: #
            raise ValueError("A chave de acesso do Mercado Pago não foi configurada.") #
        self.sdk = mercadopago.SDK(access_token) #

    def create_pix_payment(self, amount, description, payer_email, user_id): # <--- ADICIONE user_id
        """Cria uma cobrança PIX e retorna os dados para o frontend."""
        payment_data = {
            "transaction_amount": float(amount), #
            "description": description, #
            "payment_method_id": "pix", #
            "payer": { #
                "email": payer_email, #
            },
            "external_reference": str(user_id) # Adicione uma referência externa para vincular ao seu usuário
        }
        try:
            payment_response = self.sdk.payment().create(payment_data) #
            payment = payment_response.get("response") #

            if payment and payment.get("status") == "pending": #
                qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"] #
                qr_code_text = payment["point_of_interaction"]["transaction_data"]["qr_code"] #
                
                # SALVE O PAGAMENTO NO SEU BANCO DE DADOS AQUI
                if user_id:
                    new_payment_record = Payment(
                        user_id=user_id,
                        mercado_pago_id=payment.get("id"),
                        amount=amount,
                        status=payment.get("status")
                    )
                    db.session.add(new_payment_record)
                    db.session.commit()
                    print(f"Pagamento PIX {payment.get('id')} registrado no DB para user {user_id}")

                return {"success": True, "qr_code_base64": qr_code_base64, "qr_code_text": qr_code_text} #
            else:
                print(f"Erro na criação do PIX, resposta do Mercado Pago: {payment_response}") # Imprima a resposta completa para depuração
                return {"success": False, "error": payment.get("message", "Erro desconhecido na API do Mercado Pago")} #

        except Exception as e:
            print(f"Exceção ao criar pagamento PIX: {e}")
            import traceback
            traceback.print_exc() # Imprime o stack trace completo
            return {"success": False, "error": f"Erro interno ao processar pagamento: {str(e)}"} #

    def get_payment_details(self, payment_id):
        """Busca os detalhes de um pagamento no Mercado Pago."""
        try:
            payment_response = self.sdk.payment().get(payment_id)
            payment = payment_response.get("response")
            if payment:
                return payment
            else:
                print(f"Erro ao buscar detalhes do pagamento {payment_id}: {payment_response.get('message')}")
                return None
        except Exception as e:
            print(f"Erro ao buscar detalhes do pagamento {payment_id}: {e}")
            return None