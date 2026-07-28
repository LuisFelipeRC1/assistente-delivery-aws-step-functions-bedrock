import json
import os
from datetime import datetime, timezone
from typing import Any

import boto3

DYNAMODB = boto3.resource("dynamodb")
TABLE = DYNAMODB.Table(os.environ["ORDERS_TABLE"])


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_assistant_message(assistant: Any) -> str | None:
    if not isinstance(assistant, dict):
        return None

    body = assistant.get("Body", assistant)
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return body

    try:
        return body["output"]["message"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return None


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    order_id = event.get("orderId")
    if not order_id:
        raise ValueError("orderId é obrigatório.")

    status = event.get("status")
    assistant_message = _extract_assistant_message(event.get("assistant"))
    timestamp = _utc_now()

    names: dict[str, str] = {"#updatedAt": "updatedAt"}
    values: dict[str, Any] = {":updatedAt": timestamp}
    expressions = ["#updatedAt = :updatedAt"]

    if status:
        names["#status"] = "status"
        names["#history"] = "history"
        values[":status"] = status
        values[":historyEntry"] = [
            {
                "status": status,
                "timestamp": timestamp,
                **({"details": event["details"]} if event.get("details") else {}),
            }
        ]
        values[":emptyHistory"] = []
        expressions.extend(
            [
                "#status = :status",
                "#history = list_append(if_not_exists(#history, :emptyHistory), :historyEntry)",
            ]
        )

    if assistant_message:
        names["#assistantMessage"] = "assistantMessage"
        values[":assistantMessage"] = assistant_message
        expressions.append("#assistantMessage = :assistantMessage")

    TABLE.update_item(
        Key={"orderId": order_id},
        UpdateExpression="SET " + ", ".join(expressions),
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
        ConditionExpression="attribute_exists(orderId)",
    )

    return {
        "orderId": order_id,
        "status": status,
        "assistantMessageSaved": bool(assistant_message),
        "updatedAt": timestamp,
    }
