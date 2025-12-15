import streamlit as st
import requests
import json

# --- CẤU HÌNH ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

with st.sidebar:
    st.header("Cài đặt")
    api_key = st.text_input("Nhập Google API Key", type="password")
    if not api_key:
        st.warning("⚠️ Nhập Key lấy từ Google Cloud.")

# --- HÀM TỰ ĐỘNG TÌM MODEL ---
def find_best_model(key):
    # Hỏi Google xem tài khoản này được dùng những model nào
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            # Ưu tiên tìm các model chat tốt nhất
            priority_list = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
            
            # 1. Tìm trong danh sách ưu tiên
            for p_model in priority_list:
                for m in models:
                    if p_model in m['name']:
                        return m['name'].replace("models/", "")
            
            # 2. Nếu không có, lấy bất kỳ cái nào tạo được nội dung
            for m in models:
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    return m['name'].replace("models/", "")
        return None
    except:
        return None

# --- NỘI DUNG ---
SYSTEM_PROMPT = """
Bạn là AI Luật sư hỗ trợ bị hại Nguyễn Thị Hồng.
Nhiệm vụ: Hỏi lần lượt các câu hỏi.
Quy tắc: Đưa ra câu hỏi -> Chờ user trả lời -> Đóng vai Luật sư phân tích (Đánh giá, Điểm mạnh, Cạm bẫy, Gợi ý) -> Hỏi câu tiếp theo.
Ngân hàng câu hỏi:
1. Tại sao tin Nhung gửi 5 tỷ?
2. Có kiểm tra giấy tờ không?
3. Chuyển tiền hoa hồng thế nào?
4. Có ai khác liên hệ không?
5. Phát hiện lừa khi nào?
6. Quan hệ với Nhung là gì?
7. Lãi suất cao có nghi ngờ không?
8. Nói gì khi giới thiệu người thân?
9. Biết mình giúp sức lừa đảo không?
10. Có nhận lợi ích khác không?
"""

st.title("⚖️ Mô Phỏng Phiên Tòa - Tự Động Xử Lý Lỗi")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Chào chị Hồng. Tôi là AI Luật sư. Hãy gõ 'Sẵn sàng' để bắt đầu."})

# Hiển thị chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Nhập câu trả lời..."):
    if not api_key:
        st.stop()

    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # --- XỬ LÝ KẾT NỐI ---
    try:
        # Mặc định thử dùng Flash
        current_model = "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={api_key}"
        
        # Chuẩn bị nội dung
        contents = []
        contents.append({"role": "user", "parts": [{"text": "System: " + SYSTEM_PROMPT}]})
        contents.append({"role": "model", "parts": [{"text": "OK"}]})
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
        payload = {"contents": contents}
        headers = {'Content-Type': 'application/json'}

        with st.spinner(f'Luật sư đang suy nghĩ...'):
            response = requests.post(url, headers=headers, json=payload)
            
            # NẾU LỖI 404 -> KÍCH HOẠT CHẾ ĐỘ TỰ TÌM MODEL
            if response.status_code == 404:
                st.toast("⚠️ Model mặc định bị lỗi, đang tự động tìm model khác...", icon="🔄")
                found_model = find_best_model(api_key)
                
                if found_model:
                    st.success(f"✅ Đã tìm thấy model khả dụng: {found_model}. Đang thử lại...")
                    # Thử lại với model mới tìm được
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{found_model}:generateContent?key={api_key}"
                    response = requests.post(url, headers=headers, json=payload)
                else:
                    st.error("❌ Tài khoản Google Cloud của bạn chưa được cấp quyền dùng bất kỳ Model nào. Hãy kiểm tra lại phần Billing (Thanh toán) hoặc tạo tài khoản mới.")

            # Xử lý kết quả cuối cùng
            if response.status_code == 200:
                result = response.json()
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
                st.chat_message("assistant").write(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
            else:
                st.error(f"Lỗi: {response.text}")

    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
