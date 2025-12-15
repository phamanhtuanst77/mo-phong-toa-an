import streamlit as st
from groq import Groq

# --- CẤU HÌNH ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

with st.sidebar:
    st.header("Cài đặt")
    api_key = st.text_input("Nhập Groq API Key", type="password")
    if not api_key:
        st.warning("👉 Lấy Key miễn phí tại: console.groq.com")
    else:
        st.success("Đã nhập Key!")

# --- NỘI DUNG PROMPT ---
SYSTEM_PROMPT = """
Bạn là AI Luật sư hỗ trợ bị hại Nguyễn Thị Hồng trong vụ án Eximbank.
Nhiệm vụ: Hỏi lần lượt 17 câu hỏi trong ngân hàng câu hỏi.
Quy tắc:
1. Đưa ra câu hỏi.
2. Chờ user trả lời.
3. Sau khi user trả lời, đóng vai Luật sư phân tích (Đánh giá, Điểm mạnh, Cạm bẫy, Gợi ý) rồi mới hỏi câu tiếp theo.
Luôn trả lời bằng Tiếng Việt mạch lạc, chuyên nghiệp.
"""

st.title("⚖️ Mô Phỏng Phiên Tòa (Groq AI)")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Chào chị Hồng. Tôi là AI Luật sư. Hãy gõ 'Sẵn sàng' để bắt đầu."})

# Hiển thị chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Xử lý nhập liệu
if prompt := st.chat_input("Nhập câu trả lời..."):
    if not api_key:
        st.error("Vui lòng nhập API Key trước!")
        st.stop()

    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # KẾT NỐI GROQ (Siêu nhanh & Miễn phí)
        client = Groq(api_key=api_key)
        
        # Chuẩn bị lịch sử chat
        chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in st.session_state.messages:
            chat_history.append({"role": msg["role"], "content": msg["content"]})

        with st.spinner('Luật sư đang phân tích...'):
            completion = client.chat.completions.create(
                model="llama3-8b-8192", # Model miễn phí, mạnh mẽ
                messages=chat_history,
                temperature=0.7,
                max_tokens=2048,
                top_p=1,
            )
            
            ai_text = completion.choices[0].message.content
            st.chat_message("assistant").write(ai_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})

    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
