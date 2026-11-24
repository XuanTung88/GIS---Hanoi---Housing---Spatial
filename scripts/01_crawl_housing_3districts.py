import os
import re
import time
import requests
import pandas as pd
from pathlib import Path

# --- 1. XÁC ĐỊNH ĐƯỜNG DẪN CHUẨN TRONG THƯ MỤC DỰ ÁN ---
# Đi từ Detai_GIS/scripts/ ra Detai_GIS/ rồi vào data/raw/housing_listings/
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "housing_listings"
OUTPUT_FILE = OUTPUT_DIR / "housing_hanoi_center_150.csv"


def extract_floors(text):
    """Trích xuất số tầng từ tiêu đề nếu API trả về None"""
    if not text:
        return 1
    match = re.search(r'(\d+)\s*(tầng|lầu|fl)', str(text).lower())
    return int(match.group(1)) if match else 1


def determine_house_type(ad):
    """Phân loại Mặt phố / Hẻm phục vụ biến mô hình Hedonic"""
    road_type = ad.get("property_road_sub_type") or ad.get("house_type")
    if road_type in [1, "1", "mặt phố", "mặt tiền"]:
        return "Mặt phố"
    if road_type in [2, 3, 4, "2", "3", "4", "ngõ", "hẻm"]:
        return "Hẻm"
    subject = (ad.get("subject") or "").lower()
    if any(k in subject for k in ["mặt phố", "mặt tiền", "kinh doanh"]):
        return "Mặt phố"
    return "Hẻm"


def crawl_chotot(district_name, area_id, target_count=50):
    base_url = "https://gateway.chotot.com/v1/public/ad-listing"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.nhatot.com",
        "Referer": "https://www.nhatot.com/"
    }

    records = []
    offset = 0
    print(f"\n[+] Bắt đầu cào dữ liệu: {district_name} (area_v2 = {area_id})...")

    while len(records) < target_count:
        params = {
            "cg": 1020,               # Nhà ở
            "region_v2": 12000,       # Hà Nội
            "area_v2": area_id,
            "limit": 20,
            "o": offset,
            "st": "s,k"
        }

        try:
            res = requests.get(base_url, headers=headers, params=params, timeout=10)
            if res.status_code != 200:
                print(f"[-] HTTP {res.status_code}. Dừng lượt cào này.")
                break

            ads = res.json().get("ads", [])
            if not ads:
                print(f"[*] Hết tin đăng khả dụng tại {district_name} (offset={offset}).")
                break

            for ad in ads:
                price = ad.get("price")
                size = ad.get("size")
                if not price or not size or float(size) <= 0 or float(price) <= 0:
                    continue

                floors = ad.get("floors_num") or ad.get("total_floors") or extract_floors(ad.get("subject"))
                
                address = ad.get("address")
                if not address:
                    parts = [ad.get("street_name"), ad.get("ward_name"), ad.get("area_name")]
                    address = ", ".join([p for p in parts if p])

                records.append({
                    "id": ad.get("list_id"),
                    "khu_vuc": district_name,
                    "gia": price,
                    "gia_ty": round(price / 1_000_000_000, 3),
                    "dien_tich": size,
                    "gia_trieu_m2": round((price / 1_000_000) / size, 2),
                    "so_tang": floors,
                    "loai_nha": determine_house_type(ad),
                    "dia_chi": address,
                    "latitude": ad.get("latitude"),
                    "longitude": ad.get("longitude"),
                    "url": f"https://www.nhatot.com/{ad.get('list_id')}.htm"
                })

                if len(records) >= target_count:
                    break

            offset += len(ads)
            print(f" -> Đã lấy được: {len(records)}/{target_count} tin...")
            time.sleep(1.2)

        except Exception as e:
            print(f"[-] Lỗi mạng hoặc JSON: {e}")
            break

    return pd.DataFrame(records)


if __name__ == "__main__":
    # Đảm bảo thư mục lưu data tồn tại
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------
    # CẤU HÌNH QUẬN CẦN LẤY TIẾP THEO:
    # Lần 1: Chạy lấy "Ba Đình"
    # Lần 2: Sửa tên thành "Hoàn Kiếm" và chạy tiếp
    # -----------------------------------------------------------------
    DISTRICT_NAME = "Hoàn Kiếm"    # Sửa thành "Hoàn Kiếm" sau khi Ba Đình xong
    AREA_ID = 12073              # Mã area_v2 của quận
    TARGET_PER_RUN = 50          # Lấy thêm 50 tin

    # 1. Cào dữ liệu quận mới
    df_new = crawl_chotot(DISTRICT_NAME, AREA_ID, target_count=TARGET_PER_RUN)

    # 2. Đọc file cũ hiện có để gộp
    if OUTPUT_FILE.exists():
        print(f"\n[+] Đang nạp file cũ: {OUTPUT_FILE.name}")
        df_old = pd.read_csv(OUTPUT_FILE)
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_combined = df_new

    # 3. Lọc trùng lặp (trùng ID bài viết hoặc trùng giá + diện tích + địa chỉ)
    df_combined = df_combined.drop_duplicates(subset=["id"])
    df_combined = df_combined.drop_duplicates(subset=["gia", "dien_tich", "dia_chi"])

    # 4. Ghi đè vào housing_hanoi_center_150.csv
    df_combined.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n[V] THÀNH CÔNG!")
    print(f" -> File đã lưu tại: {OUTPUT_FILE}")
    print(f" -> Tổng số dòng dữ liệu hiện có: {len(df_combined)} dòng")
    print(f" -> Thống kê theo khu vực:")
    print(df_combined["khu_vuc"].value_counts())