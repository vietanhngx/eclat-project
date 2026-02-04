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
    
    print("=" * 60)
    print("   HỆ THỐNG GỢI Ý NỘI DUNG - THUẬT TOÁN ECLAT")
    print("=" * 60)
    
    print("\n[1] ĐỌc dữ liệu clickstream")
    
    # Giới hạn số phiên để demo (có thể bỏ limit để chạy toàn bộ)
    # Lưu ý: File msnbc.seq có khoảng 989,818 phiên
    DATA_LIMIT = None       # Đọc tất cả ~989,818 phiên để có kết quả khách quan nhất
    TOP_RULES = 15          # Số luật gợi ý hiển thị
    
    transactions = load_data(limit=DATA_LIMIT)
    
    if not transactions:
        print("Không có dữ liệu. Vui lòng kiểm tra file.")
        return
    
    total_transactions = len(transactions)

    # ============================================================
    # BƯỚC 2: CẤU HÌNH THUẬT TOÁN
    # ============================================================
    # min_support = 0.02: Cặp chuyên mục phải xuất hiện trong ít nhất 2% số phiên
    # min_confidence = 0.4: 40% người xem A sẽ xem B thì mới gợi ý
    MIN_SUPPORT = 0.02
    MIN_CONFIDENCE = 0.4    # 40% người xem A sẽ xem B thì mới gợi ý
    
    print(f"\n[2] Cấu hình: Min Support = {MIN_SUPPORT*100}%, Min Confidence = {MIN_CONFIDENCE*100}%")
    
    print("\n[3] Chạy thuật toán Eclat")
    
    # min_items=1: Bao gồm cả tập 1 phần tử (cần để tính Lift)
    eclat_model = Eclat(min_support=MIN_SUPPORT, min_items=1)
    frequent_itemsets = eclat_model.fit(transactions)
    
    if not frequent_itemsets:
        print("Không tìm thấy tập phổ biến nào.")
        return
    
    single_items = sum(1 for item, _ in frequent_itemsets if len(item) == 1)
    pair_items = sum(1 for item, _ in frequent_itemsets if len(item) == 2)
    print(f"Kết quả: {single_items} chuyên mục, {pair_items} cặp phổ biến")

    print("\n[4] Sinh luật gợi ý nội dung")
    
    rules = generate_recommendation_rules(
        frequent_itemsets, 
        total_transactions=total_transactions,
        min_confidence=MIN_CONFIDENCE
    )
    
    if rules:
        print_recommendations(rules, top_n=TOP_RULES)
    else:
        print("Không tìm thấy luật nào đủ độ tin cậy.")


if __name__ == "__main__":
    main()