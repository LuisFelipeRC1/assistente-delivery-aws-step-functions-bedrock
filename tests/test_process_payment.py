import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src" / "process_payment"))
from app import process_payment


def test_payment_is_approved():
    result = process_payment(50, {"method": "PIX"})
    assert result["approved"] is True


def test_simulated_failure_is_rejected():
    result = process_payment(50, {"method": "CARD", "simulateFailure": True})
    assert result["approved"] is False
