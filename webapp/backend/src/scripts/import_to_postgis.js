/**
 * import_to_postgis.js
 * Script tự động nạp toàn bộ dữ liệu (Housing, Amenities, Model Stats) vào PostgreSQL + PostGIS.
 * Chạy lệnh: npm run import (hoặc node src/scripts/import_to_postgis.js)
 */

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const PROJECT_ROOT = path.resolve(__dirname, '../../../..');
const HOUSING_GEOJSON = path.resolve(__dirname, '../../data/housing.geojson');
const AMENITY_DIR = path.join(PROJECT_ROOT, 'data/raw/amenities_osm');
const MODEL_COMPARISON_CSV = path.join(PROJECT_ROOT, 'outputs/tables/model_comparison.csv');
const SCHEMA_FILE = path.resolve(__dirname, '../../schema.sql');

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

const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  port: parseInt(process.env.PGPORT || '5432', 10),
  database: process.env.PGDATABASE || 'detai_gis',
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'postgres',
});

async function main() {
  console.log('====================================================');
  console.log('[+] BẮT ĐẦU NẠP DỮ LIỆU VÀO POSTGRESQL / POSTGIS');
  console.log('====================================================');

  const client = await pool.connect();
  try {
    // 1. Chạy schema.sql
    console.log('[1/4] Khởi tạo bảng và PostGIS extension...');
    const schemaSql = fs.readFileSync(SCHEMA_FILE, 'utf8');
    await client.query(schemaSql);
    console.log('    ✓ Bảng housing, amenities, model_stats đã sẵn sàng.');

    // 2. Nạp dữ liệu Housing
    console.log('\n[2/4] Nạp dữ liệu nhà ở từ GeoJSON...');
    if (!fs.existsSync(HOUSING_GEOJSON)) {
      console.log('    Chưa có housing.geojson, đang chạy convert...');
      require('./convert_csv_to_geojson').convert();
    }
    const housingData = JSON.parse(fs.readFileSync(HOUSING_GEOJSON, 'utf8'));

    await client.query('TRUNCATE TABLE housing CASCADE;');
    let houseCount = 0;

    for (const feat of housingData.features) {
      const p = feat.properties;
      const [lon, lat] = feat.geometry.coordinates;

      const query = `
        INSERT INTO housing (
          id, fid, khu_vuc, gia, gia_ty, gia_trieu_m2, dien_tich, so_tang,
          loai_nha, dia_chi, url, dist_bus_stop_m, dist_hospital_m, dist_marketplace_m,
          dist_park_m, dist_school_m, dist_supermarket_m, dist_water_lakes_m,
          z_score, p_value, p_fdr, geom
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8,
          $9, $10, $11, $12, $13, $14,
          $15, $16, $17, $18,
          $19, $20, $21, ST_SetSRID(ST_MakePoint($22, $23), 4326)
        ) ON CONFLICT (id) DO UPDATE SET
          gia = EXCLUDED.gia,
          gia_trieu_m2 = EXCLUDED.gia_trieu_m2,
          geom = EXCLUDED.geom;
      `;

      await client.query(query, [
        p.id, p.fid, p.khu_vuc, p.gia, p.gia_ty, p.gia_trieu_m2, p.dien_tich, p.so_tang,
        p.loai_nha, p.dia_chi, p.url, p.dist_bus_stop_m, p.dist_hospital_m, p.dist_marketplace_m,
        p.dist_park_m, p.dist_school_m, p.dist_supermarket_m, p.dist_water_lakes_m,
        p.Z_score, p.p_value, p.p_fdr, lon, lat
      ]);
      houseCount++;
    }
    console.log(`    ✓ Đã nạp thành công ${houseCount} bản ghi nhà ở.`);

    // 3. Nạp dữ liệu tiện ích (amenities)
    console.log('\n[3/4] Nạp dữ liệu tiện ích từ OpenStreetMap...');
    await client.query('TRUNCATE TABLE amenities RESTART IDENTITY;');

    const amenityTypes = ['school', 'hospital', 'park', 'supermarket', 'marketplace', 'bus_stop', 'water_lakes'];
    let totalAmenities = 0;

    for (const type of amenityTypes) {
      const filePath = path.join(AMENITY_DIR, `${type}.geojson`);
      if (!fs.existsSync(filePath)) {
        console.log(`    ⚠ Không thấy file ${type}.geojson, bỏ qua.`);
        continue;
      }

      const geoData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      let count = 0;

      for (const feat of geoData.features) {
        const name = feat.properties.name || feat.properties['name:vi'] || feat.properties['name:en'] || type;
        const osmId = feat.properties['@id'] || null;
        const geomJson = JSON.stringify(feat.geometry);

        const insertQuery = `
          INSERT INTO amenities (amenity_type, name, osm_id, properties, geom)
          VALUES ($1, $2, $3, $4, ST_SetSRID(ST_GeomFromGeoJSON($5), 4326));
        `;
        await client.query(insertQuery, [type, name, osmId, JSON.stringify(feat.properties), geomJson]);
        count++;
      }
      totalAmenities += count;
      console.log(`    ✓ [${type}]: ${count} đối tượng.`);
    }
    console.log(`    ✓ Tổng cộng đã nạp ${totalAmenities} tiện ích.`);

    // 4. Nạp model_comparison
    console.log('\n[4/4] Nạp dữ liệu so sánh mô hình...');
    if (fs.existsSync(MODEL_COMPARISON_CSV)) {
      const csvContent = fs.readFileSync(MODEL_COMPARISON_CSV, 'utf8');
      const lines = csvContent.split(/\r?\n/).filter(l => l.trim().length > 0);
      await client.query('TRUNCATE TABLE model_stats;');
      for (let i = 1; i < lines.length; i++) {
        const parts = parseCSVLine(lines[i]);
        if (parts.length >= 4) {
          const modelName = parts[0].replace(/^"|"$/g, '').trim();
          const nObs = parseInt(parts[1], 10);
          const nFeatures = parseInt(parts[2], 10);
          const r2 = parseFloat(parts[3]);

          if (!isNaN(nObs) && !isNaN(nFeatures) && !isNaN(r2)) {
            await client.query(
              'INSERT INTO model_stats (model_name, n_obs, n_features, r2_score) VALUES ($1, $2, $3, $4)',
              [modelName, nObs, nFeatures, r2]
            );
          }
        }
      }
      console.log('    ✓ Đã nạp thông số so sánh mô hình OLS và Random Forest.');
    }

    console.log('\n[V] HOÀN TẤT NẠP DỮ LIỆU POSTGIS THÀNH CÔNG!');
  } catch (err) {
    console.error('[-] Lỗi nạp dữ liệu vào PostGIS:', err.message);
  } finally {
    client.release();
    await pool.end();
  }
}

if (require.main === module) {
  main();
}
