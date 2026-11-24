from pathlib import Path
import geopandas as gpd

# Lùi 1 cấp từ scripts/ ra Detai_GIS/
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_GEOJSON = BASE_DIR / "data" / "raw" / "boundary" / "data_3_quan.geojson"
OUTPUT_GPKG = BASE_DIR / "data" / "raw" / "boundary" / "boundary_clean.gpkg"

print(f"[+] Đang đọc dữ liệu từ: {INPUT_GEOJSON}")
gdf = gpd.read_file(INPUT_GEOJSON)

# 1. Chỉ giữ lại hình học là Polygon hoặc MultiPolygon
gdf_poly = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()

# 2. Xóa các trường metadata OSM phức tạp (@relations, @id...), chỉ giữ geometry và name nếu có
cols_to_keep = [col for col in ["name", "admin_level"] if col in gdf_poly.columns] + ["geometry"]
gdf_clean = gdf_poly[cols_to_keep]

# 3. Chuyển sang hệ tọa độ mét EPSG:32648 (UTM zone 48N)
gdf_clean = gdf_clean.to_crs(epsg=32648)

# 4. Gộp thành một đa giác duy nhất
dissolved = gdf_clean.dissolve()

# 5. Xuất file GeoPackage
dissolved.to_file(OUTPUT_GPKG, driver="GPKG")
print(f"[V] Đã tạo thành công file ranh giới chuẩn tại:\n -> {OUTPUT_GPKG}")