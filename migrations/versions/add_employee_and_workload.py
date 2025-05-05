"""add employee and workload

Revision ID: add_employee_and_workload
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_employee_and_workload'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создаем enum для сложности задач
    task_complexity = postgresql.ENUM('easy', 'medium', 'hard', name='taskcomplexity')
    task_complexity.create(op.get_bind())

    # Создаем таблицу сотрудников
    op.create_table(
        'employee',
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('current_workload', postgresql.JSONB(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
        sa.PrimaryKeyConstraint('employee_id')
    )

    # Обновляем таблицу задач
    op.add_column('task', sa.Column('complexity', sa.Enum('easy', 'medium', 'hard', name='taskcomplexity'), nullable=False, server_default='medium'))
    op.add_column('task', sa.Column('status', sa.String(), nullable=False, server_default='new'))
    op.drop_constraint('task_assignee_fkey', 'task', type_='foreignkey')
    op.create_foreign_key('task_assignee_fkey', 'task', 'employee', ['assignee'], ['employee_id'])


def downgrade():
    # Удаляем внешний ключ и колонки из таблицы задач
    op.drop_constraint('task_assignee_fkey', 'task', type_='foreignkey')
    op.drop_column('task', 'status')
    op.drop_column('task', 'complexity')
    op.create_foreign_key('task_assignee_fkey', 'task', 'user', ['assignee'], ['user_id'])

    # Удаляем таблицу сотрудников
    op.drop_table('employee')

    # Удаляем enum
    task_complexity = postgresql.ENUM(name='taskcomplexity')
    task_complexity.drop(op.get_bind()) 