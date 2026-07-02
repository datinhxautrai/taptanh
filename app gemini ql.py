import streamlit as st
import pandas as pd
import os

# 1. Cấu hình giao diện hiển thị trên di động/máy tính
st.set_page_config(page_title="Hệ Thống Quản Lý MEP Nội Bộ", layout="centered")
st.title("🚧 HỆ THỐNG QUẢN LÝ TIẾN ĐỘ & GIAO VIỆC")

# Tạo thư mục lưu trữ file và database nếu chưa có
if not os.path.exists("stored_files"):
    os.makedirs("stored_files")

DB_USERS_PATH = "stored_files/db_users.csv"
DB_TASKS_PATH = "stored_files/db_tasks.csv"

# 2. KHỞI TẠO CƠ SỞ DỮ LIỆU VĨNH VIỄN (FILE CSV CHẠY NGẦM)
if not os.path.exists(DB_USERS_PATH):
    init_users = {
        "tai_khoan": ["Sir", "PhoBan_MEP", "KeToan_DA"],
        "mat_khau": ["admin123", "phoban2026", "ketoan2026"],
        "quyen": ["admin", "dac_biet", "dac_biet"],
        "trang_thai": ["Hoạt động", "Hoạt động", "Hoạt động"]
    }
    for i in range(1, 22):
        init_users["tai_khoan"].append(f"NhanVien_{i}")
        init_users["mat_khau"].append("nv123")
        init_users["quyen"].append("nhan_vien")
        init_users["trang_thai"].append("Hoạt động")
    pd.DataFrame(init_users).to_csv(DB_USERS_PATH, index=False)

if not os.path.exists(DB_TASKS_PATH):
    init_tasks = [{
        "id": "1",
        "task_name": "Lắp trục đứng MEP tầng 3",
        "assigned_to": "NhanVien_1",
        "status": "Đang triển khai",
        "deadline": "2026-07-05",
        "note": "Cần chú ý cao độ ống thoát nước tầng này.",
        "file_path": "",
        "updated_by": "Hệ thống"
    }]
    pd.DataFrame(init_tasks).to_csv(DB_TASKS_PATH, index=False)

# Đọc dữ liệu luôn ép về dạng chữ (str) để tránh lỗi lệch kiểu dữ liệu
df_users = pd.read_csv(DB_USERS_PATH, dtype=str)
df_tasks = pd.read_csv(DB_TASKS_PATH, dtype=str)

if "notifications" not in st.session_state:
    st.session_state.notifications = ["Hệ thống dữ liệu vĩnh viễn đã được đồng bộ hóa!"]

# 3. XỬ LÝ ĐĂNG NHẬP BẢO MẬT
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_current" not in st.session_state:
    st.session_state.user_current = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if not st.session_state.logged_in:
    st.subheader("🔐 ĐĂNG NHẬP HỆ THỐNG NỘI BỘ")
    user_input = st.text_input("Tên tài khoản đăng nhập:")
    pass_input = st.text_input("Mật khẩu:", type="password")
    
    if st.button("Xác nhận đăng nhập"):
        user_row = df_users[df_users["tai_khoan"] == user_input]
        if not user_row.empty:
            if user_row.iloc[0]["mat_khau"] == pass_input:
                if user_row.iloc[0]["trang_thai"] == "Hoạt động":
                    st.session_state.logged_in = True
                    st.session_state.user_current = user_input
                    st.session_state.user_role = user_row.iloc[0]["quyen"]
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("🛑 Tài khoản của bạn đã bị Khóa/Đình chỉ. Vui lòng liên hệ Sir!")
            else:
                st.error("Sai mật khẩu! Vui lòng kiểm tra lại.")
        else:
            st.error("Tài khoản không tồn tại trên hệ thống!")
    st.stop()

