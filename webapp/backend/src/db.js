/**
 * db.js
 * Quản lý kết nối cơ sở dữ liệu PostGIS và cơ chế Fallback thông minh.
 * Khi có PostgreSQL/PostGIS, sử dụng các hàm ST_DWithin, ST_AsGeoJSON,...
 * Khi chưa cấu hình PostgreSQL, tự động fallback sang file GeoJSON/CSV nội bộ
 * đảm bảo hệ thống luôn hoạt động mượt mà 100% trong mọi môi trường.
 */

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const PROJECT_ROOT = path.resolve(__dirname, '../../..');
const HOUSING_GEOJSON_PATH = path.resolve(__dirname, '../data/housing.geojson');
const AMENITY_DIR = path.join(PROJECT_ROOT, 'data/raw/amenities_osm');
const BOUNDARY_FILE = path.join(PROJECT_ROOT, 'data/raw/boundary/data_3_quan.geojson');
const MODEL_COMPARISON_CSV = path.join(PROJECT_ROOT, 'outputs/tables/model_comparison.csv');
const OLS_SUMMARY_TXT = path.join(PROJECT_ROOT, 'outputs/tables/ols_summary.txt');

// Cấu hình PostgreSQL Pool
const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  port: parseInt(process.env.PGPORT || '5432', 10),
  database: process.env.PGDATABASE || 'detai_gis',
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'postgres',
  connectionTimeoutMillis: 2000, // Timeout ngắn để fallback nhanh nếu DB không bật
});

let isPostgresAvailable = false;
let memoryHousingData = null;
const memoryAmenitiesCache = new Map();

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim());
  return result;
}

// Hàm tính khoảng cách trắc địa Haversine (mét) giữa 2 tọa độ WGS84
function haversineDistanceMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Bán kính Trái Đất (mét)
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

// Khởi tạo và kiểm tra kết nối DB
async function initDB() {
  try {
    const client = await pool.connect();
    // Kiểm tra extension PostGIS
    const res = await client.query("SELECT postgis_version();");
    console.log(`[PostGIS] Đã kết nối PostgreSQL thành công! Phiên bản PostGIS: ${res.rows[0].postgis_version}`);
    client.release();
    isPostgresAvailable = true;
  } catch (err) {
    console.warn(`[PostGIS] Chưa kết nối được PostgreSQL (${err.message}).`);
    console.log(`[Engine] Đang kích hoạt chế độ File-based GIS Fallback Engine (sử dụng GeoJSON/CSV chuẩn xác).`);
    isPostgresAvailable = false;
  }

  // Tải trước dữ liệu GeoJSON cho chế độ fallback
  loadFallbackHousing();
}

function loadFallbackHousing() {
  if (!fs.existsSync(HOUSING_GEOJSON_PATH)) {
    console.log('[Fallback] Chưa có housing.geojson, tiến hành tạo mới từ CSV...');
    try {
      require('./scripts/convert_csv_to_geojson').convert();
    } catch (e) {
      console.error('[Fallback] Lỗi tạo housing.geojson:', e.message);
    }
  }

  if (fs.existsSync(HOUSING_GEOJSON_PATH)) {
    const raw = fs.readFileSync(HOUSING_GEOJSON_PATH, 'utf8');
    memoryHousingData = JSON.parse(raw);
    console.log(`[Fallback] Đã tải ${memoryHousingData.features.length} điểm nhà ở vào bộ nhớ đệm.`);
  }
}

