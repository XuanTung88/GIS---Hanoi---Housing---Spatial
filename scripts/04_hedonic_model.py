"""
Bước 04 : So sánh OLS và Random Forest
để dự đoán giá nhà/m2 từ các biến không gian + thống kê Local Moran's I (Z_score, p_value).

Input : data/processed/housing_model_ready
Output: outputs/tables/ols_summary.txt
        outputs/tables/model_comparison.csv
        outputs/figures/rf_feature_importance.png

Cài đặt: pip install pandas scikit-learn statsmodels matplotlib
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score

# File CSV xuất thẳng từ QGIS (layer đã Join Attributes by Location với Gi*/Moran's I)
# Export: chuột phải layer > Export > Save Features As... > CSV
INPUT_FILE = "data/processed/housing_model_ready.csv"
TARGET = "gia_trieu_m2"  # biến Y: giá/m2 (triệu đồng)

OUT_TABLES = "outputs/tables"
OUT_FIGS = "outputs/figures"
os.makedirs(OUT_TABLES, exist_ok=True)
os.makedirs(OUT_FIGS, exist_ok=True)

# 1. Đọc dữ liệu đã join nhãn cluster
if not os.path.exists(INPUT_FILE):
    raise SystemExit(
        f"Không thấy {INPUT_FILE}. Hãy export layer đã gộp Hotspot/Moran's I "
        f"ra CSV trong QGIS trước (xem hướng dẫn), rồi chạy lại."
    )

df = pd.read_csv(INPUT_FILE)
print(f"Đọc {len(df)} dòng, {len(df.columns)} cột: {list(df.columns)}")

# Bỏ các cột trùng lặp dạng "..._2" (sinh ra do bước Join Attributes by Location
# bị khớp dư với chính layer housing — chỉ là bản sao, không chứa thông tin mới).
dist_cols = sorted([c for c in df.columns if c.startswith("dist_") and not c.endswith("_2")])
count_cols = sorted([c for c in df.columns if c.startswith("count_") and not c.endswith("_2")])
duplicate_cols = [c for c in df.columns if c.endswith("_2")]
if duplicate_cols:
    print(f"⚠ Bỏ qua {len(duplicate_cols)} cột trùng lặp '_2' (bản sao dư thừa từ bước Join): {duplicate_cols[:5]}...")

# --- Ép kiểu số an toàn cho toàn bộ cột khoảng cách/mật độ/diện tích/số tầng ---
# Tránh lỗi "Cannot cast ... to dtype float64" khi 1 cột bị đọc sai kiểu.
numeric_candidates = dist_cols + count_cols + [c for c in ["dien_tich", "so_tang"] if c in df.columns]
broken_cols = []
for c in numeric_candidates:
    converted = pd.to_numeric(df[c], errors="coerce")
    if converted.isna().all() and df[c].notna().any():
        # Thử lại coi là số thập phân kiểu Việt Nam (dấu phẩy thay vì dấu chấm),
        # thường gặp khi CSV được QGIS xuất theo locale Windows tiếng Việt.
        converted_vn = pd.to_numeric(df[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        if converted_vn.notna().any():
            print(f"  (tự sửa) '{c}' dùng dấu phẩy thập phân kiểu VN -> đã chuyển đổi lại thành công")
            df[c] = converted_vn
        else:
            broken_cols.append(c)  # thật sự không chuyển được sang số -> loại khỏi mô hình
            sample_raw = df[c].head(5).tolist()
            print(f"  (chẩn đoán) '{c}' không chuyển được sang số. 5 giá trị thô đầu tiên: {sample_raw}")
    else:
        df[c] = converted

if broken_cols:
    print(f"⚠ Loại các cột không chuyển được sang số (kiểm tra lại kiểu dữ liệu trong QGIS): {broken_cols}")
    dist_cols = [c for c in dist_cols if c not in broken_cols]
    count_cols = [c for c in count_cols if c not in broken_cols]

# Cột phân loại thực sự có trong dữ liệu
CATEGORICAL_CANDIDATES = ["khu_vuc", "loai_nha"]
categorical_cols = [c for c in CATEGORICAL_CANDIDATES if c in df.columns]
print(f"Cột phân loại dùng được: {categorical_cols}")

# Cột thống kê không gian dạng SỐ từ Local Moran's I (join trước đó) — dùng trực tiếp
# thay vì tìm nhãn phân loại HH/LL vì file của bạn không có cột đó.
# Lưu ý: Z_score/p_value được TÍNH TỪ chính giá nhà, nên đưa vào mô hình chỉ mang tính
# minh họa mối liên hệ giữa mức độ tụ cụm không gian và giá, không dùng để dự báo thực sự.
MORAN_CANDIDATES = ["Z_score", "p_value", "p_fdr"]
moran_cols = [c for c in MORAN_CANDIDATES if c in df.columns]
if moran_cols:
    print(f"Cột thống kê Local Moran's I dùng được (đưa vào dạng số): {moran_cols}")
else:
    print("Không thấy cột Z_score/p_value — bỏ qua phần thống kê không gian, vẫn chạy bình thường.")
numeric_candidates += moran_cols
for c in moran_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Nếu sau này bạn join thêm kết quả Gi* (thường có tên GiZScore/GiPValue), script sẽ tự nhận luôn
GI_CANDIDATES = ["GiZScore", "GiPValue", "Gi_Bin"]
gi_cols = [c for c in GI_CANDIDATES if c in df.columns]
if gi_cols:
    print(f"Cột thống kê Gi* dùng được: {gi_cols}")
    numeric_candidates += gi_cols
    for c in gi_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
moran_cols += gi_cols

# --- Chẩn đoán: in số dòng bị thiếu (NaN) ở từng cột ứng viên ---
print("\n== Kiểm tra dữ liệu thiếu theo từng cột ==")
all_candidate_cols = [TARGET] + [c for c in ["dien_tich", "so_tang"] if c in df.columns] + dist_cols + moran_cols + categorical_cols
for c in all_candidate_cols:
    n_missing = df[c].isna().sum()
    if n_missing > 0:
        print(f"  {c}: thiếu {n_missing}/{len(df)} dòng ({n_missing / len(df):.0%})")


def filter_usable(df, cols, min_frac=0.7):
    """Loại cột có quá nhiều dòng thiếu dữ liệu (>30%), tránh dropna() xóa sạch toàn bộ dữ liệu."""
    keep, dropped = [], []
    for c in cols:
        frac_ok = df[c].notna().mean()
        if frac_ok >= min_frac:
            keep.append(c)
        else:
            dropped.append((c, frac_ok))
    if dropped:
        print(f"⚠ Loại khỏi mô hình (thiếu quá nhiều dữ liệu): {[(c, f'{f:.0%} đầy đủ') for c, f in dropped]}")
    return keep


# -------------------------------------------------------------------
# MÔ HÌNH 1: OLS — chỉ dùng tập biến gọn (tránh đa cộng tuyến, dễ đọc hệ số)
# -------------------------------------------------------------------
OLS_NUMERIC_RAW = [c for c in ["dien_tich", "so_tang"] if c in df.columns] + dist_cols + moran_cols
OLS_NUMERIC = filter_usable(df, OLS_NUMERIC_RAW)
ols_data = df[[TARGET] + OLS_NUMERIC + categorical_cols].dropna()
print(f"\n[OLS] Còn lại sau khi loại dòng thiếu dữ liệu: {len(ols_data)}/{len(df)} dòng")
if len(ols_data) == 0:
    raise SystemExit(
        "Vẫn còn 0 dòng sau khi lọc — xem danh sách '⚠ Loại khỏi mô hình' ở trên và phần "
        "'Kiểm tra dữ liệu thiếu' để biết chính xác cột nào gây ra, rồi kiểm tra lại bước Join trong QGIS."
    )

X_ols_num = ols_data[OLS_NUMERIC]
X_ols_cat = (
    pd.get_dummies(ols_data[categorical_cols], drop_first=True)
    if categorical_cols
    else pd.DataFrame(index=ols_data.index)
)
X_ols = pd.concat([X_ols_num, X_ols_cat], axis=1).astype(float)
X_ols = sm.add_constant(X_ols)
y_ols = ols_data[TARGET].astype(float)

ols_model = sm.OLS(y_ols, X_ols).fit()
with open(f"{OUT_TABLES}/ols_summary.txt", "w", encoding="utf-8") as f:
    f.write(ols_model.summary().as_text())

print(f"\n[OLS] n = {len(ols_data)}, R² = {ols_model.rsquared:.3f}")
print(f"Đã lưu bảng hệ số: {OUT_TABLES}/ols_summary.txt")

# -------------------------------------------------------------------
# MÔ HÌNH 2: Random Forest — dùng toàn bộ biến không gian (dist_ + count_)
# để xem biến nào quan trọng nhất, không cần giả định tuyến tính.
# -------------------------------------------------------------------
RF_NUMERIC_RAW = [c for c in ["dien_tich", "so_tang"] if c in df.columns] + dist_cols + count_cols + moran_cols
RF_NUMERIC = filter_usable(df, RF_NUMERIC_RAW)
rf_data = df[[TARGET] + RF_NUMERIC + categorical_cols].dropna()
print(f"[Random Forest] Còn lại sau khi loại dòng thiếu dữ liệu: {len(rf_data)}/{len(df)} dòng")
if len(rf_data) == 0:
    raise SystemExit("Vẫn còn 0 dòng cho Random Forest — xem log '⚠ Loại khỏi mô hình' ở trên.")

X_rf_num = rf_data[RF_NUMERIC]
X_rf_cat = (
    pd.get_dummies(rf_data[categorical_cols], drop_first=True)
    if categorical_cols
    else pd.DataFrame(index=rf_data.index)
)
X_rf = pd.concat([X_rf_num, X_rf_cat], axis=1)
y_rf = rf_data[TARGET]

rf = RandomForestRegressor(n_estimators=300, max_depth=6, random_state=42)
kf = KFold(n_splits=5, shuffle=True, random_state=42)

r2_scores = cross_val_score(rf, X_rf, y_rf, cv=kf, scoring="r2")
mae_scores = -cross_val_score(rf, X_rf, y_rf, cv=kf, scoring="neg_mean_absolute_error")

print(f"\n[Random Forest] n = {len(rf_data)}, 5-fold CV")
print(f"  R² trung bình  : {r2_scores.mean():.3f} (+/- {r2_scores.std():.3f})")
print(f"  MAE trung bình : {mae_scores.mean():.2f} triệu/m²")
print("  Lưu ý: n nhỏ (121 dòng) -> kết quả CV chỉ mang tính tham khảo, không nên diễn giải quá chắc chắn.")

# Huấn luyện lại trên toàn bộ dữ liệu để lấy feature importance
rf.fit(X_rf, y_rf)
importance = pd.Series(rf.feature_importances_, index=X_rf.columns).sort_values(ascending=False)

plt.figure(figsize=(8, 6))
importance.head(10).sort_values().plot(kind="barh")
plt.title("Random Forest - Top 10 biến quan trọng nhất")
plt.xlabel("Độ quan trọng (feature importance)")
plt.tight_layout()
plt.savefig(f"{OUT_FIGS}/rf_feature_importance.png", dpi=150)
plt.close()
print(f"Đã lưu biểu đồ: {OUT_FIGS}/rf_feature_importance.png")

# -------------------------------------------------------------------
# Bảng so sánh 2 mô hình
# -------------------------------------------------------------------
comparison = pd.DataFrame(
    {
        "model": ["OLS (toàn bộ dữ liệu, biến gọn)", "Random Forest (5-fold CV, toàn bộ biến)"],
        "n_obs": [len(ols_data), len(rf_data)],
        "n_features": [X_ols.shape[1] - 1, X_rf.shape[1]],
        "r2": [round(ols_model.rsquared, 3), round(r2_scores.mean(), 3)],
    }
)
comparison.to_csv(f"{OUT_TABLES}/model_comparison.csv", index=False, encoding="utf-8-sig")
print(f"\nĐã lưu bảng so sánh: {OUT_TABLES}/model_comparison.csv")
print(comparison.to_string(index=False))

print("\nTop 5 biến quan trọng nhất (Random Forest):")
print(importance.head(5))