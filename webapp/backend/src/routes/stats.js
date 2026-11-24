/**
 * routes/stats.js
 * API Cung cấp dữ liệu thống kê, so sánh mô hình hồi quy Hedonic (OLS vs Random Forest)
 */

const express = require('express');
const router = express.Router();
const db = require('../db');

// GET /api/stats
router.get('/', (req, res) => {
  try {
    const stats = db.getStats();
    res.json(stats);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
