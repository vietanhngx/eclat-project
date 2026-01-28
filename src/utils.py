"""
Module utils.py - Sinh luật kết hợp và hiển thị gợi ý nội dung

Các chỉ số được tính theo chuẩn lý thuyết Association Rule Mining:

1. Support(A → B) = P(A ∩ B) = |T(A ∩ B)| / |T|
   - Tần suất xuất hiện đồng thời của A và B trong toàn bộ giao dịch
   
2. Confidence(A → B) = P(B|A) = Support(A ∪ B) / Support(A)
   - Xác suất có điều kiện: Nếu người dùng xem A, khả năng xem B là bao nhiêu?
   
3. Lift(A → B) = Support(A ∪ B) / (Support(A) × Support(B))
   - Độ tương quan: Lift > 1 nghĩa là A và B có tương quan tích cực
   - Lift = 1: A và B độc lập thống kê
   - Lift < 1: A và B có tương quan âm (hiếm khi xuất hiện cùng nhau)

Tài liệu tham khảo:
- Agrawal, R., Imielinski, T., & Swami, A. (1993). 
  "Mining association rules between sets of items in large databases"
  ACM SIGMOD Conference
"""


def generate_recommendation_rules(frequent_itemsets, total_transactions, min_confidence=0.5):
    """
    Sinh ra các luật gợi ý nội dung từ tập mục phổ biến.
    
    Với mỗi tập {A, B}, sinh 2 luật:
    - A → B: Nếu người dùng xem A, gợi ý B
    - B → A: Nếu người dùng xem B, gợi ý A
    
    Args:
        frequent_itemsets (list): Kết quả từ thuật toán Eclat.
            Dạng: [(['News', 'Tech'], 500), (['News'], 1000), ...]
            
        total_transactions (int): Tổng số phiên giao dịch (N).
            Cần thiết để tính Support dạng phần trăm.
            
        min_confidence (float): Ngưỡng tin cậy tối thiểu [0.0, 1.0]
            - 0.4 = 40%: Ít nhất 40% người xem A sẽ xem B
            - 0.5 = 50%: Ít nhất 50% người xem A sẽ xem B
    
    Returns:
        rules (list of dict): Danh sách các luật gợi ý, mỗi luật gồm:
            - antecedent: Vế trái (điều kiện) - list
            - consequent: Vế phải (kết luận) - list
            - support: Support(A ∪ B) - float [0, 1]
            - confidence: P(B|A) - float [0, 1]
            - lift: Độ tương quan - float (> 1 là tốt)
    
    Example:
        >>> rules = generate_recommendation_rules(itemsets, 50000, 0.4)
        >>> for r in rules[:3]:
        ...     print(f"{r['antecedent']} → {r['consequent']}: Lift={r['lift']:.2f}")
    """
    rules = []
    
    # 1. Chuyển list thành dictionary để tra cứu nhanh Support Count
    # Key: tuple đã sort để đảm bảo ('News', 'Tech') == ('Tech', 'News')
    support_lookup = {}
    for itemset, support_count in frequent_itemsets:
        key = tuple(sorted(itemset))
        support_lookup[key] = support_count

    print(f"🔄 Đang sinh luật từ {len(frequent_itemsets)} tập phổ biến...")

    # 2. Duyệt qua các tập phổ biến có từ 2 items trở lên
    for itemset, support_count_AB in frequent_itemsets:
        if len(itemset) < 2:
            continue  # Bỏ qua tập đơn lẻ (không tạo được luật A → B)
        
        # Support(A ∪ B) = |T(A ∩ B)| / N
        support_AB = support_count_AB / total_transactions
            
        # Với tập {A, B}, tạo các luật:
        # - A → B: Confidence = Support(A,B) / Support(A)
        # - B → A: Confidence = Support(A,B) / Support(B)
        
        for antecedent_item in itemset:
            # Vế trái (Antecedent): Item được chọn làm điều kiện
            antecedent = [antecedent_item]
            antecedent_key = tuple(antecedent)
            
            # Vế phải (Consequent): Các items còn lại
            consequent = [item for item in itemset if item != antecedent_item]
            consequent_key = tuple(sorted(consequent))
            
            # Lấy Support Count của vế trái (A) và vế phải (B)
            support_count_A = support_lookup.get(antecedent_key)
            support_count_B = support_lookup.get(consequent_key)
            
            # Kiểm tra: Cần có support của cả A và B để tính Lift
            if support_count_A is None or support_count_B is None:
                continue
            
            # Tính Support của A và B riêng lẻ
            support_A = support_count_A / total_transactions
            support_B = support_count_B / total_transactions
            
            # ============================================================
            # CÔNG THỨC CHÍNH
            # ============================================================
            
            # Confidence(A → B) = P(B|A) = Support(A ∪ B) / Support(A)
            confidence = support_AB / support_A if support_A > 0 else 0
            
            # Lift(A → B) = Support(A ∪ B) / (Support(A) × Support(B))
            # Công thức tương đương: Lift = Confidence / Support(B)
            # Interpretation:
            #   - Lift > 1: A và B xuất hiện cùng nhau nhiều hơn ngẫu nhiên (Tích cực)
            #   - Lift = 1: A và B độc lập thống kê
            #   - Lift < 1: A và B ít xuất hiện cùng nhau (Tiêu cực)
            expected_support = support_A * support_B
            lift = support_AB / expected_support if expected_support > 0 else 0
            
            # Chỉ lưu luật nếu đạt ngưỡng Confidence
            if confidence >= min_confidence:
                rules.append({
                    'antecedent': antecedent,
                    'consequent': consequent,
                    'support': support_AB,
                    'confidence': confidence,
                    'lift': lift
                })

    # Sắp xếp: Ưu tiên Lift cao (tương quan mạnh), sau đó là Confidence
    rules.sort(key=lambda x: (x['lift'], x['confidence']), reverse=True)
    
    print(f"✅ Đã sinh {len(rules)} luật thỏa mãn Confidence >= {min_confidence*100:.0f}%")
    
    return rules


