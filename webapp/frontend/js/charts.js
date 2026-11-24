/**
 * charts.js
 * Quản lý khởi tạo và render các biểu đồ phân tích kinh tế lượng không gian (Hedonic Price Model)
 * Sử dụng thư viện Chart.js (tương thích cả trực tuyến lẫn offline)
 */

const STATS_API_BASE = (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '3000'))
  ? 'http://localhost:3000'
  : '';

let chartsInitialized = false;
let modelChart = null;
let districtChart = null;
let olsChart = null;

// Dữ liệu mặc định trích xuất từ outputs/tables của đề tài (dự phòng khi API chưa sẵn sàng)
const DEFAULT_STATS_DATA = {
  models: [
    { model: 'OLS (toàn bộ dữ liệu, biến gọn)', n_obs: 121, n_features: 15, r2: 0.407 },
    { model: 'Random Forest (5-fold CV, toàn bộ biến)', n_obs: 121, n_features: 36, r2: 0.092 },
  ],
  districtsSummary: [
    { district: 'Hoàn Kiếm', count: 26, avg_price_per_m2: 525.4, avg_area: 73.2, min_price: 70.9, max_price: 1185.7 },
    { district: 'Ba Đình', count: 50, avg_price_per_m2: 312.9, avg_area: 61.0, min_price: 66.7, max_price: 681.8 },
    { district: 'Đống Đa', count: 45, avg_price_per_m2: 245.2, avg_area: 47.3, min_price: 130.8, max_price: 558.0 },
  ],
  olsCoefficients: [
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
  ],
};

async function initCharts() {
  let data = DEFAULT_STATS_DATA;

  try {
    const res = await fetch(`${STATS_API_BASE}/api/stats`);
    if (res.ok) {
      const serverData = await res.json();
      if (serverData && serverData.models && serverData.models.length > 0) {
        data = serverData;
      }
    }
  } catch (err) {
    console.warn('[Charts] Đang dùng dữ liệu thống kê tích hợp sẵn:', err.message);
  }

  // Luôn render bảng phân tích OLS
  renderOlsTable(data.olsCoefficients);

  // Kiểm tra thư viện Chart.js trước khi vẽ
  if (typeof Chart === 'undefined') {
    console.error('[Charts] Chưa nạp được thư viện Chart.js.');
    return;
  }

  // Khởi tạo các biểu đồ (hủy instance cũ nếu đã có)
  try {
    renderModelComparisonChart(data.models);
    renderDistrictPriceChart(data.districtsSummary);
    renderOlsCoefficientsChart(data.olsCoefficients);
    chartsInitialized = true;
  } catch (err) {
    console.error('[Charts] Lỗi khởi tạo biểu đồ:', err);
  }

  // Kích thước co giãn sau khi container hiển thị
  setTimeout(() => {
    if (modelChart) modelChart.resize();
    if (districtChart) districtChart.resize();
    if (olsChart) olsChart.resize();
  }, 100);
}

// 1. Biểu đồ so sánh R² giữa OLS và Random Forest
function renderModelComparisonChart(models = []) {
  const canvas = document.getElementById('chart-model-comparison');
  if (!canvas) return;

  if (modelChart) {
    modelChart.destroy();
    modelChart = null;
  }

  const items = models && models.length ? models : DEFAULT_STATS_DATA.models;
  const labels = items.map(m => m.model.split('(')[0].trim());
  const r2Values = items.map(m => m.r2);

  modelChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Hệ số xác định R²',
          data: r2Values,
          backgroundColor: ['rgba(37, 99, 235, 0.85)', 'rgba(16, 185, 129, 0.85)'],
          borderColor: ['#1d4ed8', '#059669'],
          borderWidth: 1.5,
          borderRadius: 8,
          barThickness: 48,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => ` R² = ${context.parsed.y} (Giải thích ${(context.parsed.y * 100).toFixed(1)}% biến thiên)`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 0.5,
          title: { display: true, text: 'Hệ số xác định R²', font: { weight: 'bold', size: 11 } },
          grid: { color: '#f1f5f9' },
        },
        x: {
          grid: { display: false },
        },
      },
    },
  });
}

