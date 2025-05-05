import pytest
from datetime import date, timedelta
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.schemas.employee import Employee, TaskComplexity, EmployeeWorkload
from app.schemas.task import Task, TaskCreate
from app.services.workload_service import WorkloadService


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def workload_service(db_session):
    return WorkloadService(db_session)


@pytest.fixture
def test_employees(db_session):
    # Создаем тестовых сотрудников
    employees = [
        Employee(
            user_id=1,
            position="Developer",
            specialization="Python",
            current_workload=EmployeeWorkload(),
            is_available=True
        ),
        Employee(
            user_id=2,
            position="Developer",
            specialization="Python",
            current_workload=EmployeeWorkload(),
            is_available=True
        )
    ]
    for employee in employees:
        db_session.add(employee)
    db_session.commit()
    return employees


def test_create_task_with_workload(db_session, workload_service, test_employees):
    # Создаем задачу для первого сотрудника
    task = TaskCreate(
        task_description="Test task",
        assignee=test_employees[0].employee_id,
        complexity=TaskComplexity.MEDIUM,
        due_date=date.today() + timedelta(days=1)
    )
    
    # Проверяем начальную загруженность
    initial_workload = workload_service.get_employee_workload(test_employees[0].employee_id)
    assert initial_workload.current_tasks == 0
    assert initial_workload.total_complexity == 0.0
    
    # Создаем задачу
    db_task = Task.from_orm(task)
    db_session.add(db_task)
    db_session.commit()
    
    # Обновляем загруженность
    workload_service.update_employee_workload(db_task.assignee, db_task.complexity)
    
    # Проверяем обновленную загруженность
    updated_workload = workload_service.get_employee_workload(test_employees[0].employee_id)
    assert updated_workload.current_tasks == 1
    assert updated_workload.total_complexity == 2.0  # MEDIUM task = 2.0 complexity


def test_reassign_task(db_session, workload_service, test_employees):
    # Создаем задачу для первого сотрудника
    task = TaskCreate(
        task_description="Test task",
        assignee=test_employees[0].employee_id,
        complexity=TaskComplexity.HARD,
        due_date=date.today() + timedelta(days=1)
    )
    
    db_task = Task.from_orm(task)
    db_session.add(db_task)
    db_session.commit()
    
    # Обновляем загруженность первого сотрудника
    workload_service.update_employee_workload(db_task.assignee, db_task.complexity)
    
    # Переназначаем задачу
    new_assignee = workload_service.reassign_task(db_task.task_id)
    
    # Проверяем, что задача переназначена второму сотруднику
    assert new_assignee.employee_id == test_employees[1].employee_id
    
    # Проверяем загруженность обоих сотрудников
    workload1 = workload_service.get_employee_workload(test_employees[0].employee_id)
    workload2 = workload_service.get_employee_workload(test_employees[1].employee_id)
    
    assert workload1.current_tasks == 0
    assert workload1.total_complexity == 0.0
    assert workload2.current_tasks == 1
    assert workload2.total_complexity == 3.0  # HARD task = 3.0 complexity


def test_workload_limits(db_session, workload_service, test_employees):
    # Создаем несколько задач для первого сотрудника
    for i in range(4):
        task = TaskCreate(
            task_description=f"Test task {i}",
            assignee=test_employees[0].employee_id,
            complexity=TaskComplexity.MEDIUM,
            due_date=date.today() + timedelta(days=1)
        )
        db_task = Task.from_orm(task)
        db_session.add(db_task)
        db_session.commit()
        workload_service.update_employee_workload(db_task.assignee, db_task.complexity)
    
    # Проверяем загруженность
    workload = workload_service.get_employee_workload(test_employees[0].employee_id)
    assert workload.current_tasks == 4
    assert workload.total_complexity == 8.0  # 4 MEDIUM tasks = 8.0 complexity
    
    # Пытаемся создать еще одну задачу
    task = TaskCreate(
        task_description="Overload task",
        assignee=test_employees[0].employee_id,
        complexity=TaskComplexity.HARD,
        due_date=date.today() + timedelta(days=1)
    )
    
    # Проверяем, что сотрудник не может взять еще одну задачу
    assert not workload.can_take_task(TaskComplexity.HARD) 