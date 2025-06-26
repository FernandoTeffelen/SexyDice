from flask import Blueprint, request, jsonify, session
from app import db
from app.models import User, Subscription, Payment, Donation
from app.services.payment_service import PaymentService
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation # Importar o tipo Decimal

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/create_donation_pix', methods=['POST'])
def create_donation_pix():
    data = request.get_json()
    message = data.get('message')
    email = data.get('email') or "doacao.anonima@email.com"

    # --- CORREÇÃO AQUI: Validação e conversão para Decimal ---
    try:
        amount_str = data.get('amount')
        if not amount_str:
            return jsonify({"error": "O valor da doação é obrigatório."}), 400
        
        amount = Decimal(amount_str) # Converte para Decimal
        if amount < Decimal('1.00'):
            return jsonify({"error": "O valor da doação deve ser de no mínimo R$ 1,00."}), 400
    except (InvalidOperation, TypeError):
        return jsonify({"error": "O valor da doação é inválido."}), 400
    # --- FIM DA CORREÇÃO ---
    
    payment_service = PaymentService()
    result = payment_service.create_donation_pix(
        amount=amount, # Envia o valor já como Decimal
        payer_email=email
    )

    if not result.get("success"):
        return jsonify({"error": result.get("error", "Falha ao criar PIX")}), 500
    
    mercado_pago_id = result.get("mercado_pago_id")
        
    try:
        new_donation = Donation(
            email=email,
            amount=amount, # Salva o Decimal no banco
            message=message,
            mercado_pago_id=mercado_pago_id,
            status='pending'
        )
        db.session.add(new_donation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log do erro real no console do servidor para depuração
        print(f"CRÍTICO: Falha ao salvar registro de doação. Erro: {e}")
        return jsonify({"error": "Erro crítico ao salvar dados da doação."}), 500

    return jsonify({
        "success": True,
        "qr_code_base64": result.get("qr_code_base64"),
        "qr_code_text": result.get("qr_code_text"),
        "mercado_pago_id": mercado_pago_id
    }), 200

# O resto do seu arquivo payment.py continua aqui...
# (create_pix, webhook, etc.)
# ...
@payment_bp.route('/create_pix', methods=['POST'])
def create_pix():
    data = request.get_json()
    plan_type = data.get('planType')
    duration_days = data.get('durationDays')

    try:
        amount_str = data.get('amount')
        if not amount_str: return jsonify({"error": "Valor é obrigatório."}), 400
        amount = Decimal(amount_str)
    except (InvalidOperation, TypeError):
        return jsonify({"error": "Valor inválido."}), 400

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuário não encontrado ou não logado."}), 401
    
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
        return jsonify({"error": result.get("error", "internal_error")}), 500

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

    description = payment_info.get("description", "")
    
    if "Doação para o projeto SexyDice" in description:
        donation = Donation.query.filter_by(mercado_pago_id=payment_id).first()
        if donation and donation.status != 'approved':
            donation.status = 'approved'
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"ERRO: Falha ao atualizar status da doação: {e}")
    else:
        local_payment = Payment.query.filter_by(mercado_pago_id=payment_id).first()
        if local_payment and local_payment.status != 'approved':
            user = User.query.get(local_payment.user_id)
            if user:
                subscription = user.subscription
                if not subscription:
                    subscription = Subscription(user_id=user.id)
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
                    print(f"ERRO: Falha ao salvar assinatura no banco: {e}")

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