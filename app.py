import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

with st.sidebar:
    st.title("Cài đặt")
    api_key = st.text_input("Nhập Google API Key", type="password")
    st.caption("Lấy Key tại: aistudio.google.com")
    st.divider()
    st.info("App hỗ trợ bị hại luyện tập đối chất.")

# --- NỘI DUNG PROMPT ---
SYSTEM_PROMPT = """
Bạn là một ứng dụng AI có tên "Mô Phỏng Đối Chất Tại Tòa". Nhiệm vụ của bạn là giúp bị hại Nguyễn Thị Hồng luyện tập trả lời câu hỏi tại tòa.
Bối cảnh: Hồng bị Vũ Thị Thu Nhung (Eximbank) lừa 5 tỷ, cũng là người giới thiệu người thân nên sợ bị coi là đồng phạm. 
Nhiệm vụ: Hỏi từng câu trong ngân hàng câu hỏi. Sau khi Hồng trả lời, hãy đóng vai Luật sư phân tích: Đánh giá, Điểm mạnh, Cạm bẫy, Gợi ý tối ưu và Lưu ý chiến lược.
Ngân hàng câu hỏi: 
1. Tại sao chị tin Nhung gửi 5 tỷ và giới thiệu người thân?
2. Chị có kiểm tra chứng chỉ tiền gửi không?
3. Việc nhận/chuyển tiền hoa hồng diễn ra thế nào?
4. Có ai khác ở Eximbank làm việc với chị không?
5. Chị phát hiện bị lừa khi nào?
6. Quan hệ chị và Nhung là gì?
7. Lãi suất cao bất thường chị có nghi ngờ không?
8. Chị nói gì khi giới thiệu người thân?
9. Chị có biết mình tạo điều kiện cho Nhung lừa thêm người không?
10. Chị có nhận lợi ích gì khác ngoài hoa hồng không?
11. Tổng số tiền bị chiếm đoạt yêu cầu bồi thường là bao nhiêu?
12. Chị có chuyên môn kế toán sao không nhận ra rủi ro?
13. Chị thúc giục người thân tham gia để lấy hoa hồng đúng không?
14. Chị giữ lại tiền, chị là người hưởng lợi đúng không?
15. Tại sao giao dịch phải qua chị mà không trực tiếp với Nhung?
16. Chị thấy mình có trách nhiệm gì khi người thân mất tiền không?
17. Chị có đòi tiền riêng trước khi báo công an không?
"""

# --- GIAO DIỆN CHÍNH ---
st.title("⚖️ Mô Phỏng Đối Chất Tại Tòa - Vụ Án Eximbank")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "Chào chị Hồng. Tôi là AI Luật sư. Chị đã sẵn sàng cho câu hỏi đầu tiên chưa? Hãy gõ 'Sẵn sàng' để bắt đầu."})

for message in st.session_state.messages:
    with st.chat_message("user" if message["role"] == "user" else "assistant"):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập câu trả lời..."):
    if not api_key:
        st.warning("Vui lòng nhập API Key!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        genai.configure(api_key=api_key)
        # Sửa lỗi: Chuyển Prompt vào nội dung chat thay vì system_instruction để tránh lỗi 404
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        full_prompt = f"Hệ thống: {SYSTEM_PROMPT}\n\nNgười dùng: {prompt}"
        
        with st.spinner('Đang phân tích...'):
            response = model.generate_content(full_prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "model", "content": response.text})

    except Exception as e:
        st.error(f"Đã xảy ra lỗi: {str(e)}")