// 1. Lấy danh sách nhà ở (có lọc)
async function getHousing(filters = {}) {
  const { district, houseType, minPrice, maxPrice, minArea, maxArea } = filters;

  if (isPostgresAvailable) {
    try {
      let query = `
        SELECT id, fid, khu_vuc, gia, gia_ty, gia_trieu_m2, dien_tich, so_tang, loai_nha, dia_chi, url,
               dist_bus_stop_m, dist_hospital_m, dist_marketplace_m, dist_park_m, dist_school_m,
               dist_supermarket_m, dist_water_lakes_m, z_score, p_value, p_fdr,
               ST_AsGeoJSON(geom) AS geometry
        FROM housing
        WHERE 1=1
      `;
      const params = [];
      let pIdx = 1;

      if (district) {
        query += ` AND khu_vuc = $${pIdx++}`;
        params.push(district);
      }
      if (houseType) {
        query += ` AND loai_nha = $${pIdx++}`;
        params.push(houseType);
      }
      if (minPrice) {
        query += ` AND gia_trieu_m2 >= $${pIdx++}`;
        params.push(parseFloat(minPrice));
      }
      if (maxPrice) {
        query += ` AND gia_trieu_m2 <= $${pIdx++}`;
        params.push(parseFloat(maxPrice));
      }
      if (minArea) {
        query += ` AND dien_tich >= $${pIdx++}`;
        params.push(parseFloat(minArea));
      }
      if (maxArea) {
        query += ` AND dien_tich <= $${pIdx++}`;
        params.push(parseFloat(maxArea));
      }

      query += ` ORDER BY gia_trieu_m2 DESC`;

      const result = await pool.query(query, params);
      return {
        type: 'FeatureCollection',
        features: result.rows.map(r => ({
          type: 'Feature',
          properties: {
            id: r.id,
            fid: r.fid,
            khu_vuc: r.khu_vuc,
            gia: r.gia ? parseFloat(r.gia) : null,
            gia_ty: r.gia_ty ? parseFloat(r.gia_ty) : null,
            gia_trieu_m2: r.gia_trieu_m2 ? parseFloat(r.gia_trieu_m2) : null,
            dien_tich: r.dien_tich ? parseFloat(r.dien_tich) : null,
            so_tang: r.so_tang,
            loai_nha: r.loai_nha,
            dia_chi: r.dia_chi,
            url: r.url,
            dist_bus_stop_m: r.dist_bus_stop_m ? parseFloat(r.dist_bus_stop_m) : null,
            dist_hospital_m: r.dist_hospital_m ? parseFloat(r.dist_hospital_m) : null,
            dist_marketplace_m: r.dist_marketplace_m ? parseFloat(r.dist_marketplace_m) : null,
            dist_park_m: r.dist_park_m ? parseFloat(r.dist_park_m) : null,
            dist_school_m: r.dist_school_m ? parseFloat(r.dist_school_m) : null,
            dist_supermarket_m: r.dist_supermarket_m ? parseFloat(r.dist_supermarket_m) : null,
            dist_water_lakes_m: r.dist_water_lakes_m ? parseFloat(r.dist_water_lakes_m) : null,
            Z_score: r.z_score ? parseFloat(r.z_score) : null,
            p_value: r.p_value ? parseFloat(r.p_value) : null,
            p_fdr: r.p_fdr ? parseFloat(r.p_fdr) : null,
          },
          geometry: JSON.parse(r.geometry),
        })),
      };
    } catch (e) {
      console.warn('[PostGIS Error, falling back]:', e.message);
    }
  }

  // Fallback từ GeoJSON file
  if (!memoryHousingData) {
    loadFallbackHousing();
  }

  let filtered = memoryHousingData ? [...memoryHousingData.features] : [];

  if (district && district !== 'Tất cả') {
    filtered = filtered.filter(f => f.properties.khu_vuc === district);
  }
  if (houseType && houseType !== 'Tất cả') {
    filtered = filtered.filter(f => f.properties.loai_nha === houseType);
  }
  if (minPrice) {
    const val = parseFloat(minPrice);
    filtered = filtered.filter(f => f.properties.gia_trieu_m2 >= val);
  }
  if (maxPrice) {
    const val = parseFloat(maxPrice);
    filtered = filtered.filter(f => f.properties.gia_trieu_m2 <= val);
  }
  if (minArea) {
    const val = parseFloat(minArea);
    filtered = filtered.filter(f => f.properties.dien_tich >= val);
  }
  if (maxArea) {
    const val = parseFloat(maxArea);
    filtered = filtered.filter(f => f.properties.dien_tich <= val);
  }

  return {
    type: 'FeatureCollection',
    features: filtered,
  };
}