// 2. Biểu đồ giá trung bình theo từng Quận
function renderDistrictPriceChart(districts = []) {
  const canvas = document.getElementById('chart-district-price');
  if (!canvas) return;

  if (districtChart) {
    districtChart.destroy();
    districtChart = null;
  }

  const items = districts && districts.length ? districts : DEFAULT_STATS_DATA.districtsSummary;
  const sorted = [...items].sort((a, b) => b.avg_price_per_m2 - a.avg_price_per_m2);
  const labels = sorted.map(d => d.district);
  const prices = sorted.map(d => d.avg_price_per_m2);

  districtChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Đơn giá TB (triệu VNĐ/m²)',
          data: prices,
          backgroundColor: [
            'rgba(239, 68, 68, 0.85)',
            'rgba(59, 130, 246, 0.85)',
            'rgba(139, 92, 246, 0.85)',
          ],
          borderColor: ['#dc2626', '#2563eb', '#7c3aed'],
          borderWidth: 1.5,
          borderRadius: 8,
          barThickness: 40,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => ` Giá TB: ${Number(context.parsed.y).toLocaleString()} triệu VNĐ/m²`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Triệu VNĐ / m²', font: { weight: 'bold', size: 11 } },
          grid: { color: '#f1f5f9' },
        },
        x: {
          grid: { display: false },
        },
      },
    },
  });
}

// 3. Biểu đồ hệ số hồi quy OLS (OLS Coefficients)
function renderOlsCoefficientsChart(coefficients = []) {
  const canvas = document.getElementById('chart-ols-coefficients');
  if (!canvas) return;

  if (olsChart) {
    olsChart.destroy();
    olsChart = null;
  }

  const items = coefficients && coefficients.length ? coefficients : DEFAULT_STATS_DATA.olsCoefficients;
  const filtered = items.filter(c => !c.variable.includes('const'));
  const labels = filtered.map(c => c.variable);
  const values = filtered.map(c => c.coef);
  const colors = filtered.map(c => (c.sig ? 'rgba(239, 68, 68, 0.85)' : 'rgba(148, 163, 184, 0.85)'));
  const borderColors = filtered.map(c => (c.sig ? '#dc2626' : '#64748b'));

  olsChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Hệ số hồi quy (β)',
          data: values,
          backgroundColor: colors,
          borderColor: borderColors,
          borderWidth: 1,
          borderRadius: 6,
        },
      ],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            afterLabel: context => {
              const item = filtered[context.dataIndex];
              const pStr = item && item.p_val != null ? item.p_val : 'N/A';
              const sigStr = item && item.sig ? 'Ý nghĩa p < 0.05' : 'Không có ý nghĩa';
              const descStr = item && item.desc ? item.desc : '';
              return `p-value: ${pStr} (${sigStr})\nÝ nghĩa: ${descStr}`;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: 'Hệ số ảnh hưởng đến giá/m² (triệu VNĐ)', font: { weight: 'bold', size: 11 } },
          grid: { color: '#f1f5f9' },
        },
        y: {
          grid: { display: false },
        },
      },
    },
  });
}

// 4. Bảng mô tả chi tiết các biến OLS
function renderOlsTable(coefficients = []) {
  const tbody = document.querySelector('#table-ols-summary tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  const items = coefficients && coefficients.length ? coefficients : DEFAULT_STATS_DATA.olsCoefficients;

  items.forEach(c => {
    const tr = document.createElement('tr');
    const pValFormatted = c.p_val != null ? Number(c.p_val).toFixed(3) : 'N/A';
    tr.innerHTML = `
      <td><strong>${c.variable}</strong></td>
      <td><code>${c.coef > 0 ? '+' : ''}${c.coef}</code></td>
      <td><code>${pValFormatted}</code></td>
      <td>
        ${
          c.sig
            ? '<span class="badge-sig"><i class="fa-solid fa-check"></i> Có (p &lt; 0.05)</span>'
            : '<span class="badge-not-sig">Không</span>'
        }
      </td>
      <td>${c.desc || ''}</td>
    `;
    tbody.appendChild(tr);
  });
}

window.initCharts = initCharts;
