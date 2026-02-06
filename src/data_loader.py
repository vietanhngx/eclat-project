"""
Module data_loader.py - Đọc và tiền xử lý dữ liệu MSNBC Clickstream

Bộ dữ liệu: MSNBC.com Anonymous Web Data (UCI Machine Learning Repository)
Link: https://archive.ics.uci.edu/dataset/133/msnbc+com+anonymous+web+data

Mô tả dữ liệu:
- Ghi lại hành vi truy cập của 989,818 người dùng trên msnbc.com (ngày 28/09/1999)
- Mỗi dòng = 1 phiên (session) của 1 người dùng
- Mỗi số trong dòng = ID chuyên mục được truy cập (theo thứ tự thời gian)
- Có 17 chuyên mục nội dung được đánh số từ 1-17

Tham khảo:
- Cadez, I.V., Heckerman, D., Smyth, P., Meek, C., and White, S. (2003)
  "Model-Based Clustering and Visualization of Navigation Patterns on a Web Site"
"""

import os
from collections import Counter

# ============================================================
# CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ============================================================
# Lấy đường dẫn tuyệt đối của file này (data_loader.py)
CURRENT_FILE_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE_PATH)

# Đi ngược ra thư mục gốc dự án (Từ src ra Eclat_Project)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Đường dẫn đến file dữ liệu: Eclat_Project -> data -> raw -> msnbc.seq
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'msnbc.seq')

# ============================================================
# BẢNG ÁNH XẠ CHUYÊN MỤC (CATEGORY MAPPING)
# ============================================================
# Theo tài liệu UCI: 17 chuyên mục được đánh số từ 1-17
# Thứ tự chính xác theo file msnbc.names từ UCI Repository
# Đã dịch sang tiếng Việt cho dễ hiểu
CATEGORY_NAMES = {
    '1': 'Trang chủ',       # Frontpage
    '2': 'Tin tức',         # News
    '3': 'Công nghệ',       # Tech
    '4': 'Địa phương',      # Local
    '5': 'Ý kiến',          # Opinion
    '6': 'Phát sóng',       # On-air
    '7': 'Tổng hợp',        # Misc
    '8': 'Thời tiết',       # Weather
    '9': 'Sức khỏe',        # Health
    '10': 'Đời sống',       # Living
    '11': 'Kinh doanh',     # Business
    '12': 'Thể thao',       # Sports
    '13': 'Tóm tắt',        # Summary
    '14': 'Diễn đàn',       # BBS (Bulletin Board Service)
    '15': 'Du lịch',        # Travel
    '16': 'Tin MSN',        # MSN-News
    '17': 'Thể thao MSN'    # MSN-Sports
}

# Mapping ngược: Tên -> ID
CATEGORY_IDS = {v: k for k, v in CATEGORY_NAMES.items()}


def load_data(filepath=DATA_PATH, limit=None, verbose=True):
    """
    Đọc và tiền xử lý dữ liệu MSNBC clickstream.
    
    Quy trình:
    1. Bỏ qua các dòng metadata (bắt đầu bằng %)
    2. Với mỗi dòng dữ liệu, tách các ID số và ánh xạ sang tên chuyên mục
    3. Dùng set() để loại bỏ trùng lặp trong cùng 1 phiên (phù hợp cho Eclat)
    
    Args:
        filepath (str): Đường dẫn tới file msnbc.seq (mặc định tự động tìm)
        limit (int): Giới hạn số phiên đọc (None = đọc tất cả, dùng để test nhanh)
        verbose (bool): In thông tin debug ra màn hình
    
    Returns:
        dataset (list of sets): Danh sách các phiên giao dịch đã làm sạch.
                                Mỗi phiên là 1 set các tên chuyên mục.
                                VD: [{'News', 'Tech'}, {'Frontpage', 'Sports'}, ...]
    
    Example:
        >>> data = load_data(limit=1000)
        >>> print(len(data))
        1000
        >>> print(data[0])
        {'Frontpage', 'News'}
    """
    # Kiểm tra file tồn tại
    if not os.path.exists(filepath):
        if verbose:
            print("❌ Không tìm thấy file dữ liệu!")
        return []

    dataset = []
    category_counter = Counter()  # Đếm số lần xuất hiện từng chuyên mục
    skipped_lines = 0  # Đếm số dòng bị bỏ qua
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Dừng nếu đã đọc đủ số lượng limit
                if limit and len(dataset) >= limit:
                    break
                
                clean_line = line.strip()
                
                # --- QUAN TRỌNG: Lọc bỏ dòng không hợp lệ ---
                # 1. Bỏ qua dòng trống
                # 2. Bỏ qua dòng metadata (bắt đầu bằng %)
                if not clean_line or clean_line.startswith('%'):
                    skipped_lines += 1
                    continue
                
                # Tách các ID số theo khoảng trắng
                item_ids = clean_line.split()
                
                # Dùng set() để:
                # 1. Loại bỏ các click trùng lặp trong cùng 1 phiên
                # 2. Thuận tiện cho thuật toán Eclat (tập hợp)
                transaction = set()
                
                for item_id in item_ids:
                    # Validate: ID phải nằm trong khoảng 1-17
                    if item_id in CATEGORY_NAMES:
                        category_name = CATEGORY_NAMES[item_id]
                        transaction.add(category_name)
                        category_counter[category_name] += 1
                
                # Chỉ thêm vào dataset nếu phiên đó có ít nhất 1 click hợp lệ
                if transaction:
                    dataset.append(transaction)

        if verbose:
            print(f"Đã tải {len(dataset):,} phiên giao dịch.")
        
        return dataset

    except Exception as e:
        if verbose:
            print(f"❌ Có lỗi xảy ra khi đọc file: {e}")
        return []


def get_statistics(dataset):
    """
    Tính các thống kê cơ bản về bộ dữ liệu.
    
    Args:
        dataset: Danh sách các phiên từ load_data()
    
    Returns:
        dict: Dictionary chứa các thống kê
    """
    if not dataset:
        return {}
    
    session_lengths = [len(session) for session in dataset]
    
    return {
        'total_sessions': len(dataset),
        'avg_items_per_session': sum(session_lengths) / len(session_lengths),
        'min_items': min(session_lengths),
        'max_items': max(session_lengths),
        'unique_categories': len(set.union(*dataset)) if dataset else 0
    }


# ============================================================
# KHỐI TEST (Chỉ chạy khi bạn chạy trực tiếp file này)
# ============================================================
if __name__ == "__main__":
    # Test thử đọc 10 dòng đầu tiên
    data = load_data(limit=10)
    
    if data:
        print("\n--- KẾT QUẢ MẪU (5 dòng đầu) ---")
        for i, trans in enumerate(data[:5]):
            print(f"Phiên {i+1}: {trans}")
        
        # Thống kê
        stats = get_statistics(data)
        print(f"\n--- THỐNG KÊ ---")
        print(f"Tổng phiên: {stats['total_sessions']}")
        print(f"Trung bình items/phiên: {stats['avg_items_per_session']:.2f}")
    else:
        print("\n Không đọc được dữ liệu nào.")