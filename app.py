import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

with st.sidebar:
    st.title("Cài đặt")
    api_key = st.text_input("Nhập Google API Key", type="password")
    st.caption("Lấy Key tại: aistudio.google.com")
    st.divider()
    st.info("App mô phỏng phiên tòa Eximbank.")

# --- NỘI DUNG PROMPT ---
SYSTEM_PROMPT = """
Đóng vai: Ứng dụng AI tên "Mô Phỏng Đối Chất Tại Tòa", giúp bị hại Nguyễn Thị Hồng luyện tập.
Bối cảnh: Hồng bị Vũ Thị Thu Nhung (Eximbank) lừa 5 tỷ.
Nhiệm vụ: Hỏi từng câu trong ngân hàng câu hỏi. Người dùng trả lời xong thì đóng vai Luật sư phân tích (Đánh giá, Điểm mạnh, Cạm bẫy, Gợi ý).
Ngân hàng câu hỏi (Hỏi lần lượt từng câu):
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

# --- GIAO DIỆN CHÍNH ---
st.title("⚖️ Mô Phỏng Đối Chất Tại Tòa - Vụ Án Eximbank")

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Câu chào mở đầu
    st.session_state.messages.append({"role": "model", "content": "Chào chị Hồng. Tôi là AI Luật sư. Hãy gõ 'Sẵn sàng' để bắt đầu câu hỏi số 1."})

# Hiển thị lịch sử
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])

# Xử lý nhập liệu
if prompt := st.chat_input("Nhập câu trả lời..."):
    if not api_key:
        st.warning("Vui lòng nhập API Key ở menu bên trái!")
        st.stop()

    # Hiện câu trả lời người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GỌI GOOGLE AI
    try:
        genai.configure(api_key=api_key)
        
        # --- SỬA ĐỔI QUAN TRỌNG: Dùng gemini-pro ---
        model = genai.GenerativeModel("gemini-pro")
        
        # Ghép prompt thủ công để tránh lỗi hệ thống
        chat_history_text = ""
        for msg in st.session_state.messages:
            role_str = "AI" if msg["role"] == "model" else "User"
            chat_history_text += f"{role_str}: {msg['content']}\n"
            
        full_prompt = f"{SYSTEM_PROMPT}\n\nLịch sử chat:\n{chat_history_text}\n\nUser trả lời mới nhất: {prompt}\n\nAI hãy phản hồi:"
        
        with st.spinner('Luật sư đang phân tích...'):
            response = model.generate_content(full_prompt)
        
        # Hiện phản hồi AI
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "model", "content": response.text})

    except Exception as e:
        st.error(f"Lỗi: {e}")
