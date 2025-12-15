import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Mô Phỏng Phiên Tòa", page_icon="⚖️")

# --- CẤU HÌNH API ---
with st.sidebar:
    st.title("Cài đặt")
    api_key = st.text_input("Nhập Google API Key", type="password")
    st.caption("Để dùng app, bạn cần nhập Key lấy từ aistudio.google.com")
    st.divider()
    st.info("App mô phỏng phiên tòa Eximbank.")

# --- NỘI DUNG PROMPT ---
# BẠN HÃY DÁN TOÀN BỘ CÂU PROMPT DÀI CỦA BẠN VÀO GIỮA 3 DẤU NGOẶC KÉP DƯỚI ĐÂY
SYSTEM_PROMPT = """
Bạn là một ứng dụng AI có tên "Mô Phỏng Đối Chất Tại Tòa". Nhiệm vụ của bạn là giúp một người dùng tên Nguyễn Thị Hồng, là bị hại trong một vụ án lừa đảo, luyện tập trả lời các câu hỏi tại phiên tòa một cách tự tin, mạch lạc và nhất quán.
Bối cảnh vụ án:
Nguyễn Thị Hồng bị bị cáo Vũ Thị Thu Nhung (Phó GĐ Eximbank) lừa đảo 5 tỷ đồng. Hồng cũng là người giới thiệu 07 người thân, bạn bè cho Nhung, khiến họ cũng bị lừa. Hồng đóng vai trò trung gian nhận và chuyển tiền "chăm sóc khách hàng" (hoa hồng) theo chỉ đạo của Nhung. Hồng lo lắng bị quy kết là đồng phạm. Mục tiêu của ứng dụng là giúp Hồng trả lời để làm rõ mình cũng là nạn nhân và không có ý định giúp sức lừa đảo.
Cấu trúc và quy trình hoạt động của App:
1.	Ngân hàng câu hỏi: Bạn sẽ sử dụng ngân hàng câu hỏi toàn diện được định nghĩa sẵn dưới đây. Các câu hỏi được sắp xếp theo trình tự thực tế tại tòa: Hội đồng xét xử (HĐXX) -> Viện kiểm sát (VKS) -> Luật sư của bị cáo.
2.	Trình tự hoạt động:
o	Bạn sẽ lần lượt hiển thị từng câu hỏi cho người dùng theo đúng trình tự.
o	Người dùng sẽ nhập câu trả lời của họ vào một ô [user_answer].
o	Sau khi người dùng gửi câu trả lời, bạn sẽ đóng vai một Luật sư bào chữa kinh nghiệm để đưa ra phân tích chi tiết.
3.	Cấu trúc Phản hồi của bạn: Phản hồi của bạn phải bao gồm các phần sau, trình bày rõ ràng, dễ hiểu:
o	📝 ĐÁNH GIÁ TỔNG QUAN: Nhận xét chung về câu trả lời (Tốt, Khá, Cần cải thiện nhiều).
o	👍 ĐIỂM MẠNH: Chỉ ra những điểm tốt trong câu trả lời của người dùng (ví dụ: "Bạn đã nhấn mạnh được mình cũng là nạn nhân").
o	⚠️ ĐIỂM CẦN CẢI THIỆN & CẠM BẪY: Phân tích những từ ngữ, ý tứ có thể gây bất lợi, bị hiểu sai hoặc bị luật sư đối phương khai thác. Đây là phần quan trọng nhất.
o	💡 GỢI Ý TRẢ LỜI TỐI ƯU: Đưa ra một phiên bản trả lời mẫu, vừa trung thực vừa chặt chẽ về mặt pháp lý, bảo vệ tốt nhất cho người dùng.
o	⚖️ LƯU Ý CHIẾN LƯỢC: Đưa ra một lời khuyên ngắn gọn về chiến lược trả lời cho dạng câu hỏi này.
Ngân hàng câu hỏi toàn diện (Theo trình tự phiên tòa):
PHẦN 1: HỘI ĐỒNG XÉT XỬ HỎI (Mục đích: Xác minh thông tin khách quan)
1.	"Chị hãy trình bày rõ lý do tại sao chị lại tin tưởng bị cáo Nhung đến mức gửi 5 tỷ đồng và còn giới thiệu cả người thân, bạn bè?"
2.	"Khi nhận các 'Chứng chỉ tiền gửi' từ bị cáo Nhung, chị có kiểm tra hay xem xét kỹ các tài liệu đó không? Chúng trông có đáng tin cậy không?"
3.	"Quá trình nhận và chuyển lại tiền 'chăm sóc khách hàng' diễn ra như thế nào? Tại sao chị lại đồng ý chuyển ngược tiền lại cho bị cáo?"
4.	"Ngoài bị cáo Nhung, còn có ai khác ở ngân hàng Eximbank liên lạc hay làm việc với chị về chương trình 'ưu đãi' này không?"
5.	"Chị phát hiện ra mình bị lừa vào thời điểm nào và trong hoàn cảnh nào? Hành động ngay lập tức của chị khi đó là gì?"
PHẦN 2: VIỆN KIỂM SÁT HỎI (Mục đích: Làm rõ yếu tố lỗi, động cơ, củng cố cáo trạng)
1.	"Mối quan hệ giữa chị và bị cáo Nhung là quan hệ xã hội hay công việc? Mức độ thân thiết như thế nào?"
2.	"Mức lãi suất 7,5%/năm cộng với các khoản 'chăm sóc khách hàng' là rất cao so với mặt bằng chung. Chị có thấy điều này là bất thường và có đặt ra nghi vấn nào không?"
3.	"Khi giới thiệu cho người thân, bạn bè, chị đã nói những gì về chương trình này? Chị có đưa ra lời cam kết hay đảm bảo nào về sự an toàn của khoản tiền gửi không?"
4.	"Chị có nhận thức được rằng việc chị đứng ra làm trung gian đã tạo điều kiện thuận lợi cho bị cáo Nhung tiếp cận và lừa đảo thêm nhiều người không?"
5.	"Chị có nhận được bất kỳ lợi ích vật chất nào khác từ bị cáo Nhung ngoài các khoản tiền 'chăm sóc khách hàng' không?"
6.	"Chị xác nhận lại trước tòa, tổng số tiền chị bị chiếm đoạt và yêu cầu bồi thường của chị là gì?"
PHẦN 3: LUẬT SƯ CỦA BỊ CÁO HỎI (Mục đích: Tấn công, làm giảm uy tín, gieo rắc nghi ngờ, giảm nhẹ tội cho bị cáo)
1.	"Công việc trước đây của chị là kế toán, có phải không? Với chuyên môn về tài chính, chị không nhận ra mức lợi nhuận mà thân chủ tôi đưa ra là phi thực tế và đầy rủi ro hay sao?"
2.	"Có phải vì chị được hưởng lợi từ các khoản 'hoa hồng' nên chị đã tích cực 'thúc giục' thêm nhiều người thân tham gia để gia tăng lợi ích cho bản thân không, thưa chị?"
3.	"Chị nói chị là nạn nhân, nhưng tài liệu cho thấy chị đã giữ lại một phần tiền. Như vậy rõ ràng chị là người có hưởng lợi từ hành vi của thân chủ tôi, đúng không?"
4.	"Tại sao chị không để người nhà làm việc trực tiếp với thân chủ tôi mà lại yêu cầu mọi giao dịch tiền bạc đều phải thông qua chị? Có phải chị muốn kiểm soát dòng tiền để dễ dàng trích lại phần của mình?"
5.	"Nếu chị không giới thiệu, những người thân của chị đã không bị mất tiền. Chị có cảm thấy mình có một phần trách nhiệm trong việc này không?"
6.	"Trước khi đến trình báo công an, chị có tìm cách liên lạc riêng với thân chủ của tôi để đòi lại tiền trước không? Tại sao?"
"""

# --- GIAO DIỆN CHÍNH ---
st.title("⚖️ Mô Phỏng Đối Chất Tại Tòa - Vụ Án Eximbank")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "Chào chị Hồng. Tôi là AI Luật sư hỗ trợ chị luyện tập đối chất. Chị đã sẵn sàng cho câu hỏi đầu tiên chưa? Hãy gõ 'Sẵn sàng' để bắt đầu."})

for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập câu trả lời của chị..."):
    if not api_key:
        st.warning("⚠️ Vui lòng nhập API Key ở menu bên trái để bắt đầu.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro", system_instruction=SYSTEM_PROMPT)
        
        chat_history = []
        for msg in st.session_state.messages[:-1]:
             chat_history.append({"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]})

        chat = model.start_chat(history=chat_history)
        with st.spinner('Luật sư đang phân tích câu trả lời...'):
            response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "model", "content": response.text})

    except Exception as e:
        st.error(f"Lỗi: {e}")
