"""Build the whole site into site/: python tools/build.py

  tools/build_start.py  /start, /es/start, /privacy, /terms
  tools/build_home.py   home page, case-type pages, /fees, share pages, 404, robots.txt, sitemap.xml
  tools/make_assets.py  run by hand after changing a drawing or the brand line (step images, icons, og.png)

Retired builders kept for reference only (not run, not published): build_clone.py (the Framer clone, removed from the
site after the round 2 review) and the v2 page in build_site.py, which still holds CONFIG and the FAQ data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_home  # noqa: E402
import build_start  # noqa: E402

if __name__ == "__main__":
    build_start.build()
    build_home.build()
