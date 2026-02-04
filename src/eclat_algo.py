"""
Module eclat_algo.py - Thuật toán Eclat cho Khai phá Itemsets Phổ biến

Thuật toán: ECLAT (Equivalence Class Clustering and bottom-up Lattice Traversal)
Tác giả gốc: Mohammed J. Zaki (1997)

Tài liệu tham khảo:
- Zaki, M.J. (2000). "Scalable Algorithms for Association Mining"
  IEEE Transactions on Knowledge and Data Engineering, 12(3), 372-390.

Đặc điểm chính:
1. Sử dụng Vertical Data Format (Định dạng dữ liệu dọc)
   - Mỗi item được lưu kèm danh sách TID (Transaction IDs) chứa item đó
   - VD: Item "News" -> TID-Set = {0, 2, 5, 8, 12, ...}

2. Sử dụng phép giao TID-Sets để tính Support
   - Support(A ∪ B) = |TID(A) ∩ TID(B)| / N
   - Nhanh hơn Apriori do không cần quét lại database nhiều lần

3. Duyệt theo Depth-First Search (DFS)
   - Tiết kiệm bộ nhớ hơn Breadth-First Search (BFS)
   - Phù hợp cho mining tập phổ biến có nhiều items
"""


class Eclat:
    """
    Lớp triển khai thuật toán Eclat để tìm tập mục phổ biến (Frequent Itemsets).
    
    Thuật toán hoạt động theo 4 bước chính:
    1. Chuyển đổi dữ liệu ngang -> dọc (TID-Set format)
    2. Lọc các item đơn lẻ không đạt ngưỡng support
    3. Đệ quy kết hợp các item và tính giao TID-Sets
    4. Lưu các itemsets có support >= min_support
    
    Attributes:
        min_support (float): Ngưỡng support tối thiểu (0.0-1.0)
        min_items (int): Số items tối thiểu trong 1 itemset (thường là 1 hoặc 2)
        frequent_itemsets (list): Kết quả - danh sách (itemset, support_count)
    
    Example:
        >>> eclat = Eclat(min_support=0.02, min_items=2)
        >>> itemsets = eclat.fit(transactions)
        >>> for items, count in itemsets[:5]:
        ...     print(f"{items}: {count}")
    """
    
    def __init__(self, min_support=0.01, min_items=1):
        """
        Khởi tạo thuật toán Eclat.
        
        Args:
            min_support (float): Ngưỡng hỗ trợ tối thiểu, phạm vi [0.0, 1.0]
                - 0.01 = 1%: Item phải xuất hiện trong ít nhất 1% số giao dịch
                - 0.02 = 2%: Item phải xuất hiện trong ít nhất 2% số giao dịch
                
            min_items (int): Số lượng item tối thiểu trong một itemset
                - 1: Bao gồm cả đơn lẻ (cần thiết để tính Lift)
                - 2: Chỉ lấy các cặp item trở lên (dùng cho sinh luật)
        
        Raises:
            ValueError: Nếu min_support không nằm trong [0, 1]
        """
        if not 0 <= min_support <= 1:
            raise ValueError("min_support phải nằm trong khoảng [0, 1]")
        
        self.min_support = min_support
        self.min_items = min_items
        self.frequent_itemsets = []  # Nơi lưu kết quả cuối cùng
        self._total_transactions = 0  # Lưu để tính support %

    def fit(self, dataset):
        """
        Chạy thuật toán Eclat trên bộ dữ liệu.
        
        Quy trình:
        1. Tính min_support_count = total_transactions × min_support
        2. Chuyển đổi sang Vertical Data Format (TID-Sets)
        3. Lọc các item không đạt ngưỡng
        4. Đệ quy tìm các itemsets phổ biến
        
        Args:
            dataset (list of sets): Dữ liệu đầu vào từ data_loader.
                Mỗi phần tử là 1 set các items (tên chuyên mục).
                VD: [{'News', 'Tech'}, {'Frontpage', 'News'}, ...]
        
        Returns:
            list: Danh sách các itemsets phổ biến dạng (itemset, support_count)
                VD: [(['News', 'Tech'], 150), (['News'], 500), ...]
        
        Time Complexity: O(n × m × k) với n=số giao dịch, m=số items, k=độ sâu
        Space Complexity: O(n × m) cho TID-Sets
        """
        # Reset kết quả từ lần chạy trước (nếu có)
        self.frequent_itemsets = []
        
        # 1. Tính ngưỡng support tuyệt đối (số lượng giao dịch)
        self._total_transactions = len(dataset)
        min_support_count = self._total_transactions * self.min_support
        
        print(f"Tổng số phiên: {self._total_transactions:,}")
        print(f"Ngưỡng hỗ trợ: {min_support_count:.0f} ({self.min_support*100}%)")

        # 2. CHUYỂN ĐỔI DỮ LIỆU NGANG -> DỌC (Vertical Data Format)
        # Dạng: { 'Item_A': {tid0, tid1, tid5}, 'Item_B': {tid2, tid3}, ... }
        # tid = Transaction ID (index của giao dịch trong dataset)
        tid_dict = {}
        
        for tid, transaction in enumerate(dataset):
            for item in transaction:
                if item not in tid_dict:
                    tid_dict[item] = set()
                tid_dict[item].add(tid)
        
        # 3. LỌC SỚM: Loại bỏ các item đơn lẻ không đủ support (Pruning)
        # Theo nguyên lý Apriori: Nếu item đơn lẻ không phổ biến,
        # thì mọi tập chứa item đó cũng không phổ biến
        tid_dict = {
            item: tids 
            for item, tids in tid_dict.items() 
            if len(tids) >= min_support_count
        }
        
        print(f"Số items phổ biến: {len(tid_dict)}")
        
        # 4. Sắp xếp theo độ phổ biến giảm dần (Tối ưu: Pruning hiệu quả hơn)
        # Items phổ biến nhất xét trước giúp cắt tỉa nhánh nhanh hơn
        sorted_items = sorted(
            tid_dict.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )
        
        # 5. BẮT ĐẦU ĐỆ QUY (Depth-First Search)
        print(f"Đang chạy thuật toán Eclat...")
        
        self._eclat_recursive(
            prefix=[], 
            tid_subset=sorted_items, 
            min_support_count=min_support_count
        )
        
        print(f"Tìm thấy {len(self.frequent_itemsets)} tập mục phổ biến.")
        return self.frequent_itemsets

    def _eclat_recursive(self, prefix, tid_subset, min_support_count):
        """
        Hàm đệ quy cốt lõi của thuật toán Eclat (Depth-First Search).
        
        Thuật toán:
        - Với mỗi item trong tid_subset, tạo itemset mới = prefix + [item]
        - Tính support = |TID-Set của itemset mới|
        - Nếu đủ support: Lưu vào kết quả và tiếp tục mở rộng
        - Dừng khi không còn item nào có thể kết hợp
        
        Args:
            prefix (list): Itemset hiện tại đang xét
                VD: [] -> ['News'] -> ['News', 'Tech']
                
            tid_subset (list): Danh sách các (item, TID-Set) còn lại để xét
                Được sắp xếp theo độ phổ biến giảm dần
                
            min_support_count (float): Ngưỡng support tuyệt đối để cắt tỉa
        """
        while tid_subset:
            # Lấy item đầu tiên ra khỏi danh sách xét
            item, tids = tid_subset.pop(0)
            
            # Tạo itemset mới bằng cách thêm item vào prefix
            # VD: prefix=['News'], item='Tech' -> new_itemset=['News', 'Tech']
            new_itemset = prefix + [item]
            
            # Support = Số giao dịch chứa itemset này
            support_count = len(tids)
            
            # Lưu itemset nếu có đủ số items theo yêu cầu
            # (min_items=1: lấy cả đơn lẻ, min_items=2: chỉ lấy cặp trở lên)
            if len(new_itemset) >= self.min_items:
                self.frequent_itemsets.append((new_itemset, support_count))
            
            # --- BƯỚC THEN CHỐT: TÍNH GIAO TID-SETS ---
            # Tìm các item có thể kết hợp tiếp với new_itemset
            new_tid_subset = []
            
            for other_item, other_tids in tid_subset:
                # Phép giao: Chỉ giữ lại TID xuất hiện ở CẢ HAI items
                # Support(A ∪ B) = |TID(A) ∩ TID(B)|
                intersect_tids = tids & other_tids  # Phép toán set intersection
                
                # Chỉ giữ lại nếu tập giao vẫn đủ lớn (Pruning)
                if len(intersect_tids) >= min_support_count:
                    new_tid_subset.append((other_item, intersect_tids))
            
            # Đệ quy để đi sâu hơn (Depth-First)
            if new_tid_subset:
                self._eclat_recursive(
                    new_itemset, 
                    new_tid_subset, 
                    min_support_count
                )

    def get_support(self, itemset):
        """
        Tính support của một itemset cụ thể.
        
        Args:
            itemset (list): Itemset cần tính support
            
        Returns:
            float: Support dạng tỷ lệ (0.0 - 1.0), hoặc None nếu không tìm thấy
        """
        for items, count in self.frequent_itemsets:
            if sorted(items) == sorted(itemset):
                return count / self._total_transactions if self._total_transactions > 0 else 0
        return None


# ============================================================
# KHỐI TEST (Chạy thử file này độc lập)
# ============================================================
if __name__ == "__main__":
    # Dữ liệu giả lập để test logic thuật toán
    # Các giao dịch mẫu với 5 items: A, B, C, D, E
    dummy_data = [
        {'A', 'C', 'D'},
        {'B', 'C', 'E'},
        {'A', 'B', 'C', 'E'},
        {'B', 'E'},
        {'A', 'B', 'C', 'E'},
    ]
    
    print("=" * 50)
    print("TEST THUẬT TOÁN ECLAT VỚI DỮ LIỆU GIẢ LẬP")
    print("=" * 50)
    
    # Min support 40% (xuất hiện trong ít nhất 2/5 giao dịch)
    model = Eclat(min_support=0.4, min_items=1)
    results = model.fit(dummy_data)
    
    print("\n📊 Kết quả (Itemset : Support Count : Support %):")
    print("-" * 50)
    for itemset, count in sorted(results, key=lambda x: len(x[0])):
        support_pct = count / len(dummy_data) * 100
        print(f"  {itemset} : {count} : {support_pct:.1f}%")
    
    print("\n✅ Test hoàn tất!")