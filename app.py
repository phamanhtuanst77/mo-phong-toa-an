import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

with st.sidebar:
    st.header("Cài đặt")
    api_key = st.text_input("Nhập Google API Key", type="password")
    if not api_key:
        st.info("Nhập Key để bắt đầu.")

# --- NỘI DUNG ---
SYSTEM_PROMPT = """
Bạn là AI Luật sư hỗ trợ bị hại Nguyễn Thị Hồng.
Hỏi lần lượt từng câu hỏi sau. Sau khi user trả lời, hãy đóng vai Luật sư phân tích (Đánh giá, Điểm mạnh, Cạm bẫy, Gợi ý).
Câu hỏi 1: Tại sao chị tin tưởng Nhung gửi 5 tỷ?
Câu hỏi 2: Chị có kiểm tra giấy tờ không?
Câu hỏi 3: Việc chuyển tiền hoa hồng ra sao?
Câu hỏi 4: Có ai khác liên hệ không?
Câu hỏi 5: Phát hiện bị lừa khi nào?
Câu hỏi 6: Quan hệ với Nhung là gì?
Câu hỏi 7: Lãi suất cao có nghi ngờ không?
Câu hỏi 8: Nói gì khi giới thiệu người thân?
Câu hỏi 9: Biết mình giúp sức lừa đảo không?
Câu hỏi 10: Có nhận lợi ích khác không?
Câu hỏi 11: Tổng tiền thiệt hại?
Câu hỏi 12: Có chuyên môn kế toán sao không biết rủi ro?
Câu hỏi 13: Có thúc giục người thân không?
Câu hỏi 14: Có hưởng lợi từ việc giữ lại tiền không?
Câu hỏi 15: Tại sao giao dịch qua trung gian?
Câu hỏi 16: Thấy có trách nhiệm không?
Câu hỏi 17: Có đòi tiền riêng trước không?
"""

st.title("⚖️ Mô Phỏng Phiên Tòa")

if "history" not in st.session_state:
    st.session_state.history = []
    # Thêm prompt vào ngữ cảnh ngầm
    st.session_state.history.append({"role": "user", "parts": ["Yêu cầu hệ thống: " + SYSTEM_PROMPT]})
    st.session_state.history.append({"role": "model", "parts": ["Đã rõ. Tôi sẽ bắt đầu hỏi câu 1."]})
    # Hiển thị lời chào
    st.session_state.history.append({"role": "model", "parts": ["Chào chị Hồng. Tôi là AI Luật sư. Chị đã sẵn sàng cho câu hỏi số 1 chưa?"]})

# Hiển thị chat cũ
for msg in st.session_state.history[2:]: # Bỏ qua 2 câu lệnh ngầm đầu tiên
    role = "assistant" if msg["role"] == "model" else "user"
    st.chat_message(role).write(msg["parts"][0])

# Xử lý chat mới
if prompt := st.chat_input("Nhập câu trả lời..."):
    if not api_key:
        st.stop()

    st.chat_message("user").write(prompt)
    st.session_state.history.append({"role": "user", "parts": [prompt]})

    try:
        genai.configure(api_key=api_key)
        # SỬ DỤNG GEMINI PRO (Bản ổn định nhất cho Project mới)
        model = genai.GenerativeModel("gemini-pro")
        
        chat = model.start_chat(history=st.session_state.history)
        
        with st.spinner('Luật sư đang soạn thảo...'):
            response = chat.send_message(prompt)
            st.chat_message("assistant").write(response.text)
            
        st.session_state.history.append({"role": "model", "parts": [response.text]})

    except Exception as e:
        st.error(f"Lỗi: {e}")
