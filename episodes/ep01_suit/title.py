"""Opening title card for ep 1 (series template lives in tools/style.py)."""
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from style import *

S = Path(sys.argv[1])        # holds f_title.png (frame from IMG_2004 @ 8.5s, first fitting)
im = Image.open(S / 'f_title.png').convert('RGBA').resize((W, H))
series_title(im, '[ ep 1: custom suits ]', cy=H // 2 + 60)
im.convert('RGB').save(Path(__file__).parent / 'still_title.jpg', quality=92)
print('ok')
