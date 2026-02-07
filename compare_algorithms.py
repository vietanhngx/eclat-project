
import sys
import os
import time
import tracemalloc
import csv
import matplotlib.pyplot as plt

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_data
from eclat import Eclat
from apriori import Apriori

def run_experiment(algorithm_class, dataset, min_support, algorithm_name):
    """
    Chạy thuật toán và đo lường thời gian + bộ nhớ.
    """
    print(f"--- Đang chạy {algorithm_name} với Min Support = {min_support} ---")
    
    # Bắt đầu đo bộ nhớ
    tracemalloc.start()
    
    start_time = time.time()
    
    model = algorithm_class(min_support=min_support, min_items=1)
    results = model.fit(dataset)
    
    end_time = time.time()
    
    # Dừng đo bộ nhớ
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    execution_time = end_time - start_time
    peak_memory_mb = peak / 1024 / 1024
    
    print(f"  -> Thời gian: {execution_time:.4f}s")
    print(f"  -> Bộ nhớ đỉnh: {peak_memory_mb:.4f} MB")
    print(f"  -> Số tập phổ biến tìm được: {len(results)}")
    
    return {
        "Algorithm": algorithm_name,
        "Min_Support": min_support,
        "Execution_Time_s": execution_time,
        "Peak_Memory_MB": peak_memory_mb,
        "Frequent_Itemsets": len(results)
    }

def main():
    print("=" * 60)
    print("SO SÁNH THUẬT TOÁN APRIORI VÀ ECLAT")
    print("=" * 60)
    
    # 1. Load Data
    # USER YÊU CẦU: Chạy trên toàn bộ tập dữ liệu (gần 1 triệu dòng)
    LIMIT = None 
    print(f"Đang tải TOÀN BỘ dữ liệu (msnbc.seq)...")
    dataset = load_data(limit=LIMIT, verbose=True)
    
    if not dataset:
        print("Lỗi tải dữ liệu.")
        return

    # 2. Cấu hình Experiment
    # Thử nghiệm với các mức support khác nhau
    # Lưu ý: min_support càng thấp -> càng nhiều itemset -> càng lâu
    supports = [0.05, 0.03, 0.02, 0.01] 
    
    results = []
    
    for sup in supports:
        # Run Apriori
        res_apriori = run_experiment(Apriori, dataset, sup, "Apriori")
        results.append(res_apriori)
        
        # Run Eclat
        res_eclat = run_experiment(Eclat, dataset, sup, "Eclat")
        results.append(res_eclat)
        
    # 3. Xuất kết quả ra CSV
    csv_file = "comparison_results.csv"
    keys = results[0].keys()
    with open(csv_file, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)
        
    print(f"\nĐã lưu kết quả vào {csv_file}")
    
    # 4. Vẽ biểu đồ (nếu có matplotlib)
    try:
        plot_results(results, supports)
    except Exception as e:
        print(f"Không thể vẽ biểu đồ: {e}")

def plot_results(results, supports):
    # Tách dữ liệu
    apriori_times = [r["Execution_Time_s"] for r in results if r["Algorithm"] == "Apriori"]
    eclat_times = [r["Execution_Time_s"] for r in results if r["Algorithm"] == "Eclat"]
    
    apriori_mem = [r["Peak_Memory_MB"] for r in results if r["Algorithm"] == "Apriori"]
    eclat_mem = [r["Peak_Memory_MB"] for r in results if r["Algorithm"] == "Eclat"]
    
    # Vẽ Time Chart
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(supports, apriori_times, marker='o', label='Apriori', color='red')
    plt.plot(supports, eclat_times, marker='o', label='Eclat', color='blue')
    plt.title('Execution Time Comparison')
    plt.xlabel('Min Support')
    plt.ylabel('Time (seconds)')
    plt.gca().invert_xaxis() # Trục x giảm dần (độ khó tăng dần)
    plt.legend()
    plt.grid(True)
    
    # Vẽ Memory Chart
    plt.subplot(1, 2, 2)
    plt.plot(supports, apriori_mem, marker='o', label='Apriori', color='red', linestyle='--')
    plt.plot(supports, eclat_mem, marker='o', label='Eclat', color='blue', linestyle='--')
    plt.title('Peak Memory Comparison')
    plt.xlabel('Min Support')
    plt.ylabel('Memory (MB)')
    plt.gca().invert_xaxis()
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    output_img = os.path.join("docs", "images", "comparison_chart.png")
    
    # Tạo thư mục images nếu chưa có
    os.makedirs(os.path.dirname(output_img), exist_ok=True)
    
    plt.savefig(output_img)
    print(f"Đã lưu biểu đồ vào {output_img}")

if __name__ == "__main__":
    main()
