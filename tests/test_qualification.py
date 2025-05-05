import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.db import get_session
from app.schemas.employee import Employee, Skill, SkillLevel
from app.schemas.task import TaskComplexity
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


def test_add_skill_to_employee(client: TestClient, test_employee: Employee):
    # Сначала нужно получить токен авторизации
    auth_response = client.post(
        "/auth/login",
        json={"username": "test@example.com", "password": "testpassword"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]

    # Добавляем навык
    skill_data = {
        "name": "Python",
        "level": "middle",
        "years_of_experience": 3.5
    }
    response = client.post(
        f"/employees/{test_employee.employee_id}/skills",
        json=skill_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Skill Python added to employee" in response.json()["message"]


def test_get_employee_qualification(client: TestClient, test_employee: Employee):
    # Получаем токен авторизации
    auth_response = client.post(
        "/auth/login",
        json={"username": "test@example.com", "password": "testpassword"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]

    # Добавляем несколько навыков
    skills = [
        {"name": "Python", "level": "middle", "years_of_experience": 3.5},
        {"name": "FastAPI", "level": "junior", "years_of_experience": 1.0}
    ]
    for skill in skills:
        client.post(
            f"/employees/{test_employee.employee_id}/skills",
            json=skill,
            headers={"Authorization": f"Bearer {token}"}
        )

    # Проверяем квалификацию
    response = client.get(
        f"/employees/{test_employee.employee_id}/qualification",
        params={
            "required_skills": ["Python", "FastAPI", "Django"],
            "min_level": "middle"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Проверяем структуру ответа
    assert "total_qualification_score" in data
    assert "skill_scores" in data
    assert "missing_skills" in data
    assert "low_level_skills" in data
    assert "recommendations" in data
    
    # Проверяем конкретные значения
    assert "Django" in data["missing_skills"]
    assert "FastAPI" in data["low_level_skills"]
    assert data["skill_scores"]["Python"] > data["skill_scores"]["FastAPI"]


def test_qualification_with_invalid_employee(client: TestClient):
    # Получаем токен авторизации
    auth_response = client.post(
        "/auth/login",
        json={"username": "test@example.com", "password": "testpassword"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]

    # Проверяем несуществующего сотрудника
    response = client.get(
        "/employees/999/qualification",
        params={"required_skills": ["Python"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "Employee not found" in response.json()["detail"]


def test_qualification_without_auth(client: TestClient, test_employee: Employee):
    # Проверяем доступ без авторизации
    response = client.get(
        f"/employees/{test_employee.employee_id}/qualification",
        params={"required_skills": ["Python"]}
    )
    assert response.status_code == 401


def test_qualification_with_empty_skills(client: TestClient, test_employee: Employee):
    # Получаем токен авторизации
    auth_response = client.post(
        "/auth/login",
        json={"username": "test@example.com", "password": "testpassword"}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]

    # Проверяем с пустым списком навыков
    response = client.get(
        f"/employees/{test_employee.employee_id}/qualification",
        params={"required_skills": []},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_qualification_score"] == 0
    assert len(data["skill_scores"]) == 0
    assert len(data["missing_skills"]) == 0
    assert len(data["low_level_skills"]) == 0 