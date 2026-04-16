from glob import glob
import subprocess
from datetime import datetime, timedelta
import argparse
import sys
import re
import os

def get_time_from_filename(filename, pattern=r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})'):
    """
    從 DJI 檔名提取時間。
    格式: CAM_20250128212939_0256_D.MP4 -> 2025:01:28 21:29:39
    """
    # 正則表達式尋找 14 位數字 (YYYYMMDDHHMMSS)
    match = re.search(pattern, filename)
    if match:
        return f"{match.group(1)}:{match.group(2)}:{match.group(3)} {match.group(4)}:{match.group(5)}:{match.group(6)}"
    return None

def has_description(filepath, description):
    if not os.path.exists(filepath):
        return False
    
    cmd = ["exiftool", "-s3", description, filepath]
    
    try:
        # 使用 capture_output 取得結果，並去除空白字元
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # 如果輸出的字串長度大於 0，代表標籤存在
        return len(result.stdout.strip()) > 0
    except subprocess.CalledProcessError:
        # 如果 exiftool 執行失敗（例如檔案損壞），視為不存在
        return False

def has_xmp_description(filepath):
    """
    檢查 MP4 檔案中是否存在 XMP:Description 標籤。
    回傳: True (存在且有內容), False (不存在或讀取失敗)
    """
    return has_description(filepath, "-XMP:Description")

def get_createdate(filepath):
    """取得影片內部的 CreateDate，若無則回傳 None"""
    cmd = ["exiftool", "-s3", "-CreateDate", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout.strip()

    if out:
        return out
    return None

def copy_exif(src, dst, new_tz=8, default_tz=8, model='DJI Osmo360', debug=False):
    tz_str = f"{new_tz:+03d}:00"

    shift = new_tz - 0
    shift_str = f"{shift:+d}" # 建立偏移字串，例如 "+1" 或 "-5"

    create_date = get_createdate(src)
    if create_date is None:
        create_date = get_time_from_filename(os.path.basename(src))

        if not create_date:
            print(f"Failed (No time info from filename)")
            return False
        
        create_date_ts = datetime.strptime(create_date, "%Y:%m:%d %H:%M:%S") + timedelta(hours=-default_tz)
        create_date = create_date_ts.strftime("%Y:%m:%d %H:%M:%S")
    else:
        create_date_ts = datetime.strptime(create_date, "%Y:%m:%d %H:%M:%S")
    
    local_date_ts = create_date_ts + timedelta(hours=shift)
    local_date = local_date_ts.strftime("%Y:%m:%d %H:%M:%S")

    cmd = [
        "exiftool", 
        "-overwrite_original", 
        "-api", "LargeFileSupport=1",
        "-tagsFromFile", 
        f"{src}", 
        "-all:all",                   # 包含所有元數據
        f"-Model={model}",            # 覆蓋 Model 標籤
        # "-FileModifyDate",            # 同步檔案修改日期
        "-globalTimeShift", shift_str,
        f"-XMP:description={create_date}",
        f"-Keys:CreationDate={local_date}{tz_str}",
        f"{dst}"
    ]

    if debug:
        print('command', ' '.join(cmd))

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed ({e.stderr})")
        return False
    
    src_stat = os.stat(src)
    mtime = src_stat.st_mtime
    atime = src_stat.st_atime

    os.utime(dst, (atime, mtime))
    
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="path")
    parser.add_argument("-c", "--correct-tz", type=int, default=8, choices=range(-12, 15), help="correct timezone")
    parser.add_argument("-t", "--default-tz", type=int, default=8, choices=range(-12, 15), help="default timezone")
    parser.add_argument("-f", "--overwrite", action="store_true", help="overwrite")
    parser.add_argument("-d", "--debug", action="store_true", help="debug flag")

    args = parser.parse_args()

    for mp4 in sorted(glob(args.dir)):
        if mp4.lower().endswith(".mp4"):
            print(f"File: {mp4} ...", end='', flush=True)

            name = os.path.basename(mp4).split('.')[0]
            osv = os.path.join(os.path.dirname(mp4), f"{name}.OSV")
            
            if not args.overwrite and has_xmp_description(mp4):
                print(f"Skipped. (already fixed)")
                continue

            if os.path.isfile(osv):
                if copy_exif(osv, mp4, new_tz=args.correct_tz, default_tz=args.default_tz, debug=args.debug):
                    print("Finished.")
            else:
                print(f"Skipped. ({os.path.basename(osv)} not found)")