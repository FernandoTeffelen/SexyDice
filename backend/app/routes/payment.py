from flask import Blueprint, request, jsonify, session
from app import db
from app.models import User, Subscription, Payment
from app.services.payment_service import PaymentService
from datetime import datetime, timedelta, timezone

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/create_pix', methods=['POST'])
def create_pix():
    data = request.get_json()
    amount = data.get('amount')
    plan_type = data.get('planType')
    duration_days = data.get('durationDays')

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuário não encontrado ou não logado."}), 401
    
    email = user.email

    if not all([amount, email, plan_type, duration_days]):
        return jsonify({"error": "Dados da solicitação incompletos."}), 400

    payment_service = PaymentService()
    result = payment_service.create_pix_payment(
        amount=amount,
        description=f"Assinatura SexyDice - Plano {plan_type}",
        payer_email=email,
        user_id=user_id,
        plan_type=plan_type,
        duration_days=duration_days
    )

    if result.get("success"):
        return jsonify({
            "success": True,
            "qr_code_base64": result.get("qr_code_base64"),
            "qr_code_text": result.get("qr_code_text"),
            "mercado_pago_id": result.get("mercado_pago_id") # ID para o frontend
        }), 200
    else:
        return jsonify({"error": result.get("error", "internal_error")}), 500


@payment_bp.route('/webhook', methods=['POST'])
def mercado_pago_webhook():
    print("--- ROTA /api/payment/webhook ATINGIDA! ---")
    data = request.get_json()
    print(f"Dados recebidos do webhook: {data}")

    if data and data.get('type') == 'payment':
        payment_id = data['data']['id']
        action = data.get('action')

        if action == 'payment.created':
            print(f"Webhook 'payment.created' recebido. Nenhuma ação de aprovação tomada.")
            return jsonify(success=True), 200

        print(f"Webhook '{action}' recebido para o pagamento ID: {payment_id}. Processando aprovação...")
        local_payment = Payment.query.filter_by(mercado_pago_id=payment_id).first()

        if not local_payment:
            print(f"Pagamento local com ID {payment_id} não encontrado.")
            return jsonify(success=False, message="Pagamento local não encontrado"), 404
        
        user = User.query.get(local_payment.user_id)
        if not user:
            print(f"Usuário com ID {local_payment.user_id} não encontrado.")
            return jsonify(success=False, message="Usuário não encontrado"), 404

        subscription = user.subscription
        if not subscription:
            subscription = Subscription(user_id=user.id)
            db.session.add(subscription)

        # --- MUDANÇA PRINCIPAL AQUI ---
        # Usamos datetime.now(timezone.utc) para garantir que a data seja salva com fuso horário
        subscription.status = 'active'
        subscription.plan_type = local_payment.plan_type
        subscription.expires_at = datetime.now(timezone.utc) + timedelta(days=local_payment.duration_days)
        local_payment.status = 'approved'
        
        try:
            db.session.commit()
            print(f"SUCESSO: Assinatura do usuário {user.email} atualizada para o plano '{local_payment.plan_type}'.")
        except Exception as e:
            db.session.rollback()
            print(f"ERRO: Falha ao salvar no banco: {e}")

    return jsonify(success=True), 200

@payment_bp.route('/status/<int:mercado_pago_id>', methods=['GET'])
def payment_status(mercado_pago_id):
    """Verifica o status de um pagamento no nosso banco de dados."""
    payment = Payment.query.filter_by(mercado_pago_id=mercado_pago_id).first()
    
    if not payment:
        return jsonify({"status": "not_found"}), 404
        
    return jsonify({"status": payment.status}), 200
