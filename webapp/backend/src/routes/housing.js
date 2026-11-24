/**
 * routes/housing.js
 * API Quản lý dữ liệu nhà ở và truy vấn không gian bán kính
 */

const express = require('express');
const router = express.Router();
const db = require('../db');

// GET /api/housing/nearby?lat=&lon=&radius=
// Đặt trước /:id để tránh trùng khớp route
router.get('/nearby', async (req, res) => {
  try {
    const { lat, lon, radius = 500 } = req.query;

    if (!lat || !lon) {
      return res.status(400).json({
        error: 'Thiếu tham số bắt buộc: lat và lon. Ví dụ: /api/housing/nearby?lat=21.025&lon=105.83&radius=500',
      });
    }

    const data = await db.getNearbyHousing(lat, lon, radius);
    res.json(data);
  } catch (err) {
    console.error('Lỗi truy vấn nearby:', err);
    res.status(500).json({ error: err.message });
  }
});

// GET /api/housing
// Lấy toàn bộ danh sách nhà, hỗ trợ lọc theo quận, khoảng giá, diện tích, loại nhà
router.get('/', async (req, res) => {
  try {
    const { district, houseType, minPrice, maxPrice, minArea, maxArea } = req.query;
    const data = await db.getHousing({ district, houseType, minPrice, maxPrice, minArea, maxArea });
    res.json(data);
  } catch (err) {
    console.error('Lỗi truy vấn housing:', err);
    res.status(500).json({ error: err.message });
  }
});

// GET /api/housing/:id
// Lấy chi tiết 1 căn nhà theo ID
router.get('/:id', async (req, res) => {
  try {
    const data = await db.getHousing({});
    const house = data.features.find(f => String(f.properties.id) === String(req.params.id));
    if (!house) {
      return res.status(404).json({ error: `Không tìm thấy tin đăng với id ${req.params.id}` });
    }
    res.json(house);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
