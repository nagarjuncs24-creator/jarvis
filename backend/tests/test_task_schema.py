from app.schemas.productivity import TaskCreate


def test_task_schema_accepts_prioritized_task() -> None:
    task = TaskCreate(title="Prepare report", priority="high")
    assert task.title == "Prepare report"
    assert task.priority == "high"
