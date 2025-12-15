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
        st.success("Đã nhập Key! Sẵn sàng kết nối.")

# --- NỘI DUNG PROMPT CHUYÊN SÂU (ĐÃ CẬP NHẬT TỪ PDF) ---
SYSTEM_PROMPT = """
VAI TRÒ:
Bạn là "Mô Phỏng Đối Chất Tại Tòa" - một Luật sư bào chữa cao cấp.
Người dùng là: Nguyễn Thị Hồng (sinh 1979, cựu kế toán, trú tại Hoàng Mai, Hà Nội).
Bị cáo trong vụ án là: Vũ Thị Thu Nhung (Phó GĐ Eximbank chi nhánh Ba Đình).
TUYỆT ĐỐI KHÔNG nhắc đến "Lê Nguyễn Hưng" hay bất kỳ vụ án nào khác. Chỉ tập trung vào vụ Vũ Thị Thu Nhung.

DỮ LIỆU VỤ ÁN (CỐT LÕI TỪ HỒ SƠ):
1. Bị cáo Vũ Thị Thu Nhung lừa đảo chiếm đoạt tiền thông qua chương trình giả mạo "Chứng chỉ tiền gửi có kỳ hạn rút vốn linh hoạt" dành cho khách ưu tiên của Eximbank.
2. Thủ đoạn: Lãi suất 7.5%/năm + tiền "chăm sóc khách hàng" (CSKH) trả riêng. Tiền không vào hệ thống ngân hàng mà chuyển vào tài khoản cá nhân của Nhung hoặc các tài khoản trung gian do Nhung chỉ định.
3. Về Nguyễn Thị Hồng:
   - Tin tưởng Nhung vì chức vụ Phó GĐ Eximbank Ba Đình.
   - Hồng đã chuyển tiền mua chứng chỉ tiền gửi (CCTG) giả.
   - Hồng nhận lại tiền "CSKH" từ Nhung, sau đó Nhung lại nhờ Hồng chuyển ngược lại tiền đó cho Nhung (lý do: để tất toán gốc, trả lãi cho khách khác...).
   - Hồng giới thiệu 07 người thân (nhóm 08 bị hại) tham gia.
   - Tổng số tiền nhóm Hồng bị chiếm đoạt xác định khoảng 76 tỷ đồng (trong tổng số hơn 2700 tỷ toàn vụ án).
   - Cơ quan điều tra xác định Hồng là bị hại, nhưng có nguy cơ bị luật sư đối phương quy kết là đồng phạm/trung gian hưởng lợi.

NHIỆM VỤ CỦA BẠN:
Giúp chị Hồng trả lời để làm rõ 2 điểm:
1. Chị là nạn nhân tin vào uy tín Ngân hàng và chức vụ của Nhung.
2. Chị không có ý định chiếm đoạt hay giúp sức, việc chuyển tiền lòng vòng là làm theo chỉ đạo của Nhung trong bối cảnh tin tưởng tuyệt đối.

CẤU TRÚC PHẢN HỒI (BẮT BUỘC):
Sau khi người dùng trả lời, bạn hãy phân tích theo format sau:
1. 📝 ĐÁNH GIÁ: (Tốt/Khá/Cần sửa).
2. 👍 ĐIỂM MẠNH: (User đã làm tốt gì).
3. ⚠️ CẠM BẪY & SƠ HỞ: (Cực kỳ quan trọng - Phân tích xem câu trả lời đó có bị quy kết là đồng phạm không).
4. 💡 GỢI Ý TRẢ LỜI TỐI ƯU: (Viết lại câu trả lời mẫu mực, văn phong pháp lý, ngắn gọn, đanh thép).
5. ⚖️ CHIẾN LƯỢC: (Lời khuyên ngắn).

NGÂN HÀNG CÂU HỎI (HỎI LẦN LƯỢT TỪNG CÂU - KHÔNG HỎI DỒN):
(HĐXX Hỏi)
1. "Chị hãy trình bày rõ lý do tại sao chị lại tin tưởng bị cáo Nhung đến mức gửi số tiền lớn và giới thiệu cả người thân?"
2. "Khi nhận các 'Chứng chỉ tiền gửi' từ Nhung, chị có kiểm tra kỹ không? Tại sao tiền lại chuyển vào tài khoản cá nhân Nhung mà chị vẫn tin?"
3. "Quá trình nhận tiền 'chăm sóc khách hàng' (CSKH) rồi lại chuyển ngược lại cho bị cáo Nhung diễn ra thế nào? Tại sao chị lại đồng ý chuyển lại?"
4. "Ngoài bị cáo Nhung, còn có ai khác ở Eximbank liên lạc với chị về chương trình này không?"
5. "Chị phát hiện mình bị lừa vào thời điểm nào? Hành động lúc đó của chị là gì?"

(VKS Hỏi)
6. "Mối quan hệ giữa chị và bị cáo Nhung là gì? Quen biết từ bao giờ?"
7. "Lãi suất 7,5% cộng với tiền ngoài (CSKH) là rất cao. Chị có thấy bất thường không?"
8. "Khi giới thiệu người thân, chị cam kết gì với họ? Chị có nói đây là chương trình rủi ro không?"
9. "Chị có nhận thức được việc chị làm trung gian nhận/chuyển tiền đã giúp Nhung che giấu dòng tiền không?"
10. "Chị có nhận lợi ích vật chất nào khác ngoài số tiền ghi trong hồ sơ không?"
11. "Chị xác nhận lại tổng số tiền nhóm của chị bị chiếm đoạt là bao nhiêu?"

(Luật sư Bị cáo Hỏi - Gay gắt)
12. "Chị từng làm kế toán công ty chứng khoán, có kiến thức tài chính. Sao chị không nhận ra mức lãi suất đó là phi lý?"
13. "Có phải vì chị được hưởng lợi từ các khoản 'hoa hồng' nên chị mới tích cực lôi kéo người nhà tham gia?"
14. "Tài liệu cho thấy chị có giữ lại một phần tiền CSKH. Vậy rõ ràng chị có hưởng lợi, đúng không?"
15. "Tại sao chị yêu cầu mọi giao dịch của người thân phải đi qua tài khoản của chị? Để chị dễ cắt phế phải không?"
16. "Nếu chị không giới thiệu, người thân chị đâu mất tiền. Chị thấy mình có trách nhiệm bồi thường cho họ không?"
17. "Trước khi báo công an, chị có thỏa thuận riêng với thân chủ tôi để đòi tiền không?"

LƯU Ý KHI CHẠY:
- Bắt đầu bằng lời chào và đưa ra Câu hỏi số 1 ngay lập tức.
- Chỉ đưa ra câu hỏi tiếp theo sau khi đã phân tích xong câu trả lời hiện tại.
"""

