import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

def test_workload_api():
    # 1. Создаем сотрудника
    employee_data = {
        "user_id": 1,
        "position": "Developer",
        "specialization": "Python",
        "is_available": True
    }
    response = requests.post(f"{BASE_URL}/employees/", json=employee_data)
    assert response.status_code == 201
    employee_id = response.json()["employee_id"]

    # 2. Создаем задачу
    task_data = {
        "task_description": "Test task",
        "assignee": employee_id,
        "complexity": "medium",
        "due_date": (date.today() + timedelta(days=1)).isoformat()
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data)
    assert response.status_code == 201
    task_id = response.json()["task_id"]

    # 3. Проверяем загруженность сотрудника
    response = requests.get(f"{BASE_URL}/tasks/employee/{employee_id}/workload")
    assert response.status_code == 200
    workload = response.json()
    assert workload["current_tasks"] == 1
    assert workload["total_complexity"] == 2.0

    # 4. Создаем еще одного сотрудника
    employee2_data = {
        "user_id": 2,
        "position": "Developer",
        "specialization": "Python",
        "is_available": True
    }
    response = requests.post(f"{BASE_URL}/employees/", json=employee2_data)
    assert response.status_code == 201
    employee2_id = response.json()["employee_id"]

    # 5. Переназначаем задачу
    response = requests.put(f"{BASE_URL}/tasks/{task_id}/reassign")
    assert response.status_code == 200

    # 6. Проверяем загруженность обоих сотрудников
    response = requests.get(f"{BASE_URL}/tasks/employee/{employee_id}/workload")
    assert response.status_code == 200
    workload1 = response.json()
    assert workload1["current_tasks"] == 0
    assert workload1["total_complexity"] == 0.0

    response = requests.get(f"{BASE_URL}/tasks/employee/{employee2_id}/workload")
    assert response.status_code == 200
    workload2 = response.json()
    assert workload2["current_tasks"] == 1
    assert workload2["total_complexity"] == 2.0

if __name__ == "__main__":
    test_workload_api()
    print("All tests passed!") 