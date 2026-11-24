/**
 * gallery.js
 * Quản lý Bộ sưu tập Bản đồ QGIS & Biểu đồ Mô hình
 * Bao gồm:
 * 1. Dữ liệu giải thích chuyên sâu (Thuật toán QGIS, Ý nghĩa không gian, Giá trị kinh tế đô thị)
 * 2. Trình phóng to hình ảnh tương tác Lightbox (Zoom in/out, Kéo rê Pan/Drag, Cuộn chuột)
 * 3. Cửa sổ Modal chi tiết giải nghĩa từng bản đồ
 */

const GALLERY_ITEMS = {
  map_idw: {
    id: 'map_idw',
    title: 'Bản đồ nội suy không gian IDW (Inverse Distance Weighting)',
    badge: 'Nội suy không gian • QGIS Raster',
    image: 'img/map_idw_price.png',
    shortDesc: 'Mô phỏng trường giá nhà liên tục trên địa bàn 3 quận trung tâm Hà Nội từ 121 điểm khảo sát.',
    method: `
      <p>Sử dụng thuật toán <strong>Inverse Distance Weighting (IDW)</strong> trong phần mềm QGIS (Processing Toolbox &gt; Raster Analysis &gt; IDW Interpolation) với tham số lũy thừa khoảng cách <code>p = 2</code>.</p>
      <ul>
        <li><strong>Dữ liệu đầu vào:</strong> 121 điểm nhà đất đã qua tiền xử lý, gán hệ tọa độ phẳng <code>EPSG:32648 (UTM 48N)</code> để bảo toàn khoảng cách đo lường bằng mét.</li>
        <li><strong>Lớp mặt nạ (Mask Layer):</strong> Ranh giới gộp 3 quận (Ba Đình, Đống Đa, Hoàn Kiếm) nhằm cắt bỏ phần ngoài rìa không có dữ liệu (Clipped Mask).</li>
      </ul>
    `,
    meaning: `
      <p>Bản đồ thể hiện sự phân hóa không gian của mặt bằng giá đất:</p>
      <ul>
        <li><strong style="color:#dc2626;">Vùng màu đỏ thẫm / cam rực:</strong> Tập trung dày đặc tại lõi Quận Hoàn Kiếm (khu phố cổ, quanh hồ Hoàn Kiếm và hồ Thiền Quang), với mức giá đạt từ <strong>500 đến trên 1.100 triệu VNĐ/m²</strong>.</li>
        <li><strong style="color:#d97706;">Vùng màu vàng / xanh lục:</strong> Trải rộng ở Quận Ba Đình (quanh đường Liễu Giai, Kim Mã, Đội Cấn) với mức giá dao động ổn định từ <strong>280 đến 400 triệu VNĐ/m²</strong>.</li>
        <li><strong style="color:#2563eb;">Vùng màu xanh lam:</strong> Chiếm ưu thế ở khu vực phía tây nam Quận Đống Đa (Khương Thượng, Trung Liệt, Láng Thượng) với mức giá phổ biến từ <strong>180 đến 260 triệu VNĐ/m²</strong>.</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Bản đồ IDW là bằng chứng trực quan cho <strong>quy luật suy giảm giá đất theo khoảng cách tâm đô thị (Distance Decay from CBD)</strong>. Phương pháp này hỗ trợ cơ quan quản lý và các đơn vị định giá lập bảng giá đất liên tục thay vì các khung giá rời rạc cứng nhắc.</p>
    `,
  },

  gi_hotspot: {
    id: 'gi_hotspot',
    title: 'Phân tích điểm nóng Hot Spot (Getis-Ord Gi*)',
    badge: 'Phân cụm không gian • Thống kê Gi*',
    image: 'img/GI_output.png',
    shortDesc: 'Xác định cụm điểm nóng giá cao và điểm lạnh giá thấp có ý nghĩa thống kê 95% - 99%.',
    method: `
      <p>Thực hiện thống kê không gian <strong>Getis-Ord Gi*</strong> trong QGIS bằng cách so sánh tổng giá trị cục bộ của biến <code>gia_trieu_m2</code> trong bán kính láng giềng so với tổng kỳ vọng của toàn bộ tập dữ liệu.</p>
      <ul>
        <li>Chỉ số tính toán: Điểm chuẩn hóa <code>Z-score</code> và mức ý nghĩa <code>p-value</code> sau khi hiệu chỉnh sai số ngẫu nhiên.</li>
      </ul>
    `,
    meaning: `
      <ul>
        <li><strong style="color:#dc2626;">Cụm Hot Spot (Màu đỏ, Z-score &gt; +2.58, p &lt; 0.01):</strong> Phân bố tập trung trọn vẹn tại Quận Hoàn Kiếm. Đây là nơi các bất động sản giá cao đứng cạnh các bất động sản giá cao khác ở mức tin cậy 99%, tạo thành cực tăng trưởng địa tô đô thị.</li>
        <li><strong style="color:#2563eb;">Cụm Cold Spot (Màu xanh, Z-score &lt; -1.96, p &lt; 0.05):</strong> Cụm điểm lạnh giá thấp hình thành ở phía tây nam quận Đống Đa tiếp giáp quận Thanh Xuân.</li>
        <li><strong>Điểm xám / Không có ý nghĩa (p &gt; 0.05):</strong> Các căn nhà có giá cả phân tán ngẫu nhiên, không chịu hiệu ứng lây lan không gian mạnh mẽ.</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Chứng minh khoa học sự hiện diện của <strong>hiệu ứng láng giềng (Spatial Spillover Effect)</strong>: giá trị bất động sản chịu ảnh hưởng trực tiếp từ đẳng cấp và mức giá của các công trình kế cận, bác bỏ giả định độc lập ngẫu nhiên của các mô hình định giá truyền thống.</p>
    `,
  },

  moran: {
    id: 'moran',
    title: 'Tương quan không gian cục bộ (Local Moran\'s I)',
    badge: 'Anselin Local Moran\'s I • Phân loại LISA',
    image: 'img/moran_output.png',
    shortDesc: 'Đo lường mức độ tương quan không gian, nhận diện các cụm đồng nhất và các điểm dị biệt.',
    method: `
      <p>Sử dụng thuật toán <strong>Anselin Local Moran's I (LISA)</strong> để phân tích sự tương quan giữa giá trị tại một điểm với trung bình trọng số không gian của các điểm xung quanh.</p>
    `,
    meaning: `
      <ul>
        <li><strong style="color:#dc2626;">High-High (HH):</strong> Điểm giá cao nằm giữa khu vực giá cao (trọng tâm Hoàn Kiếm).</li>
        <li><strong style="color:#2563eb;">Low-Low (LL):</strong> Điểm giá thấp nằm giữa khu vực giá thấp (các ngõ nhỏ sâu tại Đống Đa).</li>
        <li><strong style="color:#d946ef;">High-Low (HL - Spatial Outlier):</strong> Bất động sản có giá cao bất thường nằm lọt thỏm trong khu vực giá trung bình thấp (thường là nhà mặt phố kinh doanh nằm trước ngõ chợ).</li>
        <li><strong style="color:#0ea5e9;">Low-High (LH - Spatial Outlier):</strong> Bất động sản giá thấp hiếm hoi nằm giữa khu đất vàng (nhà ngõ cụt quá hẹp hoặc diện tích &lt; 20m²).</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Giúp phát hiện sự không đồng nhất không gian (Spatial Heterogeneity) và lọc ra các <strong>bất động sản dị biệt (Outliers)</strong> để mô hình hồi quy đạt độ tin cậy và không bị nhiễu bởi các trường hợp đặc thù.</p>
    `,
  },

  rf_importance: {
    id: 'rf_importance',
    title: 'Tầm quan trọng của đặc trưng (Random Forest Importance)',
    badge: 'Học máy • Random Forest Regressor',
    image: 'img/rf_feature_importance.png',
    shortDesc: 'Đánh giá mức độ đóng góp của từng biến tiện ích và vị trí đối với dự báo giá nhà.',
    method: `
      <p>Mô hình <strong>Random Forest Regressor</strong> với 100 cây quyết định, huấn luyện trên 36 biến không gian và cấu trúc. Độ quan trọng của biến được đo bằng <em>Mean Decrease in Impurity (Gini Importance)</em> khi phân nhánh các cây.</p>
    `,
    meaning: `
      <ul>
        <li><strong>Top 1:</strong> Biến <code>dien_tich</code> đóng góp mức độ phân loại giá trị lớn nhất.</li>
        <li><strong>Top 2-5:</strong> Mật độ trạm xe buýt <code>count_bus_stop_1000m</code>, khoảng cách bệnh viện <code>dist_hospital_m</code>, khoảng cách chợ <code>dist_marketplace_m</code> và khoảng cách hồ nước <code>dist_water_lakes_m</code>.</li>
        <li><strong>Đặc trưng không gian:</strong> Chỉ số tương quan không gian <code>Z_score</code> xếp thứ hạng quan trọng cao hơn số tầng của ngôi nhà.</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Khẳng định người mua nhà tại trung tâm Hà Nội đặc biệt coi trọng <strong>bán kính tiếp cận các dịch vụ công cộng và giao thông trong phạm vi 1km</strong>, thậm chí vượt trên các tiện ích xa hơn.</p>
    `,
  },

  actual_pred: {
    id: 'actual_pred',
    title: 'Giá thực tế vs Giá dự đoán (Mô hình Hedonic OLS)',
    badge: 'Đánh giá mô hình • Hồi quy OLS',
    image: 'img/actual_vs_predicted.png',
    shortDesc: 'Đường phân giác 45 độ minh họa mức độ tin cậy và phần dư của phương trình Hedonic.',
    method: `
      <p>Đồ thị phân tán (Scatter Plot) so sánh giữa đơn giá thực tế từ bài đăng Chợ Tốt ($Y$) và giá dự đoán bởi phương trình hồi quy tuyến tính Hedonic ($\hat{Y}$). Đường chấm đỏ là đường phân giác lý tưởng <code>Y = X</code>.</p>
    `,
    meaning: `
      <ul>
        <li><strong>Khu vực trung tâm (150 - 450 tr/m²):</strong> Các điểm bám rất sát đường phân giác, phản ánh mô hình OLS giải thích tốt <strong>40.7%</strong> biến động giá thị trường phổ thông.</li>
        <li><strong>Khu vực ngoại biên (&gt; 700 tr/m²):</strong> Các điểm có xu hướng nằm lệch nhẹ phía dưới đường chấm đỏ, cho thấy mô hình có xu hướng dự đoán thận trọng hơn giá rao bán của các căn nhà mặt phố cổ giá siêu cao.</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Phương trình OLS với 15 biến tinh lọc là công cụ tin cậy để <strong>định giá bất động sản hàng loạt (Mass Appraisal)</strong>, giúp phát hiện các bài đăng rao giá "ảo" hoặc quá cao so với mặt bằng tiện ích xung quanh.</p>
    `,
  },

  boxplot: {
    id: 'boxplot',
    title: 'Biểu đồ hộp (Boxplot) Phân bố giá theo Quận',
    badge: 'Thống kê mô tả • Phân tích biến thiên',
    image: 'img/price_by_district_boxplot.png',
    shortDesc: 'Quan sát trung vị, tứ phân vị và các điểm ngoại lai giá nhà ở 3 quận trung tâm.',
    method: `
      <p>Vẽ biểu đồ hộp (Box-and-Whisker Plot) phân rã 121 quan sát theo 3 nhóm địa bàn: Đống Đa, Ba Đình, Hoàn Kiếm; thể hiện giá trị Min, Q1 (25%), Median Q2 (50%), Q3 (75%), Max và Outliers.</p>
    `,
    meaning: `
      <ul>
        <li><strong style="color:#dc2626;">Quận Hoàn Kiếm:</strong> Hộp nằm ở vị trí cao nhất (Trung vị ~480 tr/m²), chiều cao hộp rất dài (từ ~70 tr/m² ngõ nhỏ đến 1.185 tr/m² mặt phố), phản ánh độ phân hóa giàu nghèo và địa tô cực lớn.</li>
        <li><strong style="color:#2563eb;">Quận Ba Đình:</strong> Hộp cân đối quanh trung vị ~310 tr/m², là thị trường nhà ở dân cư chuẩn mực và ổn định.</li>
        <li><strong style="color:#7c3aed;">Quận Đống Đa:</strong> Mức giá tập trung thấp nhất trong 3 quận (Trung vị ~245 tr/m²), xuất hiện các điểm ngoại lai giá cao thuộc trục phố thương mại sầm uất (Xã Đàn, Chùa Bộc, Thái Hà).</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Cung cấp bằng chứng thực nghiệm cho việc chọn Ba Đình làm quận cơ sở trong mô hình OLS và giải thích lý do biến giả <code>khu_vuc_Hoàn Kiếm</code> có hệ số tác động dương khổng lồ (+202.4 tr/m²).</p>
    `,
  },

  ols_coef: {
    id: 'ols_coef',
    title: 'Hệ số hồi quy Hedonic OLS (OLS Coefficients)',
    badge: 'Kinh tế lượng • Ý nghĩa thống kê',
    image: 'img/ols_coefficients.png',
    shortDesc: 'Đánh giá mức độ ảnh hưởng của từng biến tới đơn giá nhà đất, đánh dấu các biến có ý nghĩa thống kê.',
    method: `
      <p>Biểu đồ thanh ngang biểu diễn các hệ số $\\beta$ của mô hình Hedonic OLS. Các thanh màu đỏ đánh dấu biến đạt ý nghĩa thống kê ở mức $p < 0.05$; các thanh màu xám là các biến chưa đạt ý nghĩa thống kê.</p>
    `,
    meaning: `
      <ul>
        <li><strong style="color:#dc2626;">Quận Hoàn Kiếm (&beta; = +202.4, p = 0.011):</strong> Bất động sản cùng điều kiện nằm tại Hoàn Kiếm có giá cao hơn ~202.4 triệu VNĐ/m² so với Ba Đình.</li>
        <li><strong style="color:#dc2626;">Loại nhà Mặt phố (&beta; = +88.0, p = 0.018):</strong> Nhà mặt tiền tạo giá trị thương mại vượt trội so với nhà trong ngõ.</li>
        <li><strong style="color:#dc2626;">Khoảng cách hồ nước (&beta; = -0.209, p = 0.047):</strong> Mỗi 100m cách xa hồ nước làm giá giảm ~20.9 triệu VNĐ/m².</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Khẳng định 3 trụ cột định giá đất trung tâm Hà Nội: <strong>Yếu tố thương hiệu quận di sản</strong>, <strong>Khả năng kinh doanh mặt tiền</strong>, và <strong>Giá trị cảnh quan vi khí hậu hồ nước</strong>.</p>
    `,
  },

  model_r2: {
    id: 'model_r2',
    title: 'So sánh độ phù hợp R² giữa OLS và Random Forest',
    badge: 'So sánh mô hình • Machine Learning vs OLS',
    image: 'img/model_r2_comparison.png',
    shortDesc: 'So sánh năng lực giải thích giá giữa OLS (15 biến gọn) và Random Forest 5-fold CV (36 biến).',
    method: `
      <p>So sánh hệ số xác định $R^2$ giữa mô hình hồi quy tuyến tính OLS (15 biến chọn lọc) và mô hình phi tuyến Random Forest (sử dụng 36 biến kèm kiểm định chéo 5-fold Cross-Validation).</p>
    `,
    meaning: `
      <ul>
        <li><strong>Hồi quy OLS:</strong> Đạt $R^2 = 0.407$, giải thích được hơn 40% sự biến thiên của giá nhà.</li>
        <li><strong>Random Forest:</strong> Đạt $R^2 = 0.092$ trên tập kiểm thử chéo. Nguyên nhân: do cỡ mẫu khảo sát 121 tin tương đối nhỏ, Random Forest với 36 đặc trưng bị phân nhánh quá sâu, dẫn tới hiện tượng quá khớp (overfitting) trên tập huấn luyện nhưng giảm độ chính xác khi dự báo chéo.</li>
      </ul>
    `,
    urbanSignificance: `
      <p>Khẳng định trong các đề tài GIS cỡ mẫu vừa và nhỏ (100 - 300 điểm), mô hình Hedonic OLS truyền thống kết hợp chọn lọc biến không gian vẫn là giải pháp <strong>tối ưu, ổn định và có khả năng giải thích kinh tế rõ ràng hơn</strong> các thuật toán hộp đen phức tạp.</p>
    `,
  },
};

