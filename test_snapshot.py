from engine import add_time_log, get_current_rate
from models import get_session, Rate, TimeLog, User
import datetime

def test_rate_snapshot():
    session = get_session()
    
    # 找一個測試開發者 (Alice)
    alice = session.query(User).filter(User.username == 'dev_alice').first()
    task = session.query(Task).first()
    
    print(f"--- 開始測試費率快照 ---")
    
    # 1. 檢查目前費率
    initial_rate = get_current_rate(alice.id)
    print(f"Alice 目前費率: ${initial_rate}")
    
    # 2. 記錄工時 (2 小時)
    add_time_log(alice.id, task.id, 2.0)
    log = session.query(TimeLog).order_by(TimeLog.id.desc()).first()
    print(f"紀錄工時: 2hr, 應用費率: ${log.applied_rate}, 總成本: ${log.total_cost}")
    
    # 3. 調整費率 (調升至 $100)
    new_rate_val = 100.0
    new_rate = Rate(user_id=alice.id, hourly_rate=new_rate_val, effective_date=datetime.date.today())
    session.add(new_rate)
    session.commit()
    print(f"HR 調整 Alice 費率至: ${new_rate_val}")
    
    # 4. 再次檢查目前費率
    updated_rate = get_current_rate(alice.id)
    print(f"Alice 更新後費率: ${updated_rate}")
    
    # 5. 檢查舊紀錄是否受影響
    old_log = session.query(TimeLog).filter(TimeLog.id == log.id).first()
    print(f"檢查舊紀錄 (ID: {old_log.id}):")
    print(f"  舊紀錄費率: ${old_log.applied_rate} (預期應為 ${initial_rate})")
    
    if old_log.applied_rate == initial_rate:
        print("✅ 測試通過：費率快照成功保護歷史數據！")
    else:
        print("❌ 測試失敗：舊紀錄費率被意外更新。")
        
    session.close()

if __name__ == "__main__":
    from models import Task # 補上匯入
    test_rate_snapshot()
