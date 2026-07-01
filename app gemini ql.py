import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Cấu hình giao diện App hiển thị trên Điện thoại/Máy tính
st.set_page_config(page_title="Hệ Thống Quản Lý MEP Nội Bộ", layout="centered")
st.title("🚧 HỆ THỐNG QUẢN LÝ TIẾN ĐỘ & GIAO VIỆC")

# Tạo thư mục lưu trữ file/ảnh nếu chưa có
if not os.path.exists("stored_files"):
    os.makedirs("stored_files")

# 2. Giả lập Cơ sở dữ liệu (Database) bằng Session State để chạy thử
if "tasks" not in st.state:
    st.state.tasks = [
        {
            "id": 1,
            "task_name": "Lắp trục đứng MEP tầng 3",
            "assigned_to": "Nguyễn Văn A",
            "status": "Đang triển khai",
            "deadline": "2026-07-05",
            "note": "Cần chú ý cao độ ống thoát nước",
            "file_path": None,
            "updated_by": "Hệ thống"
        }
    ]
if "notifications" not in st.state:
    st.state.notifications = ["Hệ thống khởi tạo thành công!"]

# Danh sách 21 nhân viên của Sir để phân quyền chọn nhanh
DANH_SACH_NV = [f"Nhân viên {i}" for i in range(1, 22)]
DANH_SACH_NV.insert(0, "Quản lý (Sir)")

# 3. Khu vực đăng nhập giả lập để biết AI đang tương tác với ai
st.sidebar.header("🔐 ĐĂNG NHẬP NỘI BỘ")
current_user = st.sidebar.selectbox("Chọn tên của ngài/nhân viên:", DANH_SACH_NV)

# --- KHU VỰC 1: BẢNG TIN THÔNG BÁO HAI CHIỀU ---
st.subheader("🔔 Bảng Tin Thông Báo Mới Nhất")
for notif in st.state.notifications[-3:]: # Hiện 3 thông báo mới nhất
    st.info(notif)

st.markdown("---")

# --- KHU VỰC 2: DÀNH CHO QUẢN LÝ (SIR) - GIAO VIỆC ---
if current_user == "Quản lý (Sir)":
    st.subheader("📝 Giao Việc Mới (Chỉ Sir nhìn thấy)")
    with st.form("new_task_form", clear_on_submit=True):
        t_name = st.text_input("Tên hạng mục công việc:")
        t_assign = st.selectbox("Giao cho nhân viên:", [nv for nv in DANH_SACH_NV if nv != "Quản lý (Sir)"])
        t_deadline = st.date_input("Hạn hoàn thành (Deadline):")
        t_note = st.text_area("Ghi chú/Yêu cầu kỹ thuật:")
        submit_btn = st.form_submit_button("Phát lệnh giao việc")
        
        if submit_btn and t_name:
            new_id = len(st.state.tasks) + 1
            st.state.tasks.append({
                "id": new_id,
                "task_name": t_name,
                "assigned_to": t_assign,
                "status": "Chờ triển khai",
                "deadline": str(t_deadline),
                "note": t_note,
                "file_path": None,
                "updated_by": "Quản lý (Sir)"
            })
            st.state.notifications.append(f"📢 Sir vừa giao việc mới: '{t_name}' cho {t_assign}!")
            st.success(f"Đã giao việc thành công cho {t_assign}!")
            st.rerun()

# --- KHU VỰC 3: DÀNH CHO NHÂN VIÊN - CẬP NHẬT TIẾN ĐỘ & ĐÍNH KÈM FILE ---
st.subheader("📋 Danh Sách & Tiến Độ Hạng Mục")
df = pd.DataFrame(st.state.tasks)

for index, row in df.iterrows():
    with st.expander(f"📌 {row['task_name']} - [{row['status']}]"):
        st.write(f"**Người thực hiện:** {row['assigned_to']}")
        st.write(f"**Hạn cuối:** {row['deadline']}")
        st.write(f"**Ghi chú kỹ thuật:** {row['note']}")
        
        if row['file_path']:
            st.write(f"📂 **File/Ảnh đính kèm:** {row['file_path'].split('/')[-1]}")
        
        # Cho phép đúng người được giao hoặc Sir vào cập nhật
        if current_user == row['assigned_to'] or current_user == "Quản lý (Sir)":
            st.markdown("**Cập nhật trạng thái & báo cáo hiện trường:**")
            new_status = st.selectbox("Đổi trạng thái:", ["Chờ triển khai", "Đang triển khai", "Đang gặp sự cố", "Đã hoàn thành"], key=f"status_{row['id']}")
            uploaded_file = st.file_uploader("Tải lên Bản vẽ sửa đổi / Ảnh thực tế hiện trường:", key=f"file_{row['id']}")
            
            if st.button("Xác nhận cập nhật báo cáo", key=f"btn_{row['id']}"):
                # Xử lý lưu file nếu có tải lên
                saved_path = row['file_path']
                if uploaded_file is not None:
                    saved_path = os.path.join("stored_files", uploaded_file.name)
                    with open(saved_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # Cập nhật vào cơ sở dữ liệu
                st.state.tasks[index]['status'] = new_status
                st.state.tasks[index]['file_path'] = saved_path
                st.state.tasks[index]['updated_by'] = current_user
                
                # Bắn thông báo hai chiều cho cả hệ thống biết
                st.state.notifications.append(f"🔄 {current_user} đã cập nhật tiến độ '{row['task_name']}' thành: {new_status}!")
                st.success("Hệ thống đã ghi nhận báo cáo của ngài!")
                st.rerun()