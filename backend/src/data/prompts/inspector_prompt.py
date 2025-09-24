Inspector_PROMPT = """
Nhiệm vụ của bạn là KIỂM TRA scene graph được sinh ra có hợp lệ hay không.

Yêu cầu kiểm tra:
1. Kết quả phải ở đúng định dạng JSON (list các string).
2. Mỗi phần tử trong JSON phải theo định dạng:
   "<object1 (mô tả)> - <quan hệ> - <object2 (mô tả)>".
3. Các object phải tuân theo quy tắc đánh số, giữ ID, mô tả chi tiết (tuổi, giới tính, quần áo, hành động, cảm xúc cho người; màu sắc, chất liệu, kiểu dáng cho vật thể khác).
4. Không được có văn bản ngoài JSON (không thêm câu giải thích, tiêu đề hoặc ký hiệu khác).
5. Nếu phát hiện vi phạm, hãy trả về một JSON hợp lệ trống: [].
6. Nếu hợp lệ, trả về nguyên bản JSON đó (không sửa đổi nội dung).

Chỉ trả về JSON kết quả cuối cùng, không thêm bất kỳ chữ nào khác.
"""
