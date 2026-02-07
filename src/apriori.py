"""
Module apriori.py - Cài đặt thuật toán Apriori chuẩn để so sánh.

Thuật toán: Apriori
Đặc điểm:
1. Sử dụng Horizontal Data Format.
2. Nguyên lý Apriori: Nếu một tập mục phổ biến thì mọi tập con của nó cũng phải phổ biến.
3. Quy trình lặp (Breadth-First Search):
   - Quét CSDL nhiều lần (mỗi lần cho 1 kích thước k).
   - Tốn kém chi phí I/O (hoặc duyệt mảng lớn) hơn Eclat (chỉ quét 1 lần để dựng TID-list).
"""
from collections import defaultdict
from itertools import combinations
import time

class Apriori:
    def __init__(self, min_support=0.02, min_items=1):
        self.min_support = min_support
        self.min_items = min_items
        self.frequent_itemsets = []
        self._total_trans = 0
        
    def fit(self, dataset):
        """
        Chạy thuật toán Apriori trên bộ dữ liệu.
        Dataset là list of sets.
        """
        self.frequent_itemsets = []
        self._total_trans = len(dataset)
        min_sup_count = self._total_trans * self.min_support
        
        # 1. Tìm L1 (Frequent 1-itemsets)
        # Quét CSDL lần 1
        item_counts = defaultdict(int)
        for trans in dataset:
            for item in trans:
                item_counts[frozenset([item])] += 1
        
        L_current = []
        for itemset, count in item_counts.items():
            if count >= min_sup_count:
                L_current.append(itemset)
                if len(itemset) >= self.min_items:
                    self.frequent_itemsets.append((list(itemset), count))
        
        # Sort để chuẩn bị cho bước sinh ứng viên
        # Convert frozenset -> sorted tuple để dễ so sánh prefix
        L_current = sorted([tuple(sorted(list(x))) for x in L_current])
        
        k = 2
        while L_current:
            # 2. Sinh tập ứng viên C_k (Candidate Generation)
            C_k = self._apriori_gen(L_current, k)
            
            if not C_k:
                break
                
            # 3. Quét CSDL để đếm support cho C_k (Lần quét thứ k)
            # Tối ưu: Nếu số lượng candidate quá lớn (>100k) và transaction nhỏ,
            # duyệt transaction rồi check subset trong C_k (dùng hash set) nhanh hơn.
            # Ngược lại nếu C_k nhỏ, duyệt C_k check subset của transaction.
            # Với dataset loãng như market basket, cách hash tree/set check transaction thường tốt hơn.
            
            C_k_set = set(C_k) # Để lookup O(1)
            candidates_counts = defaultdict(int)
            
            for trans in dataset:
                if len(trans) < k:
                    continue
                
                # Tìm tất cả tập con kích thước k của transaction nằm trong C_k
                # Với transaction ngắn (avg 5-10 items), combinations k=2,3 là nhỏ.
                trans_list = sorted(list(trans))
                for candidate in combinations(trans_list, k):
                    if candidate in C_k_set:
                        candidates_counts[candidate] += 1
            
            # 4. Lọc L_k (Frequent k-itemsets)
            L_next = []
            for cand, count in candidates_counts.items():
                if count >= min_sup_count:
                    L_next.append(cand)
                    if len(cand) >= self.min_items:
                        # Convert tuple back to list
                        self.frequent_itemsets.append((list(cand), count))
            
            # Update L_current cho vòng lặp kế tiếp
            L_current = sorted(L_next)
            k += 1
            
        return self.frequent_itemsets

    def _apriori_gen(self, L_prev, k):
        """
        Sinh ứng viên C_k từ L_{k-1} bằng phép join và prune.
        L_prev: list of sorted tuples (k-1 itemsets)
        """
        C_k = []
        len_L_prev = len(L_prev)
        
        # Tạo set để lookup cho bước prune
        L_prev_set = set(L_prev)
        
        for i in range(len_L_prev):
            for j in range(i + 1, len_L_prev):
                l1 = L_prev[i]
                l2 = L_prev[j]
                
                # Join step: check nếu k-2 phần tử đầu giống nhau
                # Với k=2: l1[:0] == l2[:0] (luôn đúng list rỗng)
                # Với k=3: l1[:1] == l2[:1] (item đầu giống nhau)
                if l1[:k-2] == l2[:k-2]:
                    # Cái nào nhỏ hơn sẽ đứng trước (do L_prev đã sort)
                    # l1[k-2] < l2[k-2] do loop i < j và sort
                    candidate = l1 + (l2[k-2],)
                    
                    # Prune step: Kiểm tra mọi tập con k-1 của candidate có trong L_prev không
                    if self._has_infrequent_subset(candidate, L_prev_set, k):
                        continue
                        
                    C_k.append(candidate)
                else:
                    # Do L_prev đã sort nên nếu prefix khác nhau thì các phần tử sau j cũng sẽ khác
                    # Optim: break inner loop?
                    # Không hẳn, vì prefix có thể khác ở index < k-2
                    # Nhưng ở đây ta sort theo thứ tự từ điển, nên nếu l1[:k-2] < l2[:k-2] thì l2' > l2 > l1 cũng sẽ khác.
                    # Nên break được nếu chỉ xét prefix.
                    # Tuy nhiên logic so sánh tuple của python là từng phần tử.
                    # Nếu l1[:k-2] != l2[:k-2], mà l2 > l1, thì các phần tử sau j cũng > l1 và có prefix > prefix l1 -> khác.
                    break
        return C_k

    def _has_infrequent_subset(self, candidate, L_prev_set, k):
        """
        Kiểm tra tính chất Apriori: Nếu tập con (k-1) nào đó không phổ biến -> loại.
        """
        # Ta chỉ cần tạo các subset size k-1.
        # Candidate là tuple size k.
        # Subset tạo bằng cách bỏ 1 phần tử.
        # Lưu ý: Các join đã đảm bảo 2 subset (đầu và cuối) có trong L_prev (từ l1 và l2).
        # Ta cần check các subset còn lại (bỏ phần tử ở giữa).
        for i in range(k):
            # Tạo subset bằng cách bỏ phần tử thứ i
            subset = candidate[:i] + candidate[i+1:]
            if subset not in L_prev_set:
                return True # Có tập con không phổ biến -> Prune candidate này
        return False

# ============================================================
# KHỐI TEST ĐỘC LẬP
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DEMO THUẬT TOÁN APRIORI")
    print("=" * 60)

    # 1. Dữ liệu mẫu (Khớp báo cáo)
    dataset = [
        {'A', 'B', 'C'},
        {'B', 'C', 'D'},
        {'A', 'C', 'D'},
        {'A', 'B', 'D'}
    ]
    
    # 2. Cấu hình
    MIN_SUP_PCT = 0.5
    print(f"Cấu hình: Min Support = {MIN_SUP_PCT*100}%")

    # 3. Chạy thuật toán
    model = Apriori(min_support=MIN_SUP_PCT, min_items=1)
    results = model.fit(dataset)
    
    # 4. In kết quả
    print("\n------------------------------------------------------------")
    print(f"{'Itemset':<15} | {'Count':<5}")
    print("-" * 40)
    
    results.sort(key=lambda x: (len(x[0]), x[0]))
    
    for itemset, count in results:
        item_str = "{" + ", ".join(sorted(itemset)) + "}"
        print(f"{item_str:<15} | {count:<5}")
        
    print("-" * 40)
    print(f"Tổng số tập phổ biến: {len(results)}")
