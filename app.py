import streamlit as st
import pandas as pd
import plotly.express as px
from models import get_session, User, Project, Task, Rate, TimeLog
from engine import (
    get_projects_summary_df, 
    get_user_load_df, 
    get_user_tasks, 
    add_time_log, 
    update_task_status
)
from reports import export_project_summary_to_excel, export_project_details_to_excel
import datetime

# 設定頁面配置
st.set_page_config(page_title="專案成本控管系統", layout="wide")

# --- Session State 初始化 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.role = ""

# --- 登入頁面 ---
def login_page():
    st.title("🔐 系統登入")
    with st.form("login_form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        submit = st.form_submit_button("登入")
        
        if submit:
            session = get_session()
            user = session.query(User).filter(User.username == username, User.password == password).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.success(f"歡迎回來, {user.username} ({user.role})")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
            session.close()

# --- 儀表板頁面 ---
def dashboard_page():
    st.title("📊 決策儀表板")
    
    # 專案摘要
    df_projects = get_projects_summary_df()
    
    col1, col2, col3 = st.columns(3)
    total_budget = df_projects['預算'].sum()
    total_spent = df_projects['實際支出'].sum()
    
    col1.metric("總預算", f"${total_budget:,.0f}")
    col2.metric("總實際支出", f"${total_spent:,.0f}", delta=f"{(total_spent/total_budget*100 if total_budget > 0 else 0):.1f}% 執行率", delta_color="inverse")
    col3.metric("活躍專案數", len(df_projects[df_projects['狀態'] == 'Active']))
    
    st.subheader("專案預算執行概況")
    fig_budget = px.bar(
        df_projects, 
        x="專案名稱", 
        y=["預算", "實際支出"], 
        barmode="group",
        title="預算 vs 實際支出",
        labels={"value": "金額 (USD)", "variable": "類別"}
    )
    st.plotly_chart(fig_budget, use_container_width=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("專案進度 (%)")
        fig_progress = px.pie(df_projects, values="進度", names="專案名稱", title="各專案進度佔比")
        st.plotly_chart(fig_progress, use_container_width=True)
        
    with col_b:
        st.subheader("資源負載概況 (總工時)")
        df_load = get_user_load_df()
        if not df_load.empty:
            fig_load = px.bar(df_load, x="使用者", y="總工時", color="使用者", title="成員投入工時統計")
            st.plotly_chart(fig_load, use_container_width=True)
        else:
            st.info("尚無工時紀錄")

# --- 專案管理頁面 (PM/HR) ---
def project_management_page():
    st.title("📁 專案管理")
    
    tab1, tab2 = st.tabs(["專案列表", "新增專案"])
    
    with tab1:
        df_projects = get_projects_summary_df()
        st.dataframe(df_projects, use_container_width=True)
        
        # 匯出功能
        if st.button("匯出專案摘要報表 (Excel)"):
            excel_data = export_project_summary_to_excel(df_projects)
            st.download_button(
                label="點此下載 Excel",
                data=excel_data,
                file_name=f"Project_Summary_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        st.divider()
        st.subheader("專案詳細明細匯出")
        selected_p = st.selectbox("選擇專案以匯出詳細工時明細", df_projects['專案 ID'].tolist(), format_func=lambda x: df_projects[df_projects['專案 ID']==x]['專案名稱'].values[0])
        if st.button("匯出該專案明細"):
            excel_data, p_name = export_project_details_to_excel(selected_p)
            st.download_button(
                label=f"下載 {p_name} 明細",
                data=excel_data,
                file_name=f"Details_{p_name}_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab2:
        with st.form("new_project_form"):
            name = st.text_input("專案名稱")
            desc = st.text_area("專案描述")
            benefit = st.text_area("效益說明 (ROI)")
            budget = st.number_input("預算上限", min_value=0.0)
            priority = st.selectbox("優先級", ["H", "M", "L"])
            submit = st.form_submit_button("建立專案")
            
            if submit:
                session = get_session()
                new_p = Project(name=name, description=desc, benefit_description=benefit, budget=budget, priority=priority)
                session.add(new_p)
                session.commit()
                session.close()
                st.success("專案建立成功！")
                st.rerun()

# --- 任務與工時頁面 (Dev) ---
def task_tracking_page():
    st.title("📝 我的任務與工時填報")
    
    df_tasks = get_user_tasks(st.session_state.user_id)
    if df_tasks.empty:
        st.info("目前沒有指派給您的任務。")
        return
        
    st.subheader("待辦任務清單")
    st.dataframe(df_tasks, use_container_width=True)
    
    st.divider()
    st.subheader("回報進度與工時")
    
    with st.form("time_log_form"):
        task_id = st.selectbox("選擇任務", df_tasks['任務 ID'].tolist(), format_func=lambda x: df_tasks[df_tasks['任務 ID']==x]['任務名稱'].values[0])
        hours = st.number_input("投入小時數", min_value=0.1, step=0.5)
        new_status = st.selectbox("更新任務狀態", ["To Do", "In Progress", "Done"])
        submit = st.form_submit_button("提交工時紀錄")
        
        if submit:
            if add_time_log(st.session_state.user_id, task_id, hours):
                update_task_status(task_id, new_status)
                st.success("工時已記錄並執行成本快照！")
                st.rerun()

# --- 費率與人員設定頁面 (HR) ---
def hr_management_page():
    st.title("💰 費率與人員設定")
    
    session = get_session()
    users = session.query(User).all()
    
    st.subheader("人員名冊與目前費率")
    user_data = []
    for u in users:
        from engine import get_current_rate
        current_rate = get_current_rate(u.id)
        user_data.append({
            "ID": u.id,
            "帳號": u.username,
            "角色": u.role,
            "目前時薪 (USD)": current_rate
        })
    st.table(user_data)
    
    st.divider()
    st.subheader("更新費率")
    with st.form("update_rate_form"):
        u_id = st.selectbox("選擇員工", [u.id for u in users], format_func=lambda x: next(user['帳號'] for user in user_data if user['ID']==x))
        new_rate = st.number_input("新時薪", min_value=0.0)
        eff_date = st.date_input("生效日期", value=datetime.date.today())
        submit = st.form_submit_button("儲存新費率")
        
        if submit:
            rate = Rate(user_id=u_id, hourly_rate=new_rate, effective_date=eff_date)
            session.add(rate)
            session.commit()
            st.success("費率更新成功！後續工時將採用新費率計算。")
            st.rerun()
    session.close()

# --- 主程式控制 ---
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        # 側邊欄導航
        st.sidebar.title(f"👤 {st.session_state.username}")
        st.sidebar.write(f"角色: {st.session_state.role}")
        
        menu = ["📊 決策儀表板"]
        
        # 根據角色過濾選單
        if st.session_state.role in ['PM', 'HR']:
            menu.append("📁 專案管理")
        
        if st.session_state.role == 'DEV':
            menu.append("📝 我的任務")
            
        if st.session_state.role == 'HR':
            menu.append("💰 費率設定")
            
        choice = st.sidebar.radio("選單", menu)
        
        if st.sidebar.button("登出"):
            st.session_state.logged_in = False
            st.rerun()
            
        # 頁面跳轉
        if choice == "📊 決策儀表板":
            dashboard_page()
        elif choice == "📁 專案管理":
            project_management_page()
        elif choice == "📝 我的任務":
            task_tracking_page()
        elif choice == "💰 費率設定":
            hr_management_page()

if __name__ == "__main__":
    main()
