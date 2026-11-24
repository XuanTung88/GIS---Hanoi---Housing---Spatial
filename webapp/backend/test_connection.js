/**
 * test_connection.js
 * Script kiểm tra kết nối PostgreSQL và extension PostGIS dành riêng cho dự án
 * Chạy lệnh: node test_connection.js
 */

const path = require('path');
const { Pool } = require('pg');
require('dotenv').config({ path: path.resolve(__dirname, '.env') });

const config = {
  host: process.env.PGHOST || 'localhost',
  port: parseInt(process.env.PGPORT || '5432', 10),
  database: process.env.PGDATABASE || 'detai_gis',
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'postgres',
  connectionTimeoutMillis: 3000,
};

async function testConnection() {
  console.log('====================================================');
  console.log('[*] KIỂM TRA KẾT NỐI POSTGRESQL & POSTGIS CHO DỰ ÁN');
  console.log('====================================================');
  console.log(`Host:     ${config.host}`);
  console.log(`Port:     ${config.port}`);
  console.log(`Database: ${config.database}`);
  console.log(`User:     ${config.user}`);
  console.log('----------------------------------------------------');

  const pool = new Pool(config);

  try {
    const client = await pool.connect();
    console.log('[✓] Kết nối thành công tới máy chủ PostgreSQL!');

    // 1. Kiểm tra database
    const dbRes = await client.query('SELECT current_database();');
    console.log(`[✓] Đang làm việc trên Database: ${dbRes.rows[0].current_database}`);

    // 2. Kiểm tra PostGIS extension
    try {
      const gisRes = await client.query('SELECT postgis_full_version();');
      console.log('\n[🎉 THÀNH CÔNG] PostGIS đã được kích hoạt hoàn hảo:');
      console.log(`    ${gisRes.rows[0].postgis_full_version.split('\n')[0]}`);
      console.log('\n-> Bạn đã có thể chạy: npm run seed để nạp dữ liệu vào PostGIS!');
    } catch (e) {
      console.log('\n[!] LƯU Ý: Đã kết nối DB nhưng CHƯA bật extension PostGIS.');
      console.log('    Hãy chạy lệnh SQL sau trong pgAdmin hoặc psql:');
      console.log('    CREATE EXTENSION postgis;\n');
    }

    client.release();
  } catch (err) {
    console.error('\n[X] Không thể kết nối tới cơ sở dữ liệu:');
    console.error(`    Chi tiết lỗi: ${err.message}`);
    if (err.message.includes('password authentication failed')) {
      console.log('\n💡 Gợi ý: Mật khẩu chưa đúng. Hãy mở file webapp/backend/.env và sửa lại PGPASSWORD.');
    } else if (err.message.includes('database "detai_gis" does not exist')) {
      console.log('\n💡 Gợi ý: Chưa có database "detai_gis". Hãy tạo database trước:');
      console.log('    CREATE DATABASE detai_gis;');
    } else if (err.message.includes('ECONNREFUSED')) {
      console.log('\n💡 Gợi ý: Dịch vụ PostgreSQL chưa chạy hoặc sai cổng (Port).');
    }
  } finally {
    await pool.end();
  }
}

testConnection();
