from app.api.routes.chat import tool_result_text


def test_chat_formats_actual_calculator_result() -> None:
    assert tool_result_text("calculator", {"expression": "2 + 2", "result": 4.0}) == "2 + 2 = 4"
