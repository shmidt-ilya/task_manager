from sqlmodel import Session, SQLModel, create_engine, select
from app.schemas.task import User, Project
from app.schemas.employee import Employee, Skill, SkillLevel
from app.schemas.task import Task, TaskComplexity
from datetime import date, timedelta
import json
import os

# Создаем директорию для базы данных, если она не существует
os.makedirs("data", exist_ok=True)

# Создаем подключение к базе данных SQLite
DB_URL = "sqlite:///data/taskman.db"
engine = create_engine(DB_URL, echo=True)

def init_db():
    # Создаем все таблицы
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Проверяем, есть ли уже пользователи в базе
        existing_users = session.exec(select(User)).all()
        if not existing_users:
            # Создаем тестовых пользователей
            users = [
                User(
                    name="Иван Иванов",
                    email="ivan@example.com",
                    password="password123"
                ),
                User(
                    name="Петр Петров",
                    email="petr@example.com",
                    password="password123"
                ),
                User(
                    name="Анна Сидорова",
                    email="anna@example.com",
                    password="password123"
                ),
                User(
                    name="Мария Кузнецова",
                    email="maria@example.com",
                    password="password123"
                ),
                User(
                    name="Алексей Смирнов",
                    email="alexey@example.com",
                    password="password123"
                ),
                User(
                    name="Елена Новикова",
                    email="elena@example.com",
                    password="password123"
                )
            ]
            
            for user in users:
                session.add(user)
            session.commit()
            
            # Проверяем, есть ли уже проекты в базе
            existing_projects = session.exec(select(Project)).all()
            if not existing_projects:
                # Создаем тестовые проекты
                projects = [
                    Project(
                        project_name="Разработка API",
                        project_description="Разработка REST API для системы управления задачами"
                    ),
                    Project(
                        project_name="Тестирование",
                        project_description="Написание тестов для API"
                    ),
                    Project(
                        project_name="Документация",
                        project_description="Создание технической документации"
                    )
                ]
                
                for project in projects:
                    session.add(project)
                session.commit()
                
                # Создаем тестовых сотрудников
                employees = [
                    Employee(
                        user_id=users[0].user_id,
                        position="Senior Developer",
                        specialization="Python",
                        current_workload_json=json.dumps({
                            "current_tasks": 0,
                            "total_complexity": 0.0,
                            "max_workload": 10.0
                        }),
                        skills_json=json.dumps([
                            {
                                "name": "Python",
                                "level": "senior",
                                "years_of_experience": 5.0
                            },
                            {
                                "name": "FastAPI",
                                "level": "middle",
                                "years_of_experience": 2.0
                            }
                        ]),
                        is_available=True
                    ),
                    Employee(
                        user_id=users[1].user_id,
                        position="Developer",
                        specialization="Python",
                        current_workload_json=json.dumps({
                            "current_tasks": 0,
                            "total_complexity": 0.0,
                            "max_workload": 8.0
                        }),
                        skills_json=json.dumps([
                            {
                                "name": "Python",
                                "level": "middle",
                                "years_of_experience": 3.0
                            },
                            {
                                "name": "Django",
                                "level": "junior",
                                "years_of_experience": 1.0
                            }
                        ]),
                        is_available=True
                    ),
                    Employee(
                        user_id=users[2].user_id,
                        position="QA Engineer",
                        specialization="Testing",
                        current_workload_json=json.dumps({
                            "current_tasks": 0,
                            "total_complexity": 0.0,
                            "max_workload": 7.0
                        }),
                        skills_json=json.dumps([
                            {
                                "name": "Python",
                                "level": "middle",
                                "years_of_experience": 2.0
                            },
                            {
                                "name": "Pytest",
                                "level": "middle",
                                "years_of_experience": 2.0
                            }
                        ]),
                        is_available=True
                    ),
                    Employee(
                        user_id=users[3].user_id,
                        position="Technical Writer",
                        specialization="Documentation",
                        current_workload_json=json.dumps({
                            "current_tasks": 0,
                            "total_complexity": 0.0,
                            "max_workload": 6.0
                        }),
                        skills_json=json.dumps([
                            {
                                "name": "Technical Writing",
                                "level": "senior",
                                "years_of_experience": 4.0
                            },
                            {
                                "name": "Markdown",
                                "level": "middle",
                                "years_of_experience": 3.0
                            }
                        ]),
                        is_available=True
                    ),
                    Employee(
                        user_id=users[4].user_id,
                        position="DevOps Engineer",
                        specialization="Infrastructure",
                        current_workload_json=json.dumps({
                            "current_tasks": 0,
                            "total_complexity": 0.0,
                            "max_workload": 9.0
                        }),
                        skills_json=json.dumps([
                            {
                                "name": "Docker",
                                "level": "senior",
                                "years_of_experience": 4.0
                            },
                            {
                                "name": "Kubernetes",
                                "level": "middle",
                                "years_of_experience": 2.0
                            }
                        ]),
                        is_available=True
                    ),
                    Employee(
                        user_id=users[5].user_id,
                        position="Frontend Developer",
                        specialization="JavaScript",
                        current_workload_json=json.dumps({
                            "current_tasks": 0,
                            "total_complexity": 0.0,
                            "max_workload": 8.0
                        }),
                        skills_json=json.dumps([
                            {
                                "name": "JavaScript",
                                "level": "senior",
                                "years_of_experience": 4.0
                            },
                            {
                                "name": "React",
                                "level": "middle",
                                "years_of_experience": 3.0
                            }
                        ]),
                        is_available=True
                    )
                ]
                
                for employee in employees:
                    session.add(employee)
                session.commit()
                
                # Создаем тестовые задачи
                tasks = [
                    Task(
                        task_description="Разработать API для управления задачами",
                        assignee=employees[0].employee_id,
                        complexity=TaskComplexity.HARD,
                        due_date=date.today() + timedelta(days=7),
                        project=projects[0].project_id,
                        status="new"
                    ),
                    Task(
                        task_description="Написать тесты для API",
                        assignee=employees[2].employee_id,
                        complexity=TaskComplexity.MEDIUM,
                        due_date=date.today() + timedelta(days=5),
                        project=projects[1].project_id,
                        status="new"
                    ),
                    Task(
                        task_description="Добавить документацию API",
                        assignee=employees[3].employee_id,
                        complexity=TaskComplexity.EASY,
                        due_date=date.today() + timedelta(days=3),
                        project=projects[2].project_id,
                        status="new"
                    ),
                    Task(
                        task_description="Настроить CI/CD пайплайн",
                        assignee=employees[4].employee_id,
                        complexity=TaskComplexity.HARD,
                        due_date=date.today() + timedelta(days=10),
                        project=projects[0].project_id,
                        status="new"
                    ),
                    Task(
                        task_description="Разработать пользовательский интерфейс",
                        assignee=employees[5].employee_id,
                        complexity=TaskComplexity.MEDIUM,
                        due_date=date.today() + timedelta(days=14),
                        project=projects[0].project_id,
                        status="new"
                    )
                ]
                
                for task in tasks:
                    session.add(task)
                session.commit()

if __name__ == "__main__":
    init_db() 