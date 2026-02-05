"""
Module eclat.py - Cài đặt thuật toán Eclat chuẩn.

Thuật toán: ECLAT (Equivalence Class Transformation)
Tác giả gốc: Mohammed J. Zaki (2000)

Đặc điểm chính:
1. Sử dụng Vertical Data Format (Định dạng dữ liệu dọc):
   - Thay vì lưu giao dịch (TID -> Items), ta lưu item (Item -> TIDs).
2. Sử dụng phép giao (Intersection) để tính Support:
   - TID(A u B) = TID(A) n TID(B).
   - Nhanh hơn việc quét lại toàn bộ CSDL như Apriori.
3. Duyệt cây theo chiều sâu (DFS):
   - Tiết kiệm bộ nhớ và phù hợp để tìm itemsets dài.
"""

class Eclat:
    """
    Lớp triển khai thuật toán Eclat (Equivalence Class Transformation).
    Tìm kiếm các tập mục phổ biến (Frequent Itemsets) bằng cách duyệt cây DFS trên dữ liệu dọc.
    """
    
    def __init__(self, min_support=0.02, min_items=1):
        self.min_support = min_support
        self.min_items = min_items
        self.frequent_itemsets = []
        self._total_wb = 0

    def fit(self, dataset):
        """
        Chạy thuật toán trên bộ dữ liệu (list of sets).
        """
        self.frequent_itemsets = []
        self._total_wb = len(dataset)
        
        # 1. Tính ngưỡng support tuyệt đối (số lượng)
        min_sup = self._total_wb * self.min_support
        print(f"Tổng phiên: {self._total_wb:,} | Min Support: {min_sup:.0f} ({self.min_support:.0%})")

        # 2. Chuyển đổi sang Vertical Data Format (TID-Sets)
        # tid_dict: {item: {tid1, tid2, ...}}
        tid_dict = {}
        for tid, transaction in enumerate(dataset):
            for item in transaction:
                if item not in tid_dict:
                    tid_dict[item] = set()
                tid_dict[item].add(tid)
        
        # 3. Lọc 1-itemsets (Pruning sớm)
        # Sắp xếp item theo tần suất giảm dần để tối ưu duyệt cây
        sorted_items = []
        for item, tids in tid_dict.items():
            if len(tids) >= min_sup:
                sorted_items.append((item, tids))
        
        sorted_items.sort(key=lambda x: len(x[1]), reverse=True)
        
        print(f"Số 1-itemsets phổ biến: {len(sorted_items)}")
        
        # 4. Bắt đầu đệ quy DFS
        self._eclat_recursive(
            prefix=[], 
            items=sorted_items, 
            min_sup=min_sup
        )
        
        return self.frequent_itemsets

    def _eclat_recursive(self, prefix, items, min_sup):
        """
        Hàm đệ quy cốt lõi (DFS).
        
        Args:
            prefix: Itemset hiện tại (VD: ['A', 'B'])
            items: Danh sách các (item, tids) có thể kết hợp tiếp
            min_sup: Ngưỡng support (số lượng)
        """
        while items:
            # Lấy item đầu tiên, đảm bảo không xét lại (Pop)
            item, tids = items.pop(0)
            
            # Tạo itemset mới
            new_itemset = prefix + [item]
            support = len(tids)
            
            # Lưu kết quả
            if len(new_itemset) >= self.min_items:
                self.frequent_itemsets.append((new_itemset, support))
            
            # Tạo danh sách ứng viên cho bước sau (Intersection)
            next_items = []
            for other_item, other_tids in items:
                # Phép giao TIDs
                new_tids = tids & other_tids
                
                # Pruning: Chỉ giữ lại nếu đủ support
                if len(new_tids) >= min_sup:
                    next_items.append((other_item, new_tids))
            
            # Gọi đệ quy nếu còn ứng viên
            if next_items:
                self._eclat_recursive(new_itemset, next_items, min_sup)

# ============================================================
# KHỐI TEST ĐỘC LẬP (Unit Test)
# Chạy trực tiếp file này để kiểm tra logic với dữ liệu mẫu
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DEMO THUẬT TOÁN ECLAT (Dữ liệu khớp với Báo cáo/Slide)")
    print("=" * 60)

    # 1. Dữ liệu mẫu (Khớp 100% với ví dụ minh họa trong báo cáo)
    # T1: A, B, C
    # T2: B, C, D
    # T3: A, C, D
    # T4: A, B, D
    dataset = [
        {'A', 'B', 'C'},
        {'B', 'C', 'D'},
        {'A', 'C', 'D'},
        {'A', 'B', 'D'}
    ]
    
    print("Input Dataset:")
    for i, trans in enumerate(dataset, 1):
        # Sort để in ra đẹp
        items_sorted = sorted(list(trans))
        print(f"  T{i}: {items_sorted}")
    
    # 2. Cấu hình (Khớp slide: Min Support = 50% = 2 giao dịch)
    MIN_SUP_PCT = 0.5
    print(f"\nCấu hình: Min Support = {MIN_SUP_PCT*100}%")

    # 3. Chạy thuật toán
    # Min items = 1 để xem được cả A, B, C...
    model = Eclat(min_support=MIN_SUP_PCT, min_items=1)
    results = model.fit(dataset)
    
    # 4. In kết quả
    print("\n------------------------------------------------------------")
    print("KẾT QUẢ TÌM ĐƯỢC (So sánh với bảng trong Slide)")
    print("------------------------------------------------------------")
    print(f"{'Itemset':<15} | {'Count':<5} | {'Support':<8}")
    print("-" * 40)
    
    # Sắp xếp kết quả: Itemsets ngắn trước, dài sau. Cùng độ dài thì theo count
    results.sort(key=lambda x: (len(x[0]), x[0]))
    
    count_1 = 0
    count_2 = 0
    
    for itemset, count in results:
        # Format itemset đẹp: ['A', 'B'] -> {A, B}
        item_str = "{" + ", ".join(sorted(itemset)) + "}"
        support_pct = (count / len(dataset)) * 100
        print(f"{item_str:<15} | {count:<5} | {support_pct:.0f}%")
        
        if len(itemset) == 1: count_1 += 1
        if len(itemset) == 2: count_2 += 1
        
    print("-" * 40)
    print(f"Tổng số tập phổ biến: {len(results)}")
    print(f"\nKiểm tra:\n- 1-itemsets: {count_1} (Slide: 4)\n- 2-itemsets: {count_2} (Slide: 6)")