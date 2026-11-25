"""Person matte for a video with MediaPipe's selfie_multiclass model: writes a grayscale alpha video.

Usage: python3 matte_mediapipe.py <in.mp4> <alpha_out.mp4> <selfie_multiclass.tflite> [max_frames]
Background = class 0; everything else (hair, body, face, clothes) is the person. The confidence mask is
smoothed over time (EMA) and edges softened, so the cut-out does not flicker.
"""
import subprocess, sys
import numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

src, out, model = sys.argv[1:4]
maxf = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(","))
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=model), output_confidence_masks=True, output_category_mask=False))
rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                       "-vf", "gblur=sigma=1.2", "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
prev, n = None, 0
while n < maxf:
    buf = rd.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(img)))
    a = 1.0 - r.confidence_masks[0].numpy_view().astype(np.float32)  # 1 - P(background)
    a = a if prev is None else 0.6 * a + 0.4 * prev  # temporal smoothing against flicker
    prev = a
    a8 = np.clip((a - 0.25) / 0.5, 0, 1)  # firm up the core, keep a soft edge
    wr.stdin.write((a8 * 255).astype(np.uint8).tobytes()); n += 1
wr.stdin.close(); wr.wait(); rd.kill()
print("frames", n)
