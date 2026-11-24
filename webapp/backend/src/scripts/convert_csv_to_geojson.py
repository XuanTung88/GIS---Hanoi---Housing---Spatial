"""
Script Python: Chuyển đổi housing_model_ready.csv -> housing.geojson
Chuẩn tọa độ WGS84 (EPSG:4326) để nạp vào PostGIS hoặc nạp trực tiếp qua Web GIS.
"""
import os
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CSV_PATH = BASE_DIR / "data" / "processed" / "housing_model_ready.csv"
OUT_DIR = BASE_DIR / "webapp" / "backend" / "data"
OUT_GEOJSON = OUT_DIR / "housing.geojson"

def main():
    print(f"[+] Đọc CSV từ: {CSV_PATH}")
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy {CSV_PATH}")
    
    df = pd.read_csv(CSV_PATH)
    
    features = []
    for _, row in df.iterrows():
        lat = row.get("latitude")
        lon = row.get("longitude")
        if pd.isna(lat) or pd.isna(lon) or (lat == 0 and lon == 0):
            continue
            
        props = {
            "id": str(row.get("id")),
            "fid": int(row.get("fid")) if pd.notna(row.get("fid")) else None,
            "khu_vuc": str(row.get("khu_vuc", "")),
            "gia": float(row.get("gia")) if pd.notna(row.get("gia")) else None,
            "gia_ty": float(row.get("gia_ty")) if pd.notna(row.get("gia_ty")) else None,
            "gia_trieu_m2": float(row.get("gia_trieu_m2")) if pd.notna(row.get("gia_trieu_m2")) else None,
            "dien_tich": float(row.get("dien_tich")) if pd.notna(row.get("dien_tich")) else None,
            "so_tang": int(row.get("so_tang")) if pd.notna(row.get("so_tang")) else 1,
            "loai_nha": str(row.get("loai_nha", "Hẻm")),
            "dia_chi": str(row.get("dia_chi", "")) if pd.notna(row.get("dia_chi")) else "",
            "url": str(row.get("url", "")) if pd.notna(row.get("url")) else "",
            "dist_bus_stop_m": round(float(row.get("dist_bus_stop_m")), 2) if pd.notna(row.get("dist_bus_stop_m")) else None,
            "dist_hospital_m": round(float(row.get("dist_hospital_m")), 2) if pd.notna(row.get("dist_hospital_m")) else None,
            "dist_marketplace_m": round(float(row.get("dist_marketplace_m")), 2) if pd.notna(row.get("dist_marketplace_m")) else None,
            "dist_park_m": round(float(row.get("dist_park_m")), 2) if pd.notna(row.get("dist_park_m")) else None,
            "dist_school_m": round(float(row.get("dist_school_m")), 2) if pd.notna(row.get("dist_school_m")) else None,
            "dist_supermarket_m": round(float(row.get("dist_supermarket_m")), 2) if pd.notna(row.get("dist_supermarket_m")) else None,
            "dist_water_lakes_m": round(float(row.get("dist_water_lakes_m")), 2) if pd.notna(row.get("dist_water_lakes_m")) else None,
            "Z_score": round(float(row.get("Z_score")), 4) if pd.notna(row.get("Z_score")) else None,
            "p_value": round(float(row.get("p_value")), 4) if pd.notna(row.get("p_value")) else None,
            "p_fdr": round(float(row.get("p_fdr")), 4) if pd.notna(row.get("p_fdr")) else None
        }
        
        feat = {
            "type": "Feature",
            "properties": props,
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon), float(lat)]
            }
        }
        features.append(feat)
        
    fc = {
        "type": "FeatureCollection",
        "name": "housing_listings",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": features
    }
    
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=2)
        
    print(f"[V] Thành công! Đã tạo file GeoJSON với {len(features)} điểm tại: {OUT_GEOJSON}")

if __name__ == "__main__":
    main()
