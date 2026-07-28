import json
import os
from decimal import Decimal
from typing import Any

import boto3

DYNAMODB = boto3.resource("dynamodb")
TABLE = DYNAMODB.Table(os.environ["ORDERS_TABLE"])


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, cls=DecimalEncoder, ensure_ascii=False),
    }


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    order_id = event.get("pathParameters", {}).get("orderId")
    if not order_id:
        return _response(400, {"message": "orderId é obrigatório."})

    result = TABLE.get_item(Key={"orderId": order_id}, ConsistentRead=True)
    order = result.get("Item")

    if not order:
        return _response(404, {"message": "Pedido não encontrado."})

    safe_order = dict(order)
    payment = safe_order.get("payment")
    if isinstance(payment, dict):
        safe_order["payment"] = {"method": payment.get("method")}

    return _response(200, safe_order)
