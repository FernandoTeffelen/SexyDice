from flask import Blueprint, request, jsonify
from ..services.payment_service import PaymentService

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
        description="Assinatura SexyDice",
        payer_email=email
    )

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify({"error": result.get("error")}), 500