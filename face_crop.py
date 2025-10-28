import cv2
import numpy as np
import os
from pathlib import Path

# 路徑設定
INPUT_DIR = "photos"
CROP_DIR = "crop_faces"
os.makedirs(CROP_DIR, exist_ok=True)

# OpenCV 內建正面人臉分類器
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def imread_unicode(path_str):
    """
    讀取含中文/特殊字元路徑的圖片
    """
    data = np.fromfile(path_str, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img

def imwrite_unicode(path_str, img_bgr, quality=95):
    """
    寫出含中文/特殊字元路徑的圖片
    """
    ok, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        return False
    buf.tofile(path_str)
    return True

def expand_box(x, y, w, h, scale, img_w, img_h):
    """
    以臉框為中心 扩大成接近正方形
    scale 決定留多少額頭+下巴
    """
    cx = x + w / 2.0
    cy = y + h / 2.0
    size = max(w, h) * scale  # 1.4 = 臉再加一圈頭髮/下巴

    nx = int(cx - size / 2.0)
    ny = int(cy - size / 2.0)
    nw = int(size)
    nh = int(size)

    # 邊界裁剪
    if nx < 0:
        nx = 0
    if ny < 0:
        ny = 0
    if nx + nw > img_w:
        nw = img_w - nx
    if ny + nh > img_h:
        nh = img_h - ny

    return nx, ny, nw, nh

def crop_biggest_face(img_bgr):
    img_h, img_w, _ = img_bgr.shape

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 偵測臉
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return None

    # 取面積最大的一張臉
    best = None
    best_area = 0
    for (x, y, w, h) in faces:
        area = w * h
        if area > best_area:
            best_area = area
            best = (x, y, w, h)

    x, y, w, h = best

    # 放大臉框 比例 1.4
    ex, ey, ew, eh = expand_box(x, y, w, h, scale=1.4, img_w=img_w, img_h=img_h)

    face_crop = img_bgr[ey:ey+eh, ex:ex+ew]
    return face_crop

def process_all():
    exts = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".PNG"]
    for p in Path(INPUT_DIR).iterdir():
        if p.suffix not in exts:
            continue

        # 用自定義讀檔 讓中文檔名不會爆
        img = imread_unicode(str(p))
        if img is None:
            print(f"讀取失敗 {p}")
            continue

        face_img = crop_biggest_face(img)
        if face_img is None:
            print(f"沒找到臉 {p}")
            continue

        # 固定輸出為 512x512
        out_img = cv2.resize(face_img, (512, 512), interpolation=cv2.INTER_CUBIC)

        out_name = p.stem + "_face.jpg"
        out_path = Path(CROP_DIR) / out_name

        ok = imwrite_unicode(str(out_path), out_img, quality=95)
        if ok:
            print(f"OK {out_path}")
        else:
            print(f"寫出失敗 {out_path}")

if __name__ == "__main__":
    process_all()
