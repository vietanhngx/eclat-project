# 🎯 Hệ thống Gợi ý Nội dung dựa trên Thuật toán Eclat

> **Bài tập lớn môn Khai phá Dữ liệu** - Trường Đại học Xây dựng Hà Nội

## 👥 Nhóm thực hiện

| STT | Họ và tên | MSSV |
|-----|-----------|------|
| 1 | Nguyễn Việt Anh | 0203968 |
| 2 | Nguyễn Việt Hùng | 0208768 |
| 3 | Đỗ Quang Hợp | 0208568 |

**Lớp:** 68CS2  
**GVHD:** Phạm Hồng Phong

---

## 📌 Mục tiêu đề tài

Phân tích dữ liệu log truy cập (clickstream) để tìm ra các nhóm nội dung thường được xem cùng nhau, từ đó đưa ra gợi ý:

> *"Nếu người dùng xem nội dung A, hãy gợi ý nội dung B"*

## 📂 Cấu trúc thư mục

Eclat_Project/
|-- data/
|   +-- raw/
|       +-- msnbc.seq           # Dữ liệu gốc từ UCI
|-- docs/
|   |-- baocao.tex              # Báo cáo LaTeX chính
|   |-- presentation.tex        # Slide thuyết trình
|   +-- images/                 # Hình ảnh biểu đồ
|-- src/
|   |-- data_loader.py          # Module đọc và tiền xử lý dữ liệu
|   |-- eclat.py                # Thuật toán Eclat (Vertical Data Format)
|   |-- apriori.py              # Thuật toán Apriori (để so sánh)
|   +-- utils.py                # Sinh luật và hiển thị gợi ý
|-- main.py                     # File điều phối chính (Entry point)
|-- compare_algorithms.py       # Script so sánh hiệu năng Eclat vs Apriori
|-- comparison_results.csv      # Kết quả so sánh dạng CSV
|-- requirements.txt            # Dependencies (matplotlib, etc.)
+-- README.md                   # File hướng dẫn này
```

## 🚀 Hướng dẫn chạy

### 1. Phân tích dữ liệu (Python)
Yêu cầu: Python 3.x (Chỉ sử dụng thư viện chuẩn: `os`, `collections`, `itertools`)

```bash
# Tại thư mục gốc Eclat_Project/
python main.py
```

**Tham số cấu hình (trong main.py):**
- `MIN_SUPPORT = 0.02` (2%) - Ngưỡng hỗ trợ tối thiểu
- `MIN_CONFIDENCE = 0.4` (40%) - Ngưỡng độ tin cậy tối thiểu
- `DATA_LIMIT = None` - Đọc toàn bộ dữ liệu

### 2. So sánh hiệu năng Eclat vs Apriori
Kịch bản: Chạy cả 2 thuật toán trên cùng tập dữ liệu (989,818 dòng) với các ngưỡng Support khác nhau.

```bash
python compare_algorithms.py
```
*Kết quả sẽ được lưu vào `comparison_results.csv` và vẽ biểu đồ vào `docs/images/comparison_chart.png`.*

## 📊 Dữ liệu

**Nguồn:** [MSNBC.com Anonymous Web Data - UCI Repository](https://archive.ics.uci.edu/dataset/133/msnbc+com+anonymous+web+data)

**Thông tin:**
- Số phiên: **989,818**
- Số chuyên mục: **17**
- Thu thập: 28/09/1999

**Bảng ánh xạ 17 chuyên mục:**

| ID | Tên tiếng Việt | ID | Tên tiếng Việt |
|----|----------------|----|----------------|
| 1  | Trang chủ      | 10 | Đời sống       |
| 2  | Tin tức        | 11 | Kinh doanh     |
| 3  | Công nghệ      | 12 | Thể thao       |
| 4  | Địa phương     | 13 | Tóm tắt        |
| 5  | Ý kiến         | 14 | Diễn đàn       |
| 6  | Phát sóng      | 15 | Du lịch        |
| 7  | Tổng hợp       | 16 | Tin MSN        |
| 8  | Thời tiết      | 17 | Thể thao MSN   |
| 9  | Sức khỏe       |    |                |

## 🧠 Thuật toán Eclat

**Eclat (Equivalence Class Clustering and bottom-up Lattice Traversal)** - Zaki (2000)

**Đặc điểm:**
- Sử dụng **Vertical Data Format** (định dạng dữ liệu dọc)
- **Depth-First Search** thay vì BFS như Apriori
- Tính Support bằng **phép giao TID-Sets**
- Chỉ cần **một lần quét** cơ sở dữ liệu

## 📈 Các chỉ số đánh giá

| Chỉ số | Công thức | Ý nghĩa |
|--------|-----------|---------|
| **Support** | P(A ∩ B) | Tần suất xuất hiện đồng thời |
| **Confidence** | Support(A∪B) / Support(A) | Xác suất B khi đã xem A |
| **Lift** | Support(A∪B) / (Support(A) × Support(B)) | Độ tương quan (>1: tích cực) |

## 📝 Kết quả thực nghiệm

Khi chạy với cấu hình `MIN_SUPPORT=0.02` và `MIN_CONFIDENCE=0.40`:

```text
[1] Đọc dữ liệu: 989,818 phiên
[2] Kết quả Eclat: 32 tập phổ biến (15 items đơn, 17 cặp)
[3] Sinh luật: 5 luật thỏa mãn
```

**Top 5 luật gợi ý mạnh nhất:**

| STT | Nếu xem | Gợi ý | Support | Conf. | Lift | Ý nghĩa |
|---|---|---|---|---|---|---|
| 1 | Tổng hợp | Phát sóng | 3.36% | 41.3% | **1.88** | Khả năng xem tiếp cao hơn ngẫu nhiên 88% |
| 2 | Kinh doanh | Trang chủ | 3.31% | **56.8%** | 1.80 | Hơn 56% người xem Kinh doanh sẽ về Trang chủ |
| 3 | Đời sống | Trang chủ | 2.65% | 51.9% | 1.64 | |
| 4 | Tổng hợp | Trang chủ | 3.68% | 45.2% | 1.43 | |
| 5 | Tin tức | Trang chủ | 7.55% | 42.6% | 1.35 | |

```
===========================================================================
   💡 TOP 5 LUẬT GỢI Ý NỘI DUNG MẠNH NHẤT
