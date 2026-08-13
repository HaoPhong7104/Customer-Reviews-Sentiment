# Phân tích & Phân loại Review Sản phẩm Skincare trên sàn TMĐT

## Vì sao chọn bài toán này
Xử lý/phân loại dữ liệu từ MXH/sàn TMĐT, xác định
thông tin có giá trị, phân loại cảm xúc phản hồi, phân loại tính chất sản phẩm từ đó hỗ trợ cho các brand.
Project dùng 7.366 review skincare, chủ yểu phân tích 5 brand: Eucerin, CeraVe, Obagi, URIAGE, Murad;
để giải quyết đúng việc cốt lõi đó, project này gói gọn trong **4 notebook chính**:

| Notebook | Việc |
|---|---|
| `00_data_collection_merge.ipynb` | Xử lý cơ bản dữ liệu thô thu thập được từ Lazada |
| `01_data_processing.ipynb` | Lọc ngôn ngữ, làm sạch, EDA, phát hiện review rác/mẫu, gắn cờ khía cạnh | 
| `02_absa_sentiment.ipynb` | ABSA rule-based: sentiment riêng cho từng khía cạnh trong 1 review |
| `03_powerbi_export.ipynb` | Xuất star schema, sẵn sàng nạp Power BI | 


## Notebook 0  — Thu thập & Gom dữ liệu thô
- Xử lý dữ liệu cơ bản sau khi có dữ liệu thô từ sàn Lazada
## Notebook 1 — Xử lý dữ liệu
- **Lọc ngôn ngữ**: dùng `langdetect` để chỉ giữ lại review tiếng Việt —
  phát hiện dữ liệu gốc có lẫn 383/7.806 review (~4.9%) không phải tiếng
  Việt (196 review tiếng Anh hợp lệ + phần còn lại là spam/gibberish bị
  nhận nhầm mã ngôn ngữ khác). Lexicon ABSA ở notebook 2 chỉ đúng với
  tiếng Việt, nên bước này bắt buộc phải làm trước, nếu không các review
  ngoại ngữ sẽ làm loãng mẫu số khi tính % ở mọi bước sau.
- Làm sạch whitespace, loại review rỗng/gần rỗng (<3 ký tự).
- Phát hiện review **rác/mẫu có sẵn**: quá ngắn (<8 ký tự) hoặc lặp lại
  y hệt ≥5 lần, cần loại trừ khi tính điểm trung bình để tránh sai lệch.
- Gắn cờ **7 khía cạnh sản phẩm** (Hiệu quả, Giá cả, Chất lượng/Đóng gói,
  Giao hàng, Mùi hương/Kết cấu, Thành phần, Dịch vụ/Uy tín) cho từng
  review bằng từ điển từ khóa (multi-label).

## Notebook 2 — ABSA rule-based
Vì sao không dùng "1 review = 1 sentiment": review skincare thường **vừa
khen vừa chê** ("sản phẩm tốt nhưng giao hàng chậm") — nếu gán 1 nhãn
chung sẽ mất thông tin. ABSA giải quyết bằng cách:
1. Tách review thành từng **clause** (mệnh đề) theo dấu câu/liên từ
   tương phản ("nhưng", "tuy nhiên", "còn"...).
2. Với mỗi clause: phát hiện khía cạnh + tính cực tính **riêng trong
   clause đó** bằng lexicon tiếng Việt, có xử lý phủ định đơn giản
   ("không tốt" → tiêu cực, "không tệ" → tích cực).

**Kết quả (trên 7.366 review tiếng Việt đã lọc):**
- **32.3% review có sentiment khác nhau giữa các khía cạnh** (mixed-
  sentiment) — con số định lượng chứng minh giá trị của ABSA so với
  whole-review sentiment.
- **"Complaint ẩn"** (review ≥4⭐ nhưng có khía cạnh bị chê): 5.6% tổng
  review; URIAGE và Eucerin có tỉ lệ cao nhất (7.6%, 6.2%).
- Bảng **net sentiment (%positive − %negative) theo aspect × brand**:
  **"Giao hàng" là điểm yếu chung của mọi brand** (0.07–0.23, thấp nhất
  trong 7 khía cạnh), "Mùi hương/Kết cấu" luôn được khen nhiều nhất
  (0.63–0.79).

## 5. Notebook 4 — Xuất Power BI
Xuất theo mô hình **star schema**: 3 bảng dimension (`dim_brand`,
`dim_product` đã dedup giá/sold_count, `dim_date`) + 2 bảng fact:
- `fact_reviews` (grain = 1 review, có sẵn cờ khía cạnh + `hidden_complaint`)
- `fact_absa` (grain = 1 review × 1 khía cạnh, dùng để lọc/slice theo
  khía cạnh trong Power BI, VD "chỉ xem sentiment khía cạnh Giao hàng")

## Hạn chế 
- Aspect keyword và lexicon cảm xúc là rule-based, tự xây bằng tay — nếu
  có 200-300 review được gán nhãn thủ công sẽ đánh giá được độ chính xác
  thật (hiện tại chưa có ground truth để tính precision/recall chính
  thức, mới chỉ kiểm tra bằng cách đọc mẫu).
- Có thể mở rộng aspect keywords bằng topic modeling (BERTopic) thay vì
  liệt kê tay, hoặc thay lexicon bằng PhoBERT cho ABSA nếu cần
  độ chính xác cao hơn ở các câu phức tạp/phủ định gián tiếp.
