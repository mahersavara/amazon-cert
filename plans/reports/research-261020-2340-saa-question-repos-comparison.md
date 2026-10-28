# So sánh 4 repo câu hỏi SAA-C03 trên GitHub

Date: 2026-10-20 · Method: đọc cấu trúc, README, lịch sử commit, issue; đếm câu; chấm thử mẫu. Không chép lại nội dung câu hỏi.

## Kết quả
| Tiêu chí | Iamrushabhshahh | NebulaTris | Ditectrev | Thiago-code-lab |
|---|---|---|---|---|
| ★ / fork | 1118 / 422 | 72 / 21 | 766 / 321 | 968 / 242 |
| Số câu thật | ~540 (README ghi 650+, số thứ tự nhảy tới 613, có câu trống) | = bản sao repo 1 | 220 bản free | ~5/file × 30 file |
| Kiểu câu | Tình huống SAA-C03 | như repo 1 | Phần lớn trivia cũ (EC2 SOAP, EC2-Classic, "Master account"); 28 lần nhắc dịch vụ/khái niệm legacy | Sinh từ template, 4 lựa chọn chung chung, đáp án hiển nhiên |
| Giải thích | ~94% câu có | như repo 1 | Không (giải thích chỉ có ở khoá Udemy trả phí) | Có nhưng rỗng, lặp |
| Chấm mẫu | 6/6 câu có đáp án đúng; 2/8 câu mẫu thiếu đáp án | — | Đúng nhưng không còn sát đề C03 | Vô nghĩa để luyện |
| Cộng đồng sửa lỗi | ~30 issue báo sai đáp án, phần lớn đã đóng; còn mở: #31, #33, #45, #53, #58, #60, #61, #63 | Không | Ít | Không |
| Cập nhật | Commit cuối 2026-08 | Chỉ 1 ngày commit (2025-08-02) | 2026-10 (chủ yếu link bán hàng) | 2026-09 |
| Nguồn gốc | Tên gốc repo là "...Exam-Dump-With-Solution"; còn nhãn "Most Voted" → chép từ ExamTopics (câu hỏi người thi nhớ lại) | Ghi rõ lấy từ repo 1 (97% đoạn trùng); kèm PDF slide khoá Stephane Maarek (phát tán tài liệu có bản quyền) | Funnel bán ebook/sách/khoá học | Tự viết (khả năng cao AI) |

## Xếp hạng
1. **Iamrushabhshahh** — bộ duy nhất đáng giá: đúng kiểu đề C03, có giải thích, có cộng đồng báo lỗi. Rủi ro lớn nhất: nguồn là câu hỏi đề thật được nhớ lại → vi phạm điều khoản thi AWS.
2. NebulaTris — không thêm gì so với repo 1.
3. Ditectrev — lỗi thời, không giải thích, chủ yếu để bán hàng.
4. Thiago — câu hỏi vô dụng (phần ghi chú tiếng Bồ có thể vẫn đọc được).

## Nếu dùng repo 1
- Đọc các issue đang mở trước, ghi chú câu bị báo sai.
- Câu "ans" trống hoặc không có giải thích → tự kiểm tra bằng docs AWS / Tutorials Dojo.
- Nhãn "Most Voted" là phiếu bầu cộng đồng, không phải đáp án chính thức.

## Câu hỏi mở
- Mẫu chấm chỉ 8 câu; tỉ lệ sai thực tế của repo 1 chưa đo.
