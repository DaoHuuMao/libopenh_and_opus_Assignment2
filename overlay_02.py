from moviepy import VideoFileClip, ImageSequenceClip, CompositeVideoClip

video = VideoFileClip("recorded_video.mp4")
overlay = ImageSequenceClip("frames", fps=30)  # fps video của bạn là 30 nhé

# Đặt vị trí overlay chính xác
overlay = overlay.with_position(("center", "center"))

final = CompositeVideoClip([video, overlay])
final.write_videofile("output_with_overlay.mp4", codec="libx264", audio_codec="aac")
