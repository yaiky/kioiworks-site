# -*- coding: utf-8 -*-
"""紀尾井ワークスのサービス告知用画像を Pillow で生成する。

  python3 promo/make_images.py

出力（このファイルと同じ promo/ フォルダ）:
  thumb1.png / thumb2.png / thumb3.png  … 1200x1200 のサムネイル
  cover.png                             … 1600x400 のカバー画像

フォントは macOS のヒラギノ角ゴ W6 を第一候補にし、無ければ
Linux の IPAゴシック等にフォールバックする。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

WHITE = (255, 255, 255)
NAVY = (0x1A, 0x2A, 0x4A)
FRAME = (0xC8, 0xCD, 0xD6)  # スクリーンショットの薄い枠
SHADOW = (0xE6, 0xE9, 0xEE)

FONT_CANDIDATES = [
    ("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 0),      # macOS
    ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 0),   # Linux (Noto)
    ("/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf", 0),    # Linux (IPA Pゴシック)
    ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", 0),   # Linux (IPAゴシック)
]

CREDIT = "紀尾井ワークス｜上智大学 村田祐希"

THUMBS = [
    ("thumb1.png", ["英語ページ付き", "店舗サイト制作"], "5ページ・スマホ対応・¥49,800"),
    ("thumb2.png", ["英語の紹介ページ", "1枚追加"], "今のサイトはそのまま・¥20,000"),
    ("thumb3.png", ["予約サイトの英語", "自然な英語に書き直し"], "Airbnb体験・GetYourGuide・¥5,000"),
]

COVER_HEADLINE = ["外国人のお客様に伝わる", "英語ページ付きの店舗サイト"]
COVER_SUB = "紀尾井ワークス｜上智大学 村田祐希｜翻訳ソフトは使いません"
SCREENSHOT = os.path.join(HERE, "en-screenshot.png")


def find_font_path():
    for path, index in FONT_CANDIDATES:
        if os.path.exists(path):
            return path, index
    sys.exit("日本語フォントが見つかりません。FONT_CANDIDATES にパスを追加してください。")


FONT_PATH, FONT_INDEX = find_font_path()
print("font:", FONT_PATH)


def font(size):
    return ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)


def text_width(draw, text, f):
    left, _, right, _ = draw.textbbox((0, 0), text, font=f)
    return right - left


def fit_font(draw, lines, size, max_width):
    """最長行が max_width に収まるまで文字サイズを下げる。"""
    while size > 10:
        f = font(size)
        if max(text_width(draw, t, f) for t in lines) <= max_width:
            return f, size
        size -= 2
    return font(size), size


def draw_centered(draw, text, y, f, canvas_width, fill=NAVY):
    w = text_width(draw, text, f)
    draw.text(((canvas_width - w) / 2, y), text, font=f, fill=fill)


def make_thumb(filename, headline, sub):
    W = H = 1200
    margin = 80
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # 見出し（2行、大きく）
    head_font, head_size = fit_font(d, headline, 118, W - 2 * margin)
    line_gap = int(head_size * 0.35)
    y = 300
    for line in headline:
        draw_centered(d, line, y, head_font, W)
        y += head_size + line_gap

    # 見出し下の細い罫線
    rule_w = 160
    y += 30
    d.rectangle([(W - rule_w) // 2, y, (W + rule_w) // 2, y + 6], fill=NAVY)
    y += 70

    # 補足（小さく）
    sub_font, _ = fit_font(d, [sub], 56, W - 2 * margin)
    draw_centered(d, sub, y, sub_font, W)

    # 下部の署名
    credit_font = font(40)
    draw_centered(d, CREDIT, H - 120, credit_font, W)

    out = os.path.join(HERE, filename)
    img.save(out, "PNG")
    print("saved", out)


def make_cover():
    W, H = 1600, 400
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # 右側：英語ページのスクリーンショット（薄い枠付き）
    shot_h = 320
    shot = Image.open(SCREENSHOT).convert("RGB")
    ratio = shot_h / shot.height
    shot = shot.resize((int(shot.width * ratio), shot_h), Image.LANCZOS)
    sx = W - shot.width - 70
    sy = (H - shot_h) // 2
    # ごく薄い影 → 枠 → 画像
    d.rectangle([sx + 4, sy + 6, sx + shot.width + 4, sy + shot_h + 6], fill=SHADOW)
    d.rectangle([sx - 2, sy - 2, sx + shot.width + 1, sy + shot_h + 1], outline=FRAME, width=2, fill=WHITE)
    img.paste(shot, (sx, sy))

    # 左側：見出しと補足
    left = 80
    text_max_w = sx - left - 60
    head_font, head_size = fit_font(d, COVER_HEADLINE, 66, text_max_w)
    line_gap = int(head_size * 0.3)
    block_h = head_size * 2 + line_gap
    y = (H - block_h) // 2 - 30
    for line in COVER_HEADLINE:
        d.text((left, y), line, font=head_font, fill=NAVY)
        y += head_size + line_gap

    sub_font, _ = fit_font(d, [COVER_SUB], 26, text_max_w)
    d.text((left, y + 28), COVER_SUB, font=sub_font, fill=NAVY)

    out = os.path.join(HERE, "cover.png")
    img.save(out, "PNG")
    print("saved", out)


if __name__ == "__main__":
    for filename, headline, sub in THUMBS:
        make_thumb(filename, headline, sub)
    make_cover()
