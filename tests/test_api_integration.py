import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.db import get_session
from app.schemas.employee import Employee, Skill, SkillLevel
from app.schemas.task import Task, TaskComplexity
import json


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    # Регистрация пользователя
    register_response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert register_response.status_code == 200

    # Получение токена
    login_response = client.post(
        "/auth/login",
        json={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="test_employee")
def test_employee_fixture(session: Session):
    employee = Employee(
        user_id=1,
        position="Developer",
        specialization="Python",
        current_workload_json='{"current_tasks": 0, "total_complexity": 0.0, "max_workload": 10.0}',
        skills_json='[]',
        is_available=True
    )
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


class TestEmployeeAPI:
    def test_create_employee(self, client: TestClient, auth_headers: dict):
        employee_data = {
            "user_id": 2,
            "position": "Senior Developer",
            "specialization": "Python",
            "is_available": True
        }
        response = client.post(
            "/employees/",
            json=employee_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["position"] == employee_data["position"]
        assert data["specialization"] == employee_data["specialization"]

    def test_get_employees(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        response = client.get("/employees/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_employee(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        response = client.get(
            f"/employees/{test_employee.employee_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == test_employee.employee_id

    def test_update_employee_availability(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        response = client.put(
            f"/employees/{test_employee.employee_id}/availability",
            json={"is_available": False},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "availability updated" in data["message"].lower()


class TestSkillsAPI:
    def test_add_skill(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        skill_data = {
            "name": "Python",
            "level": "middle",
            "years_of_experience": 3.5
        }
        response = client.post(
            f"/employees/{test_employee.employee_id}/skills",
            json=skill_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "Skill Python added" in response.json()["message"]

    def test_get_qualification(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        # Сначала добавляем навыки
        skills = [
            {"name": "Python", "level": "middle", "years_of_experience": 3.5},
            {"name": "FastAPI", "level": "junior", "years_of_experience": 1.0}
        ]
        for skill in skills:
            client.post(
                f"/employees/{test_employee.employee_id}/skills",
                json=skill,
                headers=auth_headers
            )

        # Проверяем квалификацию
        response = client.get(
            f"/employees/{test_employee.employee_id}/qualification",
            params={
                "required_skills": ["Python", "FastAPI", "Django"],
                "min_level": "middle"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_qualification_score" in data
        assert "Django" in data["missing_skills"]
        assert "FastAPI" in data["low_level_skills"]


class TestTaskAPI:
    def test_create_task(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "complexity": "medium",
            "assignee": test_employee.employee_id
        }
        response = client.post(
            "/v1/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["assignee"] == task_data["assignee"]

    def test_get_tasks(self, client: TestClient, auth_headers: dict):
        response = client.get("/v1/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_reassign_task(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        # Сначала создаем задачу
        task_data = {
            "title": "Task to Reassign",
            "description": "Will be reassigned",
            "complexity": "medium",
            "assignee": test_employee.employee_id
        }
        create_response = client.post(
            "/v1/tasks",
            json=task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["task_id"]

        # Пытаемся переназначить задачу
        response = client.put(
            f"/v1/tasks/{task_id}/reassign",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "reassigned" in data["message"].lower()


class TestErrorHandling:
    def test_invalid_employee_id(self, client: TestClient, auth_headers: dict):
        response = client.get("/employees/999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_invalid_task_id(self, client: TestClient, auth_headers: dict):
        response = client.get("/v1/tasks/999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unauthorized_access(self, client: TestClient, test_employee: Employee):
        response = client.get(f"/employees/{test_employee.employee_id}")
        assert response.status_code == 401

    def test_invalid_skill_level(self, client: TestClient, auth_headers: dict, test_employee: Employee):
        skill_data = {
            "name": "Python",
            "level": "invalid_level",
            "years_of_experience": 3.5
        }
        response = client.post(
            f"/employees/{test_employee.employee_id}/skills",
            json=skill_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation Error 