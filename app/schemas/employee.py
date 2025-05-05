from enum import Enum
from sqlmodel import SQLModel, Field as SQLField
from pydantic import BaseModel
from typing import Optional, Dict, List
import json


class TaskComplexity(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SkillLevel(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"


class Skill(BaseModel):
    name: str
    level: SkillLevel
    years_of_experience: float

    def dict(self) -> Dict:
        return {
            "name": self.name,
            "level": self.level,
            "years_of_experience": self.years_of_experience
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Skill":
        return cls(**data)


class EmployeeWorkload(BaseModel):
    current_tasks: int = 0
    total_complexity: float = 0.0  # Сумма сложности всех текущих задач
    max_workload: float = 10.0  # Максимальная допустимая загруженность

    @property
    def workload_percentage(self) -> float:
        return (self.total_complexity / self.max_workload) * 100

    def can_take_task(self, complexity: TaskComplexity) -> bool:
        complexity_values = {
            TaskComplexity.EASY: 1.0,
            TaskComplexity.MEDIUM: 2.0,
            TaskComplexity.HARD: 3.0
        }
        return (self.total_complexity + complexity_values[complexity]) <= self.max_workload

    def dict(self) -> Dict:
        return {
            "current_tasks": self.current_tasks,
            "total_complexity": self.total_complexity,
            "max_workload": self.max_workload
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EmployeeWorkload":
        return cls(**data)


class Employee(SQLModel, table=True):
    employee_id: int = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="user.user_id")
    position: str
    specialization: str
    current_workload_json: str = SQLField(default='{"current_tasks": 0, "total_complexity": 0.0, "max_workload": 10.0}')
    skills_json: str = SQLField(default='[]')  # JSON строка со списком навыков
    is_available: bool = True

    @property
    def current_workload(self) -> EmployeeWorkload:
        return EmployeeWorkload.from_dict(json.loads(self.current_workload_json))

    @current_workload.setter
    def current_workload(self, workload: EmployeeWorkload):
        self.current_workload_json = json.dumps(workload.dict())

    @property
    def skills(self) -> List[Skill]:
        return [Skill.from_dict(skill) for skill in json.loads(self.skills_json)]

    @skills.setter
    def skills(self, skills: List[Skill]):
        self.skills_json = json.dumps([skill.dict() for skill in skills])