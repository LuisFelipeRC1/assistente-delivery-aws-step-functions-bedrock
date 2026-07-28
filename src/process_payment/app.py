import uuid
from decimal import Decimal, InvalidOperation
from typing import Any

ALLOWED_PAYMENT_METHODS = {"PIX", "CARD", "CASH"}


def process_payment(amount: Any, payment: dict[str, Any]) -> dict[str, Any]:
    try:
        numeric_amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        return {"approved": False, "reason": "Valor de pagamento inválido."}

    method = str(payment.get("method", "")).upper()

    if numeric_amount <= 0:
        return {"approved": False, "reason": "O valor deve ser maior que zero."}
    if method not in ALLOWED_PAYMENT_METHODS:
        return {"approved": False, "reason": "Método de pagamento não suportado."}
    if payment.get("simulateFailure") is True:
        return {"approved": False, "reason": "Falha de pagamento simulada."}

    return {
        "approved": True,
        "transactionId": f"sim-{uuid.uuid4()}",
        "method": method,
    }


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    payment = event.get("payment")
    if not isinstance(payment, dict):
        payment = {}
    return process_payment(event.get("amount"), payment)
