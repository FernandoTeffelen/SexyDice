from flask import Blueprint, request, jsonify, session
from app import db
from app.models import User, Subscription, Payment, Donation # Importar o novo modelo Donation
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

    # A notificação pode ser de vários tipos, mas só nos importamos com pagamentos
    if data and data.get('type') == 'payment':
        payment_id = data['data']['id']
        print(f"Webhook recebido para o pagamento ID: {payment_id}")

        # --- LÓGICA DE PRODUÇÃO ---
        # 1. Buscamos os detalhes REAIS do pagamento na API do Mercado Pago
        payment_service = PaymentService()
        payment_info = payment_service.get_payment_details(payment_id)

        # 2. Verificamos se o pagamento foi realmente aprovado
        if payment_info and payment_info.get("status") == "approved":
            print(f"Pagamento {payment_id} foi APROVADO no Mercado Pago!")
            
            # 3. Encontramos o pagamento correspondente no nosso banco de dados
            local_payment = Payment.query.filter_by(mercado_pago_id=payment_id).first()
            if not local_payment:
                print(f"ALERTA: Pagamento aprovado {payment_id} não encontrado no nosso banco de dados.")
                return jsonify(success=False), 404

            # Se o pagamento já foi processado, não fazemos nada
            if local_payment.status == 'approved':
                print(f"Pagamento {payment_id} já foi processado anteriormente. Nenhuma ação tomada.")
                return jsonify(success=True), 200

            # 4. Encontramos o usuário e atualizamos sua assinatura
            user = User.query.get(local_payment.user_id)
            if user:
                subscription = user.subscription
                if not subscription:
                    subscription = Subscription(user_id=user.id)
                    db.session.add(subscription)

                subscription.status = 'active'
                subscription.plan_type = local_payment.plan_type
                subscription.expires_at = datetime.utcnow() + timedelta(days=local_payment.duration_days)
                local_payment.status = 'approved'
                
                try:
                    db.session.commit()
                    print(f"SUCESSO: Assinatura do usuário {user.email} atualizada para o plano '{local_payment.plan_type}'.")
                except Exception as e:
                    db.session.rollback()
                    print(f"ERRO: Falha ao salvar no banco: {e}")
    
    # Sempre retornamos 200 OK para o Mercado Pago saber que recebemos a notificação
    return jsonify(success=True), 200

@payment_bp.route('/status/<int:mercado_pago_id>', methods=['GET'])
def payment_status(mercado_pago_id):
    """Verifica o status de um pagamento no nosso banco de dados."""
    payment = Payment.query.filter_by(mercado_pago_id=mercado_pago_id).first()
    
    if not payment:
        return jsonify({"status": "not_found"}), 404
        
    return jsonify({"status": payment.status}), 200

@payment_bp.route('/create_donation_pix', methods=['POST'])
def create_donation_pix():
    data = request.get_json()
    amount = data.get('amount')
    email = data.get('email', 'doacao.anonima@email.com')
    message = data.get('message')

    if not amount or float(amount) < 1.00:
        return jsonify({"error": "O valor da doação deve ser de no mínimo R$ 1,00."}), 400

    # Salva a tentativa de doação no banco de dados
    try:
        new_donation = Donation(
            email=email,
            amount=amount,
            message=message
        )
        db.session.add(new_donation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"ERRO AO SALVAR DOAÇÃO: {e}")
        return jsonify({"error": "Erro ao salvar dados da doação."}), 500

    # Continua para gerar o PIX no Mercado Pago
    payment_service = PaymentService()
    result = payment_service.create_donation_pix(
        amount=amount,
        payer_email=email
    )

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify({"error": result.get("error")}), 500