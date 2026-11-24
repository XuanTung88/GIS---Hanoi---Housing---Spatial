-- ============================================================
-- Schema cơ sở dữ liệu GIS cho Đề tài Phân tích Giá nhà Hà Nội
-- Hỗ trợ lưu trữ không gian PostGIS và truy vấn ST_DWithin
-- ============================================================

-- 1. Kích hoạt PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Bảng nhà ở (Housing listings)
CREATE TABLE IF NOT EXISTS housing (
    id                  TEXT PRIMARY KEY,
    fid                 INTEGER,
    khu_vuc             TEXT,
    gia                 NUMERIC,
    gia_ty              NUMERIC,
    gia_trieu_m2        NUMERIC,
    dien_tich           NUMERIC,
    so_tang             INTEGER,
    loai_nha            TEXT,
    dia_chi             TEXT,
    url                 TEXT,
    dist_bus_stop_m     NUMERIC,
    dist_hospital_m     NUMERIC,
    dist_marketplace_m  NUMERIC,
    dist_park_m         NUMERIC,
    dist_school_m       NUMERIC,
    dist_supermarket_m  NUMERIC,
    dist_water_lakes_m  NUMERIC,
    z_score             NUMERIC,   -- Local Moran's I Z-score
    p_value             NUMERIC,   -- Local Moran's I p-value
    p_fdr               NUMERIC,
    geom                GEOMETRY(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_housing_geom ON housing USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_housing_khu_vuc ON housing (khu_vuc);
CREATE INDEX IF NOT EXISTS idx_housing_gia_m2 ON housing (gia_trieu_m2);

-- 3. Bảng tiện ích đô thị (Amenities)
CREATE TABLE IF NOT EXISTS amenities (
    id           SERIAL PRIMARY KEY,
    amenity_type TEXT NOT NULL,  -- school, hospital, park, supermarket, marketplace, bus_stop, water_lakes
    name         TEXT,
    osm_id       TEXT,
    properties   JSONB,
    geom         GEOMETRY(Geometry, 4326)
);

CREATE INDEX IF NOT EXISTS idx_amenities_geom ON amenities USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_amenities_type ON amenities (amenity_type);

-- 4. Bảng kết quả so sánh mô hình Hedonic (OLS vs Random Forest)
CREATE TABLE IF NOT EXISTS model_stats (
    id           SERIAL PRIMARY KEY,
    model_name   TEXT,
    n_obs        INTEGER,
    n_features   INTEGER,
    r2_score     NUMERIC,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
