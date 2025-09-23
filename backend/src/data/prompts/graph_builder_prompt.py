GRAPH_BUILDER_PROMPT = """
Nhiệm vụ:
1. So sánh các object giữa các frame dựa trên tên và mô tả trong ().
2. Nếu cùng một object xuất hiện ở nhiều frame, trả về quan hệ same_entity:
   <object_x> (frame: <frame_i>) - same_entity - <object_y> (frame: <frame_j>)
3. Chỉ trả về **text thuần**, mỗi quan hệ 1 dòng, không JSON, không ngoặc vuông, không dấu nháy.
4. Giữ quan hệ gốc từ các frame, chỉ thêm quan hệ same_entity.
"""