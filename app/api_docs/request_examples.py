from fastapi import Body


example_create_task = Body(
    openapi_examples={
        "normal":   {
            "summary": "Типовой запрос",
            "description": "Типовой запрос для создания задачи",
            "value": {
                "task_description": "Подготовить презентацию",
                "assignee": "123",
                "due_date": "2025-05-26"
            }
        },
        "empty_date": {
            "summary": "Запрос без указания срока",
            "description": "Запрос для создания задачи без указания "
                           "крайнего срока исполнения. В поле `due_date` "
                           "будет автоматически подставлен завтрашний день",
            "value": {
                "task_description": "Подготовить презентацию",
                "assignee": "Василий"
            },
        },
        "invalid": {
            "summary": "Некорректные данные, возвращается ошибка 422",
            "value": {
                "task_description": "Подготовить презентацию",
                "assignee": "Василий",
                "due_date": "сегодня"
            },
        },
    }
)
