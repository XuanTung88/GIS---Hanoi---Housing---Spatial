/**
 * routes/amenities.js
 * API Quản lý dữ liệu các lớp tiện ích OpenStreetMap (Trường học, Bệnh viện, Công viên, v.v.)
 */

const express = require('express');
const router = express.Router();
const db = require('../db');

// GET /api/amenities
// Danh sách các loại tiện ích có sẵn kèm metadata
router.get('/', async (req, res) => {
  try {
    const meta = db.getAmenityMeta();
    const result = await Promise.all(
      meta.map(async m => {
        const layer = await db.getAmenities(m.type);
        return {
          ...m,
          count: layer.features ? layer.features.length : 0,
        };
      })
    );
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/amenities/:type
// Lấy layer GeoJSON của một loại tiện ích cụ thể (vd: school, hospital, park, bus_stop...)
router.get('/:type', async (req, res) => {
  try {
    const { type } = req.params;
    const data = await db.getAmenities(type);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