// ================= LIGHTBOX INTERACTIVE ZOOM =================
let currentLightboxScale = 1.0;
let currentLightboxX = 0;
let currentLightboxY = 0;
let isDraggingLightbox = false;
let startDragX = 0;
let startDragY = 0;

function initGallery() {
  const lightboxModal = document.getElementById('image-lightbox-modal');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxViewport = document.getElementById('lightbox-viewport');

  if (!lightboxModal || !lightboxImg || !lightboxViewport) return;

  // Zoom In / Out / Reset
  const btnZoomIn = document.getElementById('btn-lightbox-zoomin');
  const btnZoomOut = document.getElementById('btn-lightbox-zoomout');
  const btnReset = document.getElementById('btn-lightbox-reset');
  const btnClose = document.getElementById('btn-close-lightbox');

  if (btnZoomIn) {
    btnZoomIn.addEventListener('click', e => {
      e.stopPropagation();
      setLightboxZoom(currentLightboxScale + 0.3);
    });
  }

  if (btnZoomOut) {
    btnZoomOut.addEventListener('click', e => {
      e.stopPropagation();
      setLightboxZoom(currentLightboxScale - 0.3);
    });
  }

  if (btnReset) {
    btnReset.addEventListener('click', e => {
      e.stopPropagation();
      resetLightboxTransform();
    });
  }

  if (btnClose) {
    btnClose.addEventListener('click', closeLightbox);
  }

  // Cuộn chuột để phóng to / thu nhỏ
  lightboxViewport.addEventListener('wheel', e => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 0.2 : -0.2;
    setLightboxZoom(currentLightboxScale + delta);
  });

  // Kéo chuột để Pan (di chuyển ảnh khi phóng to)
  lightboxViewport.addEventListener('mousedown', e => {
    if (e.target === lightboxImg || e.target === lightboxViewport) {
      isDraggingLightbox = true;
      startDragX = e.clientX - currentLightboxX;
      startDragY = e.clientY - currentLightboxY;
    }
  });

  window.addEventListener('mousemove', e => {
    if (!isDraggingLightbox) return;
    currentLightboxX = e.clientX - startDragX;
    currentLightboxY = e.clientY - startDragY;
    applyLightboxTransform();
  });

  window.addEventListener('mouseup', () => {
    isDraggingLightbox = false;
  });

  // Đóng khi bấm Escape
  window.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeLightbox();
      closeGalleryDetailModal();
    }
  });

  // Đóng khi click ngoài ảnh
  lightboxModal.addEventListener('click', e => {
    if (e.target === lightboxModal || e.target === lightboxViewport) {
      closeLightbox();
    }
  });
}

