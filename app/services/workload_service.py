from typing import List, Optional
from sqlmodel import Session, select
from ..schemas.employee import Employee, EmployeeWorkload, TaskComplexity
from ..schemas.task import Task


class WorkloadService:
    def __init__(self, db: Session):
        self.db = db

    def get_employee_workload(self, employee_id: int) -> EmployeeWorkload:
        employee = self.db.get(Employee, employee_id)
        if not employee:
            raise ValueError(f"Employee with id {employee_id} not found")
        return employee.current_workload

    def update_employee_workload(self, employee_id: int, task_complexity: TaskComplexity, is_adding: bool = True):
        employee = self.db.get(Employee, employee_id)
        if not employee:
            raise ValueError(f"Employee with id {employee_id} not found")

        complexity_values = {
            TaskComplexity.EASY: 1.0,
            TaskComplexity.MEDIUM: 2.0,
            TaskComplexity.HARD: 3.0
        }

        if is_adding:
            employee.current_workload.current_tasks += 1
            employee.current_workload.total_complexity += complexity_values[task_complexity]
        else:
            employee.current_workload.current_tasks -= 1
            employee.current_workload.total_complexity -= complexity_values[task_complexity]

        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

    def find_available_employee(self, task_complexity: TaskComplexity) -> Optional[Employee]:
        """Находит доступного сотрудника с наименьшей загруженностью"""
        employees = self.db.exec(
            select(Employee)
            .where(Employee.is_available == True)
            .order_by(Employee.current_workload.total_complexity)
        ).all()

        for employee in employees:
            if employee.current_workload.can_take_task(task_complexity):
                return employee

        return None

    def reassign_task(self, task_id: int) -> Optional[Employee]:
        """Переназначает задачу другому сотруднику"""
        task = self.db.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        # Освобождаем текущего сотрудника
        self.update_employee_workload(task.assignee, task.complexity, is_adding=False)

        # Ищем нового сотрудника
        new_assignee = self.find_available_employee(task.complexity)
        if new_assignee:
            task.assignee = new_assignee.employee_id
            task.status = "reassigned"
            self.update_employee_workload(new_assignee.employee_id, task.complexity, is_adding=True)
            self.db.add(task)
            self.db.commit()
            return new_assignee

        return None 