// 2. Truy vấn không gian bán kính (ST_DWithin)
async function getNearbyHousing(lat, lon, radius = 500) {
  const latitude = parseFloat(lat);
  const longitude = parseFloat(lon);
  const rad = parseFloat(radius);

  if (isNaN(latitude) || isNaN(longitude) || isNaN(rad)) {
    throw new Error('Tọa độ lat, lon hoặc bán kính radius không hợp lệ.');
  }

  if (isPostgresAvailable) {
    try {
      const query = `
        SELECT id, fid, khu_vuc, gia, gia_ty, gia_trieu_m2, dien_tich, so_tang, loai_nha, dia_chi, url,
               dist_bus_stop_m, dist_hospital_m, dist_marketplace_m, dist_park_m, dist_school_m,
               dist_supermarket_m, dist_water_lakes_m, z_score, p_value, p_fdr,
               ROUND(ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography)::numeric, 1) AS distance_m,
               ST_AsGeoJSON(geom) AS geometry
        FROM housing
        WHERE ST_DWithin(
          geom::geography,
          ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
          $3
        )
        ORDER BY distance_m ASC;
      `;

      const result = await pool.query(query, [longitude, latitude, rad]);
      const features = result.rows.map(r => ({
        type: 'Feature',
        properties: {
          id: r.id,
          fid: r.fid,
          khu_vuc: r.khu_vuc,
          gia: r.gia ? parseFloat(r.gia) : null,
          gia_ty: r.gia_ty ? parseFloat(r.gia_ty) : null,
          gia_trieu_m2: r.gia_trieu_m2 ? parseFloat(r.gia_trieu_m2) : null,
          dien_tich: r.dien_tich ? parseFloat(r.dien_tich) : null,
          so_tang: r.so_tang,
          loai_nha: r.loai_nha,
          dia_chi: r.dia_chi,
          url: r.url,
          distance_m: parseFloat(r.distance_m),
          dist_bus_stop_m: r.dist_bus_stop_m ? parseFloat(r.dist_bus_stop_m) : null,
          dist_hospital_m: r.dist_hospital_m ? parseFloat(r.dist_hospital_m) : null,
          dist_marketplace_m: r.dist_marketplace_m ? parseFloat(r.dist_marketplace_m) : null,
          dist_park_m: r.dist_park_m ? parseFloat(r.dist_park_m) : null,
          dist_school_m: r.dist_school_m ? parseFloat(r.dist_school_m) : null,
          dist_supermarket_m: r.dist_supermarket_m ? parseFloat(r.dist_supermarket_m) : null,
          dist_water_lakes_m: r.dist_water_lakes_m ? parseFloat(r.dist_water_lakes_m) : null,
          Z_score: r.z_score ? parseFloat(r.z_score) : null,
          p_value: r.p_value ? parseFloat(r.p_value) : null,
        },
        geometry: JSON.parse(r.geometry),
      }));

      return createNearbyResponse(features, latitude, longitude, rad);
    } catch (e) {
      console.warn('[PostGIS Nearby Query Error, falling back]:', e.message);
    }
  }

  // Fallback Haversine Distance
  if (!memoryHousingData) {
    loadFallbackHousing();
  }

  const nearbyFeatures = [];
  for (const feat of (memoryHousingData ? memoryHousingData.features : [])) {
    const [fLon, fLat] = feat.geometry.coordinates;
    const dist = haversineDistanceMeters(latitude, longitude, fLat, fLon);
    if (dist <= rad) {
      nearbyFeatures.push({
        ...feat,
        properties: {
          ...feat.properties,
          distance_m: dist,
        },
      });
    }
  }

  nearbyFeatures.sort((a, b) => a.properties.distance_m - b.properties.distance_m);
  return createNearbyResponse(nearbyFeatures, latitude, longitude, rad);
}

function createNearbyResponse(features, lat, lon, radius) {
  const prices = features.map(f => f.properties.gia_trieu_m2).filter(p => p != null && !isNaN(p));
  const avgPrice = prices.length > 0 ? Math.round((prices.reduce((a, b) => a + b, 0) / prices.length) * 10) / 10 : 0;
  const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
  const maxPrice = prices.length > 0 ? Math.max(...prices) : 0;

  return {
    type: 'FeatureCollection',
    center: { lat, lon, radius },
    summary: {
      total: features.length,
      avg_price_per_m2: avgPrice,
      min_price_per_m2: minPrice,
      max_price_per_m2: maxPrice,
    },
    features,
  };
}

