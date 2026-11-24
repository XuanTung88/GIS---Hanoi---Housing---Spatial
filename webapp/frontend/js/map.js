/**
 * map.js
 * Quản lý bản đồ số tương tác Leaflet.js
 * Bao gồm: nạp layer nhà, tiện ích OSM, ranh giới 3 quận, overlay ảnh IDW,
 * truy vấn không gian bán kính (ST_DWithin), lọc thuộc tính, và hiển thị popups.
 */

// Global State
let map = null;
let currentBasemap = null;
const baseTileLayers = {};

let housingLayerGroup = null;
let boundariesLayerGroup = null;
let idwImageOverlay = null;
const amenityLayerGroups = {};

// Dữ liệu bộ nhớ client
let allHousingFeatures = [];
let currentSpatialCenter = null;
let currentSpatialRadius = 500;
let spatialBufferCircle = null;
let spatialCenterMarker = null;
let isSpatialModeActive = false;

// Tọa độ bounding box ảnh IDW (từ extent QGIS xuất)
const IDW_BOUNDS = [
  [20.99, 105.80],
  [21.04, 105.86],
];

const MAP_API_BASE = (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '3000'))
  ? 'http://localhost:3000'
  : '';

// Khởi chạy khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  checkBackendStatus();
  setupUIEvents();
  loadAllLayers();
});

// 1. KHỞI TẠO BẢN ĐỒ LEAFLET
function initMap() {
  // Tâm 3 quận trung tâm Hà Nội (Ba Đình, Đống Đa, Hoàn Kiếm)
  map = L.map('map', {
    center: [21.025, 105.835],
    zoom: 14,
    minZoom: 11,
    maxZoom: 18,
    zoomControl: false,
  });

  // Đặt thanh zoom góc dưới bên phải
  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // Định nghĩa các bản đồ nền
  baseTileLayers.osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  });

  baseTileLayers.positron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CartoDB Positron',
  });

  baseTileLayers.dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CartoDB Dark Matter',
  });

  baseTileLayers.satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; Esri World Imagery',
  });

  // Mặc định dùng OpenStreetMap
  currentBasemap = baseTileLayers.osm;
  currentBasemap.addTo(map);

  // Khởi tạo các nhóm layer
  housingLayerGroup = L.layerGroup().addTo(map);
  boundariesLayerGroup = L.layerGroup().addTo(map);

  // Khởi tạo ảnh Overlay IDW (nội suy từ QGIS)
  idwImageOverlay = L.imageOverlay('img/map_idw_price.png', IDW_BOUNDS, {
    opacity: 0.6,
    interactive: false,
  }).addTo(map);

  // Lắng nghe di chuột để hiển thị tọa độ góc dưới
  map.on('mousemove', e => {
    const coordsEl = document.getElementById('map-coords-display');
    if (coordsEl) {
      coordsEl.textContent = `${e.latlng.lat.toFixed(4)}° N, ${e.latlng.lng.toFixed(4)}° E`;
    }
  });

  // Lắng nghe click bản đồ cho tính năng truy vấn bán kính
  map.on('click', handleMapClick);
}

// 2. NẠP TOÀN BỘ DỮ LIỆU
async function loadAllLayers() {
  await Promise.all([
    loadBoundaries(),
    loadHousingData(),
    loadAmenities(),
  ]);
}

// Kiểm tra trạng thái backend
async function checkBackendStatus() {
  try {
    const res = await fetch(`${MAP_API_BASE}/api/status`);
    const data = await res.json();
    const modeEl = document.getElementById('backend-mode');
    if (modeEl) {
      modeEl.textContent = data.mode.includes('PostgreSQL') ? 'PostgreSQL + PostGIS' : 'GIS Engine (Fallback)';
      modeEl.title = `Chế độ: ${data.mode}`;
    }
  } catch (e) {
    const modeEl = document.getElementById('backend-mode');
    if (modeEl) modeEl.textContent = 'Lỗi kết nối API';
  }
}

