# 溈來 AI 電視｜學生資料批量導入脚本

處理目標：
1) 批量裁切學生「人臉」並統一輸出為 512×512 JPG。  
2) 批量改名為「姓名+學號後四位」格式。  
3) 依檔名生成導入名單（Excel 模板由你方提供，本專案只說明欄位對齊方式）。

---

## 環境需求

- Python 3.8+
- 依賴套件：

```bash
pip install opencv-python numpy
```

> Windows、macOS、Linux 皆可。路徑與檔名支援中文。

---

## 目錄結構（建議）

```
project-root/
├─ photos/            # 原始大圖（拍照公司交付）
├─ crop_faces/        # 輸出的人臉頭像（腳本自動建立）
├─ face_crop.py       # 人臉裁切
├─ rename_photos.py   # 批量改名
└─ weilai_import.xlsx # 交付溈來系統的導入模板（示意）
```

---

## 工作流程

**Step 1｜放圖**  
把所有原始照片放到 `photos/`。

**Step 2｜裁臉**

```bash
python3 face_crop.py
```
輸出至 `crop_faces/`，命名為 `原檔名_face.jpg`。  
腳本邏輯：OpenCV Haar Cascade 偵測正面人臉 → 取「最大臉」→ 放大框 ≈1.4 倍 → 裁切 → resize 到 **512×512** → 存為 JPG（品量 95）。

常見訊息：
- `OK crop_faces/xxx_face.jpg`：成功
- `讀取失敗 photos/xxx.jpg`：檔案壞掉或無法解碼
- `沒找到臉 photos/xxx.jpg`：需手動處理或重拍

**Step 3｜改名**  
把 `rename_photos.py` 指向 `crop_faces/`（或你要處理的任意資料夾）：

試跑（不動檔案）：
```bash
python3 rename_photos.py crop_faces --dry-run
```
正式改名：
```bash
python3 rename_photos.py crop_faces
```

改名規則：
- 來源檔名用 `-` 分段，**第二段 = 學號**，**第六段 = 姓名**。格式至少六段：  
  `欄1-學號-欄3-欄4-欄5-姓名`
- 學號尾碼若含 `X/x` 先去掉再取數字，僅 **最後四位**。  
- 新檔名：`{姓名}{後四位}.jpg`。  
- 檔名衝突時自動加 `_1/_2/...`。  
- 例：  
  `ABC-2024006617X-IMG-P1-RAW-陳大文_face.jpg` → `陳大文_face6617.jpg`  
  若不想 `_face` 出現在成品，可批次移除：

  **PowerShell**
  ```powershell
  Get-ChildItem crop_faces | Rename-Item -NewName { $_.Name -replace "_face", "" }
  ```

輸出統計：`完成：N 個已更名，跳過：M 個`（跳過多半是因為命名不滿足 6 段或取不到後四位）。

**Step 4｜對齊 Excel 模板後導入**  
溈來 AI 電視的模板以你方提供為準。常見對齊方式：

- `学生姓名(必填)` = `姓名 + 學號後四位`，需與最終圖片檔名（去掉 `.jpg`）**完全一致**。
- `性别`：`M→男`，`F→女`。
- `手机号`：建議加區號，例如 `+853-6xxxxxxx`。
- `所在班级(必填)`：用對方要求的全稱，例如 `聖保祿學校小學部-小學-P1A`。

> 請保留模板**第一列標題不動**，從第二列開始填資料。

---

## 疑難排解

- **裁切失敗或「沒找到臉」**：側臉、遮擋、太暗或人臉太小。需手動裁切或重拍。  
- **大批量「跳過」**：來源檔名未滿足 `a-b-c-d-e-f` 結構，請先整理檔名。  
- **中文檔名亂碼**：請確保終端字元集為 UTF-8，或直接在 OS 檔案總管檢視。

---

## 進階建議

- 保留原圖，裁切與改名在複本資料夾進行。  
- 對同學號不同人名的情況加校驗（可在 Excel 用 `圖片名` 與 `学生姓名(必填)` 做 VLOOKUP 驗重）。  
- 如有多臉照片，務必人工複核 `沒找到臉` 清單。

---

## 授權

校內專案用途。未標註即沿用原始檔案授權。