// 3. Lấy dữ liệu tiện ích theo loại (school, hospital, park, etc.)
async function getAmenities(type) {
  if (isPostgresAvailable) {
    try {
      const query = `
        SELECT name, osm_id, properties, ST_AsGeoJSON(geom) AS geometry
        FROM amenities
        WHERE amenity_type = $1;
      `;
      const result = await pool.query(query, [type]);
      if (result.rows.length > 0) {
        return {
          type: 'FeatureCollection',
          amenity_type: type,
          features: result.rows.map(r => ({
            type: 'Feature',
            properties: {
              name: r.name,
              osm_id: r.osm_id,
              ...(r.properties || {}),
            },
            geometry: JSON.parse(r.geometry),
          })),
        };
      }
    } catch (e) {
      console.warn(`[PostGIS Amenities Error (${type}), falling back]:`, e.message);
    }
  }

  // Fallback từ file GeoJSON gốc
  if (memoryAmenitiesCache.has(type)) {
    return memoryAmenitiesCache.get(type);
  }

  const filePath = path.join(AMENITY_DIR, `${type}.geojson`);
  if (!fs.existsSync(filePath)) {
    return { type: 'FeatureCollection', amenity_type: type, features: [] };
  }

  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    const geojson = JSON.parse(raw);
    geojson.amenity_type = type;
    memoryAmenitiesCache.set(type, geojson);
    return geojson;
  } catch (err) {
    console.error(`[-] Lỗi đọc ${type}.geojson:`, err.message);
    return { type: 'FeatureCollection', amenity_type: type, features: [] };
  }
}

// 4. Lấy danh sách các loại tiện ích hỗ trợ
function getAmenityMeta() {
  return [
    { type: 'school', nameVi: 'Trường học', icon: 'graduation-cap', color: '#e67e22' },
    { type: 'hospital', nameVi: 'Bệnh viện / Y tế', icon: 'hospital', color: '#e74c3c' },
    { type: 'park', nameVi: 'Công viên cây xanh', icon: 'tree', color: '#27ae60' },
    { type: 'supermarket', nameVi: 'Siêu thị', icon: 'shopping-cart', color: '#f39c12' },
    { type: 'marketplace', nameVi: 'Chợ truyền thống', icon: 'store', color: '#d35400' },
    { type: 'bus_stop', nameVi: 'Điểm dừng xe buýt', icon: 'bus', color: '#2980b9' },
    { type: 'water_lakes', nameVi: 'Hồ nước / Mặt nước', icon: 'water', color: '#3498db' },
  ];
}

// 5. Lấy ranh giới 3 quận (Ba Đình, Đống Đa, Hoàn Kiếm)
function getBoundaries() {
  if (fs.existsSync(BOUNDARY_FILE)) {
    const raw = fs.readFileSync(BOUNDARY_FILE, 'utf8');
    return JSON.parse(raw);
  }
  return { type: 'FeatureCollection', features: [] };
}

