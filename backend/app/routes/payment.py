from flask import Blueprint, request, jsonify, session, current_app
from app import db
from app.models import User, Subscription, Payment, Donation
from app.services.payment_service import PaymentService
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/create_donation_pix', methods=['POST'])
def create_donation_pix():
    data = request.get_json()
    message = data.get('message')
    email = data.get('email') or "doacao.anonima@email.com"

    try:
        amount = Decimal(data.get('amount'))
        if amount < Decimal('1.00'):
            return jsonify({"error": "O valor mínimo da doação é R$ 1,00."}), 400
    except (InvalidOperation, TypeError):
        return jsonify({"error": "Valor da doação inválido."}), 400
    
    payment_service = PaymentService()
    
    # CORREÇÃO APLICADA AQUI: Garantindo que todos os argumentos sejam passados.
    result = payment_service.create_donation_pix(
        amount=amount,
        payer_email=email,
        message=message
    )

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify({"error": result.get("error", "Falha ao criar PIX de doação")}), 500

@payment_bp.route('/create_pix', methods=['POST'])
def create_pix():
    data = request.get_json()
    try:
        amount = Decimal(data.get('amount'))
        plan_type = data.get('planType')
        duration_days = data.get('durationDays')
    except (InvalidOperation, TypeError):
        return jsonify({"error": "Dados inválidos."}), 400

    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    if not user:
        return jsonify({"error": "Usuário não logado."}), 401
    
    payment_service = PaymentService()
    result = payment_service.create_pix_payment(
        amount=amount,
        description=f"Assinatura SexyDice - Plano {plan_type}",
        payer_email=user.email,
        user_id=user_id,
        plan_type=plan_type,
        duration_days=duration_days
    )

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify({"error": result.get("error", "Erro interno")}), 500

@payment_bp.route('/webhook', methods=['POST'])
def mercado_pago_webhook():
    data = request.get_json()
    if not data or data.get('type') != 'payment':
        return jsonify(success=True), 200

    payment_id = data['data']['id']
    payment_service = PaymentService()
    payment_info = payment_service.get_payment_details(payment_id)

    if not payment_info or payment_info.get("status") != "approved":
        return jsonify(success=False), 404

    # Lógica para atualizar doação
    donation = Donation.query.filter_by(mercado_pago_id=payment_id).first()
    if donation and donation.status != 'approved':
        donation.status = 'approved'
        try:
            db.session.commit()
            return jsonify(success=True), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"ERRO: Falha ao atualizar status da doação: {e}")
            return jsonify(success=False), 500
    
    # Lógica para atualizar assinatura de usuário
    local_payment = Payment.query.filter_by(mercado_pago_id=payment_id).first()
    if local_payment and local_payment.status != 'approved':
        user = User.query.get(local_payment.user_id)
        if user:
            subscription = user.subscription or Subscription(user_id=user.id)
            if not user.subscription:
                db.session.add(subscription)
            
            now_utc = datetime.now(timezone.utc)
            start_date = subscription.expires_at if subscription.expires_at and subscription.expires_at > now_utc else now_utc
            subscription.expires_at = start_date + timedelta(days=local_payment.duration_days)
            
            subscription.status = 'active'
            subscription.plan_type = local_payment.plan_type
            local_payment.status = 'approved'
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"ERRO: Falha ao salvar assinatura no banco: {e}")

    return jsonify(success=True), 200

@payment_bp.route('/status/<int:mercado_pago_id>', methods=['GET'])
def payment_status(mercado_pago_id):
    payment = Payment.query.filter_by(mercado_pago_id=mercado_pago_id).first()
    if payment:
        return jsonify({"status": payment.status}), 200
    
    donation = Donation.query.filter_by(mercado_pago_id=mercado_pago_id).first()
    if donation:
        return jsonify({"status": donation.status}), 200

    return jsonify({"status": "not_found"}), 404