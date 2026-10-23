"""Paint a wide user photo (whole scene, no cut-out) into a 1080x1920 Reel background.

Usage (from engine/specials): python3 paint_wide.py ../assets/src_<name>.jpg ../assets/bg_<name>.jpg
Scale 1.2 + crop x 200-1280 was tuned for a 1080x570 image; adjust for other sizes."""
import sys, numpy as np, cv2
import os; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from PIL import Image
import neha_poster as npost
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
s = 1.2
im = im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS).crop((200, 0, 1280, int(570*s)))
rgb = np.asarray(im)[..., ::-1]
sm = cv2.edgePreservingFilter(rgb, flags=1, sigma_s=30, sigma_r=0.2)
st = cv2.addWeighted(sm, 0.65, cv2.stylization(sm, sigma_s=20, sigma_r=0.12), 0.35, 0)
scene = Image.fromarray(st[..., ::-1].copy())
canvas = npost.watercolor_bg(11).resize((1080, 1920), Image.LANCZOS)
canvas = npost.painterly(canvas)
Y = 980; h = scene.height
m = Image.new('L', (1, h), 0)
for y in range(h):
    m.putpixel((0, y), int(255*min(1, y/150, (h-1-y)/90)))
canvas.paste(scene, (0, Y), m.resize((1080, h)))
a = np.asarray(canvas, np.float32)
yy = np.arange(1920)[:, None, None]
dark = np.clip((yy - (Y+h-90))/120, 0, 1)
a = a*(1-0.92*dark)
canvas = Image.fromarray(np.uint8(np.clip(a, 0, 255)))
canvas.save(out, quality=92)
print('saved', out, canvas.size)
