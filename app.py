import streamlit as st
import requests
import json

# --- CẤU HÌNH ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

with st.sidebar:
    st.header("Cài đặt")
    api_key = st.text_input("Nhập Google API Key", type="password")
    if not api_key:
        st.warning("⚠️ Hãy nhập Key lấy từ Google Cloud.")

# --- NỘI DUNG ---
SYSTEM_PROMPT = """
Bạn là AI Luật sư hỗ trợ bị hại Nguyễn Thị Hồng.
Nhiệm vụ: Hỏi lần lượt 17 câu hỏi trong ngân hàng câu hỏi.
Quy tắc:
1. Đưa ra câu hỏi.
2. Chờ user trả lời.
3. Sau khi user trả lời, đóng vai Luật sư phân tích (Đánh giá, Điểm mạnh, Cạm bẫy, Gợi ý) rồi mới hỏi câu tiếp theo.
"""

st.title("⚖️ Mô Phỏng Phiên Tòa - Kết Nối Trực Tiếp")

# Khởi tạo lịch sử
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Chào chị Hồng. Tôi là AI Luật sư. Hãy gõ 'Sẵn sàng' để bắt đầu."})

# Hiển thị chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Xử lý nhập liệu
if prompt := st.chat_input("Nhập câu trả lời..."):
    if not api_key:
        st.stop()

    # Hiển thị câu user
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # --- KẾT NỐI TRỰC TIẾP (KHÔNG QUA THƯ VIỆN TRUNG GIAN) ---
    try:
        # Chuẩn bị URL cho model Gemini 1.5 Flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # Chuẩn bị nội dung gửi đi (Ghép toàn bộ lịch sử để AI nhớ)
        contents = []
        # Thêm System Prompt vào đầu
        contents.append({"role": "user", "parts": [{"text": "Yêu cầu hệ thống: " + SYSTEM_PROMPT}]})
        contents.append({"role": "model", "parts": [{"text": "Đã rõ."}]})
        
        # Thêm lịch sử chat
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": 0.7}
        }
        headers = {'Content-Type': 'application/json'}

        with st.spinner('Luật sư đang suy nghĩ...'):
            # Gửi lệnh POST trực tiếp
            response = requests.post(url, headers=headers, json=payload)
            
            # Kiểm tra kết quả
            if response.status_code == 200:
                result = response.json()
                try:
                    ai_text = result['candidates'][0]['content']['parts'][0]['text']
                    st.chat_message("assistant").write(ai_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                except:
                    st.error("AI không trả lời đúng định dạng. Hãy thử lại.")
            else:
                # Nếu lỗi, in nguyên văn lỗi từ Google để biết chính xác lý do
                error_msg = response.json().get('error', {}).get('message', 'Lỗi không xác định')
                st.error(f"❌ Lỗi từ Google (Mã {response.status_code}): {error_msg}")

    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
