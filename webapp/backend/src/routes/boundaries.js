/**
 * routes/boundaries.js
 * API Cung cấp ranh giới hành chính 3 quận trung tâm (Ba Đình, Đống Đa, Hoàn Kiếm)
 */

const express = require('express');
const router = express.Router();
const db = require('../db');

// GET /api/boundaries
router.get('/', (req, res) => {
  try {
    const data = db.getBoundaries();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