// 3. NẠP RANH GIỚI 3 QUẬN
async function loadBoundaries() {
  try {
    const res = await fetch(`${MAP_API_BASE}/api/boundaries`);
    const data = await res.json();

    boundariesLayerGroup.clearLayers();

    L.geoJSON(data, {
      style: feature => {
        const name = feature.properties.name || '';
        let color = '#2563eb';
        if (name.includes('Hoàn Kiếm')) color = '#dc2626';
        if (name.includes('Ba Đình')) color = '#059669';
        if (name.includes('Đống Đa')) color = '#7c3aed';

        return {
          color: color,
          weight: 2.5,
          opacity: 0.8,
          fillColor: color,
          fillOpacity: 0.05,
          dashArray: '6, 6',
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const name = p.name || 'Ranh giới quận';
        const nameEn = p['name:en'] || '';
        const pop = p.population ? `Dân số: ${parseInt(p.population).toLocaleString()} người` : '';

        layer.bindTooltip(`<strong>${name}</strong><br/>${nameEn}<br/>${pop}`, {
          sticky: true,
          className: 'boundary-tooltip',
        });
      },
    }).addTo(boundariesLayerGroup);
  } catch (err) {
    console.error('Lỗi tải ranh giới 3 quận:', err);
  }
}

// 4. NẠP DỮ LIỆU NHÀ Ở
async function loadHousingData(queryString = '') {
  try {
    const url = `${MAP_API_BASE}/api/housing${queryString ? '?' + queryString : ''}`;
    const res = await fetch(url);
    const data = await res.json();

    allHousingFeatures = data.features || [];
    renderHousingMarkers(allHousingFeatures);

    // Cập nhật số lượng hiển thị
    const countBadge = document.getElementById('housing-count-badge');
    const filterCount = document.getElementById('filter-count');
    if (countBadge) countBadge.textContent = allHousingFeatures.length;
    if (filterCount) filterCount.textContent = allHousingFeatures.length;
  } catch (err) {
    console.error('Lỗi tải dữ liệu nhà ở:', err);
  }
}

// Màu sắc phân cấp theo giá đất (triệu/m²)
function getPriceColor(price) {
  if (!price || isNaN(price)) return '#94a3b8';
  if (price < 200) return '#10b981'; // Xanh lá: < 200 tr/m²
  if (price <= 300) return '#3b82f6'; // Xanh lam: 200 - 300 tr/m²
  if (price <= 450) return '#f59e0b'; // Cam: 300 - 450 tr/m²
  return '#ef4444'; // Đỏ: > 450 tr/m²
}

// Vẽ các điểm nhà lên bản đồ
function renderHousingMarkers(features) {
  housingLayerGroup.clearLayers();

  features.forEach(feat => {
    const p = feat.properties;
    const [lon, lat] = feat.geometry.coordinates;
    const color = getPriceColor(p.gia_trieu_m2);

    const marker = L.circleMarker([lat, lon], {
      radius: 6.5,
      fillColor: color,
      color: '#ffffff',
      weight: 1.5,
      opacity: 1,
      fillOpacity: 0.88,
    });

    // Tạo popup chi tiết
    marker.bindPopup(buildHousingPopupContent(p), {
      className: 'custom-house-popup',
      maxWidth: 300,
    });

    marker.on('click', () => {
      marker.openPopup();
    });

    housingLayerGroup.addLayer(marker);
  });
}

// Tạo HTML nội dung Popup cho nhà
function buildHousingPopupContent(p) {
  const priceTy = p.gia_ty ? `${p.gia_ty.toFixed(1)} tỷ` : (p.gia ? `${(p.gia / 1e9).toFixed(1)} tỷ` : 'Thương lượng');
  const priceM2 = p.gia_trieu_m2 ? `${Math.round(p.gia_trieu_m2).toLocaleString()} tr/m²` : 'N/A';
  const moranText = p.Z_score != null ? `Z-Score: ${p.Z_score.toFixed(2)} (p = ${p.p_value ? p.p_value.toFixed(3) : 'N/A'})` : 'Chưa có phân cụm';

  return `
    <div class="popup-container">
      <div class="popup-header">
        <span class="popup-district-badge">${p.khu_vuc || 'Hà Nội'} • ${p.loai_nha || 'Nhà riêng'}</span>
        <div class="popup-price">${priceTy}</div>
        <div class="popup-price-sub">${priceM2}</div>
      </div>
      <div class="popup-body">
        <div class="popup-specs">
          <div class="spec-item"><i class="fa-solid fa-ruler-combined"></i> DT: <strong>${p.dien_tich || 'N/A'} m²</strong></div>
          <div class="spec-item"><i class="fa-solid fa-layer-group"></i> Số tầng: <strong>${p.so_tang || 1} tầng</strong></div>
        </div>
        <div class="popup-address">
          <i class="fa-solid fa-location-dot"></i> ${p.dia_chi || 'Trung tâm Hà Nội'}
        </div>
        <div class="popup-spatial-stats">
          <div><i class="fa-solid fa-water"></i> Cách hồ gần nhất: <strong>${p.dist_water_lakes_m || 'N/A'} m</strong></div>
          <div><i class="fa-solid fa-chart-simple"></i> Local Moran's I: <strong>${moranText}</strong></div>
        </div>
        <div class="popup-actions">
          <button class="popup-btn popup-btn-detail" onclick="openHouseDetailModal('${p.id}')">
            <i class="fa-solid fa-eye"></i> Chi tiết đầy đủ
          </button>
          ${
            p.url
              ? `<a href="${p.url}" target="_blank" class="popup-btn popup-btn-ext"><i class="fa-solid fa-arrow-up-right-from-square"></i> Xem tin</a>`
              : ''
          }
        </div>
      </div>
    </div>
  `;
}

// 5. NẠP CÁC LỚP TIỆN ÍCH OSM
async function loadAmenities() {
  try {
    const res = await fetch(`${MAP_API_BASE}/api/amenities`);
    const amenityMeta = await res.json();

    const container = document.getElementById('amenities-checkbox-list');
    if (!container) return;
    container.innerHTML = '';

    for (const meta of amenityMeta) {
      // Tạo layer group riêng cho loại tiện ích này
      const group = L.layerGroup();
      amenityLayerGroups[meta.type] = {
        layer: group,
        meta: meta,
        loaded: false,
        visible: false,
      };

      // Tạo phần tử giao diện checkbox
      const row = document.createElement('div');
      row.className = 'amenity-row';
      row.innerHTML = `
        <div class="amenity-left">
          <span class="amenity-icon" style="color: ${meta.color}">
            <i class="fa-solid fa-${meta.icon}"></i>
          </span>
          <label class="checkbox-label" for="toggle-amenity-${meta.type}">
            <input type="checkbox" id="toggle-amenity-${meta.type}" data-amenity="${meta.type}" />
            <span>${meta.nameVi}</span>
          </label>
        </div>
        <span class="badge" id="badge-${meta.type}">${meta.count}</span>
      `;
      container.appendChild(row);

      // Bắt sự kiện bật tắt checkbox
      const checkbox = row.querySelector('input');
      checkbox.addEventListener('change', async e => {
        await toggleAmenityLayer(meta.type, e.target.checked);
      });
    }
  } catch (err) {
    console.error('Lỗi nạp danh sách tiện ích:', err);
  }
}

// Bật / tắt layer tiện ích theo yêu cầu
async function toggleAmenityLayer(type, show) {
  const item = amenityLayerGroups[type];
  if (!item) return;

  if (show) {
    if (!item.loaded) {
      // Tải dữ liệu GeoJSON từ API
      const res = await fetch(`${MAP_API_BASE}/api/amenities/${type}`);
      const data = await res.json();

      L.geoJSON(data, {
        pointToLayer: (feature, latlng) => {
          return L.circleMarker(latlng, {
            radius: 5,
            fillColor: item.meta.color,
            color: '#ffffff',
            weight: 1,
            fillOpacity: 0.8,
          });
        },
        style: feature => {
          return {
            color: item.meta.color,
            fillColor: item.meta.color,
            fillOpacity: 0.35,
            weight: 1.5,
          };
        },
        onEachFeature: (feature, layer) => {
          const name = feature.properties.name || item.meta.nameVi;
          layer.bindTooltip(`<strong>${name}</strong><br/><em>${item.meta.nameVi}</em>`, { sticky: true });
        },
      }).addTo(item.layer);

      item.loaded = true;
    }
    item.layer.addTo(map);
    item.visible = true;
  } else {
    map.removeLayer(item.layer);
    item.visible = false;
  }
}

// 6. TRUY VẤN BÁN KÍNH KHÔNG GIAN (SPATIAL BUFFER QUERY)
function handleMapClick(e) {
  if (!isSpatialModeActive) return;

  const lat = e.latlng.lat;
  const lon = e.latlng.lng;
  executeSpatialQuery(lat, lon, currentSpatialRadius);
}

async function executeSpatialQuery(lat, lon, radius) {
  currentSpatialCenter = { lat, lon };

  // Xóa hình tròn đệm cũ
  if (spatialBufferCircle) map.removeLayer(spatialBufferCircle);
  if (spatialCenterMarker) map.removeLayer(spatialCenterMarker);

  // Tạo vòng tròn đệm bán kính
  spatialBufferCircle = L.circle([lat, lon], {
    radius: radius,
    color: '#8b5cf6',
    fillColor: '#8b5cf6',
    fillOpacity: 0.18,
    weight: 2,
    dashArray: '6, 6',
  }).addTo(map);

  // Marker tâm điểm
  spatialCenterMarker = L.marker([lat, lon], {
    icon: L.divIcon({
      className: 'spatial-center-icon',
      html: '<div style="background:#8b5cf6; width:16px; height:16px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 8px rgba(139,92,246,0.6)"></div>',
      iconSize: [16, 16],
      iconAnchor: [8, 8],
    }),
  }).addTo(map);

  // Gọi API backend (hỗ trợ ST_DWithin của PostGIS hoặc Haversine Fallback)
  try {
    const res = await fetch(`${MAP_API_BASE}/api/housing/nearby?lat=${lat}&lon=${lon}&radius=${radius}`);
    const result = await res.json();

    displaySpatialResults(result);
  } catch (err) {
    console.error('Lỗi truy vấn ST_DWithin:', err);
  }
}

function displaySpatialResults(result) {
  const card = document.getElementById('spatial-results-card');
  if (!card) return;

  card.classList.remove('hidden');

  const summary = result.summary || {};
  document.getElementById('res-total-houses').textContent = summary.total || 0;
  document.getElementById('res-avg-price').textContent = summary.avg_price_per_m2 ? Math.round(summary.avg_price_per_m2) : 0;
  document.getElementById('res-min-price').textContent = summary.min_price_per_m2 ? Math.round(summary.min_price_per_m2) : 0;
  document.getElementById('res-max-price').textContent = summary.max_price_per_m2 ? Math.round(summary.max_price_per_m2) : 0;

  // Render danh sách nhà trong buffer
  const listEl = document.getElementById('spatial-house-list');
  listEl.innerHTML = '';

  const features = result.features || [];
  if (features.length === 0) {
    listEl.innerHTML = '<div style="font-size:11px; color:#94a3b8; text-align:center; padding:10px;">Không có căn nhà nào trong bán kính này.</div>';
    return;
  }

  features.forEach(f => {
    const p = f.properties;
    const cardEl = document.createElement('div');
    cardEl.className = 'house-micro-card';
    cardEl.innerHTML = `
      <div class="house-micro-header">
        <span>${p.gia_ty ? p.gia_ty.toFixed(1) + ' tỷ' : 'N/A'} (${Math.round(p.gia_trieu_m2)} tr/m²)</span>
        <span style="color:#8b5cf6;">cách ${Math.round(p.distance_m)}m</span>
      </div>
      <div class="house-micro-addr">${p.dia_chi || p.khu_vuc} • ${p.dien_tich}m²</div>
    `;

    cardEl.addEventListener('click', () => {
      const [fLon, fLat] = f.geometry.coordinates;
      map.setView([fLat, fLon], 16);
      openHouseDetailModal(p.id);
    });

    listEl.appendChild(cardEl);
  });
}

function clearSpatialQuery() {
  if (spatialBufferCircle) map.removeLayer(spatialBufferCircle);
  if (spatialCenterMarker) map.removeLayer(spatialCenterMarker);
  spatialBufferCircle = null;
  spatialCenterMarker = null;
  currentSpatialCenter = null;

  const card = document.getElementById('spatial-results-card');
  if (card) card.classList.add('hidden');
}

// 7. SỰ KIỆN GIAO DIỆN NGƯỜI DÙNG (UI EVENTS)
function setupUIEvents() {
  // Chuyển đổi màn hình chính (Map / Analytics / QGIS Gallery)
  const btnMap = document.getElementById('btn-view-map');
  const btnAnalytics = document.getElementById('btn-view-analytics');
  const btnGallery = document.getElementById('btn-view-gallery');

  const viewMap = document.getElementById('view-map');
  const viewAnalytics = document.getElementById('view-analytics');
  const viewGallery = document.getElementById('view-gallery');

  function switchView(target) {
    if (btnMap) btnMap.classList.toggle('active', target === 'map');
    if (btnAnalytics) btnAnalytics.classList.toggle('active', target === 'analytics');
    if (btnGallery) btnGallery.classList.toggle('active', target === 'gallery');

    if (viewMap) viewMap.classList.toggle('active', target === 'map');
    if (viewAnalytics) viewAnalytics.classList.toggle('active', target === 'analytics');
    if (viewGallery) viewGallery.classList.toggle('active', target === 'gallery');

    if (target === 'map') {
      if (map) setTimeout(() => map.invalidateSize(), 150);
    } else if (target === 'analytics') {
      if (window.initCharts) {
        window.initCharts();
      }
    }
  }

  btnMap.addEventListener('click', () => switchView('map'));
  btnAnalytics.addEventListener('click', () => switchView('analytics'));
  btnGallery.addEventListener('click', () => switchView('gallery'));

  // Chuyển tab trong Sidebar
  const tabBtns = document.querySelectorAll('.sidebar-tabs .tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Chuyển đổi bản đồ nền
  const basemapCards = document.querySelectorAll('.basemap-card');
  basemapCards.forEach(card => {
    card.addEventListener('click', () => {
      basemapCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');

      const type = card.dataset.basemap;
      if (baseTileLayers[type]) {
        map.removeLayer(currentBasemap);
        currentBasemap = baseTileLayers[type];
        currentBasemap.addTo(map);
      }
    });
  });

  // Toggle lớp nhà
  const toggleHousing = document.getElementById('toggle-housing');
  if (toggleHousing) {
    toggleHousing.addEventListener('change', e => {
      if (e.target.checked) housingLayerGroup.addTo(map);
      else map.removeLayer(housingLayerGroup);
    });
  }

  // Toggle lớp ranh giới 3 quận
  const toggleBoundaries = document.getElementById('toggle-boundaries');
  if (toggleBoundaries) {
    toggleBoundaries.addEventListener('change', e => {
      if (e.target.checked) boundariesLayerGroup.addTo(map);
      else map.removeLayer(boundariesLayerGroup);
    });
  }

  // Toggle ảnh IDW nội suy và thanh trượt độ mờ
  const toggleIdw = document.getElementById('toggle-idw');
  const idwOpacity = document.getElementById('idw-opacity');
  const idwOpacityVal = document.getElementById('idw-opacity-val');

  if (toggleIdw) {
    toggleIdw.addEventListener('change', e => {
      if (e.target.checked) idwImageOverlay.addTo(map);
      else map.removeLayer(idwImageOverlay);
    });
  }

  if (idwOpacity) {
    idwOpacity.addEventListener('input', e => {
      const val = e.target.value;
      if (idwOpacityVal) idwOpacityVal.textContent = `${val}%`;
      idwImageOverlay.setOpacity(val / 100);
    });
  }

  // Bật/tắt tất cả tiện ích cùng lúc
  const btnToggleAllAmenities = document.getElementById('btn-toggle-all-amenities');
  if (btnToggleAllAmenities) {
    let allOn = false;
    btnToggleAllAmenities.addEventListener('click', async () => {
      allOn = !allOn;
      btnToggleAllAmenities.textContent = allOn ? 'Tắt hết' : 'Tất cả';
      const checkboxes = document.querySelectorAll('#amenities-checkbox-list input[type="checkbox"]');
      for (const cb of checkboxes) {
        cb.checked = allOn;
        await toggleAmenityLayer(cb.dataset.amenity, allOn);
      }
    });
  }

  // Bộ lọc tìm kiếm nhà
  const btnApplyFilter = document.getElementById('btn-apply-filter');
  const btnResetFilter = document.getElementById('btn-reset-filter');

  if (btnApplyFilter) {
    btnApplyFilter.addEventListener('click', () => {
      const district = document.getElementById('filter-district').value;
      const houseType = document.getElementById('filter-housetype').value;
      const minPrice = document.getElementById('filter-min-price').value;
      const maxPrice = document.getElementById('filter-max-price').value;
      const minArea = document.getElementById('filter-min-area').value;
      const maxArea = document.getElementById('filter-max-area').value;

      const params = new URLSearchParams();
      if (district && district !== 'Tất cả') params.append('district', district);
      if (houseType && houseType !== 'Tất cả') params.append('houseType', houseType);
      if (minPrice) params.append('minPrice', minPrice);
      if (maxPrice) params.append('maxPrice', maxPrice);
      if (minArea) params.append('minArea', minArea);
      if (maxArea) params.append('maxArea', maxArea);

      loadHousingData(params.toString());
    });
  }

  if (btnResetFilter) {
    btnResetFilter.addEventListener('click', () => {
      document.getElementById('filter-district').value = 'Tất cả';
      document.getElementById('filter-housetype').value = 'Tất cả';
      document.getElementById('filter-min-price').value = '';
      document.getElementById('filter-max-price').value = '';
      document.getElementById('filter-min-area').value = '';
      document.getElementById('filter-max-area').value = '';

      loadHousingData();
    });
  }

  // Kích hoạt chế độ chọn tâm truy vấn bán kính
  const btnActivateSpatial = document.getElementById('btn-activate-spatial');
  const spatialRadiusSlider = document.getElementById('spatial-radius-slider');
  const spatialRadiusVal = document.getElementById('spatial-radius-val');
  const btnClearSpatial = document.getElementById('btn-clear-spatial');

  if (btnActivateSpatial) {
    btnActivateSpatial.addEventListener('click', () => {
      isSpatialModeActive = !isSpatialModeActive;
      if (isSpatialModeActive) {
        btnActivateSpatial.classList.add('active');
        btnActivateSpatial.innerHTML = '<i class="fa-solid fa-check"></i> <span>Đang chờ click chọn tâm...</span>';
        document.getElementById('map').style.cursor = 'crosshair';
      } else {
        btnActivateSpatial.classList.remove('active');
        btnActivateSpatial.innerHTML = '<i class="fa-solid fa-crosshairs"></i> <span>Kích hoạt chế độ chọn tâm</span>';
        document.getElementById('map').style.cursor = '';
      }
    });
  }

  if (spatialRadiusSlider) {
    spatialRadiusSlider.addEventListener('input', e => {
      currentSpatialRadius = parseInt(e.target.value, 10);
      if (spatialRadiusVal) spatialRadiusVal.textContent = `${currentSpatialRadius} m`;

      if (currentSpatialCenter) {
        executeSpatialQuery(currentSpatialCenter.lat, currentSpatialCenter.lon, currentSpatialRadius);
      }
    });
  }

  // Quick picks bán kính
  const pillBtns = document.querySelectorAll('.radius-quick-picks .pill-btn');
  pillBtns.forEach(p => {
    p.addEventListener('click', () => {
      pillBtns.forEach(x => x.classList.remove('active'));
      p.classList.add('active');

      const rad = parseInt(p.dataset.radius, 10);
      currentSpatialRadius = rad;
      if (spatialRadiusSlider) spatialRadiusSlider.value = rad;
      if (spatialRadiusVal) spatialRadiusVal.textContent = `${rad} m`;

      if (currentSpatialCenter) {
        executeSpatialQuery(currentSpatialCenter.lat, currentSpatialCenter.lon, currentSpatialRadius);
      }
    });
  });

  if (btnClearSpatial) {
    btnClearSpatial.addEventListener('click', clearSpatialQuery);
  }

  // Modals
  setupModals();
}

// 8. CỬA SỔ CHI TIẾT VÀ TRỢ GIÚP (MODALS)
function setupModals() {
  const houseModal = document.getElementById('house-detail-modal');
  const btnCloseHouseModal = document.getElementById('btn-close-house-modal');
  if (btnCloseHouseModal) {
    btnCloseHouseModal.addEventListener('click', () => houseModal.classList.remove('active'));
  }

  const helpModal = document.getElementById('help-modal');
  const btnHelp = document.getElementById('btn-help-modal');
  const btnCloseHelp = document.getElementById('btn-close-help-modal');

  if (btnHelp) {
    btnHelp.addEventListener('click', () => helpModal.classList.add('active'));
  }
  if (btnCloseHelp) {
    btnCloseHelp.addEventListener('click', () => helpModal.classList.remove('active'));
  }

  // Đóng modal khi click ra ngoài
  window.addEventListener('click', e => {
    if (e.target === houseModal) houseModal.classList.remove('active');
    if (e.target === helpModal) helpModal.classList.remove('active');
  });
}

// Mở modal hiển thị chi tiết 1 căn nhà
function openHouseDetailModal(houseId) {
  const house = allHousingFeatures.find(f => String(f.properties.id) === String(houseId));
  if (!house) return;

  const p = house.properties;
  const modal = document.getElementById('house-detail-modal');
  const titleEl = document.getElementById('modal-house-title');
  const bodyEl = document.getElementById('modal-house-body');

  titleEl.innerHTML = `<i class="fa-solid fa-house"></i> Bất động sản ID: #${p.id}`;

  const priceTy = p.gia_ty ? `${p.gia_ty.toFixed(1)} tỷ VNĐ` : 'Thương lượng';
  const priceM2 = p.gia_trieu_m2 ? `${Math.round(p.gia_trieu_m2).toLocaleString()} triệu VNĐ / m²` : 'N/A';

  bodyEl.innerHTML = `
    <div style="margin-bottom: 16px;">
      <span class="popup-district-badge" style="background:#2563eb; color:#fff; font-size:11px; padding:3px 8px;">
        ${p.khu_vuc} • Loại: ${p.loai_nha}
      </span>
      <h2 style="font-size:22px; font-weight:800; color:#2563eb; margin: 8px 0 2px 0;">${priceTy}</h2>
      <div style="font-size:13px; color:#64748b; font-weight:600;">Đơn giá: ${priceM2}</div>
    </div>

    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:14px; font-size:12px;">
      <div><strong>Địa chỉ:</strong> ${p.dia_chi || 'Trung tâm Hà Nội'}</div>
      <div style="margin-top:4px;"><strong>Diện tích:</strong> ${p.dien_tich || 'N/A'} m² • <strong>Số tầng:</strong> ${p.so_tang || 1} tầng</div>
    </div>

    <h4 style="font-size:13px; font-weight:700; margin-bottom:8px; color:#0f172a;">
      <i class="fa-solid fa-route" style="color:#2563eb;"></i> Khoảng cách đến tiện ích gần nhất (Mô hình Hedonic):
    </h4>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:12px; margin-bottom:16px;">
      <div style="background:#fff; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px;">
        <i class="fa-solid fa-water" style="color:#3498db;"></i> Hồ nước: <strong>${p.dist_water_lakes_m || 'N/A'} m</strong>
      </div>
      <div style="background:#fff; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px;">
        <i class="fa-solid fa-store" style="color:#d35400;"></i> Chợ dân sinh: <strong>${p.dist_marketplace_m || 'N/A'} m</strong>
      </div>
      <div style="background:#fff; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px;">
        <i class="fa-solid fa-graduation-cap" style="color:#e67e22;"></i> Trường học: <strong>${p.dist_school_m || 'N/A'} m</strong>
      </div>
      <div style="background:#fff; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px;">
        <i class="fa-solid fa-hospital" style="color:#e74c3c;"></i> Bệnh viện: <strong>${p.dist_hospital_m || 'N/A'} m</strong>
      </div>
      <div style="background:#fff; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px;">
        <i class="fa-solid fa-tree" style="color:#27ae60;"></i> Công viên: <strong>${p.dist_park_m || 'N/A'} m</strong>
      </div>
      <div style="background:#fff; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px;">
        <i class="fa-solid fa-bus" style="color:#2980b9;"></i> Điểm xe buýt: <strong>${p.dist_bus_stop_m || 'N/A'} m</strong>
      </div>
    </div>

    <h4 style="font-size:13px; font-weight:700; margin-bottom:8px; color:#0f172a;">
      <i class="fa-solid fa-chart-line" style="color:#8b5cf6;"></i> Thống kê tương quan không gian (Spatial Autocorrelation):
    </h4>
    <div style="background:#f5f3ff; border:1px solid #ddd6fe; border-radius:8px; padding:10px; font-size:12px; margin-bottom:16px;">
      <div>• <strong>Local Moran's I Z-score:</strong> ${p.Z_score != null ? p.Z_score.toFixed(4) : 'N/A'}</div>
      <div>• <strong>Mức ý nghĩa p-value:</strong> ${p.p_value != null ? p.p_value.toFixed(4) : 'N/A'}</div>
      <div>• <strong>Hiệu chỉnh FDR (False Discovery Rate):</strong> ${p.p_fdr != null ? p.p_fdr.toFixed(4) : 'N/A'}</div>
    </div>

    ${
      p.url
        ? `<div style="text-align:right;">
             <a href="${p.url}" target="_blank" class="btn btn-primary">
               <i class="fa-solid fa-arrow-up-right-from-square"></i> Mở bài đăng gốc trên Chợ Tốt / Nhà Tốt
             </a>
           </div>`
        : ''
    }
  `;

  modal.classList.add('active');
}

window.openHouseDetailModal = openHouseDetailModal;
