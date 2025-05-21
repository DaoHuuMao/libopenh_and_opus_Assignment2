from quality_metrics import quality_metrics
import os
import shutil
import numpy as np
import re

# Đường dẫn video gốc
original = "output_with_overlay.mp4"

# Danh sách các video máy thu cần so sánh
received_list = [
    "output/videos/500k_0001.mp4",
    "output/videos/1000k_0003.mp4",
    "output/videos/1500k_0005.mp4",
    "output/videos/2000k_001.mp4",
    "output/videos/2500k_002.mp4"
]

os.makedirs("output", exist_ok=True)

# Danh sách lưu kết quả tổng hợp
summary = []

# So sánh từng video máy thu, lưu log đầy đủ
for received in received_list:
    if not os.path.exists(received):
        print(f"Không tìm thấy file nhận: {received}")
        continue
    print(f"\n=== So sánh với: {os.path.basename(received)} ===")
    psnr, ssim = quality_metrics(original, received)
    print(f"PSNR: {psnr:.2f} dB | SSIM: {ssim:.4f}")

    # Đổi tên file log PSNR thành file riêng cho từng video
    base = os.path.splitext(os.path.basename(received))[0]
    psnr_log_src = "output/psnr_log.txt"
    psnr_log_dst = f"output/{base}_psnr_full.txt"
    if os.path.exists(psnr_log_src):
        shutil.copy(psnr_log_src, psnr_log_dst)
        print(f"Đã lưu log đầy đủ: {psnr_log_dst}")

    # Đổi tên file log SSIM thành file riêng cho từng video
    ssim_log_src = "output/ssim_log.txt"
    ssim_log_dst = f"output/{base}_ssim_full.txt"
    if os.path.exists(ssim_log_src):
        shutil.copy(ssim_log_src, ssim_log_dst)
        print(f"Đã lưu log SSIM đầy đủ: {ssim_log_dst}")

    # Thêm vào danh sách tổng hợp
    summary.append(base)

# Ghi file tổng hợp result.txt với các trường chi tiết (PSNR)
result_path = "output/result.txt"
with open(result_path, "w", encoding="utf-8") as f:
    f.write("BITRATE\tY\tU\tV\tAverage (dB)\tMin (dB)\tMax (dB)\n")
    for base in summary:
        psnr_file = f"output/{base}_psnr_full.txt"
        y_list, u_list, v_list, avg_list = [], [], [], []
        with open(psnr_file, "r") as pf:
            for line in pf:
                m = re.search(r"psnr_avg:([\d\.]+) psnr_y:([\d\.]+) psnr_u:([\d\.]+) psnr_v:([\d\.]+)", line)
                if m:
                    avg = float(m.group(1))
                    y = float(m.group(2))
                    u = float(m.group(3))
                    v = float(m.group(4))
                    avg_list.append(avg)
                    y_list.append(y)
                    u_list.append(u)
                    v_list.append(v)
        if avg_list:
            f.write(
                f"{base}\t"
                f"{np.mean(y_list):.6f}\t"
                f"{np.mean(u_list):.6f}\t"
                f"{np.mean(v_list):.6f}\t"
                f"{np.mean(avg_list):.6f}\t"
                f"{np.min(avg_list):.5f}\t"
                f"{np.max(avg_list):.5f}\n"
            )

# Ghi file tổng hợp result2.txt với các trường chi tiết (SSIM)
result2_path = "output/result2.txt"
with open(result2_path, "w", encoding="utf-8") as f:
    f.write("BITRATE\tY\tU\tV\tAverage\n")
    for base in summary:
        ssim_file = f"output/{base}_ssim_full.txt"
        y_list, u_list, v_list, all_list = [], [], [], []
        if not os.path.exists(ssim_file):
            print(f"Không tìm thấy file: {ssim_file}")
            continue
        with open(ssim_file, "r") as sf:
            for line in sf:
                m = re.search(r"Y:([\d\.]+) U:([\d\.]+) V:([\d\.]+) All:([\d\.]+)", line)
                if m:
                    y = float(m.group(1))
                    u = float(m.group(2))
                    v = float(m.group(3))
                    allv = float(m.group(4))
                    y_list.append(y)
                    u_list.append(u)
                    v_list.append(v)
                    all_list.append(allv)
        if all_list:
            f.write(
                f"{base}\t"
                f"{np.mean(y_list):.6f}\t"
                f"{np.mean(u_list):.6f}\t"
                f"{np.mean(v_list):.6f}\t"
                f"{np.mean(all_list):.6f}\n"
            )

print(f"\nĐã lưu kết quả tổng hợp chi tiết vào {result_path} và {result2_path}")