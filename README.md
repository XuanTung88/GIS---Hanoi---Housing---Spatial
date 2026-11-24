# ĐỒ ÁN MÔN HỌC HỆ THỐNG THÔNG TIN KHÔNG GIAN  (GIS)
# PHÂN TÍCH KHÔNG GIAN VÀ ĐỊNH GIÁ BẤT ĐỘNG SẢN NHÀ Ở TẠI KHU VỰC TRUNG TÂM HÀ NỘI

> **Đề tài:** Ứng dụng GIS, Thống kê không gian và Mô hình định giá Hedonic để phân tích biến động giá nhà ở tại 3 quận trung tâm Hà Nội (Ba Đình, Đống Đa, Hoàn Kiếm), tích hợp nền tảng WebGIS trực quan hóa tương tác.  
> **Ngôn ngữ & Công nghệ:** Python (GeoPandas, SciPy, Statsmodels, Scikit-learn) • QGIS 3.x • Node.js (Express) • PostGIS / GIS Fallback Engine • Leaflet.js • Chart.js.

---

## MỤC LỤC
1. [Giới thiệu tổng quan & Mục tiêu đề tài](#1-giới-thiệu-tổng-quan--mục-tiêu-đề-tài)
2. [Phạm vi nghiên cứu & Dữ liệu đầu vào](#2-phạm-vi-nghiên-cứu--dữ-liệu-đầu-vào)
3. [Hệ quy chiếu & Tiêu chuẩn không gian](#3-hệ-quy-chiếu--tiêu-chuẩn-không-gian)
4. [Kiến trúc hệ thống & Luồng xử lý dữ liệu (Pipeline)](#4-kiến-trúc-hệ-thống--luồng-xử-lý-dữ-liệu-pipeline)
5. [Phương pháp luận & Kỹ thuật phân tích GIS](#5-phương-pháp-luận--kỹ-thuật-phân-tích-gis)
   - [5.1. Kỹ thuật đặc trưng không gian (Spatial Feature Engineering)](#51-kỹ-thuật-đặc-trưng-không-gian-spatial-feature-engineering)
   - [5.2. Nội suy bề mặt giá (IDW - Inverse Distance Weighting)](#52-nội-suy-bề-mặt-giá-idw---inverse-distance-weighting)
   - [5.3. Phân tích điểm nóng (Hot Spot Analysis - Getis-Ord Gi*)](#53-phân-tích-điểm-nóng-hot-spot-analysis---getis-ord-gi)
   - [5.4. Tự tương quan không gian cục bộ (Local Moran's I - LISA)](#54-tự-tương-quan-không-gian-cục-bộ-local-morans-i---lisa)
   - [5.5. Truy vấn không gian & Ghép thuộc tính (Spatial Join)](#55-truy-vấn-không-gian--ghép-thuộc-tính-spatial-join)
6. [Mô hình kinh tế lượng Hedonic & Học máy (Machine Learning)](#6-mô-hình-kinh-tế-lượng-hedonic--học-máy-machine-learning)
   - [6.1. Hồi quy tuyến tính OLS (Ordinary Least Squares)](#61-hồi-quy-tuyến-tính-ols-ordinary-least-squares)
   - [6.2. Mô hình Random Forest Regressor & Đánh giá Cross-Validation](#62-mô-hình-random-forest-regressor--đánh-giá-cross-validation)
   - [6.3. So sánh mô hình & Đánh giá hiện tượng đa cộng tuyến](#63-so-sánh-mô-hình--đánh-giá-hiện-tượng-đa-cộng-tuyến)
7. [Nền tảng ứng dụng WebGIS tương tác](#7-nền-tảng-ứng-dụng-webgis-tương-tác)
   - [7.1. Kiến trúc Backend & Cơ chế Smart Fallback](#71-kiến-trúc-backend--cơ-chế-smart-fallback)
   - [7.2. Đặc tả hệ thống RESTful API](#72-đặc-tả-hệ-thống-restful-api)
   - [7.3. Giao diện người dùng WebGIS Frontend](#73-giao-diện-người-dùng-webgis-frontend)
8. [Cấu trúc cây thư mục dự án](#8-cấu-trúc-cây-thư-mục-dự-án)
9. [Hướng dẫn cài đặt & Triển khai](#9-hướng-dẫn-cài-đặt--triển-khai)
10. [Kết luận, Hạn chế kỹ thuật & Định hướng phát triển](#10-kết-luận-hạn-chế-kỹ-thuật--định-hướng-phát-triển)

---

## 1. GIỚI THIỆU TỔNG QUAN & MỤC TIÊU ĐỀ TÀI

### 1.1. Bối cảnh nghiên cứu
Thị trường bất động sản nhà ở tại khu vực trung tâm Thủ đô Hà Nội mang tính đặc thù cao: quỹ đất hạn chế, mật độ dân cư dày đặc, hệ thống di sản lịch sử kết hợp hạ tầng thương mại sầm uất. Giá bất động sản ở khu vực này không chỉ được định đoạt bởi các đặc tính vật lý (diện tích xây dựng, số tầng, kiến trúc) mà chịu sự tác động sâu sắc từ **vị trí địa lý** và **khả năng tiếp cận hệ thống tiện ích dịch vụ đô thị** (trường học, bệnh viện, công viên, hồ cảnh quan, chợ truyền thống, hệ thống giao thông công cộng).

### 1.2. Mục tiêu nghiên cứu
1. **Thu thập và chuẩn hóa dữ liệu địa không gian đa nguồn:** Tích hợp dữ liệu tin đăng nhà đất thực tế (Chợ Tốt / Nhà Tốt), ranh giới hành chính và dữ liệu tiện ích công cộng (OpenStreetMap).
2. **Kỹ thuật trích xuất đặc trưng không gian (Spatial Feature Engineering):** Tính toán khoảng cách trắc địa/hình học Euclid chính xác theo hệ mét từ từng bất động sản đến tiện ích gần nhất, kết hợp đếm mật độ tiện ích trong các bán kính đệm phục vụ đi bộ ($300\text{ m}$, $500\text{ m}$, $1{,}000\text{ m}$).
3. **Phân tích cấu trúc phân bố không gian trên QGIS:**
   - Xây dựng bản đồ nội suy giá bề mặt liên tục bằng phương pháp IDW.
   - Định vị các cụm tập trung giá trị cao/thấp có ý nghĩa thống kê thông qua Getis-Ord $Gi^*$.
   - Phát hiện các điểm bất thường không gian (Spatial Outliers - High-Low, Low-High) qua chỉ số tự tương quan cục bộ Local Moran's I (LISA).
4. **Mô hình hóa định giá bất động sản Hedonic:** Đánh giá định lượng tác động của từng tiện ích đô thị tới đơn giá nhà đất ($Y = \text{triệu VNĐ/m}^2$) bằng hồi quy OLS và so sánh hiệu quả với mô hình học máy phi tuyến Random Forest.
5. **Xây dựng hệ thống WebGIS trực quan hóa:** Phát triển ứng dụng Web tương tác hoàn chỉnh cho phép người dùng xem bản đồ phân lớp, lọc dữ liệu đa tiêu chí, tra cứu bất động sản theo bán kính cự ly linh hoạt và phân tích biểu đồ thống kê trực tiếp trên trình duyệt.

---

## 2. PHẠM VI NGHIÊN CỨU & DỮ LIỆU ĐẦU VÀO

### 2.1. Phạm vi không gian
Khu vực nghiên cứu tập trung vào 3 quận nội đô lịch sử có mật độ kinh tế - thương mại cao nhất Hà Nội:
- **Quận Hoàn Kiếm:** Trung tâm hành chính, thương mại, du lịch và văn hóa lịch sử (Khu phố cổ, Hồ Gươm).
- **Quận Ba Đình:** Trung tâm chính trị, ngoại giao quốc gia, tập trung nhiều công viên và hồ nước lớn (Hồ Tây, Hồ Trúc Bạch, Công viên Bách Thảo).
- **Quận Đống Đa:** Mật độ dân số cao, mạng lưới ngõ hẻm phức hợp, dày đặc trường đại học và bệnh viện tuyến trung ương.

### 2.2. Danh mục các lớp dữ liệu đã xử lý

| STT | Lớp dữ liệu | Định dạng lưu trữ | Nguồn thu thập | Số lượng thực tế | Thuộc tính chính |
|:---:|---|:---:|:---:|:---:|---|
| **1** | Bất động sản khảo sát | `.csv` / `.gpkg` | Chợ Tốt (Nhà Tốt API) | **121 bản ghi hợp lệ** | ID, Tọa độ (Lat/Lon), Giá (VNĐ), Diện tích ($m^2$), Giá/m² (triệu đồng), Số tầng, Loại nhà (Mặt phố / Hẻm), Địa chỉ |
| **2** | Ranh giới 3 quận trung tâm | `.geojson` / `.gpkg` | OpenStreetMap (Overpass Turbo) | 3 quận (đã gộp thành vùng bao chuẩn) | Tên quận, Mã hành chính `admin_level=6`, Hình học Polygon chuẩn |
| **3** | Trường học (`amenity=school`) | `.geojson` | OpenStreetMap | **153 điểm** | Tên trường, hình học Point/Centroid |
| **4** | Cơ sở y tế & Bệnh viện (`amenity=hospital`) | `.geojson` | OpenStreetMap | **54 điểm** | Tên bệnh viện, hình học Point/Centroid |
| **5** | Công viên & Cây xanh (`leisure=park`) | `.geojson` | OpenStreetMap | **89 đối tượng** | Tên công viên, diện tích, tâm điểm Point |
| **6** | Siêu thị bán lẻ (`shop=supermarket`) | `.geojson` | OpenStreetMap | **79 điểm** | Tên chuỗi bán lẻ, hình học Point |
| **7** | Chợ dân sinh truyền thống (`shop=marketplace`) | `.geojson` | OpenStreetMap | **39 điểm** | Tên chợ dân sinh, hình học Point |
| **8** | Điểm dừng xe buýt (`highway=bus_stop`) | `.geojson` | OpenStreetMap | **462 điểm** | Vị trí trạm xe buýt, hình học Point |
| **9** | Mặt nước & Hồ cảnh quan (`natural=water`) | `.geojson` | OpenStreetMap | **124 đối tượng** | Hồ Gươm, Hồ Trúc Bạch, Hồ Ba Mẫu,... |

---

## 3. HỆ QUY CHIẾU & TIÊU CHUẨN KHÔNG GIAN

Dự án tuân thủ nghiêm ngặt chuẩn quản lý tọa độ trong GIS:

```
[Dữ liệu Web / GPS thô]                      [Tính toán không gian & Phân tích GIS]
    WGS 84 (EPSG:4326)         ──────►            WGS 84 / UTM Zone 48N (EPSG:32648)
- Kinh độ / Vĩ độ (Độ thập phân)                - Lưới phẳng chiếu mét khu vực Bắc Bộ
- Dùng cho Leaflet.js, OSM API, GeoJSON         - Dùng cho cKDTree, Buffer 300m/500m/1000m, IDW
```

1. **WGS 84 (EPSG:4326):** Hệ tọa độ trắc địa elipsoid quốc tế (tọa độ góc: độ, phút, giây / độ thập phân). Dùng để giao tiếp với bản đồ trực tuyến Leaflet, lưu trữ GeoJSON gốc và trao đổi API RESTful.
2. **WGS 84 / UTM Zone 48N (EPSG:32648):** Hệ tọa độ phẳng Universal Transverse Mercator (UTM) múi 48 Bắc. 
   - *Lý do bắt buộc:* Khi đo khoảng cách và diện tích, nếu để nguyên EPSG:4326 khoảng cách sẽ tính bằng độ ($^\circ$), sai lệch nghiêm trọng theo vĩ độ. Chuyển sang EPSG:32648 giúp đơn vị đo trở thành **mét thực tế ($m$)**, đảm bảo độ chính xác tuyệt đối khi tính cự ly tới tiện ích và tạo bán kính vùng đệm (Buffer).

---

## 4. KIẾN TRÚC HỆ THỐNG & LUỒNG XỬ LÝ DỮ LIỆU (PIPELINE)

Toàn bộ đồ án được thiết kế theo luồng quy trình khoa học dữ liệu không gian khép kín (Spatial Data Science Pipeline):

mermaid
flowchart TD
    subgraph ThuThap [1. Thu thập & Làm sạch dữ liệu]
        A1[Chợ Tốt API] -->|Python crawl & clean| A2[housing_hanoi_center_150.csv]
        B1[Overpass Turbo OSM] -->|7 nhóm tiện ích GeoJSON| B2[data/raw/amenities_osm/]
        C1[OSM Admin Boundary] -->|02_fix_boundary.py| C2[boundary_clean.gpkg / EPSG:32648]
    end

    subgraph KhongGian [2. Kỹ thuật đặc trưng không gian]
        A2 & B2 -->|03_spatial_analysis.py \n SciPy cKDTree & Buffer| D1[housing_with_spatial_features.csv \n 40 thuộc tính không gian]
    end

    subgraph QGIS_Analysis [3. Thống kê & Phân tích chuyên sâu QGIS]
        D1 & C2 -->|IDW Interpolation| E1[Bản đồ nội suy giá IDW]
        D1 -->|Spatial Statistics: Gi*| E2[Hot Spot Analysis Gi_output]
        D1 -->|Spatial Statistics: LISA| E3[Local Moran's I moran_output]
        D1 -->|Spatial Selection & Join| E4[housing_model_ready.csv \n Gộp Z-score, p-value]
    end

    subgraph Modeling [4. Mô hình định giá Hedonic]
        E4 -->|04_hedonic_model.py| F1[Mô hình OLS \n R² = 0.407, p(F) < 0.001]
        E4 -->|04_hedonic_model.py| F2[Mô hình Random Forest \n 5-Fold CV, Feature Importance]
        F1 & F2 -->|05_visualize_results.py| F3[Hệ số OLS, Actual vs Pred, Boxplot, R²]
    end

    subgraph WebGIS [5. Ứng dụng WebGIS tương tác]
        D1 & E4 & B2 & F3 -->|Express REST API + PostGIS / Fallback| G1[Backend Service \n :3000]
        G1 -->|Leaflet.js + Chart.js| G2[Giao diện WebGIS \n Bản đồ tương tác, Lọc đa tiêu chí, Tra cứu bán kính, Thống kê]
    end


---

## 5. PHƯƠNG PHÁP LUẬN & KỸ THUẬT PHÂN TÍCH GIS

### 5.1. Kỹ thuật đặc trưng không gian (Spatial Feature Engineering)
* **Kịch bản thực thi:** `scripts/03_spatial_analysis.py`
* **Công cụ cốt lõi:** `scipy.spatial.cKDTree` kết hợp `geopandas`.
* **Cơ chế tính toán:**
  1. Chiếu toàn bộ điểm nhà ở và các lớp tiện ích sang hệ mét `EPSG:32648`.
  2. Xây dựng cây tìm kiếm nhị phân $k$-chiều (`cKDTree`) cho tọa độ của từng lớp tiện ích.
  3. Truy vấn cự ly ngắn nhất ($k=1$) cho 121 điểm nhà: độ phức tạp chỉ $O(\log N)$ thay vì $O(N \times M)$ của phép quét vòng lặp thông thường.
  4. Thực hiện thuật toán `query_ball_point` với bán kính $R \in \{300\text{ m}, 500\text{ m}, 1{,}000\text{ m}\}$ để đếm mật độ tiện ích trong tầm đi bộ.
* **Kết quả:** Sinh ra bảng dữ liệu hoàn chỉnh `housing_with_spatial_features.csv` với **40 trường thông tin**, bao gồm 7 biến cự ly `dist_<amenity>_m` và 21 biến mật độ `count_<amenity>_<radius>m`.

### 5.2. Nội suy bề mặt giá (IDW - Inverse Distance Weighting)
* **Mục đích:** Xây dựng mô hình bề mặt liên tục phản ánh sự phân bố đơn giá đất ($Y = \text{triệu VNĐ/m}^2$) trên toàn bộ địa bàn 3 quận trung tâm từ các điểm khảo sát rời rạc.
* **Công thức toán học:**
  $$\hat{Z}(s_0) = \frac{\sum_{i=1}^n \frac{1}{d_i^p} Z(s_i)}{\sum_{i=1}^n \frac{1}{d_i^p}}$$
  Trong đó: $Z(s_i)$ là giá nhà tại điểm $s_i$, $d_i$ là khoảng cách từ điểm cần ước tính $s_0$ đến $s_i$, lũy thừa khoảng cách $p=2$ (khoảng cách nghịch đảo bình phương).
* **Thiết lập trên QGIS:**
  - Lớp đầu vào: `housing_utm` ($N = 121$).
  - Thuộc tính nội suy: `gia_trieu_m2`.
  - Độ phân giải pixel: $10\text{ m} \times 10\text{ m}$.
  - Mặt nạ cắt (Clip by mask layer): `boundary_clean.gpkg`.
* **Kết quả:** Bản đồ `map_idw_price.png` chỉ rõ một **độ dốc suy giảm giá đất rõ rệt theo hướng Đông - Tây**: vùng giá cao tập trung tại trục lõi Hoàn Kiếm (đỉnh điểm $> 600 - 1{,}000\text{ triệu/m}^2$), giảm dần về phía Ba Đình ($250 - 450\text{ triệu/m}^2$) và ổn định hơn tại khu vực dân cư Đống Đa ($150 - 300\text{ triệu/m}^2$).

### 5.3. Phân tích điểm nóng (Hot Spot Analysis - Getis-Ord Gi*)
* **Mục đích:** Kiểm định thống kê xem các bất động sản giá cao (hoặc giá thấp) có xu hướng tụ cụm lại với nhau một cách ngẫu nhiên hay có ý nghĩa thống kê vượt trội.
* **Công thức toán học:**
  $$G_i^* = \frac{\sum_{j=1}^n w_{ij} x_j - \bar{X} \sum_{j=1}^n w_{ij}}{S \sqrt{\frac{n \sum_{j=1}^n w_{ij}^2 - (\sum_{j=1}^n w_{ij})^2}{n - 1}}}$$
* **Kết quả phân tích ($N = 121$):**
  - **Điểm cực nóng (Hotspot 99% - $Z > +2.58$, $p < 0.01$):** **26 điểm**, tập trung 100% tại quận Hoàn Kiếm (khu phố cổ, quanh hồ Hoàn Kiếm).
  - **Điểm cực lạnh (Coldspot 99% - $Z < -2.58$, $p < 0.01$):** **32 điểm**, tập trung chủ yếu tại các cụm dân cư sâu trong ngõ hẻm tại quận Đống Đa.
  - **Điểm không có ý nghĩa thống kê ($p \ge 0.10$):** 63 điểm, phân bố rải rác khu vực Ba Đình và vành đai trung gian.

### 5.4. Tự tương quan không gian cục bộ (Local Moran's I - LISA)
* **Mục đích:** Phân loại cấu trúc liên kết không gian và phát hiện các **điểm dị biệt không gian (Spatial Outliers)**:
  - $HH$ (High-High): Điểm giá cao nằm lọt trong vùng lân cận giá cao (Cụm điểm nóng).
  - $LL$ (Low-Low): Điểm giá thấp nằm trong vùng lân cận giá thấp (Cụm điểm lạnh).
  - $HL$ (High-Low Outlier): Điểm giá cao bất thường lọt giữa khu vực giá thấp.
  - $LH$ (Low-High Outlier): Điểm giá thấp lọt giữa khu vực giá cao.
* **Kết quả thực tế ($N = 121$):**
  - **19 điểm High-High:** Cực lõi Hoàn Kiếm (khu phố đi bộ, trung tâm du lịch).
  - **32 điểm Low-Low:** Khu vực ngõ cụt tại Khâm Thiên, Trung Phụng, Đê La Thành (Đống Đa).
  - **15 điểm High-Low (Dị biệt loại 1):** Các căn nhà mặt phố kinh doanh lớn nằm trên các trục xuyên tâm huyết mạch (Xã Đàn, Tôn Đức Thắng, Chùa Bộc) vượt trội so với khu vực nhà dân xung quanh.
  - **17 điểm Low-High (Dị biệt loại 2):** Các bất động sản nằm sâu trong ngõ nhỏ, ngõ chung, diện tích hạn hẹp hoặc pháp lý chung sổ nằm xen kẽ giữa trung tâm Hoàn Kiếm và Ba Đình.
  - **38 điểm:** Không có tương quan không gian có ý nghĩa ($p > 0.05$).

### 5.5. Truy vấn không gian & Ghép thuộc tính (Spatial Join)
* **Truy vấn theo biểu thức (Select by Expression):** `"gia_trieu_m2" > 250 OR "dist_school_m" < 300` $\rightarrow$ Chọn được **104 / 121 bản ghi ($85.95\%$)**, cho thấy ưu thế tiếp cận giáo dục cực cao tại lõi đô thị.
* **Truy vấn theo vị trí cự ly (Select within Distance):** Bán kính $500\text{ m}$ quanh hệ thống bệnh viện $\rightarrow$ Chọn được **59 / 121 căn nhà ($48.76\%$)**, minh chứng cho mạng lưới y tế dày đặc của thủ đô.
* **Ghép thuộc tính không gian (Spatial Join):** Tích hợp kết quả phân tích thống kê $Z$-score, $p$-value từ QGIS vào bảng thuộc tính nhà đất để xuất ra file `data/processed/housing_model_ready.csv`.

---

## 6. MÔ HÌNH KINH TẾ LƯỢNG HEDONIC & HỌC MÁY (MACHINE LEARNING)

### 6.1. Hồi quy tuyến tính OLS (Ordinary Least Squares)
Mô hình định giá Hedonic giả định rằng đơn giá nhà ở ($Y = \text{gia\_trieu\_m2}$) là hàm số tổng hợp của các thuộc tính vật lý nội tại ($S$), thuộc tính vị trí hành chính ($L$), và thuộc tính cự ly tiện ích môi trường xung quanh ($E$):

$$\text{Price}_i = \beta_0 + \sum \beta_k S_{ik} + \sum \gamma_m L_{im} + \sum \theta_j E_{ij} + \varepsilon_i$$

#### Bảng kết quả hồi quy OLS ($N = 121$, $R^2 = 0.407$, $\text{Adj. } R^2 = 0.322$, $F = 4.795$, $p(F) = 5.58 \times 10^{-7}$):

| Biến độc lập | Hệ số hồi quy ($\beta$) | Sai số chuẩn (Std.Err) | $t$-statistic | $p$-value ($P > |t|$) | Ý nghĩa thống kê & Diễn giải kinh tế |
|---|:---:|:---:|:---:|:---:|---|
| **const** (Hệ số chặn) | $393.80$ | $87.15$ | $4.518$ | **$0.000$** | Mức giá nền tảng cơ sở |
| **dien_tich** ($m^2$) | $+0.402$ | $0.294$ | $1.369$ | $0.174$ | Không có ý nghĩa thống kê ở mức $5\%$ |
| **so_tang** | $+8.771$ | $7.283$ | $1.204$ | $0.231$ | Mỗi tầng tăng thêm đóng góp ~8.77 triệu/m² (chưa đủ độ tin cậy $95\%$) |
| **dist_water_lakes_m** | **$-0.2093$** | **$0.104$** | **$-2.012$** | **$0.047$** | **Có ý nghĩa ($p < 0.05$):** Cách xa hồ 1m giá giảm ~209 nghìn đ/m² (xa 100m giảm ~20.9 triệu/m²) |
| **khu_vuc_Hoàn Kiếm** | **$+202.39$** | **$78.59$** | **$2.575$** | **$0.011$** | **Có ý nghĩa ($p < 0.05$):** Nhà ở Hoàn Kiếm đắt hơn khu vực cơ sở (Ba Đình) tới 202.39 triệu/m² |
| **loai_nha_Mặt phố** | **$+87.99$** | **$36.74$** | **$2.395$** | **$0.018$** | **Có ý nghĩa ($p < 0.05$):** Nhà mặt tiền kinh doanh cao hơn nhà ngõ hẻm ~87.99 triệu/m² |
| `dist_marketplace_m` | $-0.1273$ | $0.084$ | $-1.519$ | $0.132$ | Càng gần chợ giá có xu hướng tăng nhẹ nhưng không đạt mức $5\%$ |
| `dist_park_m` | $-0.1040$ | $0.089$ | $-1.169$ | $0.245$ | Xa công viên giá giảm nhẹ (không đạt mức ý nghĩa $5\%$) |
| `dist_bus_stop_m` | $-0.1326$ | $0.215$ | $-0.616$ | $0.539$ | Hệ số âm nhưng không có ý nghĩa thống kê |
| `dist_hospital_m` | $-0.0152$ | $0.080$ | $-0.191$ | $0.849$ | Tác động cự ly bệnh viện không đáng kể tại khu lõi |
| `dist_school_m` | $-0.0277$ | $0.117$ | $-0.236$ | $0.814$ | Mật độ trường học quá dày đặc khiến độ biến thiên khoảng cách ít ảnh hưởng |
| `dist_supermarket_m` | $+0.0908$ | $0.117$ | $+0.773$ | $0.441$ | Không có ý nghĩa |
| `khu_vuc_Đống Đa` | $-23.43$ | $55.83$ | $-0.420$ | $0.676$ | Chênh lệch giá giữa Đống Đa và Ba Đình không mang tính vượt trội |
| `Z_score` (LISA) | $-4.474$ | $8.494$ | $-0.527$ | $0.600$ | Biến phụ thuộc kiểm soát không gian |
| `p_value` | $+726.98$ | $899.57$ | $0.808$ | $0.421$ | Biến phụ thuộc kiểm soát không gian |
| `p_fdr` | $-689.50$ | $848.92$ | $-0.812$ | $0.419$ | Biến phụ thuộc kiểm soát không gian |

### 6.2. Mô hình Random Forest Regressor & Đánh giá Cross-Validation
* **Thiết lập:** 300 cây quyết định (`n_estimators=300`), độ sâu tối đa `max_depth=6`, sử dụng toàn bộ 36 biến không gian và thuộc tính vật lý.
* **Đánh giá 5-fold Cross-Validation:**
  - $R^2$ trung bình: $0.092 \pm 0.14$
  - MAE trung bình: $148.5\text{ triệu/m}^2$
* **Top 5 biến có độ quan trọng cao nhất (Feature Importance):**
  1. `dist_water_lakes_m` (Khoảng cách tới mặt nước/hồ cảnh quan)
  2. `khu_vuc_Hoàn Kiếm` (Địa bàn hành chính Hoàn Kiếm)
  3. `loai_nha_Mặt phố` (Hình thái tiếp cận đường giao thông)
  4. `dist_marketplace_m` (Khoảng cách tới chợ truyền thống)
  5. `count_bus_stop_1000m` (Mật độ trạm xe buýt bán kính 1km)

### 6.3. So sánh mô hình & Đánh giá hiện tượng đa cộng tuyến
1. **So sánh OLS vs Random Forest:**
   - OLS ($R^2 = 0.407$) có hiệu năng giải thích vượt trội hơn Random Forest ($R^2_{\text{CV}} = 0.092$).
   - *Nguyên nhân kỹ thuật:* Cỡ mẫu khảo sát thực tế khiêm tốn ($N = 121$) trong khi số lượng biến đưa vào Random Forest lên tới 36 biến, dẫn tới hiện tượng **quá khớp (overfitting)** trên tập train và suy giảm khả năng tổng quát hóa trên tập kiểm thử Cross-Validation. Đối với các bài toán lượng giác không gian cỡ nhỏ, mô hình tham số OLS với tập biến rút gọn mang lại độ ổn định cao hơn hẳn.
2. **Hiện tượng đa cộng tuyến (Multicollinearity):**
   - Chỉ số điều kiện của mô hình OLS: $\text{Condition Number} = 8.26 \times 10^4$ (vượt ngưỡng cảnh báo $10^3$).
   - *Nguyên nhân:* Việc đưa trực tiếp các đại lượng thống kê không gian phái sinh từ chính giá bán ($Z$-score, $p$-value, $p_{FDR}$) vào vế phải của phương trình hồi quy đã làm nảy sinh đa cộng tuyến mạnh. Bài học kinh nghiệm là chỉ nên dùng nhãn phân cụm nhị phân (dummy) hoặc phân tầng mô hình (spatial regime) thay vì đưa các giá trị xác suất liên tục vào hồi quy.

---

## 7. NỀN TẢNG ỨNG DỤNG WEBGIS TƯƠNG TÁC

Hệ thống tích hợp một module ứng dụng WebGIS hoàn chỉnh đặt trong thư mục `webapp/`, đóng vai trò công cụ trực quan hóa kết quả phân tích không gian và mô hình kinh tế lượng phục vụ người dùng cuối.

### 7.1. Kiến trúc Backend & Cơ chế Smart Fallback
Backend được xây dựng trên nền tảng **Node.js (Express)** với cơ chế cơ sở dữ liệu kép cực kỳ linh hoạt:
- **Chế độ PostGIS chính thức:** Khi có kết nối tới PostgreSQL/PostGIS, hệ thống sử dụng các hàm không gian tiêu chuẩn: `ST_DWithin`, `ST_AsGeoJSON`, `ST_SetSRID`, `ST_MakePoint`.
- **Chế độ File-based GIS Fallback Engine (Tự động):** Nếu máy tính chưa cài đặt PostgreSQL hoặc cơ sở dữ liệu chưa khởi động, server **tự động chuyển sang bộ tính toán không gian nội suy bộ nhớ**:
  - Tự động nạp dữ liệu từ các file GeoJSON/CSV tĩnh có sẵn trong dự án.
  - Tự cài đặt thuật toán tính khoảng cách trắc địa mặt cầu **Haversine Formula**:
    $$d = 2R \arcsin \left(\sqrt{\sin^2\left(\frac{\Delta \varphi}{2}\right) + \cos(\varphi_1)\cos(\varphi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
  - Tự động thực thi các bộ lọc thuộc tính và truy vấn bán kính động mà **không bao giờ bị crash hoặc gián đoạn dịch vụ**.

### 7.2. Đặc tả hệ thống RESTful API

| STT | Phương thức | Đường dẫn API | Tham số truy vấn (Query Params) | Mô tả chức năng | Kết quả trả về |
|:---:|:---:|---|---|---|---|
| **1** | `GET` | `/api/status` | Không | Kiểm tra trạng thái server và chế độ DB (PostGIS hay Fallback) | JSON `{ status, mode, appName }` |
| **2** | `GET` | `/api/housing` | `district`, `houseType`, `minPrice`, `maxPrice`, `minArea`, `maxArea` | Lấy danh sách bất động sản kết hợp lọc đa tiêu chí | GeoJSON `FeatureCollection` (121 điểm) |
| **3** | `GET` | `/api/housing/nearby` | `lat` (vĩ độ), `lon` (kinh độ), `radius` (bán kính theo mét, mặc định 500m) | **Truy vấn không gian:** Tìm các căn nhà nằm trong bán kính quanh tọa độ chỉ định | GeoJSON `FeatureCollection` kèm thuộc tính khoảng cách |
| **4** | `GET` | `/api/housing/:id` | `id` trên đường dẫn | Lấy thông tin chi tiết một bất động sản | JSON chi tiết 1 Feature |
| **5** | `GET` | `/api/amenities` | Không | Lấy danh mục 7 loại tiện ích đô thị kèm số lượng điểm | JSON mảng tiện ích |
| **6** | `GET` | `/api/amenities/:type`| `type`: `school`, `hospital`, `park`, `supermarket`, `marketplace`, `bus_stop`, `water_lakes` | Lấy lớp không gian của từng loại tiện ích đô thị | GeoJSON `FeatureCollection` |
| **7** | `GET` | `/api/boundaries` | Không | Lấy ranh giới hành chính 3 quận trung tâm | GeoJSON `MultiPolygon` |
| **8** | `GET` | `/api/stats` | Không | Cung cấp số liệu so sánh mô hình OLS, Random Forest và bảng hệ số | JSON thống kê |

### 7.3. Giao diện người dùng WebGIS Frontend
Giao diện ứng dụng được phát triển theo phong cách Dashboard hiện đại, hỗ trợ 3 phân hệ màn hình chính:
1. **Phân hệ Bản đồ không gian tương tác (Map View):**
   - Hỗ trợ chuyển đổi linh hoạt **4 lớp bản đồ nền (Base Maps)**: OpenStreetMap tiêu chuẩn, Carto Positron (nền sáng), Carto Dark (nền tối sang trọng) và Ảnh vệ tinh Esri World Imagery.
   - Hiển thị ranh giới 3 quận trung tâm (Ba Đình, Đống Đa, Hoàn Kiếm).
   - Biểu diễn 121 điểm nhà ở theo dạng bong bóng nhiệt (Circle Marker), mã hóa màu sắc linh hoạt theo đơn giá (dưới 150 triệu, 150 - 300 triệu, 300 - 500 triệu, trên 500 triệu/m²).
   - Bật/tắt độc lập 7 lớp tiện ích OSM (icon chuyên biệt cho trường học, bệnh viện, công viên, siêu thị, chợ, bus stop, hồ nước).
   - Chồng phủ trực tiếp lớp ảnh raster nội suy giá IDW lên đúng tọa độ địa lý (Bounding Box).
   - Công cụ **Truy vấn bán kính không gian tương tác**: Người dùng click bất kỳ điểm nào trên bản đồ hoặc chọn bán kính ($300\text{ m}, 500\text{ m}, 1{,}000\text{ m}, 2{,}000\text{ m}$), bản đồ vẽ vòng tròn buffer và hệ thống tự động lọc các căn nhà nằm bên trong vòng đệm.
2. **Phân hệ Phân tích mô hình (Analytics View):**
   - Tích hợp thư viện `Chart.js` hiển thị trực tiếp các biểu đồ kinh tế lượng.
   - Thẻ chỉ số tổng hợp (Cards): $R^2$ OLS ($0.407$), $R^2$ Random Forest ($0.092$), số lượng mẫu ($121$).
   - Biểu đồ hệ số hồi quy OLS có đánh dấu màu trực quan cho biến có ý nghĩa thống kê ($p < 0.05$).
   - Biểu đồ phân bổ giá nhà dạng hộp (Boxplot) phản ánh rõ nét mức chênh lệch giữa Hoàn Kiếm, Ba Đình và Đống Đa.
3. **Phân hệ Thư viện bản đồ chuyên đề QGIS (QGIS Gallery View):**
   - Trưng bày các bản đồ chuyên đề độ phân giải cao xuất từ QGIS: Hot Spot Analysis ($Gi^*$), Local Moran's I (LISA), Nội suy IDW, Truy vấn thuộc tính, Ghép không gian (Spatial Join).
   - Hỗ trợ xem phóng to chi tiết kèm giải thích khoa học cho từng loại bản đồ.

---

## 8. CẤU TRÚC CÂY THƯ MỤC DỰ ÁN

```
Detai_GIS/
├── data/                                   # Quản lý toàn bộ dữ liệu địa không gian
│   ├── raw/                                # Dữ liệu thô ban đầu
│   │   ├── amenities_osm/                  # 7 lớp tiện ích trích xuất từ OpenStreetMap (.geojson)
│   │   │   ├── bus_stop.geojson            # 462 trạm dừng xe buýt
│   │   │   ├── hospital.geojson            # 54 cơ sở y tế, bệnh viện
│   │   │   ├── marketplace.geojson         # 39 chợ dân sinh truyền thống
│   │   │   ├── park.geojson                # 89 công viên, mảng xanh đô thị
│   │   │   ├── roads_network.geojson       # Mạng lưới đường giao thông
│   │   │   ├── school.geojson              # 153 trường học các cấp
│   │   │   ├── supermarket.geojson         # 79 siêu thị bán lẻ
│   │   │   └── water_lakes.geojson         # 124 hồ cảnh quan và mặt nước
│   │   ├── boundary/                       # Dữ liệu ranh giới hành chính
│   │   │   ├── data_3_quan.geojson         # Ranh giới thô 3 quận từ OSM (EPSG:4326)
│   │   │   └── boundary_clean.gpkg         # Đa giác ranh giới chuẩn đã gộp (EPSG:32648)
│   │   ├── housing_listings/               # Dữ liệu bất động sản cào từ mạng
│   │   │   └── housing_hanoi_center_150.csv # 121 tin rao làm sạch ban đầu
│   │   └── region.png                      # Ảnh chụp màn hình vùng khảo sát trên OSM
│   └── processed/                          # Dữ liệu sau khi trích xuất đặc trưng không gian
│       ├── housing_with_spatial_features.csv # 121 nhà với 40 thuộc tính khoảng cách & buffer
│       └── housing_model_ready.csv         # Bảng dữ liệu cuối cùng ghép nhãn phân cụm QGIS
│
├── scripts/                                # Mã nguồn Python xử lý khoa học dữ liệu GIS
│   ├── 00_project_log.ipynb                # Notebook nhật ký toàn diện toàn bộ quy trình dự án
│   ├── 01_crawl_housing_3districts.py      # Script cào dữ liệu tự động từ API Chợ Tốt / Nhà Tốt
│   ├── 02_fix_boundary.py                  # Script làm sạch ranh giới, sửa lỗi topology, đổi hệ chiếu
│   ├── 03_spatial_analysis.py              # Script cKDTree tính khoảng cách tiện ích & đếm buffer
│   ├── 04_hedonic_model.py                 # Script huấn luyện OLS Hedonic & Random Forest
│   └── 05_visualize_results.py             # Script vẽ 4 biểu đồ thống kê chuyên sâu
│
├── QGIS_config/                            # Tệp dự án và các lớp phân tích xuất từ QGIS
│   ├── Ban_Do.qgz                          # File dự án QGIS tổng hợp tất cả layer
│   ├── bounding_geometry.gpkg              # Hình học bao ngoài khu vực khảo sát
│   ├── buffered.gpkg                       # Lớp vùng đệm phân tích
│   ├── Clipped_mask.tif                    # Raster nội suy giá IDW đã cắt theo ranh giới 3 quận
│   ├── gi_output.gpkg                      # Kết quả phân tích điểm nóng Getis-Ord Gi*
│   ├── housing_utm__housing_with_spatial_features.gpkg # Lớp điểm nhà ở hệ mét UTM Zone 48N
│   ├── joined_layer.gpkg                   # Lớp dữ liệu sau khi thực hiện Spatial Join
│   └── local_morans_i_output.gpkg          # Kết quả phân tích cụm không gian Local Moran's I
│
├── outputs/                                # Kết quả đầu ra của đề tài
│   ├── figures/                            # Biểu đồ và bản đồ chuyên đề chất lượng cao
│   │   ├── map_idw_price.png               # Bản đồ nội suy giá IDW
│   │   ├── GI_output.png                   # Bản đồ điểm nóng Hotspot Getis-Ord Gi*
│   │   ├── moran_output.png                # Bản đồ phân cụm LISA Local Moran's I
│   │   ├── ols_coefficients.png            # Biểu đồ hệ số hồi quy OLS kèm mức ý nghĩa
│   │   ├── actual_vs_predicted.png         # Biểu đồ phân tán giá thực tế vs dự đoán OLS
│   │   ├── model_r2_comparison.png         # Biểu đồ so sánh R² giữa OLS và Random Forest
│   │   ├── price_by_district_boxplot.png   # Biểu đồ hộp phân bố giá theo 3 quận
│   │   ├── rf_feature_importance.png       # Biểu đồ 10 biến quan trọng nhất của Random Forest
│   │   ├── housing_utm.png                 # Bản đồ phân bố điểm khảo sát UTM
│   │   └── [school, hospital, park, bus_stop, water, supermarket, marketplace].png 
│   ├── query/                              # Kết quả thực hiện các phép truy vấn không gian trên QGIS
│   │   ├── housing_full.png                # Toàn cảnh lớp điểm khảo sát
│   │   ├── filter_gia.png                  # Truy vấn biểu thức Select by Expression
│   │   ├── filter_location.png             # Truy vấn cự ly Select within distance
│   │   └── spatial_join.png                # Kết quả ghép thuộc tính không gian
│   ├── tables/                             # Bảng biểu thống kê định lượng
│   │   ├── ols_summary.txt                 # Báo cáo chi tiết kiểm định mô hình OLS
│   │   └── model_comparison.csv            # Bảng số liệu so sánh OLS vs Random Forest
│   └── report/                             # Thư mục lưu trữ tài liệu báo cáo chính thức
│
├── webapp/                                 # Ứng dụng WebGIS trực quan hóa tương tác
│   ├── backend/                            # Máy chủ API Node.js (Express)
│   │   ├── src/
│   │   │   ├── db.js                       # Quản trị kết nối PostGIS & Engine Fallback Haversine
│   │   │   ├── server.js                   # Khởi tạo Express, cấu hình middleware, port 3000
│   │   │   ├── routes/
│   │   │   │   ├── housing.js              # Route /api/housing và /api/housing/nearby
│   │   │   │   ├── amenities.js            # Route /api/amenities và /api/amenities/:type
│   │   │   │   ├── boundaries.js           # Route /api/boundaries
│   │   │   │   └── stats.js                # Route /api/stats
│   │   │   └── scripts/                    # Scripts nạp dữ liệu PostGIS (tùy chọn)
│   │   ├── .env                            # Biến môi trường cổng mạng và tài khoản DB
│   │   └── package.json                    # Khai báo phụ thuộc: express, pg, cors, dotenv
│   └── frontend/                           # Giao diện người dùng WebGIS
│       ├── index.html                      # Cấu trúc HTML Dashboard đa phân hệ
│       ├── css/
│       │   ├── style.css                   # Thiết kế giao diện UI/UX responsive hiện đại
│       │   └── leaflet.css                 # CSS Leaflet bản đồ
│       ├── js/
│       │   ├── map.js                      # Điều khiển bản đồ tương tác, layer control, radius query
│       │   ├── charts.js                   # Vẽ biểu đồ thống kê OLS & Random Forest qua Chart.js
│       │   ├── gallery.js                  # Điều khiển thư viện ảnh chuyên đề QGIS
│       │   └── leaflet.js                  # Thư viện Leaflet.js
│       └── img/                            # Ảnh bản đồ và biểu đồ phục vụ hiển thị web
│
├── Hướng dẫn trình bày các giấy tờ và cuốn báo cáo.doc # Tài liệu quy chuẩn báo cáo tốt nghiệp/môn học
└── README.md                               # Tài liệu tổng quan toàn diện của đề tài (File hiện tại)
```

---

## 9. HƯỚNG DẪN CÀI ĐẶT & TRIỂN KHAI

### 9.1. Yêu cầu môi trường hệ thống
- **Hệ điều hành:** Windows 10/11, macOS hoặc Linux.
- **Python:** Phiên bản `3.10` trở lên.
- **Node.js:** Phiên bản `18.x` hoặc `20.x LTS`.
- **QGIS:** Phiên bản `3.28 LTR` hoặc mới hơn (để mở và chỉnh sửa `QGIS_config/Ban_Do.qgz`).
- **PostgreSQL / PostGIS (Tùy chọn):** PostgreSQL `14+` kèm extension `PostGIS 3+`. *(Lưu ý: Webapp có sẵn Fallback Engine nội bộ nên không bắt buộc phải cài PostgreSQL máy vẫn chạy đầy đủ 100% tính năng).*

---

### 9.2. Triển khai phân tích dữ liệu Python (Tái lập kết quả nghiên cứu)

1. **Khởi tạo môi trường ảo và cài đặt thư viện:**
   ```bash
   # Di chuyển vào thư mục gốc dự án
   cd Detai_GIS

   # Khởi tạo virtual environment
   python -m venv .venv

   # Kích hoạt môi trường ảo
   # Trên Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Trên Linux/macOS:
   source .venv/bin/activate

   # Cài đặt các thư viện cần thiết
   pip install geopandas shapely scipy pandas numpy statsmodels scikit-learn matplotlib requests
   ```

2. **Thực thi pipeline xử lý dữ liệu theo thứ tự:**
   ```bash
   # Bước 1: (Tùy chọn) Cào dữ liệu nhà ở mới từ Chợ Tốt
   python scripts/01_crawl_housing_3districts.py

   # Bước 2: Chuẩn hóa đa giác ranh giới 3 quận sang EPSG:32648
   python scripts/02_fix_boundary.py

   # Bước 3: Tính toán khoảng cách trắc địa cKDTree và mật độ bán kính buffer
   python scripts/03_spatial_analysis.py

   # Bước 4: Chạy mô hình hồi quy Hedonic OLS và Random Forest
   python scripts/04_hedonic_model.py

   # Bước 5: Xuất 4 biểu đồ trực quan hóa kết quả mô hình
   python scripts/05_visualize_results.py
   ```

---

### 9.3. Khởi chạy Ứng dụng WebGIS tương tác

1. **Cài đặt dependencies và chạy Backend:**
   ```bash
   # Di chuyển vào thư mục backend của webapp
   cd webapp/backend

   # Cài đặt các gói Node.js
   npm install

   # Khởi chạy máy chủ Express
   npm start
   # Hoặc chế độ dev tự reload khi sửa code:
   npm run dev
   ```

2. **Truy cập ứng dụng trên trình duyệt:**
   - Mở trình duyệt web (Chrome, Edge, Firefox) và truy cập địa chỉ:
     **`http://localhost:3000`** hoặc **`http://localhost:3000/index.html`**
   - Hệ thống sẽ tự động phục vụ giao diện WebGIS tĩnh cùng toàn bộ hệ thống API tương tác.
   - Thử nghiệm tính năng:
     + Bật/tắt các lớp trường học, bệnh viện, hồ nước trên thanh sidebar bên trái.
     + Chuyển đổi giữa 4 bản đồ nền (OSM, Carto Dark, Ảnh vệ tinh).
     + Nhấp vào tab **"Bán kính"**: click chuột vào bất kỳ vị trí nào trên bản đồ để tra cứu ngay các căn nhà trong phạm vi $500\text{ m}$.
     + Nhấp nút chuyển phân hệ **"Phân Tích Mô Hình"** trên thanh tiêu đề để xem biểu đồ OLS và so sánh Random Forest.
     + Nhấp nút **"Bản Đồ QGIS"** để xem thư viện bản đồ chuyên đề Hotspot, LISA và IDW độ phân giải cao.

---

## 10. KẾT LUẬN, HẠN CHẾ KỸ THUẬT & ĐỊNH HƯỚNG PHÁT TRIỂN

### 10.1. Các phát hiện cốt lõi từ đề tài
1. **Quy luật địa tô vị trí chi phối áp đảo:** Vị trí hành chính trung tâm (`khu_vuc_Hoàn Kiếm`) mang lại mức thặng dư giá trị khổng lồ (+202.39 triệu VNĐ/$m^2$ so với vùng nền Ba Đình), phản ánh giá trị lịch sử, du lịch và thương mại dịch vụ độc nhất không thể thay thế của khu phố cổ và khu vực hồ Hoàn Kiếm.
2. **Ngoại ứng tích cực của cảnh quan mặt nước:** Khoảng cách tới mặt nước/hồ cảnh quan (`dist_water_lakes_m`) là biến tiện ích môi trường duy nhất đạt ý nghĩa thống kê bền vững ($p = 0.047$). Mỗi mét tiến gần hồ nước làm gia tăng giá trị nhà đất khoảng $209{,}000\text{ VNĐ/m}^2$, khẳng định vai trò điều hòa vi khí hậu và giá trị phong thủy/cảnh quan của hệ thống hồ Hà Nội trong quyết định mua nhà.
3. **Phần bù giá trị thương mại của nhà mặt phố:** Hình thái bất động sản mặt tiền mang lại phần bù đơn giá xấp xỉ $+88\text{ triệu VNĐ/m}^2$ so với nhà ngõ hẻm, phản ánh tiềm năng khai thác dòng tiền kinh doanh thương mại trực tiếp.

### 10.2. Nhận định hạn chế kỹ thuật & Bài học kinh nghiệm
- **Hạn chế cỡ mẫu ($N = 121$):** Cỡ mẫu còn khiêm tốn khiến các mô hình học máy phi tuyến tính phức tạp như Random Forest dễ gặp hiện tượng quá khớp (Overfitting), đạt $R^2$ thấp trên tập kiểm định chéo ($R^2_{\text{CV}} = 0.092$).
- **Hiện tượng nén trần dự đoán:** Mô hình hồi quy toàn cục OLS gặp khó khăn trong việc dự đoán chính xác nhóm bất động sản siêu sang (giá $> 800 - 1{,}000\text{ triệu/m}^2$) do sự biến động giá đất ở phân khúc cao cấp chịu ảnh hưởng bởi các yếu tố phi cấu trúc (pháp lý cá biệt, bề rộng mặt tiền, phong thủy, tính độc bản).
- **Hiện tượng đa cộng tuyến do biến không gian nội sinh:** Việc nạp trực tiếp giá trị xác suất $p$-value và điểm chuẩn hóa $Z$-score từ phân tích Local Moran's I vào mô hình OLS đã làm tăng vọt chỉ số điều kiện ($\text{Cond. No.} = 8.26 \times 10^4$). Trong thực nghiệm kinh tế lượng không gian chuẩn, các kết quả phân cụm chỉ nên đóng vai trò là biến giả phân vùng (dummy regimes) hoặc sử dụng kỹ thuật kiểm soát sai số không gian (Spatial Error / Spatial Lag Model).

### 10.3. Đề xuất hướng phát triển mở rộng
1. **Áp dụng Hồi quy trọng số địa lý (GWR - Geographically Weighted Regression):** Cho phép hệ số hồi quy của từng tiện ích đô thị thay đổi liên tục theo tọa độ không gian $(u_i, v_i)$, qua đó giải quyết triệt để tính dị biệt không gian (Spatial Heterogeneity).
2. **Mở rộng tập biến vi mô:** Bổ sung các thông số hình học chi tiết của thửa đất: độ rộng mặt tiền ($m$), chiều sâu ngõ vào ($m$), khoảng cách đến trục đường chính có vỉa hè, tình trạng pháp lý (sổ đỏ riêng / sổ hồng / giấy tờ viết tay) và định dạng hàm logarit ($\ln(\text{Price})$) để chuẩn hóa phân phối dữ liệu.
3. **Nâng cấp nền tảng WebGIS:** Tích hợp máy chủ bản đồ chuyên nghiệp **GeoServer** kết hợp cơ sở dữ liệu không gian phân tán **PostGIS**, triển khai Vector Tiles (MVT) qua Mapbox GL JS / MapLibre GL để tối ưu hóa hiệu năng render hàng chục nghìn điểm dữ liệu bất động sản trong thời gian thực.

---
*Tài liệu được tổng hợp và chuẩn hóa tự động từ toàn bộ mã nguồn, cấu hình QGIS, bảng biểu thực nghiệm và dữ liệu không gian trong đồ án.*
