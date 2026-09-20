# -*- coding: utf-8 -*-
"""ココナラ用サムネイル3枚（1200x1200）を Pillow で生成する。

  1. cd promo && node take_shots.js   … 素材のスクリーンショットを promo/shots/ に撮る
  2. python3 promo/make_images.py     … thumb1.png / thumb2.png / thumb3.png を上書き

作り：白地。中央にサイトのスクリーンショットをPC枠・スマホ枠に入れて配置。
上に濃紺の大きな1行、下に小さめの1行、右下に小さく「KIOI WORKS」。
値段・大学名・氏名は入れない。

cover.png は生成しない（--cover を付けたときだけ、従来どおり生成する）。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "shots")

WHITE = (255, 255, 255)
NAVY = (0x1B, 0x2A, 0x4A)
BEZEL = (0x2B, 0x36, 0x48)     # 画面枠の色
SHADOW = (0xE3, 0xE6, 0xEC)    # ごく薄い影
FRAME = (0xC8, 0xCD, 0xD6)

FONT_CANDIDATES = [
    ("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 0),      # macOS
    ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 0),   # Linux (Noto)
    ("/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf", 0),    # Linux (IPA Pゴシック)
    ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", 0),   # Linux (IPAゴシック)
]

BRAND = "KIOI WORKS"

# (出力名, 上の1行, 下の1行, レイアウト)
#   layout "pc+sp": PC枠(/en/ 幅1280) とスマホ枠(/en/ 幅390) を少し重ねて配置
#   layout "sp":    スマホ枠1つ（指定のスクリーンショット）
THUMBS = [
    ("thumb1.png", "英語ページ付きの店舗サイト", "日本語5ページ＋英語1ページ・スマホ対応・7日で公開",
     ("pc+sp", "en-pc.png", "en-sp.png")),
    ("thumb2.png", "今のサイトに英語ページを1枚", "作り直しなし・外国人のお客様が知りたいことだけ",
     ("sp", "en-sp.png")),
    ("thumb3.png", "予約サイトの英語、自然な文に", "Airbnb体験・GetYourGuide・自社サイト",
     ("sp", "ryokan-sp.png")),
]


def find_font_path():
    for path, index in FONT_CANDIDATES:
        if os.path.exists(path):
            return path, index
    sys.exit("日本語フォントが見つかりません。FONT_CANDIDATES にパスを追加してください。")


FONT_PATH, FONT_INDEX = find_font_path()
# ヒラギノ/Noto は太字のフォント。IPA は細いので、輪郭を足して太くする。
STROKE = 0 if ("W6" in FONT_PATH or "Bold" in FONT_PATH) else 2
print("font:", FONT_PATH)


def font(size):
    return ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)


def text_width(draw, text, f, stroke=0):
    left, _, right, _ = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    return right - left


def fit_font(draw, text, size, max_width, stroke=0):
    """1行が max_width に収まるまで文字サイズを下げる。"""
    while size > 10:
        f = font(size)
        if text_width(draw, text, f, stroke) <= max_width:
            return f
        size -= 2
    return font(size)


def draw_centered(draw, text, y, f, canvas_width, stroke=0):
    w = text_width(draw, text, f, stroke)
    draw.text(((canvas_width - w) / 2, y), text, font=f, fill=NAVY,
              stroke_width=stroke, stroke_fill=NAVY)


def load_shot(name, width):
    """スクリーンショットを指定幅に縮小して返す。"""
    path = os.path.join(SHOTS, name)
    if not os.path.exists(path):
        sys.exit(f"{path} がありません。先に `node promo/take_shots.js` を実行してください。")
    im = Image.open(path).convert("RGB")
    ratio = width / im.width
    return im.resize((width, int(im.height * ratio)), Image.LANCZOS)


def paste_device(img, shot, x, y, pad, radius, bezel=BEZEL, shadow_offset=10):
    """画面枠（角丸のベゼル）にスクリーンショットを入れて img に貼る。"""
    w, h = shot.width + pad * 2, shot.height + pad * 2
    d = ImageDraw.Draw(img)
    # 影
    d.rounded_rectangle([x + shadow_offset, y + shadow_offset, x + w + shadow_offset, y + h + shadow_offset],
                        radius=radius, fill=SHADOW)
    # ベゼル
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bezel)
    # 画面（角を少し丸める）
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, shot.width - 1, shot.height - 1],
                                           radius=max(radius - pad, 4), fill=255)
    img.paste(shot, (x + pad, y + pad), mask)
    return w, h


def make_thumb(filename, headline, sub, layout):
    W = H = 1200
    margin = 70
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # 上の1行（大きく）
    head_font = fit_font(d, headline, 92, W - 2 * margin, STROKE)
    draw_centered(d, headline, 95, head_font, W, STROKE)

    # 中央：スクリーンショット
    top, bottom = 250, 1010
    if layout[0] == "pc+sp":
        pc = load_shot(layout[1], 800)          # 800x500
        sp = load_shot(layout[2], 220)          # 220x476
        pad_pc, pad_sp = 14, 10
        pc_x = 95
        pc_y = top + 40
        paste_device(img, pc, pc_x, pc_y, pad_pc, radius=18)
        # スマホは右下に重ねる
        sp_h = sp.height + pad_sp * 2
        sp_x = pc_x + pc.width + pad_pc * 2 - 150
        sp_y = min(pc_y + 130, bottom - sp_h - 10)
        paste_device(img, sp, sp_x, sp_y, pad_sp, radius=34)
    else:
        sp = load_shot(layout[1], 330)          # 330x714
        pad_sp = 12
        w = sp.width + pad_sp * 2
        h = sp.height + pad_sp * 2
        sp_x = (W - w) // 2
        sp_y = top + (bottom - top - h) // 2
        paste_device(img, sp, sp_x, sp_y, pad_sp, radius=44)

    # 下の1行（小さめ）
    sub_font = fit_font(d, sub, 44, W - 2 * margin, 0)
    draw_centered(d, sub, 1052, sub_font, W, 0)

    # 右下に小さく KIOI WORKS
    brand_font = font(28)
    bw = text_width(d, BRAND, brand_font)
    d.text((W - margin - bw, H - 64), BRAND, font=brand_font, fill=NAVY)

    out = os.path.join(HERE, filename)
    img.save(out, "PNG")
    print("saved", out)


def make_cover():
    """カバー画像（1600x400）。今回は変更していないので --cover のときだけ作る。"""
    W, H = 1600, 400
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    shot_h = 320
    shot = Image.open(os.path.join(HERE, "en-screenshot.png")).convert("RGB")
    ratio = shot_h / shot.height
    shot = shot.resize((int(shot.width * ratio), shot_h), Image.LANCZOS)
    sx = W - shot.width - 70
    sy = (H - shot_h) // 2
    d.rectangle([sx + 4, sy + 6, sx + shot.width + 4, sy + shot_h + 6], fill=SHADOW)
    d.rectangle([sx - 2, sy - 2, sx + shot.width + 1, sy + shot_h + 1], outline=FRAME, width=2, fill=WHITE)
    img.paste(shot, (sx, sy))
    headline = ["外国人のお客様に伝わる", "英語ページ付きの店舗サイト"]
    left = 80
    text_max_w = sx - left - 60
    size = 66
    while size > 10 and max(text_width(d, t, font(size), STROKE) for t in headline) > text_max_w:
        size -= 2
    head_font = font(size)
    line_gap = int(size * 0.3)
    y = (H - (size * 2 + line_gap)) // 2 - 30
    for line in headline:
        d.text((left, y), line, font=head_font, fill=NAVY, stroke_width=STROKE, stroke_fill=NAVY)
        y += size + line_gap
    sub = "紀尾井ワークス｜翻訳ソフトは使いません"
    d.text((left, y + 28), sub, font=fit_font(d, sub, 26, text_max_w), fill=NAVY)
    out = os.path.join(HERE, "cover.png")
    img.save(out, "PNG")
    print("saved", out)


if __name__ == "__main__":
    for filename, headline, sub, layout in THUMBS:
        make_thumb(filename, headline, sub, layout)
    if "--cover" in sys.argv:
        make_cover()
