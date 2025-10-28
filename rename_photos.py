#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

def last4_from_student_id(sid: str) -> str:
    # 忽略結尾的 X/x，僅取數字的最後四位
    if sid and sid[-1] in ("X", "x"):
        sid = sid[:-1]
    digits = "".join(ch for ch in sid if ch.isdigit())
    return digits[-4:] if len(digits) >= 4 else digits

def plan_new_name(p: Path):
    # 期望格式：a-b-c-d-e-f，第二欄為學號，第六欄為姓名
    parts = p.stem.split("-")
    if len(parts) < 6:
        return None
    student_id = parts[1]
    name = parts[5]
    last4 = last4_from_student_id(student_id)
    if not last4:
        return None
    return f"{name}{last4}{p.suffix}"

def main():
    ap = argparse.ArgumentParser(description="批量將檔名改為『姓名+學號後四位』")
    ap.add_argument("folder", help="包含照片的資料夾")
    ap.add_argument("--dry-run", action="store_true", help="只顯示將要改成的名字，不實際更名")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    count = 0
    skipped = 0

    for p in folder.iterdir():
        if not p.is_file():
            continue
        new_name = plan_new_name(p)
        if not new_name:
            skipped += 1
            continue

        target = p.with_name(new_name)

        # 若目標已存在，避免覆蓋：加序號
        if target.exists():
            stem, suf = Path(new_name).stem, Path(new_name).suffix
            i = 1
            while True:
                candidate = p.with_name(f"{stem}_{i}{suf}")
                if not candidate.exists():
                    target = candidate
                    break
                i += 1

        if args.dry_run:
            print(f"[DRY] {p.name}  ->  {target.name}")
        else:
            p.rename(target)
            print(f"[OK ] {p.name}  ->  {target.name}")
            count += 1

    print(f"完成：{count} 個已更名，跳過：{skipped} 個。")

if __name__ == "__main__":
    main()
