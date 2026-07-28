from decimal import Decimal, InvalidOperation
from typing import Any

ALLOWED_PAYMENT_METHODS = {"PIX", "CARD", "CASH"}


def _positive_number(value: Any) -> bool:
    try:
        return Decimal(str(value)) > 0
    except (InvalidOperation, TypeError, ValueError):
        return False


def validate_order(order: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not order.get("orderId"):
        errors.append("orderId é obrigatório.")

    customer_name = order.get("customerName")
    if not isinstance(customer_name, str) or not customer_name.strip():
        errors.append("customerName é obrigatório.")

    items = order.get("items")
    if not isinstance(items, list) or not items:
        errors.append("O pedido deve possuir ao menos um item.")
    else:
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"O item {index + 1} deve ser um objeto.")
                continue
            if not isinstance(item.get("name"), str) or not item["name"].strip():
                errors.append(f"O item {index + 1} precisa de um nome.")
            if not _positive_number(item.get("quantity")):
                errors.append(f"A quantidade do item {index + 1} deve ser maior que zero.")
            if not _positive_number(item.get("unitPrice")):
                errors.append(f"O preço do item {index + 1} deve ser maior que zero.")

    if not _positive_number(order.get("total")):
        errors.append("total deve ser maior que zero.")

    payment = order.get("payment")
    if not isinstance(payment, dict):
        errors.append("payment é obrigatório.")
    else:
        method = str(payment.get("method", "")).upper()
        if method not in ALLOWED_PAYMENT_METHODS:
            errors.append("O método de pagamento deve ser PIX, CARD ou CASH.")

    delivery = order.get("delivery")
    if not isinstance(delivery, dict):
        errors.append("delivery é obrigatório.")
    else:
        if not delivery.get("city"):
            errors.append("delivery.city é obrigatório.")
        if not delivery.get("neighborhood"):
            errors.append("delivery.neighborhood é obrigatório.")

    return errors


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    order = event.get("order") or {}
    errors = validate_order(order)
    return {"valid": not errors, "errors": errors}
