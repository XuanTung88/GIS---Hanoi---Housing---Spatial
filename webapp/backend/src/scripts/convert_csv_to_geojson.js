/**
 * convert_csv_to_geojson.js
 * Script chuyển đổi dữ liệu nhà từ CSV (data/processed/housing_model_ready.csv)
 * sang định dạng GeoJSON chuẩn (Point geometry WGS84: EPSG 4326)
 * để nạp vào PostGIS hoặc dùng trực tiếp trong Webapp.
 */

const fs = require('fs');
const path = require('path');

// Đường dẫn tương đối từ vị trí script
const PROJECT_ROOT = path.resolve(__dirname, '../../../..');
const CSV_FILE = path.join(PROJECT_ROOT, 'data/processed/housing_model_ready.csv');
const OUT_DIR = path.resolve(__dirname, '../../data');
const OUT_FILE = path.join(OUT_DIR, 'housing.geojson');

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
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result;
}

function convert() {
  console.log(`[+] Đang đọc dữ liệu từ: ${CSV_FILE}`);
  if (!fs.existsSync(CSV_FILE)) {
    console.error(`[-] Không tìm thấy file nguồn: ${CSV_FILE}`);
    process.exit(1);
  }

  const rawData = fs.readFileSync(CSV_FILE, 'utf8');
  const lines = rawData.split(/\r?\n/).filter(l => l.trim().length > 0);
  
  if (lines.length < 2) {
    console.error('[-] File CSV rỗng hoặc chỉ có tiêu đề.');
    process.exit(1);
  }

  const headers = parseCSVLine(lines[0]).map(h => h.trim());
  const features = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    if (values.length < headers.length) continue;

    const row = {};
    headers.forEach((h, idx) => {
      row[h] = values[idx] !== undefined ? values[idx].trim() : '';
    });

    const lat = parseFloat(row.latitude);
    const lon = parseFloat(row.longitude);

    if (isNaN(lat) || isNaN(lon) || (lat === 0 && lon === 0)) {
      continue;
    }

    const properties = {
      id: row.id || `H_${i}`,
      fid: row.fid ? parseInt(row.fid, 10) : i,
      khu_vuc: row.khu_vuc || '',
      gia: row.gia ? parseFloat(row.gia) : null,
      gia_ty: row.gia_ty ? parseFloat(row.gia_ty) : (row.gia ? parseFloat(row.gia) / 1e9 : null),
      gia_trieu_m2: row.gia_trieu_m2 ? parseFloat(row.gia_trieu_m2) : null,
      dien_tich: row.dien_tich ? parseFloat(row.dien_tich) : null,
      so_tang: row.so_tang ? parseInt(row.so_tang, 10) : 1,
      loai_nha: row.loai_nha || 'Hẻm',
      dia_chi: row.dia_chi || '',
      url: row.url || '',
      
      // Khoảng cách tới các tiện ích (m)
      dist_bus_stop_m: row.dist_bus_stop_m ? Math.round(parseFloat(row.dist_bus_stop_m) * 10) / 10 : null,
      dist_hospital_m: row.dist_hospital_m ? Math.round(parseFloat(row.dist_hospital_m) * 10) / 10 : null,
      dist_marketplace_m: row.dist_marketplace_m ? Math.round(parseFloat(row.dist_marketplace_m) * 10) / 10 : null,
      dist_park_m: row.dist_park_m ? Math.round(parseFloat(row.dist_park_m) * 10) / 10 : null,
      dist_school_m: row.dist_school_m ? Math.round(parseFloat(row.dist_school_m) * 10) / 10 : null,
      dist_supermarket_m: row.dist_supermarket_m ? Math.round(parseFloat(row.dist_supermarket_m) * 10) / 10 : null,
      dist_water_lakes_m: row.dist_water_lakes_m ? Math.round(parseFloat(row.dist_water_lakes_m) * 10) / 10 : null,

      // Thống kê không gian Local Moran's I
      Z_score: row.Z_score ? parseFloat(row.Z_score) : null,
      p_value: row.p_value ? parseFloat(row.p_value) : null,
      p_fdr: row.p_fdr ? parseFloat(row.p_fdr) : null
    };

    features.push({
      type: 'Feature',
      properties,
      geometry: {
        type: 'Point',
        coordinates: [lon, lat]
      }
    });
  }

  const geojson = {
    type: 'FeatureCollection',
    name: 'housing_listings',
    crs: {
      type: 'name',
      properties: { name: 'urn:ogc:def:crs:OGC:1.3:CRS84' }
    },
    features
  };

  if (!fs.existsSync(OUT_DIR)) {
    fs.mkdirSync(OUT_DIR, { recursive: true });
  }

  fs.writeFileSync(OUT_FILE, JSON.stringify(geojson, null, 2), 'utf8');
  console.log(`[V] Thành công! Đã tạo file GeoJSON với ${features.length} điểm.`);
  console.log(`    Lưu tại: ${OUT_FILE}`);
}

if (require.main === module) {
  convert();
}

module.exports = { convert, OUT_FILE };