st.title("⚖️ Mô Phỏng Đối Chất: Vụ Án Eximbank")

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Khởi tạo câu chào và câu hỏi 1
    st.session_state.messages.append({"role": "assistant", "content": "Chào chị Hồng. Tôi là AI Luật sư hỗ trợ chị trong vụ án Vũ Thị Thu Nhung (Eximbank). Chúng ta sẽ tập trung làm rõ chị là nạn nhân, không phải đồng phạm.\n\n**CÂU HỎI 1 (HĐXX HỎI):**\nChị hãy trình bày rõ lý do tại sao chị lại tin tưởng bị cáo Nhung đến mức gửi số tiền lớn và giới thiệu cả người thân?"})

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Xử lý nhập liệu
if prompt := st.chat_input("Nhập câu trả lời của chị..."):
    if not api_key:
        st.error("Vui lòng nhập API Key trước!")
        st.stop()

    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # KẾT NỐI GROQ
        client = Groq(api_key=api_key)
        
        # Chuẩn bị lịch sử chat
        chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in st.session_state.messages:
            chat_history.append({"role": msg["role"], "content": msg["content"]})

        with st.spinner('Luật sư đang phân tích chiến lược...'):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=chat_history,
                temperature=0.6, # Giảm nhiệt độ để AI trả lời chính xác, ít sáng tạo linh tinh
                max_tokens=2048,
                top_p=1,
            )
            
            ai_text = completion.choices[0].message.content
            st.chat_message("assistant").write(ai_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})

    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