function openLightbox(imgSrc, title) {
  const modal = document.getElementById('image-lightbox-modal');
  const img = document.getElementById('lightbox-img');
  const titleEl = document.getElementById('lightbox-title');

  if (!modal || !img) return;

  img.src = imgSrc;
  if (titleEl) titleEl.textContent = title || 'Bản đồ QGIS / Biểu đồ mô hình';

  resetLightboxTransform();
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeLightbox() {
  const modal = document.getElementById('image-lightbox-modal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';
}

function setLightboxZoom(newScale) {
  currentLightboxScale = Math.min(Math.max(newScale, 0.4), 4.5);
  const zoomValEl = document.getElementById('lightbox-zoom-val');
  if (zoomValEl) zoomValEl.textContent = `${Math.round(currentLightboxScale * 100)}%`;
  applyLightboxTransform();
}

function resetLightboxTransform() {
  currentLightboxScale = 1.0;
  currentLightboxX = 0;
  currentLightboxY = 0;
  const zoomValEl = document.getElementById('lightbox-zoom-val');
  if (zoomValEl) zoomValEl.textContent = '100%';
  applyLightboxTransform();
}

function applyLightboxTransform() {
  const img = document.getElementById('lightbox-img');
  if (img) {
    img.style.transform = `translate(${currentLightboxX}px, ${currentLightboxY}px) scale(${currentLightboxScale})`;
  }
}

// ================= MODAL GIẢI THÍCH CHI TIẾT =================
function openGalleryDetail(itemId) {
  const item = GALLERY_ITEMS[itemId];
  if (!item) return;

  const modal = document.getElementById('gallery-detail-modal');
  const titleEl = document.getElementById('gallery-detail-title');
  const bodyEl = document.getElementById('gallery-detail-body');

  if (!modal || !bodyEl) return;

  if (titleEl) {
    titleEl.innerHTML = `<i class="fa-solid fa-map"></i> ${item.title}`;
  }

  bodyEl.innerHTML = `
    <div class="gallery-modal-preview-bar">
      <div class="preview-thumb-wrap">
        <img src="${item.image}" alt="${item.title}" />
        <div>
          <span class="gallery-detail-badge">${item.badge}</span>
          <div class="preview-thumb-info">${item.title}</div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="openLightbox('${item.image}', '${item.title.replace(/'/g, "\\'")}')">
        <i class="fa-solid fa-magnifying-glass-plus"></i> Phóng to bản đồ
      </button>
    </div>

    <div class="detail-section-card">
      <div class="detail-section-title title-method">
        <i class="fa-solid fa-calculator"></i> 1. Phương pháp & Công cụ thực hiện trong QGIS / Python
      </div>
      <div class="detail-section-desc">
        ${item.method}
      </div>
    </div>

    <div class="detail-section-card">
      <div class="detail-section-title title-meaning">
        <i class="fa-solid fa-eye"></i> 2. Ý nghĩa không gian & Cách đọc hiểu bản đồ
      </div>
      <div class="detail-section-desc">
        ${item.meaning}
      </div>
    </div>

    <div class="detail-section-card">
      <div class="detail-section-title title-urban">
        <i class="fa-solid fa-city"></i> 3. Giá trị thực tiễn đối với kinh tế đô thị & Đề tài
      </div>
      <div class="detail-section-desc">
        ${item.urbanSignificance}
      </div>
    </div>
  `;

  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeGalleryDetailModal() {
  const modal = document.getElementById('gallery-detail-modal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';
}

// Gắn sự kiện khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
  initGallery();

  const btnCloseDetail = document.getElementById('btn-close-gallery-detail');
  if (btnCloseDetail) {
    btnCloseDetail.addEventListener('click', closeGalleryDetailModal);
  }

  const detailModal = document.getElementById('gallery-detail-modal');
  if (detailModal) {
    detailModal.addEventListener('click', e => {
      if (e.target === detailModal) closeGalleryDetailModal();
    });
  }
});

// Xuất các hàm ra toàn cục
window.openLightbox = openLightbox;
window.closeLightbox = closeLightbox;
window.openGalleryDetail = openGalleryDetail;
window.closeGalleryDetailModal = closeGalleryDetailModal;
