# Review & Sentiment Dashboard — Power BI Project

## Cấu trúc trang

- **1 · Tổng quan**: 5 KPI, xu hướng tháng, ranking brand và tỷ lệ complaint ẩn.
- **2 · Khía cạnh**: matrix/heatmap net sentiment, tần suất khía cạnh và cơ cấu sentiment.
- **3 · Ad-hoc**: brand rủi ro, khía cạnh yếu, review khuôn mẫu và watchlist sản phẩm.

## Dữ liệu 
- `fact_reviews`: 7.364 dòng.
- `fact_absa`: 12.200 dòng. Một review có thể xuất hiện nhiều dòng cho cùng khía cạnh vì dữ liệu lưu theo lượt nhắc/clause; vì vậy visual dùng nhãn **Lượt nhắc khía cạnh**.
- `dim_product`: 152 sản phẩm; `dim_brand`: 5 brand; `dim_date`: 72 tháng.