===========================================================================

STT  | NẾU XEM         | GỢI Ý           | SUPPORT  | CONF    | LIFT
---------------------------------------------------------------------------
1    | Tổng hợp        | Phát sóng       | 3.36%    | 41.3%   | 1.88
2    | Kinh doanh      | Trang chủ       | 3.31%    | 56.8%   | 1.80
3    | Đời sống        | Trang chủ       | 2.65%    | 51.9%   | 1.64
4    | Tổng hợp        | Trang chủ       | 3.68%    | 45.2%   | 1.43
5    | Tin tức         | Trang chủ       | 7.55%    | 42.6%   | 1.35
```

## ⚖️ So sánh hiệu năng Eclat vs Apriori

Thực nghiệm trên toàn bộ tập dữ liệu (với Min Support = 1%):

| Tiêu chí | Apriori (Horizontal) | Eclat (Vertical) | Nhận xét |
|---|---|---|---|
| **Thời gian** | 15.62s | **2.16s** | **Eclat nhanh hơn ~7 lần** |
| **Bộ nhớ (RAM)** | **0.04 MB** | 111.81 MB | Apriori tốn ít RAM hơn |
| **Cơ chế** | Quét lại DB nhiều lần | Giao TID-Sets trên RAM | Space-Time Trade-off |

> **Kết luận:** Eclat đánh đổi việc tiêu tốn bộ nhớ để đạt được tốc độ xử lý vượt trội, phù hợp với các hệ thống hiện đại có dung lượng RAM lớn.

## 📚 Tài liệu tham khảo

1. Zaki, M.J. (2000). *Scalable Algorithms for Association Mining*. IEEE TKDE.
2. Han, J., Kamber, M. (2011). *Data Mining: Concepts and Techniques* (3rd ed.).
3. Agrawal, R. et al. (1993). *Mining Association Rules Between Sets of Items*.
