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

    print(f"Sinh luật từ {len(frequent_itemsets)} tập phổ biến...")

    import itertools

    # 2. Duyệt qua các tập phổ biến có từ 2 items trở lên
    for itemset, support_count_AB in frequent_itemsets:
        if len(itemset) < 2:
            continue
        
        # Support(X ∪ Y) = Support của cả itemset
        support_AB = support_count_AB / total_transactions
        
        # Sinh tất cả các tập con khác rỗng của itemset làm vế trái (X)
        # VD: itemset {A, B, C} -> X có thể là {A}, {B}, {C}, {A,B}, {A,C}, {B,C}
        all_antecedents = []
        for r in range(1, len(itemset)):
            all_antecedents.extend(itertools.combinations(itemset, r))
            
        for antecedent_tuple in all_antecedents:
            antecedent = list(antecedent_tuple)
            antecedent_key = tuple(sorted(antecedent))
            
            # Vế phải (Y) = Itemset - X
            consequent = [item for item in itemset if item not in antecedent]
            consequent_key = tuple(sorted(consequent))
            
            # Lấy Support Count của vế trái (X)
            support_count_A = support_lookup.get(antecedent_key)
            
            if support_count_A is None:
                continue
            
            # Tính các chỉ số
            support_A = support_count_A / total_transactions
            
            # Confidence(X -> Y) = Support(XY) / Support(X)
            confidence = support_AB / support_A if support_A > 0 else 0
            
            # Lift = Confidence / Support(Y)
            # Cần support_B để tính Lift
            support_count_B = support_lookup.get(consequent_key)
            if support_count_B:
                support_B = support_count_B / total_transactions
                lift = confidence / support_B if support_B > 0 else 0
            else:
                lift = 0 # Không tính được nếu không có thông tin vế phải
            
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
    
    print(f"Đã sinh {len(rules)} luật thỏa mãn Confidence >= {min_confidence*100:.0f}%")
    
    return rules


def print_recommendations(rules, top_n=10):
    """
    In danh sách gợi ý nội dung ra màn hình với định dạng bảng.
    """
    if not rules:
        print("\nKhông có luật gợi ý nào.")
        return
    
    actual_count = min(top_n, len(rules))
    
    print(f"\n{'='*60}")
    print(f"   TOP {actual_count} LUẬT GỢI Ý NỘI DUNG")
    print(f"{'='*60}")
    
    # Tính toán độ rộng cột động dựa trên dữ liệu
    # Mặc định tối thiểu là độ dài của Header (NẾU XEM = 7, GỢI Ý = 5)
    max_len_ant = 7
    max_len_cons = 5
    
    # Chỉ xét trong top_n luật sẽ in để tối ưu
    rules_to_print = rules[:top_n]
    
    for rule in rules_to_print:
        ant_len = len(", ".join(rule['antecedent']))
        cons_len = len(", ".join(rule['consequent']))
        if ant_len > max_len_ant: max_len_ant = ant_len
        if cons_len > max_len_cons: max_len_cons = cons_len
        
    # Thêm padding cho thoáng
    w_ant = max_len_ant + 2
    w_cons = max_len_cons + 2
    
    # Header bảng
    # Sử dụng biến độ rộng động trong f-string
    print(f"\n{'STT':<4} | {f'NẾU XEM':<{w_ant}} | {f'GỢI Ý':<{w_cons}} | {'SUP':<7} | {'CONF':<7} | {'LIFT':<5}")
    print("-" * (4 + 3 + w_ant + 3 + w_cons + 3 + 7 + 3 + 7 + 3 + 5))
    
    for i, rule in enumerate(rules_to_print, 1):
        antecedent_str = ", ".join(rule['antecedent'])
        consequent_str = ", ".join(rule['consequent'])
        support_pct = f"{rule['support']*100:.2f}%"
        conf_pct = f"{rule['confidence']*100:.1f}%"
        lift_val = f"{rule['lift']:.2f}"
        
        print(f"{i:<4} | {antecedent_str:<{w_ant}} | {consequent_str:<{w_cons}} | {support_pct:<7} | {conf_pct:<7} | {lift_val:<5}")
    
    print("-" * (4 + 3 + w_ant + 3 + w_cons + 3 + 7 + 3 + 7 + 3 + 5))
    
    # Luật tốt nhất
    if rules:
        top = rules[0]
        # Tổng quát hóa: Nối chuỗi tất cả các items, không chỉ lấy item đầu tiên
        ant = ", ".join(top['antecedent'])
        cons = ", ".join(top['consequent'])
        
        print(f"\nGợi ý tốt nhất: Người xem [{ant}] -> gợi ý [{cons}]")
        print(f"Lift = {top['lift']:.2f} (cao hơn ngẫu nhiên {(top['lift']-1)*100:.0f}%)\n")



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