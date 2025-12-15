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
        st.success("Đã nhập Key! Sẵn sàng.")

# --- NỘI DUNG PROMPT (ĐÃ CHỈNH FORMAT ĐẸP) ---
SYSTEM_PROMPT = """
VAI TRÒ:
Bạn là "Mô Phỏng Đối Chất Tại Tòa" - một Luật sư bào chữa cao cấp.
Người dùng là: Nguyễn Thị Hồng (sinh 1979, cựu kế toán, bị hại trong vụ án Eximbank).
Bị cáo: Vũ Thị Thu Nhung (Phó GĐ Eximbank Ba Đình).

QUY ĐỊNH VỀ ĐỊNH DẠNG (BẮT BUỘC):
Để người dùng dễ đọc, bạn KHÔNG ĐƯỢC viết liền một khối. Bạn PHẢI trình bày câu trả lời theo cấu trúc Markdown rõ ràng như sau (có xuống dòng giữa các mục):

### 📝 ĐÁNH GIÁ
(Nội dung đánh giá ngắn gọn...)

### 👍 ĐIỂM MẠNH
(Chỉ ra điểm tốt...)

### ⚠️ CẠM BẪY & SƠ HỞ
(Phân tích rủi ro pháp lý...)

### 💡 GỢI Ý TRẢ LỜI TỐI ƯU
(Viết câu trả lời mẫu...)

### ⚖️ CHIẾN LƯỢC
(Lời khuyên...)

---
**CÂU HỎI TIẾP THEO:**
(Đưa ra câu hỏi tiếp theo tại đây)

---
DỮ LIỆU VỤ ÁN:
- Vũ Thị Thu Nhung (Phó GĐ Eximbank) lừa đảo qua chương trình giả "Chứng chỉ tiền gửi rút gốc linh hoạt".
- Hồng tin tưởng chức vụ của Nhung nên gửi tiền và giới thiệu 7 người thân.
- Tiền không vào hệ thống Eximbank mà vào tài khoản cá nhân Nhung hoặc trung gian do Nhung chỉ định.
- Hồng có nhận tiền "CSKH" (tiền ngoài) và chuyển lại cho Nhung theo chỉ đạo.
- Mục tiêu: Chứng minh Hồng là nạn nhân tin vào uy tín ngân hàng, không phải đồng phạm.

NGÂN HÀNG CÂU HỎI (Hỏi lần lượt, không hỏi dồn):
1. Tại sao chị tin Nhung gửi số tiền lớn và giới thiệu người thân?
2. Khi nhận CCTG giả, chị có kiểm tra không? Tại sao tiền chuyển vào tài khoản cá nhân Nhung mà vẫn tin?
3. Quá trình nhận/chuyển lại tiền "CSKH" diễn ra thế nào?
4. Có ai khác ở Eximbank liên lạc không?
5. Phát hiện bị lừa khi nào? Hành động là gì?
6. Mối quan hệ với Nhung là gì?
7. Lãi suất cao bất thường có nghi ngờ không?
8. Cam kết gì khi giới thiệu người thân?
9. Có nhận thức việc trung gian dòng tiền là giúp sức không?
10. Có nhận lợi ích vật chất nào khác không?
11. Xác nhận tổng số tiền bị chiếm đoạt?
12. Có chuyên môn kế toán sao không biết rủi ro?
13. Có phải vì hưởng lợi hoa hồng nên lôi kéo người thân?
14. Có giữ lại một phần tiền CSKH không?
15. Tại sao giao dịch phải qua trung gian tài khoản chị?
16. Trách nhiệm của chị với người thân?
17. Có thỏa thuận đòi tiền riêng trước khi báo công an không?
"""

st.title("⚖️ Mô Phỏng Đối Chất: Vụ Án Eximbank")

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Khởi tạo câu chào
    welcome_msg = """Chào chị Hồng. Tôi là AI Luật sư hỗ trợ chị. Chúng ta sẽ bắt đầu ngay.

**CÂU HỎI 1 (HĐXX HỎI):**
Chị hãy trình bày rõ lý do tại sao chị lại tin tưởng bị cáo Nhung đến mức gửi số tiền lớn và giới thiệu cả người thân?"""
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Xử lý nhập liệu
if prompt := st.chat_input("Nhập câu trả lời của chị..."):
    if not api_key:
        st.error("Vui lòng nhập API Key trước!")
        st.stop()

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        client = Groq(api_key=api_key)
        
        chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in st.session_state.messages:
            chat_history.append({"role": msg["role"], "content": msg["content"]})

        with st.spinner('Luật sư đang phân tích...'):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=chat_history,
                temperature=0.6,
                max_tokens=2048,
                top_p=1,
            )
            
            ai_text = completion.choices[0].message.content
            st.chat_message("assistant").markdown(ai_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})

    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
