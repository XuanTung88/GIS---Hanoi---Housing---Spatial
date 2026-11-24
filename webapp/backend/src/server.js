/**
 * server.js
 * Entry point cho Backend Express Server của Webapp GIS
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const db = require('./db');
const housingRoutes = require('./routes/housing');
const amenitiesRoutes = require('./routes/amenities');
const statsRoutes = require('./routes/stats');
const boundariesRoutes = require('./routes/boundaries');

const app = express();
const PORT = process.env.PORT || 3000;
const PROJECT_ROOT = path.resolve(__dirname, '../../..');

// Middlewares
app.use(cors());
app.use(express.json());

// Phục vụ frontend tĩnh trực tiếp từ Express
const FRONTEND_DIR = path.resolve(__dirname, '../../frontend');
app.use(express.static(FRONTEND_DIR));

// Cung cấp thư mục outputs (chứa các hình ảnh phân tích QGIS)
app.use('/outputs', express.static(path.join(PROJECT_ROOT, 'outputs')));

// API Routes
app.use('/api/housing', housingRoutes);
app.use('/api/amenities', amenitiesRoutes);
app.use('/api/stats', statsRoutes);
app.use('/api/boundaries', boundariesRoutes);

// Endpoint kiểm tra trạng thái hệ thống
app.get('/api/status', (req, res) => {
  res.json({
    status: 'online',
    appName: 'Hanoi Housing GIS Webapp',
    mode: db.isPostgres() ? 'PostgreSQL/PostGIS' : 'File-based GIS Fallback Engine',
    timestamp: new Date().toISOString(),
  });
});

// Khởi chạy server
async function start() {
  await db.initDB();
  app.listen(PORT, () => {
    console.log('====================================================');
    console.log(`[🚀] GIS Webapp Server đang chạy tại: http://localhost:${PORT}`);
    console.log(`[📍] Giao diện trực quan hóa: http://localhost:${PORT}/index.html`);
    console.log(`[⚙️] Chế độ cơ sở dữ liệu: ${db.isPostgres() ? 'PostgreSQL/PostGIS' : 'GeoJSON Fallback (Tự động)'}`);
    console.log('====================================================');
  });
}

start();

module.exports = app;
