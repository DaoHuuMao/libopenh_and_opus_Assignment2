import subprocess
import socket
import random
import time
import threading
import queue
import argparse

# ====== Cấu hình mạng và stream ======
UDP_IP = "192.168.1.8"      # IP máy thu (có thể sửa ở dòng lệnh)
UDP_PORT = 1234             # Cổng UDP máy thu (có thể sửa ở dòng lệnh)
PACKET_SIZE = 1316          # MPEG-TS packet group: 7 * 188

# ====== Tham số mặc định dễ chỉnh sửa ======
DEFAULT_BITRATE = "2500k"
DEFAULT_DROP_RATE = 0.02

def is_important_packet(packet):
    """Không drop các packet hệ thống (PID < 0x0020)."""
    if len(packet) < 188 or packet[0] != 0x47:
        return False
    pid = ((packet[1] & 0x1F) << 8) | packet[2]
    return pid < 0x0020

def read_stderr(proc, stderr_queue):
    """Thread đọc stderr từ FFmpeg."""
    while True:
        line = proc.stderr.readline().decode(errors='ignore')
        if not line and proc.poll() is not None:
            break
        if line:
            stderr_queue.put(line.strip())

def send_video_over_udp(input_file, bitrate, drop_rate, udp_ip, udp_port):
    """Gửi video MPEG-TS qua UDP, drop packet theo tỷ lệ drop_rate."""
    ffmpeg_cmd = [
        "ffmpeg",
        "-re",
        "-i", input_file,
        "-c:v", "libopenh264",
        "-b:v", bitrate,
        "-profile:v", "main",
        "-g", "30",
        "-preset", "ultrafast",
        "-c:a", "libopus",
        "-b:a", "128k",
        "-f", "mpegts",
        "-mpegts_flags", "system_b",
        "-mpegts_start_pid", "0x0100",
        "-flush_packets", "1",
        "-"
    ]

    try:
        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=10**6,
            universal_newlines=False
        )
    except FileNotFoundError:
        print("❌ Không tìm thấy FFmpeg.")
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.sendto(b"hello", (udp_ip, udp_port))
        print(f"✅ Đã kết nối với {udp_ip}:{udp_port}")
    except socket.error as e:
        print(f"❌ Lỗi socket: {e}")
        proc.terminate()
        return

    stderr_queue = queue.Queue()
    threading.Thread(target=read_stderr, args=(proc, stderr_queue), daemon=True).start()

    packet_count = 0
    dropped_count = 0
    start_time = time.time()

    try:
        while proc.poll() is None:
            packet = proc.stdout.read(PACKET_SIZE)
            if not packet:
                break
            if len(packet) != PACKET_SIZE:
                continue

            packet_count += 1

            # Drop thông minh: không drop packet hệ thống
            if not is_important_packet(packet):
                if drop_rate > 0.0 and random.random() < drop_rate:
                    dropped_count += 1
                    continue

            sock.sendto(packet, (udp_ip, udp_port))

            if packet_count % 200 == 0:
                elapsed = time.time() - start_time
                print(f"✔ Sent: {packet_count}, Dropped: {dropped_count}, Time: {elapsed:.1f}s")

    except Exception as e:
        print(f"❌ Lỗi khi gửi: {e}")

    finally:
        while not stderr_queue.empty():
            print("FFmpeg:", stderr_queue.get())
        print(f"\n📊 Tổng số gói: {packet_count}, Đã drop: {dropped_count}")
        proc.stdout.close()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        sock.close()

def main():
    parser = argparse.ArgumentParser(description="Drop and send MPEG-TS over UDP")
    parser.add_argument("--bitrate", type=str, default=DEFAULT_BITRATE, help="Bitrate video (e.g. 1000k, 2000k, ...)")
    parser.add_argument("--drop_rate", type=float, default=DEFAULT_DROP_RATE, help="Drop rate (0.0 to 1.0)")
    parser.add_argument("--input", type=str, default="output_with_overlay.mp4", help="Input video file")
    parser.add_argument("--udp_ip", type=str, default=UDP_IP, help="Receiver IP address")
    parser.add_argument("--udp_port", type=int, default=UDP_PORT, help="Receiver UDP port")
    args = parser.parse_args()

    print(f"=== Streaming {args.input} | Bitrate: {args.bitrate} | Drop rate: {args.drop_rate} ===")
    send_video_over_udp(
        input_file=args.input,
        bitrate=args.bitrate,
        drop_rate=args.drop_rate,
        udp_ip=args.udp_ip,
        udp_port=args.udp_port
    )

if __name__ == "__main__":
    main()