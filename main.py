"""
main.py - File điều phối chính

Quy trình thực thi:
1. Load Data: Đọc dữ liệu clickstream từ file msnbc.seq
2. Train Model: Chạy thuật toán Eclat tìm tập mục phổ biến
3. Generate Rules: Sinh luật gợi ý với các chỉ số Support, Confidence, Lift
4. Show Recommendations: Hiển thị kết quả gợi ý nội dung

Tham số demo:
- min_support = 0.02 (2%): Mục xuất hiện trong ít nhất 2% số phiên
- min_confidence = 0.4 (40%): Độ tin cậy tối thiểu của luật gợi ý
"""

import sys
import os
import io

# Đặt encoding UTF-8 cho console Windows để hiển thị Unicode (emoji)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Thêm thư mục src vào đường dẫn hệ thống để import được các module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_data
from eclat_algo import Eclat
from utils import generate_recommendation_rules, print_recommendations


def main():
    """Hàm chính điều phối toàn bộ quy trình phân tích clickstream"""
    
    print("=" * 70)
    print("   🎯 HỆ THỐNG GỢI Ý NỘI DUNG DỰA TRÊN THUẬT TOÁN ECLAT")
    print("   📊 Phân tích hành vi người dùng qua dữ liệu Clickstream")
    print("=" * 70)
    
    # ============================================================
    # BƯỚC 1: TẢI DỮ LIỆU
    # ============================================================
    print("\n📂 BƯỚC 1: ĐỌC DỮ LIỆU CLICKSTREAM")
    
    # Giới hạn số phiên để demo (có thể bỏ limit để chạy toàn bộ)
    # Lưu ý: File msnbc.seq có khoảng 989,818 phiên
    DATA_LIMIT = None       # Đọc tất cả ~989,818 phiên để có kết quả khách quan nhất
    TOP_RULES = 15          # Số luật gợi ý hiển thị
    
    transactions = load_data(limit=DATA_LIMIT)
    
    if not transactions:
        print("❌ Không có dữ liệu để chạy. Vui lòng kiểm tra file dữ liệu.")
        return
    
    total_transactions = len(transactions)

    # ============================================================
    # BƯỚC 2: CẤU HÌNH THUẬT TOÁN
    # ============================================================
    # min_support = 0.02: Cặp chuyên mục phải xuất hiện trong ít nhất 2% số phiên
    # min_confidence = 0.4: 40% người xem A sẽ xem B thì mới gợi ý
    MIN_SUPPORT = 0.02
    MIN_CONFIDENCE = 0.4    # 40% người xem A sẽ xem B thì mới gợi ý
    
    print(f"\n⚙️ CẤU HÌNH THUẬT TOÁN:")
    print(f"   • Min Support  = {MIN_SUPPORT*100}% (xuất hiện trong {int(total_transactions * MIN_SUPPORT):,} phiên)")
    print(f"   • Min Confidence = {MIN_CONFIDENCE*100}% (tỷ lệ tối thiểu để gợi ý)")
    
    # ============================================================
    # BƯỚC 3: CHẠY THUẬT TOÁN ECLAT
    # ============================================================
    print(f"\n🔍 BƯỚC 2: CHẠY THUẬT TOÁN ECLAT (Vertical Data Format)")
    
    # min_items=1: Bao gồm cả tập 1 phần tử (cần để tính Lift)
    eclat_model = Eclat(min_support=MIN_SUPPORT, min_items=1)
    frequent_itemsets = eclat_model.fit(transactions)
    
    if not frequent_itemsets:
        print("⚠️ Không tìm thấy tập mục phổ biến nào.")
        print("👉 Hãy thử giảm Min Support xuống (ví dụ: 0.01)")
        return
    
    # Thống kê kết quả
    single_items = sum(1 for item, _ in frequent_itemsets if len(item) == 1)
    pair_items = sum(1 for item, _ in frequent_itemsets if len(item) == 2)
    print(f"   • Tìm thấy {single_items} chuyên mục phổ biến (đơn lẻ)")
    print(f"   • Tìm thấy {pair_items} cặp chuyên mục phổ biến")

    # ============================================================
    # BƯỚC 4: SINH LUẬT GỢI Ý
    # ============================================================
    print(f"\n📋 BƯỚC 3: SINH LUẬT GỢI Ý NỘI DUNG")
    
    rules = generate_recommendation_rules(
        frequent_itemsets, 
        total_transactions=total_transactions,
        min_confidence=MIN_CONFIDENCE
    )
    
    # ============================================================
    # BƯỚC 5: HIỂN THỊ KẾT QUẢ
    # ============================================================
    if rules:
        print_recommendations(rules, top_n=TOP_RULES)
    else:
        print("⚠️ Không tìm thấy luật nào đủ độ tin cậy.")
        print("👉 Hãy thử giảm Min Confidence xuống (ví dụ: 0.3)")


if __name__ == "__main__":
    main()