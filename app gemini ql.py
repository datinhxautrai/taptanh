import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. CẤU HÌNH GIAO DIỆN & ÉP XOÁ SẠCH BIỂU TƯỢNG STREAMLIT MẶC ĐỊNH
st.set_page_config(page_title="Hệ Thống Quản Lý MEP Nội Bộ", layout="centered")

# Đoạn mã CSS chuyên sâu để giấu nút vương miện đỏ ở góc phải, thanh menu và footer ẩn danh
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__1QSob {display: none !important;}
            .st-emotion-cache-1wbqy5l {display: none !important;}
            button[title="View source code"] {display: none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🚧 HỆ THỐNG ĐIỀU HÀNH MEP - PRO V2")

# Tạo hạ tầng lưu trữ dữ liệu vĩnh viễn
if not os.path.exists("stored_files"):
    os.makedirs("stored_files")

DB_USERS_PATH = "stored_files/db_users.csv"
DB_TASKS_PATH = "stored_files/db_tasks.csv"

# 2. KHỞI TẠO CƠ SỞ DỮ LIỆU CHẠY NGẦM
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
    pd.DataFrame(init_users).to_csv(DB_USERS_PATH, index=False, encoding='utf-8-sig')

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
    pd.DataFrame(init_tasks).to_csv(DB_TASKS_PATH, index=False, encoding='utf-8-sig')

df_users = pd.read_csv(DB_USERS_PATH, dtype=str)
df_tasks = pd.read_csv(DB_TASKS_PATH, dtype=str)

# Khởi tạo bộ nhớ thông báo trong phiên chạy
if "notifications" not in st.session_state:
    st.session_state.notifications = ["Hệ thống điều hành MEP bảo mật sẵn sàng vĩnh viễn!"]
if "last_task_count" not in st.session_state:
    st.session_state.last_task_count = len(df_tasks)
if "trigger_sound" not in st.session_state:
    st.session_state.trigger_sound = False

# HÀM PHÁT ÂM THANH THÔNG BÁO TỰ ĐỘNG KHÔNG CẦN ZALO
def play_alert_sound():
    # Sử dụng âm thanh Ting tinh ngắn, gọn dạng cơ bản, nhúng trực tiếp bằng HTML5 công trường
    sound_html = """
    <iframe src="https://assets.mixkit.co/active_storage/sfx/2869/2869-500.wav" allow="autoplay" style="display:none" id="iframeAudio"></iframe>
    <audio autoplay style="display:none">
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-500.wav" type="audio/wav">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# 3. MÔ ĐUN ĐĂNG NHẬP BẢO MẬT TUYỆT ĐỐI
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
    
    if st.button("Xác nhận vào hệ thống"):
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
                    st.error("🛑 Tài khoản này đã bị Sir đình chỉ truy cập!")
            else:
                st.error("Mật khẩu không chính xác!")
        else:
            st.error("Tài khoản không tồn tại!")
    st.stop()

# --- SIDEBAR: THÔNG TIN TÀI KHOẢN & LOGOUT ---
st.sidebar.markdown(f"👤 Tài khoản: **{st.session_state.user_current}**")
st.sidebar.markdown(f"🎖️ Quyền hạn: `{st.session_state.user_role.upper()}`")
if st.sidebar.button("Đăng xuất khỏi hệ thống"):
    st.session_state.logged_in = False
    st.session_state.user_current = None
    st.session_state.user_role = None
    st.rerun()

# --- CƠ CHẾ ĐÓN ĐẦU THÔNG BÁO TỰ ĐỘNG ---
# Kiểm tra nếu số lượng đầu việc tăng lên (Sir vừa giao việc mới), tự động hú còi thông báo
if len(df_tasks) > st.session_state.last_task_count:
    st.session_state.last_task_count = len(df_tasks)
    st.session_state.trigger_sound = True

if st.session_state.trigger_sound:
    play_alert_sound()
    st.session_state.trigger_sound = False # Reset trạng thái còi còi

# --- BẢNG TIN THÔNG BÁO TỰ ĐỘNG ---
st.subheader("🔔 Bảng Tin Hiện Trường Tức Thời")
for notif in st.session_state.notifications[-2:]:
    st.info(notif)
st.markdown("---")


# ⚙️ --- KHU VỰC 1: ĐẶC QUYỀN QUẢN TRỊ TÀI KHOẢN CỦA SIR ---
if st.session_state.user_role == "admin":
    with st.sidebar.expander("⚙️ QUẢN TRỊ NHÂN SỰ TỨC THỜI"):
        st.markdown("**Bảng điều khiển tài khoản:**")
        selected_user = st.selectbox("Chọn tài khoản nhân sự:", df_users["tai_khoan"].tolist())
        current_info = df_users[df_users["tai_khoan"] == selected_user].iloc[0]
        
        new_pwd = st.text_input("Đổi mật khẩu:", value=str(current_info["mat_khau"]))
        new_role = st.selectbox("Nhóm quyền:", ["admin", "dac_biet", "nhan_vien"], index=["admin", "dac_biet", "nhan_vien"].index(current_info["quyen"]))
        new_status = st.radio("Trạng thái hoạt động:", ["Hoạt động", "Bị khóa"], index=["Hoạt động", "Bị khóa"].index(current_info["trang_thai"]))
        
        if st.button("Áp dụng lệnh can thiệp"):
            df_users.loc[df_users["tai_khoan"] == selected_user, "mat_khau"] = new_pwd
            df_users.loc[df_users["tai_khoan"] == selected_user, "quyen"] = new_role
            df_users.loc[df_users["tai_khoan"] == selected_user, "trang_thai"] = new_status
            df_users.to_csv(DB_USERS_PATH, index=False, encoding='utf-8-sig')
            st.session_state.notifications.append(f"🛠️ Sir vừa can thiệp tài khoản '{selected_user}'")
            st.success("Đã ghi nhận thay đổi nhân sự!")
            st.rerun()

    # --- TÍNH NĂNG GIAO VIỆC CỦA SIR ---
    st.subheader("📝 Phát Lệnh Giao Việc Mới")
    with st.form("new_task_form", clear_on_submit=True):
        t_name = st.text_input("Tên hạng mục thi công MEP:")
        list_nv_select = df_users[df_users["quyen"] == "nhan_vien"]["tai_khoan"].tolist()
        t_assign = st.selectbox("Giao cho nhân viên chịu trách nhiệm chính:", list_nv_select)
        t_deadline = st.date_input("Hạn hoàn thành (Deadline):")
        t_note = st.text_area("Yêu cầu kỹ thuật / Tiêu chuẩn thi công (TCVN):")
        submit_btn = st.form_submit_button("Phát lệnh giao việc công trường")
        
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
            df_tasks.to_csv(DB_TASKS_PATH, index=False, encoding='utf-8-sig')
            st.session_state.notifications.append(f"📢 Sir vừa giao việc: '{t_name}' cho {t_assign}!")
            st.success("Lệnh giao việc đã được đẩy xuống hiện trường!")
            st.rerun()


# --- KHU VỰC 2: DASHBOARD THỐNG KÊ (DÀNH CHO SIR & PHÓ BAN) ---
if st.session_state.user_role in ["admin", "dac_biet"]:
    st.subheader("📊 Tổng Quan Tiến Độ Hiện Trường")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng số việc", len(df_tasks))
    c2.metric("Đang chạy", len(df_tasks[df_tasks["status"] == "Đang triển khai"]))
    c3.metric("🚨 Sự cố", len(df_tasks[df_tasks["status"] == "Đang gặp sự cố"]))
    c4.metric("Hoàn thành", len(df_tasks[df_tasks["status"] == "Đã hoàn thành"]))
    
    st.markdown("**Bộ lọc xem nhanh theo nhân sự:**")
    filter_nv = st.selectbox("Chọn nhân viên để xem tiến độ riêng biệt:", ["Tất cả nhân viên"] + df_users[df_users["quyen"] == "nhan_vien"]["tai_khoan"].tolist())
    if filter_nv != "Tất cả nhân viên":
        df_display = df_tasks[df_tasks["assigned_to"] == filter_nv]
    else:
        df_display = df_tasks
    st.markdown("---")
else:
    df_display = df_tasks[df_tasks["assigned_to"] == st.session_state.user_current]


# --- KHU VỰC 3: HIỂN THỊ CHI TIẾT CÔNG VIỆC VÀ BÁO CÁO CÔNG TRƯỜNG ---
st.subheader("📋 Chi Tiết Hạng Mục Thi Công")

if not df_display.empty:
    for index, row in df_display.iterrows():
        orig_index = df_tasks[df_tasks["id"] == row["id"]].index[0]
        
        status_colors = {"Chờ triển khai": "⚪", "Đang triển khai": "🔵", "Đang gặp sự cố": "🔴", "Đã hoàn thành": "🟢"}
        icon = status_colors.get(row['status'], "📌")
        
        # Thiết kế cảnh báo nhấp nháy màu đỏ trực quan nếu hạng mục gặp sự cố
        if row['status'] == "Đang gặp sự cố":
            st.markdown(f"<div style='padding:10px; background-color:#ffcccc; border-left: 6px solid red; border-radius:4px; margin-bottom:10px;'>🚨 <b>CẢNH BÁO KHẨN CẤP:</b> Đầu việc '{row['task_name']}' đang gặp sự cố kỹ thuật!</div>", unsafe_allow_html=True)
        
        with st.expander(f"{icon} {row['task_name']} - [{row['status']}]"):
            st.write(f"👷 **Phụ trách:** {row['assigned_to']}")
            st.write(f"📅 **Hạn cuối (Deadline):** {row['deadline']}")
            st.write(f"📝 **Chỉ thị kỹ thuật:** {row['note']}")
            
            if pd.notna(row['file_path']) and str(row['file_path']) != "":
                full_path = str(row['file_path'])
                if os.path.exists(full_path):
                    st.write(f"📂 **Ảnh hiện trường mới nhất:** `{full_path.split('/')[-1]}`")
                    if full_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        st.image(full_path, use_container_width=True)
                    with open(full_path, "rb") as file_bytes:
                        st.download_button("Tải ảnh nghiệm thu", data=file_bytes, file_name=full_path.split('/')[-1], key=f"dl_{row['id']}")
            
            if st.session_state.user_role == "admin" or st.session_state.user_current == row['assigned_to']:
                st.markdown("---")
                st.markdown("**⚙️ BÁO CÁO TIẾN ĐỘ THỰC TẾ:**")
                status_list = ["Chờ triển khai", "Đang triển khai", "Đang gặp sự cố", "Đã hoàn thành"]
                current_status = row['status'] if row['status'] in status_list else "Chờ triển khai"
                
                new_status = st.selectbox("Cập nhật trạng thái:", status_list, key=f"status_{row['id']}", index=status_list.index(current_status))
                uploaded_file = st.file_uploader("Chụp ảnh thực tế hiện trường hoặc tải file bản vẽ:", key=f"file_{row['id']}")
                
                if st.button("Gửi báo cáo về hệ thống", key=f"btn_{row['id']}"):
                    saved_path = row['file_path']
                    if uploaded_file is not None:
                        ext = os.path.splitext(uploaded_file.name)[1]
                        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        clean_task_name = "".join([c for c in row['task_name'] if c.isalnum() or c in [' ', '_']]).replace(' ', '_')
                        new_filename = f"{date_str}_{st.session_state.user_current}_{clean_task_name}{ext}"
                        saved_path = os.path.join("stored_files", new_filename)
                        
                        with open(saved_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    df_tasks.loc[orig_index, 'status'] = new_status
                    df_tasks.loc[orig_index, 'file_path'] = saved_path
                    df_tasks.loc[orig_index, 'updated_by'] = str(st.session_state.user_current)
                    df_tasks.to_csv(DB_TASKS_PATH, index=False, encoding='utf-8-sig')
                    
                    st.session_state.notifications.append(f"🔄 {st.session_state.user_current} cập nhật việc '{row['task_name']}' thành: {new_status}!")
                    st.success("Đã đồng bộ báo cáo thành công!")
                    st.rerun()
else:
    st.write("Không tìm thấy đầu việc nào.")