#!/usr/bin/env python3
"""
用 Playwright 把小红书轮播 HTML 导出为 9 张 1080x1440 PNG。

用法:
  python3 scripts/export_xhs_slides.py
  python3 scripts/export_xhs_slides.py --input output/xiaohongshu-carousel.html --outdir output/slides/
"""
import argparse, os, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=os.path.join(os.path.dirname(__file__), '..', 'output', 'xiaohongshu-carousel.html'))
    parser.add_argument('--outdir', default=None)
    parser.add_argument('--scale', type=int, default=2, help='deviceScaleFactor (2 = retina)')
    args = parser.parse_args()

    html_path = os.path.abspath(args.input)
    if not os.path.exists(html_path):
        print(f'❌ 找不到文件：{html_path}')
        sys.exit(1)

    outdir = args.outdir or os.path.join(os.path.dirname(html_path), 'slides')
    os.makedirs(outdir, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={'width': 1200, 'height': 1600},
            device_scale_factor=args.scale,
        )
        page.goto(f'file://{html_path}')
        page.wait_for_load_state('networkidle')
        # 等字体加载完
        page.wait_for_timeout(2000)

        slides = page.query_selector_all('div.slide')
        print(f'🎨 找到 {len(slides)} 张幻灯片')

        for i, slide in enumerate(slides):
            name = f'P{i+1}.png'
            path = os.path.join(outdir, name)
            slide.screenshot(path=path, type='png')
            w, h = slide.evaluate('el => [el.offsetWidth, el.offsetHeight]')
            print(f'  ✅ {name}  ({w}x{h} → {w*args.scale}x{h*args.scale} px)')

        # 封面单独导出一份（小红书发图第一张）
        cover_path = os.path.join(outdir, '00-封面.png')
        slides[0].screenshot(path=cover_path, type='png')
        print(f'  ✅ 00-封面.png（同 P1，方便上传时选第一张）')

        browser.close()

    print(f'\n📂 全部导出到：{outdir}')
    print(f'   共 {len(slides)+1} 个文件（9 张轮播 + 1 张封面副本）')
    print(f'   尺寸：{1080*args.scale}x{1440*args.scale} px（{"retina" if args.scale==2 else "标准"}）')

if __name__ == '__main__':
    main()