// 6. Lấy thống kê mô hình OLS, RF và tóm tắt đề tài
function getStats() {
  let modelComparison = [];
  if (fs.existsSync(MODEL_COMPARISON_CSV)) {
    const lines = fs.readFileSync(MODEL_COMPARISON_CSV, 'utf8').split(/\r?\n/).filter(l => l.trim().length > 0);
    for (let i = 1; i < lines.length; i++) {
      const parts = parseCSVLine(lines[i]);
      if (parts.length >= 4) {
        const modelName = parts[0].replace(/^"|"$/g, '').trim();
        const nObs = parseInt(parts[1], 10);
        const nFeatures = parseInt(parts[2], 10);
        const r2 = parseFloat(parts[3]);
        if (!isNaN(nObs) && !isNaN(nFeatures) && !isNaN(r2)) {
          modelComparison.push({
            model: modelName,
            n_obs: nObs,
            n_features: nFeatures,
            r2: r2,
          });
        }
      }
    }
  }

  // Thống kê mô tả từ dữ liệu nhà 121 bản ghi
  if (!memoryHousingData) {
    loadFallbackHousing();
  }
  const houses = memoryHousingData ? memoryHousingData.features : [];
  const districtStats = {};
  houses.forEach(h => {
    const dist = h.properties.khu_vuc || 'Khác';
    const price = h.properties.gia_trieu_m2;
    if (!districtStats[dist]) {
      districtStats[dist] = { count: 0, prices: [], areas: [] };
    }
    districtStats[dist].count++;
    if (price) districtStats[dist].prices.push(price);
    if (h.properties.dien_tich) districtStats[dist].areas.push(h.properties.dien_tich);
  });

  const districtsSummary = Object.keys(districtStats).map(dist => {
    const p = districtStats[dist].prices;
    const a = districtStats[dist].areas;
    const avgP = p.length ? Math.round((p.reduce((x, y) => x + y, 0) / p.length) * 10) / 10 : 0;
    const avgA = a.length ? Math.round((a.reduce((x, y) => x + y, 0) / a.length) * 10) / 10 : 0;
    return {
      district: dist,
      count: districtStats[dist].count,
      avg_price_per_m2: avgP,
      avg_area: avgA,
      min_price: p.length ? Math.min(...p) : 0,
      max_price: p.length ? Math.max(...p) : 0,
    };
  });

  // Hệ số mô hình OLS chính
  const olsCoefficients = [
    { variable: 'Hằng số (const)', coef: 393.8, p_val: 0.000, sig: true, desc: 'Mức giá cơ sở trung bình' },
    { variable: 'Quận Hoàn Kiếm', coef: 202.4, p_val: 0.011, sig: true, desc: 'Tăng ~202.4 tr/m² so với quận cơ sở (Ba Đình)' },
    { variable: 'Loại nhà: Mặt phố', coef: 88.0, p_val: 0.018, sig: true, desc: 'Tăng ~88.0 tr/m² so với nhà Hẻm/Ngõ' },
    { variable: 'Khoảng cách hồ nước (m)', coef: -0.209, p_val: 0.047, sig: true, desc: 'Mỗi 100m cách xa hồ làm giá giảm ~20.9 tr/m²' },
    { variable: 'Khoảng cách chợ (m)', coef: -0.127, p_val: 0.132, sig: false, desc: 'Xu hướng gần chợ giá cao hơn (p=0.13)' },
    { variable: 'Khoảng cách công viên (m)', coef: -0.104, p_val: 0.245, sig: false, desc: 'Gần công viên làm tăng giá nhẹ' },
    { variable: 'Khoảng cách xe buýt (m)', coef: -0.133, p_val: 0.539, sig: false, desc: 'Tác động không đáng kể' },
    { variable: 'Số tầng', coef: 8.77, p_val: 0.231, sig: false, desc: 'Mỗi tầng tăng ~8.8 tr/m²' },
    { variable: 'Diện tích (m²)', coef: 0.40, p_val: 0.174, sig: false, desc: 'Diện tích tăng kéo theo giá/m² tăng nhẹ' },
    { variable: 'Quận Đống Đa', coef: -23.4, p_val: 0.676, sig: false, desc: 'Không có sự khác biệt lớn so với Ba Đình' },
  ];

  return {
    overview: {
      title: 'Đề tài GIS: Phân tích Không gian và Định giá Nhà ở (Hedonic Pricing) tại Trung tâm Hà Nội',
      districts: ['Ba Đình', 'Đống Đa', 'Hoàn Kiếm'],
      total_listings: houses.length,
      model_r2_ols: 0.407,
      model_r2_rf: 0.092,
    },
    models: modelComparison,
    districtsSummary,
    olsCoefficients,
  };
}

module.exports = {
  initDB,
  pool,
  getHousing,
  getNearbyHousing,
  getAmenities,
  getAmenityMeta,
  getBoundaries,
  getStats,
  isPostgres: () => isPostgresAvailable,
};