def print_recommendations(rules, top_n=10):
    """
    In danh sách gợi ý nội dung ra màn hình với định dạng bảng.
    
    Hiển thị theo ngữ cảnh đề tài clickstream:
    "Người xem [Tech] thường xem tiếp [News]"
    
    Args:
        rules (list): Danh sách luật từ generate_recommendation_rules()
        top_n (int): Số lượng luật hiển thị (mặc định 10)
    """
    if not rules:
        print("\n⚠️ Không có luật gợi ý nào để hiển thị.")
        return
    
    actual_count = min(top_n, len(rules))
    
    print(f"\n{'='*75}")
    print(f"   💡 TOP {actual_count} LUẬT GỢI Ý NỘI DUNG MẠNH NHẤT")
    print(f"{'='*75}")
    
    # Header bảng
    print(f"\n{'STT':<4} | {'NẾU XEM':<15} | {'GỢI Ý':<15} | {'SUPPORT':<8} | {'CONF':<7} | {'LIFT':<6}")
    print("-" * 75)
    
    for i, rule in enumerate(rules[:top_n], 1):
        antecedent_str = ", ".join(rule['antecedent'])
        consequent_str = ", ".join(rule['consequent'])
        support_pct = f"{rule['support']*100:.2f}%"
        conf_pct = f"{rule['confidence']*100:.1f}%"
        lift_val = f"{rule['lift']:.2f}"
        
        print(f"{i:<4} | {antecedent_str:<15} | {consequent_str:<15} | {support_pct:<8} | {conf_pct:<7} | {lift_val:<6}")
    
    print("-" * 75)
    
    # Giải thích cách đọc kết quả
    print(f"\n📌 CÁCH ĐỌC KẾT QUẢ:")
    print(f"   • Support: Tỷ lệ phiên xuất hiện cả 2 chuyên mục cùng nhau")
    print(f"   • Confidence: Xác suất có điều kiện P(B|A)")
    print(f"   • Lift: Độ tương quan (> 1 = tích cực, = 1 = độc lập, < 1 = tiêu cực)")
    
    # Ví dụ minh họa từ luật tốt nhất
    if rules:
        top = rules[0]
        ant = top['antecedent'][0]
        cons = top['consequent'][0] if len(top['consequent']) == 1 else ", ".join(top['consequent'])
        
        print(f"\n🎯 GỢI Ý TỐT NHẤT: \"Người xem [{ant}] thường xem tiếp [{cons}]\"")
        print(f"   → Confidence: {top['confidence']*100:.1f}% người xem {ant} cũng xem {cons}")
        print(f"   → Lift = {top['lift']:.2f}: Xác suất cao hơn ngẫu nhiên {(top['lift']-1)*100:.0f}%\n")


def export_rules_to_csv(rules, filepath):
    """
    Xuất danh sách luật ra file CSV để phân tích thêm.
    
    Args:
        rules (list): Danh sách luật từ generate_recommendation_rules()
        filepath (str): Đường dẫn file CSV đầu ra
    """
    import csv
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Antecedent', 'Consequent', 'Support', 'Confidence', 'Lift'])
        
        for rule in rules:
            writer.writerow([
                ', '.join(rule['antecedent']),
                ', '.join(rule['consequent']),
                f"{rule['support']:.4f}",
                f"{rule['confidence']:.4f}",
                f"{rule['lift']:.4f}"
            ])
    
    print(f"✅ Đã xuất {len(rules)} luật ra file: {filepath}")


# ============================================================
# KHỐI TEST (Chạy thử file này độc lập)
# ============================================================
if __name__ == "__main__":
    # Dữ liệu mẫu để test công thức
    # Giả sử: 1000 giao dịch tổng cộng
    test_data = [
        (['News'], 500),          # Support(News) = 50%
        (['Tech'], 300),          # Support(Tech) = 30%
        (['Sports'], 200),        # Support(Sports) = 20%
        (['News', 'Tech'], 150),  # Support(News, Tech) = 15%
        (['News', 'Sports'], 80), # Support(News, Sports) = 8%
    ]
    
    print("=" * 60)
    print("TEST MODULE UTILS - Tính toán Association Rules")
    print("=" * 60)
    
    rules = generate_recommendation_rules(
        test_data, 
        total_transactions=1000, 
        min_confidence=0.2
    )
    
    print_recommendations(rules, top_n=10)
    
    # Kiểm tra công thức thủ công
    print("\n📐 KIỂM TRA CÔNG THỨC THỦ CÔNG:")
    print("-" * 60)
    print("Luật: News → Tech")
    print(f"   Support(News, Tech) = 150/1000 = 15%")
    print(f"   Confidence = 15% / 50% = 30%")
    print(f"   Lift = 15% / (50% × 30%) = 15% / 15% = 1.0")