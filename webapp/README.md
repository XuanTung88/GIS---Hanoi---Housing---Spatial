# Module Web GIS: Trực Quan Hóa & Định Giá Nhà Ở Hà Nội

Module Webapp mở rộng cho Đề tài GIS: **Phân tích không gian và mô hình Hedonic định giá bất động sản tại 3 quận trung tâm Hà Nội (Ba Đình, Đống Đa, Hoàn Kiếm)**.

---

## 1. Điểm nổi bật & Nâng cấp của hệ thống

- **Kiến trúc linh hoạt (Dual-Mode Engine):**
  - **Chế độ PostGIS Native:** Tự động kết nối PostgreSQL + PostGIS, sử dụng các hàm không gian tiêu chuẩn (`ST_DWithin`, `ST_Distance`, `ST_AsGeoJSON`, `ST_MakePoint`).
  - **Chế độ File-based GIS Fallback:** Nếu chưa cài đặt PostgreSQL hoặc DB offline, hệ thống tự động kích hoạt bộ xử lý không gian nội bộ (Haversine distance & GeoJSON), giúp webapp **chạy được ngay lập tức 100% không lo lỗi kết nối**.
- **Bản đồ số tương tác Leaflet.js:**
  - 4 lớp bản đồ nền chuyên nghiệp: OpenStreetMap, CartoDB Positron, CartoDB Dark Matter, Vệ tinh Esri.
  - Phân cấp màu sắc 121 điểm nhà theo 4 mức giá đất (triệu VNĐ/m²).
  - 7 lớp tiện ích OpenStreetMap (Trường học, Bệnh viện, Công viên, Siêu thị, Chợ, Trạm xe buýt, Hồ nước) với khả năng bật/tắt độc lập.
  - Ranh giới hành chính 3 quận trung tâm (Ba Đình, Đống Đa, Hoàn Kiếm).
  - Lớp phủ Raster nội suy IDW (Inverse Distance Weighting) xuất từ QGIS kèm **thanh trượt điều chỉnh độ mờ (Opacity slider)**.
- **Công cụ truy vấn không gian bán kính (Spatial Buffer Query - ST_DWithin):**
  - Nhấp chuột trực tiếp lên bản đồ để tạo tâm phân tích.
  - Tùy chỉnh bán kính (300m, 500m, 1000m, 1500m).
  - Tự động thống kê số căn nhà, giá trung bình/m², giá min/max trong vùng đệm.
- **Bộ lọc thuộc tính nâng cao:**
  - Lọc theo quận, loại nhà (Mặt phố / Hẻm), khoảng giá và khoảng diện tích.
- **Bảng điều khiển kinh tế lượng & Mô hình Hedonic (Chart.js):**
  - Biểu đồ so sánh độ phù hợp $R^2$ giữa OLS ($R^2 = 0.407$) và Random Forest ($R^2 = 0.092$).
  - Biểu đồ hệ số hồi quy OLS ($\beta$) làm nổi bật các biến có ý nghĩa thống kê ($p < 0.05$).
  - Biểu đồ so sánh đơn giá trung bình theo từng quận.
  - Bảng tổng hợp ý nghĩa kinh tế đô thị và phân tích không gian.
- **Thư viện bản đồ chuyên đề QGIS:**
  - Xem trực tiếp các bản đồ điểm nóng Gi*, Moran's I, IDW, biểu đồ tầm quan trọng của biến.

---

## 2. Cấu trúc thư mục module

