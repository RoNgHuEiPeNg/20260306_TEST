from models import get_session, Project, Task, TimeLog, User
import pandas as pd
import io

def export_project_summary_to_excel(df):
    """
    將專案摘要 DataFrame 轉換為 Excel 二進位流。
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='專案摘要')
    return output.getvalue()

def export_project_details_to_excel(project_id):
    """
    匯出特定專案的詳細工時紀錄與成本（含費率快照）。
    """
    session = get_session()
    logs = session.query(
        TimeLog.created_at.label('日期'),
        User.username.label('執行人'),
        Task.name.label('任務名稱'),
        TimeLog.hours.label('工時'),
        TimeLog.applied_rate.label('當時費率'),
        TimeLog.total_cost.label('小計成本')
    ).join(Task, TimeLog.task_id == Task.id)\
     .join(User, TimeLog.user_id == User.id)\
     .filter(Task.project_id == project_id).all()
    
    project_name = session.query(Project.name).filter(Project.id == project_id).scalar()
    session.close()
    
    df = pd.DataFrame(logs)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'專案_{project_id}_明細')
        
    return output.getvalue(), project_name
