import matplotlib.pyplot as plt
import subprocess
import numpy as np
import os

def quality_metrics(original_video, received_video):
    """Tính PSNR/SSIM và vẽ biểu đồ.
    
    Args:
        original_video (str): Đường dẫn video gốc.
        received_video (str): Đường dẫn video đã xử lý.
    
    Returns:
        tuple: (PSNR trung bình, SSIM trung bình).
    """
    if not os.path.exists(original_video) or not os.path.exists(received_video):
        raise FileNotFoundError(f"Không tìm thấy {original_video} hoặc {received_video}")
    
    # Tính PSNR/SSIM với filter_complex
    psnr_log = 'output/psnr_log.txt'
    ssim_log = 'output/ssim_log.txt'
    cmd = [
        'ffmpeg',
        '-i', received_video,
        '-i', original_video,
        '-filter_complex',
        f'[0:v][1:v]psnr=stats_file={psnr_log};[0:v][1:v]ssim=stats_file={ssim_log}',
        '-f', 'null', '-'
    ]
    subprocess.run(cmd, check=True, shell=False)
    
    # Đọc log PSNR
    psnr_values = []
    with open(psnr_log, 'r') as f:
        for line in f:
            if 'psnr_avg' in line:
                try:
                    psnr_values.append(float(line.split('psnr_avg:')[1].split()[0]))
                except Exception:
                    pass
    
    # Đọc log SSIM
    ssim_values = []
    with open(ssim_log, 'r') as f:
        for line in f:
            if 'All:' in line:
                try:
                    ssim_values.append(float(line.split('All:')[1].split()[0]))
                except Exception:
                    pass
    
    # In kết quả
    psnr_avg = np.mean(psnr_values) if psnr_values else 0
    ssim_avg = np.mean(ssim_values) if ssim_values else 0
    print(f"PSNR trung bình: {psnr_avg:.2f} dB")
    print(f"SSIM trung bình: {ssim_avg:.4f}")
    
    # Vẽ biểu đồ
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(psnr_values, 'b-')
    plt.title('PSNR theo Frame')
    plt.xlabel('Frame')
    plt.ylabel('PSNR (dB)')
    plt.grid(True)
    plt.subplot(2, 1, 2)
    plt.plot(ssim_values, 'r-')
    plt.title('SSIM theo Frame')
    plt.xlabel('Frame')
    plt.ylabel('SSIM')
    plt.grid(True)
    plt.tight_layout()
    output_plot = f"output/plots/quality_{os.path.basename(received_video)[:-4]}.png"
    os.makedirs('output/plots', exist_ok=True)
    plt.savefig(output_plot)
    plt.close()
    print(f"Đã lưu biểu đồ: {output_plot}")
    
    return psnr_avg, ssim_avg