# --- GIAO DIỆN THANH BÊN (SIDEBAR) ---
st.sidebar.markdown(f"👤 Tài khoản: **{st.session_state.user_current}**")
st.sidebar.markdown(f"🎖️ Quyền hạn: `{st.session_state.user_role.upper()}`")
if st.sidebar.button("Đăng xuất khỏi hệ thống"):
    st.session_state.logged_in = False
    st.session_state.user_current = None
    st.session_state.user_role = None
    st.rerun()

# --- BẢNG TIN THÔNG BÁO CHUNG ---
st.subheader("🔔 Bảng Tin Thông Báo Mới Nhất")
for notif in st.session_state.notifications[-2:]:
    st.info(notif)
st.markdown("---")

# ⚙️ --- ĐẶC QUYỀN TỐI CAO CỦA SIR: QUẢN LÝ TÀI KHOẢN TRỰC TIẾP TRÊN APP ---
if st.session_state.user_role == "admin":
    with st.sidebar.expander("⚙️ QUẢN TRỊ TÀI KHOẢN (Chỉ Sir)"):
        st.markdown("**Thay đổi thông tin nhân sự tức thì:**")
        selected_user = st.selectbox("Chọn tài khoản cần xử lý:", df_users["tai_khoan"].tolist())
        
        current_user_info = df_users[df_users["tai_khoan"] == selected_user].iloc[0]
        
        new_pwd = st.text_input("Đổi mật khẩu mới:", value=str(current_user_info["mat_khau"]))
        new_role = st.selectbox("Thay đổi nhóm quyền:", ["admin", "dac_biet", "nhan_vien"], index=["admin", "dac_biet", "nhan_vien"].index(current_user_info["quyen"]))
        new_status = st.radio("Trạng thái tài khoản:", ["Hoạt động", "Bị khóa"], index=["Hoạt động", "Bị khóa"].index(current_user_info["trang_thai"]))
        
        if st.button("Áp dụng lệnh can thiệp"):
            df_users.loc[df_users["tai_khoan"] == selected_user, "mat_khau"] = new_pwd
            df_users.loc[df_users["tai_khoan"] == selected_user, "quyen"] = new_role
            df_users.loc[df_users["tai_khoan"] == selected_user, "trang_thai"] = new_status
            df_users.to_csv(DB_USERS_PATH, index=False)
            
            st.session_state.notifications.append(f"🛠️ Sir vừa can thiệp tài khoản '{selected_user}' (Trạng thái: {new_status})")
            st.success(f"Đã thực thi lệnh lên tài khoản {selected_user} thành công!")
            st.rerun()

    # --- TÍNH NĂNG GIAO VIỆC CỦA SIR ---
    st.subheader("📝 Giao Việc Mới (Đặc quyền của Sir)")
    with st.form("new_task_form", clear_on_submit=True):
        t_name = st.text_input("Tên hạng mục công việc:")
        list_nv_select = df_users[df_users["quyen"] == "nhan_vien"]["tai_khoan"].tolist()
        t_assign = st.selectbox("Giao cho nhân viên chịu trách nhiệm:", list_nv_select)
        t_deadline = st.date_input("Hạn hoàn thành (Deadline):")
        t_note = st.text_area("Ghi chú kỹ thuật / Chỉ thị chi tiết:")
        submit_btn = st.form_submit_button("Phát lệnh giao việc")
        
        if submit_btn and t_name:
            new_id = int(df_tasks["id"].astype(int).max()) + 1 if not df_tasks.empty else 1
            new_row = pd.DataFrame([{
                "id": str(new_id),
                "task_name": t_name,
                "assigned_to": t_assign,
                "status": "Chờ triển khai",
                "deadline": str(t_deadline),
                "note": t_note,
                "file_path": "",
                "updated_by": f"Quản lý ({st.session_state.user_current})"
            }])
            df_tasks = pd.concat([df_tasks, new_row], ignore_index=True)
            df_tasks.to_csv(DB_TASKS_PATH, index=False)
            
            st.session_state.notifications.append(f"📢 Sir vừa phát lệnh việc mới: '{t_name}' giao cho {t_assign}!")
            st.success(f"Đã phát lệnh thành công đến {t_assign}!")
            st.rerun()

