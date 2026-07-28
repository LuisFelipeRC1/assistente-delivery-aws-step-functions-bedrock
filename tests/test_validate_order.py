import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src" / "validate_order"))
from app import validate_order


def valid_order():
    return {
        "orderId": "123",
        "customerName": "Luis",
        "items": [{"name": "Pizza", "quantity": 1, "unitPrice": 40}],
        "total": 40,
        "payment": {"method": "PIX"},
        "delivery": {"city": "Aracaju", "neighborhood": "Centro"},
    }


def test_valid_order_has_no_errors():
    assert validate_order(valid_order()) == []


def test_invalid_payment_method_is_rejected():
    order = valid_order()
    order["payment"] = {"method": "CRYPTO"}
    assert "O método de pagamento deve ser PIX, CARD ou CASH." in validate_order(order)
