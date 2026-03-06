from models import init_db, get_session, User, Project, Task, Rate, TimeLog
import datetime

def seed():
    init_db()
    session = get_session()

    # 1. 建立使用者
    hr = User(username='hr_admin', password='password', role='HR')
    pm = User(username='pm_user', password='password', role='PM')
    dev1 = User(username='dev_alice', password='password', role='DEV')
    dev2 = User(username='dev_bob', password='password', role='DEV')
    
    session.add_all([hr, pm, dev1, dev2])
    session.commit()

    # 2. 建立費率 (HR 設定)
    r1 = Rate(user_id=dev1.id, hourly_rate=50.0) # Alice $50/hr
    r2 = Rate(user_id=dev2.id, hourly_rate=40.0) # Bob $40/hr
    session.add_all([r1, r2])
    session.commit()

    # 3. 建立專案 (PM 設定)
    p1 = Project(
        name='新核心系統開發', 
        description='開發公司下一代核心業務系統',
        benefit_description='提升 20% 營運效率',
        budget=10000.0, 
        priority='H'
    )
    p2 = Project(
        name='內部入口網站', 
        description='整合各部門資訊平台',
        benefit_description='優化跨部門溝通',
        budget=5000.0, 
        priority='M'
    )
    session.add_all([p1, p2])
    session.commit()

    # 4. 建立任務 (PM 指派)
    t1 = Task(name='資料庫設計', project_id=p1.id, assigned_to=dev1.id, estimated_hours=10)
    t2 = Task(name='API 介面開發', project_id=p1.id, assigned_to=dev1.id, estimated_hours=20)
    t3 = Task(name='前端頁面製作', project_id=p2.id, assigned_to=dev2.id, estimated_hours=15)
    session.add_all([t1, t2, t3])
    session.commit()

    print("資料庫初始化與模擬數據建立完成！")
    session.close()

if __name__ == "__main__":
    seed()