# --- NHÓM QUYỀN 2: PHÓ BAN/KẾ TOÁN - XEM BÁO CÁO TỔNG ---
if st.session_state.user_role == "dac_biet":
    st.subheader("📊 Báo Cáo Tổng Hợp Tiến Độ Dự Án")
    if not df_tasks.empty:
        st.columns(3)[0].metric("Tổng đầu việc dự án", len(df_tasks))
        st.dataframe(df_tasks[["task_name", "assigned_to", "status", "deadline", "updated_by"]])
    st.markdown("---")

# --- KHU VỰC DANH SÁCH CÔNG VIỆC & BỘ LỌC BẢO MẬT ---
st.subheader("📋 Danh Sách Hạng Mục Đang Triển Khai")

if not df_tasks.empty:
    for index, row in df_tasks.iterrows():
        cho_phep_xem = False
        if st.session_state.user_role in ["admin", "dac_biet"]:
            cho_phep_xem = True
        elif st.session_state.user_role == "nhan_vien" and row["assigned_to"] == st.session_state.user_current:
            cho_phep_xem = True
             
        if cho_phep_xem:
            with st.expander(f"📌 {row['task_name']} - [{row['status']}]"):
                st.write(f"👷 **Người thực hiện:** {row['assigned_to']}")
                st.write(f"📅 **Hạn cuối:** {row['deadline']}")
                st.write(f"📝 **Chỉ thị:** {row['note']}")
                
                if pd.notna(row['file_path']) and str(row['file_path']) != "" and os.path.exists(str(row['file_path'])):
                    st.write(f"📂 **Ảnh hiện trường:** {str(row['file_path']).split('/')[-1]}")
                    with open(str(row['file_path']), "rb") as file_bytes:
                        st.download_button("Tải file/ảnh nghiệm thu", data=file_bytes, file_name=str(row['file_path']).split('/')[-1], key=f"dl_{row['id']}")
                
                if st.session_state.user_role == "admin" or st.session_state.user_current == row['assigned_to']:
                    st.markdown("**📝 Cập nhật tiến độ & Gửi ảnh:**")
                    
                    current_status = row['status'] if row['status'] in ["Chờ triển khai", "Đang triển khai", "Đang gặp sự cố", "Đã hoàn thành"] else "Chờ triển khai"
                    status_list = ["Chờ triển khai", "Đang triển khai", "Đang gặp sự cố", "Đã hoàn thành"]
                    
                    new_status = st.selectbox("Thay đổi trạng thái:", status_list, key=f"status_{row['id']}", index=status_list.index(current_status))
                    uploaded_file = st.file_uploader("Chụp ảnh hoặc tải bản vẽ hiện trường:", key=f"file_{row['id']}")
                    
                    if st.button("Xác nhận gửi báo cáo kỹ thuật", key=f"btn_{row['id']}"):
                        saved_path = row['file_path']
                        if uploaded_file is not None:
                            saved_path = os.path.join("stored_files", uploaded_file.name)
                            with open(saved_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        
                        df_tasks.loc[index, 'status'] = new_status
                        df_tasks.loc[index, 'file_path'] = saved_path
                        df_tasks.loc[index, 'updated_by'] = str(st.session_state.user_current)
                        df_tasks.to_csv(DB_TASKS_PATH, index=False)
                        
                        st.session_state.notifications.append(f"🔄 {st.session_state.user_current} đã cập nhật tiến độ '{row['task_name']}' sang: {new_status}!")
                        st.success("Hệ thống dữ liệu đã được ghi nhận!")
                        st.rerun()
else:
    st.write("Hiện tại hệ thống chưa có công việc nào.")