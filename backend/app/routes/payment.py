# backend/app/routes/payment.py

from flask import Blueprint, request, jsonify, session
from ..services.payment_service import PaymentService
from app import db
from app.models import User, Subscription, Payment
from datetime import datetime, timedelta

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/create_pix', methods=['POST'])
def create_pix():
    data = request.get_json()
    amount = data.get('amount')
    email = data.get('email')
    
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({"error": "Você precisa estar logado como usuário para fazer uma compra."}), 401

    if not amount or not email:
        return jsonify({"error": "Valor e email são obrigatórios"}), 400

    payment_service = PaymentService()
    result = payment_service.create_pix_payment(
        amount=amount,
        description="Assinatura SexyDice",
        payer_email=email,
        user_id=user_id # Passe o user_id para o serviço de pagamento
    )

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify({"error": result.get("error")}), 500

@payment_bp.route('/webhook', methods=['POST'])
def mercado_pago_webhook():
    # Adicionamos este print para depuração. Ele deve aparecer no terminal do Flask.
    print("--- ROTA /api/payment/webhook ATINGIDA! ---")
    
    try:
        data = request.get_json()
        print(f"Dados recebidos do webhook: {data}")

        if data and data.get('type') == 'payment':
            payment_id = data['data']['id']
            print(f"Webhook recebido para o pagamento ID: {payment_id}")

            payment_service = PaymentService()
            payment_info = payment_service.get_payment_details(payment_id) # Usar o novo método para buscar detalhes

            if payment_info and payment_info.get("status") == "approved":
                print(f"Pagamento {payment_id} foi aprovado!")
                
                # Primeiro, tente buscar o pagamento no seu DB local pelo mercado_pago_id
                local_payment = Payment.query.filter_by(mercado_pago_id=payment_id).first()
                
                user = None
                if local_payment:
                    user = User.query.get(local_payment.user_id) # Busca o user pelo id salvo no payment local
                else: 
                    # Fallback para email se o pagamento não foi salvo localmente ou se houver um erro
                    # Idealmente, o local_payment sempre deve ser encontrado
                    payer_email = payment_info['payer']['email']
                    user = User.query.filter_by(email=payer_email).first()

                if not user:
                    print(f"Usuário com e-mail {payment_info['payer']['email']} ou ID associado não encontrado.")
                    return jsonify(success=False, message="Usuário não encontrado"), 404

                # Atualiza o status do pagamento local ou cria um novo registro
                if local_payment:
                    local_payment.status = payment_info['status']
                    local_payment.amount = payment_info['transaction_amount'] 
                else: 
                    # Cria um novo registro de pagamento se não existia (o que não deveria acontecer se create_pix_payment salvou)
                    new_payment = Payment(
                        user_id=user.id,
                        mercado_pago_id=payment_id,
                        amount=payment_info['transaction_amount'],
                        status=payment_info['status']
                    )
                    db.session.add(new_payment)
                
                subscription = user.subscription
                if not subscription:
                    subscription = Subscription(user_id=user.id)
                    db.session.add(subscription)

                subscription.status = 'active'
                subscription.plan_type = 'mensal'
                subscription.expires_at = datetime.utcnow() + timedelta(days=30)
                
                try:
                    db.session.commit()
                    print(f"Assinatura do usuário {user.email} atualizada com sucesso.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Erro ao salvar no banco: {e}")
            elif payment_info: 
                # Se o status não for aprovado, mas temos informação do pagamento
                # Atualiza o status no seu DB local
                local_payment = Payment.query.filter_by(mercado_pago_id=payment_id).first()
                if local_payment:
                    local_payment.status = payment_info['status']
                    db.session.commit()
                    print(f"Status do pagamento {payment_id} atualizado para: {payment_info['status']}")
            else:
                print(f"Não foi possível obter detalhes do pagamento {payment_id} ou status inválido.")

        return jsonify(success=True), 200

    except Exception as e:
        print(f"Erro no webhook do Mercado Pago: {e}")
        import traceback
        traceback.print_exc() # Imprime o stack trace completo
        return jsonify({"status": "error", "message": str(e)}), 500