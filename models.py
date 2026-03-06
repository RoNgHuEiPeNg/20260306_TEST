from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) # MVP 階段簡化，實際應用應加密
    role = Column(String, nullable=False) # HR, PM, DEV

    rates = relationship("Rate", back_populates="user")
    time_logs = relationship("TimeLog", back_populates="user")

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    benefit_description = Column(String) # PRD 中的效益說明
    budget = Column(Float, default=0.0)
    priority = Column(String, default='M') # H, M, L
    status = Column(String, default='Active') # Active, Completed, On Hold

    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String, nullable=False)
    description = Column(String)
    assigned_to = Column(Integer, ForeignKey('users.id'))
    estimated_hours = Column(Float, default=0.0)
    status = Column(String, default='To Do') # To Do, In Progress, Done

    project = relationship("Project", back_populates="tasks")
    time_logs = relationship("TimeLog", back_populates="task")

class Rate(Base):
    __tablename__ = 'rates'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hourly_rate = Column(Float, nullable=False)
    effective_date = Column(Date, default=datetime.date.today)

    user = relationship("User", back_populates="rates")

class TimeLog(Base):
    __tablename__ = 'time_logs'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    hours = Column(Float, nullable=False)
    applied_rate = Column(Float, nullable=False) # 費率快照
    total_cost = Column(Float, nullable=False) # hours * applied_rate 快照
    created_at = Column(DateTime, default=datetime.datetime.now)

    task = relationship("Task", back_populates="time_logs")
    user = relationship("User", back_populates="time_logs")

# 資料庫連接設定
ENGINE = create_engine('sqlite:///cost_control.db', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

def init_db():
    Base.metadata.create_all(bind=ENGINE)

def get_session():
    return SessionLocal()
