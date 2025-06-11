import mercadopago
import os

class PaymentService:
    """Gerencia as interações com o serviço de pagamento (Mercado Pago)."""
    
    def __init__(self):
        access_token = os.environ.get('MERCADO_PAGO_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("A chave de acesso do Mercado Pago não foi configurada.")
        self.sdk = mercadopago.SDK(access_token)

    def create_pix_payment(self, amount, description, payer_email):
        """Cria uma cobrança PIX e retorna os dados para o frontend."""
        payment_data = {
            "transaction_amount": float(amount),
            "description": description,
            "payment_method_id": "pix",
            "payer": {
                "email": payer_email,
            }
        }
        try:
            payment_response = self.sdk.payment().create(payment_data)
            payment = payment_response.get("response")

            if payment and payment.get("status") == "pending":
                qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
                qr_code_text = payment["point_of_interaction"]["transaction_data"]["qr_code"]
                return {"success": True, "qr_code_base64": qr_code_base64, "qr_code_text": qr_code_text}
            else:
                return {"success": False, "error": payment.get("message", "Erro desconhecido")}

        except Exception as e:
            print(f"Erro ao criar pagamento PIX: {e}")
            return {"success": False, "error": str(e)}