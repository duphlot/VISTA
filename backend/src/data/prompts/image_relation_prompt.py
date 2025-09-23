IMAGE_RELATION_PROMPT = """
    Xác định tất cả các vật thể trong hình và mô tả quan hệ cặp giữa chúng.
    Quy tắc:
    1. Nếu nhiều vật thể cùng tên, đánh số: người1, người2, ghế1, ghế2,...
    2. Nếu vật thể xuất hiện trong frame trước, giữ cùng ID.
    3. Nếu vật thể mới xuất hiện, thêm mô tả ngắn gọn trong (): ví dụ màu sắc, kiểu dáng.
       Ví dụ: người1 (mặc áo đỏ), ghế1 (bằng gỗ)
    4. Sử dụng định dạng: <vật thể1> - <quan hệ> - <vật thể2>
    5. Chỉ xuất ra quan hệ, không thêm câu mô tả khác. NẾU ĐƯỢC THÌ HÃY THÊM CẢM XÚC CỦA NGƯỜI ĐÓ VÀO SCENE GRAPH NỮA.
    6. Chỉ trả về JSON, dạng danh sách: ["vật thể1 (mô tả) - quan hệ - vật thể2 (mô tả)", "..."]
    7. Người không chỉ là người mà còn phải mô tả trên cái ảnh gốc á.
    8. Dịch tất cả tên vật thể sang tiếng Việt.
    **LƯU Ý:***
      - Sử dụng frame mask để nhận diện object và quan hệ.
      - **Chỉ sử dụng ảnh gốc để mô tả object mới**.
      - Nếu object là người, mô tả tuổi/lớn bé/quần áo trong và hành động (): ví dụ: người1 (trẻ - nữ, mặc áo đỏ, đang ăn, vui vẻ)
      - *LÀ OBJECT NGỪOI THÌ PHẢI CÓ ĐỦ 4 CÁI LÀ MÔ TRẢ TUỔI - Giới tính, MÔ TẢ MẶC GÌ, MÔ TẢ ĐANG LÀM GÌ, MÔ TẢ CẢM XÚC*
      - Nếu object khác, mô tả màu sắc, chất liệu, kiểu dáng trong ().
      - Giữ ID object giống frame trước nếu đã xuất hiện.
      - Chỉ xuất ra quan hệ theo định dạng: <object1> - <quan hệ> - <object2>
      - Trả về JSON: ["người1 (trẻ - nam, mặc áo đỏ, đang ăn, vui vẻ) - đứng cạnh - ghế1 (bằng gỗ)", ...]
      - Tin tưởng dữ liệu ảnh trước đó, không dựa trên ảnh đã frame để xác định màu, dữ liệu là dữ liệu của các frame liền kề trong một video nên người đó không thể thay đồ được, nên mà cùng màu, *RIÊNG HÀNH ĐỘNG THÌ CÓ THỂ THAY ĐỔI THEO THỜI GIAN NHA*.
      - Nếu object trong frame này và frame trước giống nhau thì phải để giống nhau.
    *ĐẶC BIỆT LƯU Ý, CHỈ TRẢ VỀ JSON*
"""