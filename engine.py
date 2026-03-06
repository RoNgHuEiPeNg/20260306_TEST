from models import get_session, User, Project, Task, Rate, TimeLog
import pandas as pd
import datetime
from sqlalchemy import func

def get_current_rate(user_id):
    """
    獲取使用者當前最新的費率。
    """
    session = get_session()
    rate = session.query(Rate).filter(Rate.user_id == user_id).order_by(Rate.effective_date.desc(), Rate.id.desc()).first()
    session.close()
    return rate.hourly_rate if rate else 0.0

def add_time_log(user_id, task_id, hours):
    """
    提交工時紀錄，並執行成本快照。
    """
    rate = get_current_rate(user_id)
    total_cost = hours * rate
    
    session = get_session()
    log = TimeLog(
        user_id=user_id,
        task_id=task_id,
        hours=hours,
        applied_rate=rate,
        total_cost=total_cost
    )
    session.add(log)
    session.commit()
    session.close()
    return True

def get_projects_summary_df():
    """
    獲取所有專案的摘要數據。
    包含：專案名稱, 預算, 實際支出, 進度, 優先級。
    """
    session = get_session()
    projects = session.query(Project).all()
    
    data = []
    for p in projects:
        # 計算實際支出
        actual_cost = session.query(func.sum(TimeLog.total_cost))\
            .join(Task, TimeLog.task_id == Task.id)\
            .filter(Task.project_id == p.id).scalar() or 0.0
        
        # 計算進度 (以任務完成數計)
        total_tasks = session.query(func.count(Task.id)).filter(Task.project_id == p.id).scalar() or 0
        done_tasks = session.query(func.count(Task.id)).filter(Task.project_id == p.id, Task.status == 'Done').scalar() or 0
        progress = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        # 計算總預計工時 vs 總實際工時
        total_est = session.query(func.sum(Task.estimated_hours)).filter(Task.project_id == p.id).scalar() or 0.0
        total_act = session.query(func.sum(TimeLog.hours))\
            .join(Task, TimeLog.task_id == Task.id)\
            .filter(Task.project_id == p.id).scalar() or 0.0
            
        data.append({
            "專案 ID": p.id,
            "專案名稱": p.name,
            "預算": p.budget,
            "實際支出": actual_cost,
            "預算執行率": (actual_cost / p.budget * 100) if p.budget > 0 else 0.0,
            "進度": progress,
            "優先級": p.priority,
            "狀態": p.status,
            "預計總工時": total_est,
            "實際總工時": total_act
        })
    
    session.close()
    return pd.DataFrame(data)

def get_user_load_df():
    """
    獲取每位使用者的工時佔比。
    """
    session = get_session()
    # 這裡簡單統計所有紀錄，實際應用可加入時間區間過濾
    user_hours = session.query(User.username, func.sum(TimeLog.hours))\
        .join(TimeLog, User.id == TimeLog.user_id)\
        .group_by(User.id).all()
    
    session.close()
    return pd.DataFrame(user_hours, columns=["使用者", "總工時"])

def get_user_tasks(user_id):
    """
    獲取指派給特定使用者的任務。
    """
    session = get_session()
    tasks = session.query(Task).filter(Task.assigned_to == user_id).all()
    data = []
    for t in tasks:
        # 獲取專案名稱
        project_name = session.query(Project.name).filter(Project.id == t.project_id).scalar()
        data.append({
            "任務 ID": t.id,
            "任務名稱": t.name,
            "專案名稱": project_name,
            "預計工時": t.estimated_hours,
            "目前狀態": t.status
        })
    session.close()
    return pd.DataFrame(data)

def update_task_status(task_id, new_status):
    session = get_session()
    task = session.query(Task).get(task_id)
    if task:
        task.status = new_status
        session.commit()
    session.close()
