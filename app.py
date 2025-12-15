import streamlit as st
import google.generativeai as genai
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

with st.sidebar:
    st.header("Cài đặt")
    api_key = st.text_input("Nhập Google API Key", type="password")
    st.info("Lưu ý: Hãy đảm bảo bạn đã bấm nút ENABLE API trong Google Cloud Console.")

# --- NỘI DUNG PROMPT ---
SYSTEM_PROMPT = """
Đóng vai: AI Luật sư hỗ trợ bị hại Nguyễn Thị Hồng trong vụ án Eximbank.
Nhiệm vụ: Hỏi từng câu trong ngân hàng câu hỏi. Sau khi user trả lời, hãy phân tích (Đánh giá, Điểm mạnh, Cạm bẫy, Gợi ý).
Ngân hàng câu hỏi:
1. Tại sao tin Nhung gửi 5 tỷ?
2. Có kiểm tra chứng chỉ tiền gửi không?
3. Việc chuyển tiền hoa hồng thế nào?
4. Có ai khác ở Eximbank liên hệ không?
5. Phát hiện bị lừa khi nào?
6. Quan hệ với Nhung là gì?
7. Lãi suất cao có nghi ngờ không?
8. Nói gì khi giới thiệu người thân?
9. Biết mình giúp sức lừa đảo không?
10. Có nhận lợi ích gì khác không?
11. Tổng tiền bị chiếm đoạt?
12. Có chuyên môn kế toán sao không biết rủi ro?
13. Có thúc giục người thân không?
14. Có hưởng lợi từ việc giữ lại tiền không?
15. Tại sao giao dịch qua trung gian?
16. Thấy có trách nhiệm không?
17. Có đòi tiền riêng trước không?
"""

st.title("⚖️ Mô Phỏng Phiên Tòa - Vụ Án Eximbank")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Chào chị Hồng. Tôi là AI Luật sư. Hãy gõ 'Sẵn sàng' để bắt đầu."})

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Nhập câu trả lời..."):
    if not api_key:
        st.warning("Vui lòng nhập API Key!")
        st.stop()

    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        genai.configure(api_key=api_key)
        
        # SỬ DỤNG MODEL CHUẨN NHẤT HIỆN TẠI
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Tạo lịch sử chat để gửi lên Google
        history = []
        # Nhồi System Prompt vào đầu lịch sử để "tẩy não" AI
        history.append({"role": "user", "parts": ["Hệ thống yêu cầu: " + SYSTEM_PROMPT]})
        history.append({"role": "model", "parts": ["Đã rõ. Tôi sẽ đóng vai Luật sư mô phỏng."]})
        
        # Thêm các tin nhắn cũ
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                history.append({"role": "user", "parts": [msg["content"]]})
            else:
                history.append({"role": "model", "parts": [msg["content"]]})

        # Xóa tin nhắn cuối cùng vừa append (vì nó sẽ được gửi trong lệnh generate)
        history.pop() 

        chat = model.start_chat(history=history)
        
        with st.spinner('Luật sư đang phân tích...'):
            response = chat.send_message(prompt)
            st.chat_message("assistant").write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        st.warning("👉 Hãy kiểm tra: Bạn đã bấm nút ENABLE trong Google Cloud Console chưa?")
