from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Subscription, Payment
from app.services.payment_service import PaymentService
from datetime import datetime, timedelta

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/create_pix', methods=['POST'])
def create_pix():
    data = request.get_json()
    amount = data.get('amount')
    email = data.get('email')

    if not amount or not email:
        return jsonify({"error": "Valor e email são obrigatórios"}), 400

    payment_service = PaymentService()
    result = payment_service.create_pix_payment(
        amount=amount,
        description="Acesso ao SexyDice",
        payer_email=email
    )

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify({"error": result.get("error", "internal_error")}), 500


@payment_bp.route('/webhook', methods=['POST'])
def mercado_pago_webhook():
    # Adicionamos este print para depuração. Ele deve aparecer no terminal do Flask.
    print("--- ROTA /api/payment/webhook ATINGIDA! ---")
    
    data = request.get_json()
    print(f"Dados recebidos do webhook: {data}")

    if data and data.get('type') == 'payment':
        payment_id = data['data']['id']
        print(f"Webhook recebido para o pagamento ID: {payment_id}")

        payment_service = PaymentService()
        payment_details = payment_service.sdk.payment().get(payment_id)
        payment_info = payment_details.get("response")

        if payment_info and payment_info.get("status") == "approved":
            print(f"Pagamento {payment_id} foi aprovado!")
            
            payer_email = payment_info['payer']['email']
            user = User.query.filter_by(email=payer_email).first()

            if not user:
                print(f"Usuário com e-mail {payer_email} não encontrado.")
                return jsonify(success=False, message="Usuário não encontrado"), 404

            subscription = user.subscription
            if not subscription:
                subscription = Subscription(user_id=user.id)
                db.session.add(subscription)

            subscription.status = 'active'
            subscription.plan_type = 'mensal'
            subscription.expires_at = datetime.utcnow() + timedelta(days=30)
            
            new_payment = Payment(
                user_id=user.id,
                mercado_pago_id=payment_id,
                amount=payment_info['transaction_amount'],
                status=payment_info['status']
            )
            db.session.add(new_payment)
            
            try:
                db.session.commit()
                print(f"Assinatura do usuário {payer_email} atualizada com sucesso.")
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao salvar no banco: {e}")

    return jsonify(success=True), 200