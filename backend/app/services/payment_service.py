import mercadopago
from flask import current_app
from app.models import db, Payment, User
from datetime import datetime

# As credenciais são carregadas a partir da configuração do Flask
MERCADO_PAGO_ACCESS_TOKEN = None
MERCADO_PAGO_PUBLIC_KEY = None

def init_payment_service(app):
    """Inicializa o serviço de pagamento com as configurações do app Flask."""
    global MERCADO_PAGO_ACCESS_TOKEN, MERCADO_PAGO_PUBLIC_KEY
    MERCADO_PAGO_ACCESS_TOKEN = app.config.get('MERCADO_PAGO_ACCESS_TOKEN')
    MERCADO_PAGO_PUBLIC_KEY = app.config.get('MERCADO_PAGO_PUBLIC_KEY')
    if not MERCADO_PAGO_ACCESS_TOKEN or not MERCADO_PAGO_PUBLIC_KEY:
        app.logger.warning("As credenciais do Mercado Pago não estão configuradas!")

def create_pix_payment(user_id, plan_type, amount):
    """
    Cria uma ordem de pagamento PIX no Mercado Pago.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {"success": False, "error": "Usuário não encontrado."}

        # Inicializa o SDK do Mercado Pago
        sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)

        # Monta os dados do pagamento
        payment_data = {
            "transaction_amount": float(amount),
            "description": f"Plano {plan_type.capitalize()} - SexyDice",
            "payment_method_id": "pix",
            "payer": {
                "email": user.email,
                "first_name": user.name.split(' ')[0],
                "last_name": ' '.join(user.name.split(' ')[1:]) if ' ' in user.name else 'User',
            }
        }

        # Cria a requisição de pagamento
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response.get("response")

        if payment and payment.get("id"):
            # Pagamento criado com sucesso no MP, agora registra no nosso DB
            new_payment = Payment(
                user_id=user.id,
                mp_payment_id=payment["id"],
                plan_type=plan_type,
                amount=amount,
                status='pending' 
            )
            db.session.add(new_payment)
            db.session.commit()

            return {
                "success": True,
                "payment_id": payment["id"],
                "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
                "qr_code": payment["point_of_interaction"]["transaction_data"]["qr_code"],
            }
        else:
            # --- CORREÇÃO APLICADA AQUI ---
            # O bloco abaixo agora lida com respostas de erro da API de forma segura.
            current_app.logger.error(f"Erro na criação do PIX, resposta do Mercado Pago: {payment_response}")
            
            error_message = "Erro desconhecido ao se comunicar com o Mercado Pago."
            if payment and isinstance(payment, dict) and "message" in payment:
                error_message = payment["message"]
            elif payment_response and payment_response.get("status") in [400, 401, 500]:
                 error_message = (
                    "Falha ao criar o pagamento. Verifique se suas credenciais de produção "
                    "no Mercado Pago estão ativas e corretas. (Status: {})"
                 ).format(payment_response.get("status"))

            return {"success": False, "error": error_message}

    except Exception as e:
        current_app.logger.error(f"Exceção ao criar pagamento PIX: {e}", exc_info=True)
        return {"success": False, "error": "Ocorreu um erro interno no servidor."}