from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Dict
from ..db import get_session
from ..schemas.employee import Employee, EmployeeWorkload, Skill, SkillLevel
from ..auth.auth_handler import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/", response_model=Employee)
def create_employee(
    employee: Employee,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    db_employee = Employee.from_orm(employee)
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


@router.get("/", response_model=List[Employee])
def read_employees(
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    employees = session.query(Employee).all()
    return employees


@router.get("/{employee_id}", response_model=Employee)
def read_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}/availability")
def update_availability(
    employee_id: int,
    is_available: bool,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.is_available = is_available
    session.add(employee)
    session.commit()
    session.refresh(employee)
    
    return {"message": f"Employee availability updated to {is_available}"}


@router.post("/{employee_id}/skills")
def add_employee_skill(
    employee_id: int,
    skill: Skill,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    current_skills = employee.skills
    current_skills.append(skill)
    employee.skills = current_skills
    
    session.add(employee)
    session.commit()
    session.refresh(employee)
    
    return {"message": f"Skill {skill.name} added to employee {employee_id}"}


@router.get("/{employee_id}/qualification")
def get_employee_qualification(
    employee_id: int,
    required_skills: List[str],
    min_level: SkillLevel = SkillLevel.JUNIOR,
    session: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_user)
):
    """
    Оценивает квалификацию сотрудника на основе требуемых навыков.
    
    Параметры:
    - required_skills: список требуемых навыков
    - min_level: минимальный требуемый уровень навыка (junior/middle/senior)
    
    Возвращает:
    - общую оценку квалификации (0-100)
    - детальную информацию по каждому навыку
    - рекомендации по улучшению
    """
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Оценка навыков
    skill_scores = {}
    missing_skills = []
    low_level_skills = []
    
    # Преобразуем список навыков сотрудника в словарь для быстрого поиска
    employee_skills = {skill.name: skill for skill in employee.skills}
    
    # Оцениваем каждый требуемый навык
    for skill_name in required_skills:
        if skill_name not in employee_skills:
            missing_skills.append(skill_name)
            skill_scores[skill_name] = 0
            continue
            
        skill = employee_skills[skill_name]
        
        # Оценка уровня навыка
        level_score = {
            SkillLevel.JUNIOR: 1,
            SkillLevel.MIDDLE: 2,
            SkillLevel.SENIOR: 3
        }[skill.level]
        
        required_level = {
            SkillLevel.JUNIOR: 1,
            SkillLevel.MIDDLE: 2,
            SkillLevel.SENIOR: 3
        }[min_level]
        
        if level_score < required_level:
            low_level_skills.append(skill_name)
        
        # Оценка опыта (максимум 5 лет)
        experience_score = min(skill.years_of_experience / 5, 1)
        
        # Итоговая оценка навыка (уровень * 0.7 + опыт * 0.3)
        skill_scores[skill_name] = (level_score / 3 * 0.7 + experience_score * 0.3) * 100
    
    # Общая оценка квалификации
    total_score = sum(skill_scores.values()) / len(required_skills) if required_skills else 0
    
    # Формируем рекомендации
    recommendations = []
    if missing_skills:
        recommendations.append(f"Необходимо приобрести навыки: {', '.join(missing_skills)}")
    if low_level_skills:
        recommendations.append(f"Требуется повысить уровень навыков: {', '.join(low_level_skills)}")
    
    return {
        "employee_id": employee_id,
        "total_qualification_score": round(total_score, 2),
        "skill_scores": skill_scores,
        "missing_skills": missing_skills,
        "low_level_skills": low_level_skills,
        "recommendations": recommendations
    } 