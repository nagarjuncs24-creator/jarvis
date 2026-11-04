import ast
import operator
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolError(ValueError):
    pass


class CalculatorInput(BaseModel):
    expression: str = Field(min_length=1, max_length=200)


class DateTimeInput(BaseModel):
    timezone: str = "UTC"


class ToolDefinition:
    def __init__(self, name: str, description: str, input_model: type[BaseModel], permission: str, handler: Callable[[BaseModel], dict[str, Any]]) -> None:
        self.name, self.description, self.input_model, self.permission, self.handler = name, description, input_model, permission, handler

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.handler(self.input_model.model_validate(payload))


_operators: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow,
}


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and type(node.op) in _operators:
        return _operators[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    raise ToolError("Only numeric arithmetic is allowed")


def calculate(payload: CalculatorInput) -> dict[str, Any]:
    try:
        tree = ast.parse(payload.expression, mode="eval")
        value = _evaluate(tree.body)
    except (SyntaxError, ZeroDivisionError, OverflowError, ToolError) as error:
        raise ToolError(f"Invalid arithmetic expression: {error}") from error
    return {"expression": payload.expression, "result": value}


def current_time(_: DateTimeInput) -> dict[str, Any]:
    return {"utc": datetime.now(UTC).isoformat()}


TOOLS = {
    "calculator": ToolDefinition("calculator", "Safely evaluates numeric arithmetic only.", CalculatorInput, "read", calculate),
    "date_time": ToolDefinition("date_time", "Returns the current UTC time.", DateTimeInput, "read", current_time),
}