```
webapp/
├── README.md                          # Tài liệu hướng dẫn module webapp
├── backend/
│   ├── .env.example                   # Mẫu cấu hình môi trường
│   ├── .env                           # Cấu hình môi trường (port, kết nối pg)
│   ├── package.json                   # dependencies: express, pg, cors, dotenv
│   ├── schema.sql                     # Script SQL tạo database, tables và GiST index
│   ├── data/
│   │   └── housing.geojson            # Dữ liệu 121 nhà chuẩn WGS84 EPSG:4326
│   └── src/
│       ├── server.js                  # Khởi chạy Express server
│       ├── db.js                      # Kết nối PostGIS & GIS Fallback engine
│       ├── routes/
│       │   ├── housing.js             # API danh sách nhà & truy vấn bán kính nearby
│       │   ├── amenities.js           # API tiện ích theo loại
│       │   ├── stats.js               # API thống kê mô hình hồi quy Hedonic
│       │   └── boundaries.js          # API ranh giới 3 quận
│       └── scripts/
│           ├── convert_csv_to_geojson.js # Chuyển CSV sang GeoJSON
│           ├── convert_csv_to_geojson.py # Bản Python tương đương
│           └── import_to_postgis.js      # Nạp tự động toàn bộ data vào PostGIS
└── frontend/
    ├── index.html                     # Giao diện web GIS tương tác
    ├── css/
    │   └── style.css                  # Giao diện hiện đại, responsive
    ├── js/
    │   ├── map.js                     # Leaflet map, layers, buffer query, popups
    │   └── charts.js                  # Biểu đồ phân tích Chart.js
    └── img/
        └── map_idw_price.png          # Ảnh raster nội suy IDW xuất từ QGIS
```

---

## 3. Hướng dẫn cài đặt & Khởi chạy nhanh

### Cách 1: Chạy ngay (Không bắt buộc cài PostgreSQL trước)

Backend được tích hợp sẵn engine GeoJSON Fallback, bạn có thể chạy ngay lập tức:

```bash
# 1. Di chuyển vào thư mục backend
cd webapp/backend

# 2. Cài đặt các thư viện cần thiết
npm install

# 3. Khởi động server
npm start
```
 
Mở trình duyệt truy cập: **`http://localhost:3000`**

---

### Cách 2: Sử dụng PostgreSQL + PostGIS (Đầy đủ)

Nếu máy tính của bạn đã cài PostgreSQL và PostGIS:

1. **Tạo database:**
   ```sql
   CREATE DATABASE detai_gis;
   ```

2. **Cấu hình file `webapp/backend/.env`:**
   ```env
   PORT=3000
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=detai_gis
   PGUSER=postgres
   PGPASSWORD=mat_khau_cua_ban
   ```

3. **Nạp tự động toàn bộ dữ liệu vào PostgreSQL:**
   ```bash
   cd webapp/backend
   npm run seed
   # Lệnh này sẽ tự động chạy schema.sql và nạp 121 nhà + 7 lớp tiện ích vào PostGIS
   ```

4. **Khởi chạy ứng dụng:**
   ```bash
   npm start
   ```

---

## 4. Đặc tả API Endpoints

| Phương thức | Endpoint | Mô tả | Định dạng trả về |
|---|---|---|---|
| `GET` | `/api/housing` | Lấy danh sách nhà (hỗ trợ query `district`, `houseType`, `minPrice`, `maxPrice`, `minArea`, `maxArea`) | GeoJSON FeatureCollection |
| `GET` | `/api/housing/nearby?lat=&lon=&radius=` | Truy vấn nhà trong bán kính `radius` mét (dùng `ST_DWithin` hoặc Haversine) | GeoJSON FeatureCollection + Summary |
| `GET` | `/api/housing/:id` | Chi tiết 1 căn nhà theo ID | GeoJSON Feature |
| `GET` | `/api/amenities` | Danh sách 7 loại tiện ích kèm metadata và số lượng đối tượng | JSON Array |
| `GET` | `/api/amenities/:type` | Tiện ích theo loại (`school`, `hospital`, `park`, `water_lakes`, `supermarket`, `marketplace`, `bus_stop`) | GeoJSON FeatureCollection |
| `GET` | `/api/boundaries` | Ranh giới hành chính 3 quận trung tâm | GeoJSON FeatureCollection |
| `GET` | `/api/stats` | Thống kê mô hình OLS, Random Forest, hệ số hồi quy $\beta$ và giá theo quận | JSON Object |
| `GET` | `/api/status` | Kiểm tra trạng thái server và chế độ DB (PostGIS / Fallback) | JSON Object |
