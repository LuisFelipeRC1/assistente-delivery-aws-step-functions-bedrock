import base64
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

DYNAMODB = boto3.resource("dynamodb")
STEP_FUNCTIONS = boto3.client("stepfunctions")
TABLE = DYNAMODB.Table(os.environ["ORDERS_TABLE"])
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def _parse_body(event: dict[str, Any]) -> dict[str, Any]:
    raw_body = event.get("body")
    if not raw_body:
        raise ValueError("O corpo da requisição é obrigatório.")

    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body).decode("utf-8")

    if isinstance(raw_body, dict):
        return raw_body

    parsed = json.loads(raw_body)
    if not isinstance(parsed, dict):
        raise ValueError("O corpo da requisição deve ser um objeto JSON.")
    return parsed


def _to_decimal(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, list):
        return [_to_decimal(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_decimal(item) for key, item in value.items()}
    return value


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    try:
        payload = _parse_body(event)
    except (ValueError, json.JSONDecodeError) as error:
        return _json_response(400, {"message": str(error)})

    order_id = str(uuid.uuid4())
    created_at = _utc_now()

    order = {
        **payload,
        "orderId": order_id,
        "status": "RECEIVED",
        "createdAt": created_at,
        "updatedAt": created_at,
    }

    record = {
        **order,
        "history": [{"status": "RECEIVED", "timestamp": created_at}],
    }

    TABLE.put_item(
        Item=_to_decimal(record),
        ConditionExpression="attribute_not_exists(orderId)",
    )

    execution = STEP_FUNCTIONS.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=f"order-{order_id}",
        input=json.dumps({"order": order}, ensure_ascii=False),
    )

    LOGGER.info(
        "Pedido recebido",
        extra={"orderId": order_id, "executionArn": execution["executionArn"]},
    )

    return _json_response(
        202,
        {
            "orderId": order_id,
            "status": "RECEIVED",
            "executionArn": execution["executionArn"],
            "message": "Pedido recebido e enviado para processamento.",
        },
    )
