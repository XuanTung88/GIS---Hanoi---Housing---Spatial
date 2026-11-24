"""
Bước 3: Tính biến không gian - khoảng cách đến tiện ích gần nhất
         + mật độ tiện ích trong buffer 300/500/1000m
Input : data/interim/housing_geocoded.csv
        data/raw/amenities_osm/*.geojson  (school, hospital, park, supermarket, ...)
Output: data/processed/housing_with_spatial_features.csv

Cài đặt: pip install geopandas shapely scipy pandas
"""
import glob
import os

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HOUSING_FILE = "data/raw/housing_listings/housing_hanoi_center_150.csv"
AMENITY_DIR = "data/raw/amenities_osm"
OUTPUT_FILE = "data/processed/housing_with_spatial_features.csv"
CRS_METRIC = "EPSG:32648"  # UTM 48N - để tính khoảng cách bằng mét (không dùng lat/lon trực tiếp)
BUFFER_RADII = [300, 500, 1000]  # mét

LAT_COL = "latitude"
LON_COL = "longitude"

# 1. Đọc dữ liệu nhà, loại các dòng thiếu tọa độ, tạo lớp điểm và chuyển hệ tọa độ
df = pd.read_csv(HOUSING_FILE)
n_before = len(df)
df = df.dropna(subset=[LAT_COL, LON_COL])
df = df[(df[LAT_COL] != 0) & (df[LON_COL] != 0)]
print(f"Đọc {n_before} dòng, còn {len(df)} dòng có tọa độ hợp lệ.")

gdf_housing = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df[LON_COL], df[LAT_COL]), crs="EPSG:4326"
).to_crs(CRS_METRIC)

# 2. Lấy danh sách file tiện ích (bỏ lớp đường, xử lý riêng ở network analysis sau)
amenity_files = [
    f for f in glob.glob(os.path.join(AMENITY_DIR, "*.geojson")) if "road" not in f.lower()
]
if not amenity_files:
    raise SystemExit(f"Không tìm thấy file .geojson nào trong {AMENITY_DIR}")

coords_housing = np.column_stack([gdf_housing.geometry.x, gdf_housing.geometry.y])

for file in amenity_files:
    amenity_type = os.path.splitext(os.path.basename(file))[0]  # vd: school, hospital
    gdf_amenity = gpd.read_file(file).to_crs(CRS_METRIC)

    # Một số tiện ích có thể là polygon (vd: công viên) -> quy về tâm điểm
    gdf_amenity["geometry"] = gdf_amenity.geometry.apply(
        lambda g: g if g.geom_type == "Point" else g.centroid
    )

    if gdf_amenity.empty:
        print(f"⚠ {amenity_type}: không có điểm nào, bỏ qua.")
        continue

    coords_amenity = np.column_stack([gdf_amenity.geometry.x, gdf_amenity.geometry.y])
    tree = cKDTree(coords_amenity)

    # --- Khoảng cách đến tiện ích gần nhất (mét) ---
    dist, _ = tree.query(coords_housing, k=1)
    gdf_housing[f"dist_{amenity_type}_m"] = dist

    # --- Mật độ tiện ích trong từng bán kính buffer ---
    for radius in BUFFER_RADII:
        counts = tree.query_ball_point(coords_housing, r=radius, return_length=True)
        gdf_housing[f"count_{amenity_type}_{radius}m"] = counts

    print(f"✓ {amenity_type}: {len(gdf_amenity)} điểm -> đã tính khoảng cách + mật độ buffer")

# 3. Xuất bảng dữ liệu hoàn chỉnh (bỏ cột geometry vì CSV không lưu được)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
result = gdf_housing.drop(columns="geometry")
result.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"\nĐã lưu bảng dữ liệu hoàn chỉnh: {OUTPUT_FILE}")
print(f"Số dòng: {len(result)}, số cột: {len(result.columns)}")
print(f"Các cột mới: {[c for c in result.columns if c.startswith(('dist_', 'count_'))]}")
