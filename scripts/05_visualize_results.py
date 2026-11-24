"""
Giai đoạn 5 : Trực quan hóa kết quả mô hình hedonic
Tạo các biểu đồ THỐNG KÊ bổ sung cho báo cáo (khác với bản đồ GIS đã làm trong QGIS):
- Biểu đồ hệ số OLS (đánh dấu biến có ý nghĩa thống kê)
- Giá thực tế vs giá dự đoán (OLS)
- So sánh R² giữa OLS và Random Forest
- Boxplot giá theo khu vực

Input : data/processed/housing_model_ready.csv
        outputs/tables/model_comparison.csv
Output: outputs/figures/ols_coefficients.png
        outputs/figures/actual_vs_predicted.png
        outputs/figures/model_r2_comparison.png
        outputs/figures/price_by_district_boxplot.png

Cài đặt: pip install pandas statsmodels matplotlib
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

INPUT_FILE = "data/processed/housing_model_ready.csv"
COMPARISON_FILE = "outputs/tables/model_comparison.csv"
OUT_FIGS = "outputs/figures"
os.makedirs(OUT_FIGS, exist_ok=True)

# 1. Nạp dữ liệu và khớp lại đúng mô hình OLS như ở bước 04 (để lấy giá trị dự đoán + hệ số)
df = pd.read_csv(INPUT_FILE)
dist_cols = sorted([c for c in df.columns if c.startswith("dist_")])
OLS_NUMERIC = ["dien_tich", "so_tang"] + dist_cols + ["Z_score", "p_value", "p_fdr"]
CATEGORICAL = ["khu_vuc", "loai_nha"]

data = df[["gia_trieu_m2"] + OLS_NUMERIC + CATEGORICAL].dropna()
X_num = data[OLS_NUMERIC]
X_cat = pd.get_dummies(data[CATEGORICAL], drop_first=True)
X = pd.concat([X_num, X_cat], axis=1).astype(float)
X = sm.add_constant(X)
y = data["gia_trieu_m2"].astype(float)

model = sm.OLS(y, X).fit()
pred = model.predict(X)
print(f"Khớp lại OLS: n={len(data)}, R²={model.rsquared:.3f}")

# -------------------------------------------------------------------
# Biểu đồ 1: Hệ số hồi quy OLS — đỏ = có ý nghĩa thống kê (p < 0.05)
# -------------------------------------------------------------------
coef = model.params.drop("const").sort_values()
pval = model.pvalues.drop("const")
colors = ["#d62728" if pval[name] < 0.05 else "#aaaaaa" for name in coef.index]

plt.figure(figsize=(8, 7))
plt.barh(coef.index, coef.values, color=colors)
plt.axvline(0, color="black", linewidth=0.8)
plt.title("Hệ số hồi quy OLS\n(đỏ = có ý nghĩa thống kê, p < 0.05)")
plt.xlabel("Hệ số (ảnh hưởng đến giá/m² — triệu đồng)")
plt.tight_layout()
plt.savefig(f"{OUT_FIGS}/ols_coefficients.png", dpi=150)
plt.close()
print(f"Đã lưu: {OUT_FIGS}/ols_coefficients.png")

# -------------------------------------------------------------------
# Biểu đồ 2: Giá thực tế vs giá dự đoán
# -------------------------------------------------------------------
plt.figure(figsize=(6, 6))
plt.scatter(y, pred, alpha=0.6, edgecolor="white")
lims = [min(y.min(), pred.min()), max(y.max(), pred.max())]
plt.plot(lims, lims, "r--", linewidth=1, label="Dự đoán hoàn hảo")
plt.xlabel("Giá thực tế (triệu/m²)")
plt.ylabel("Giá dự đoán OLS (triệu/m²)")
plt.title(f"Giá thực tế vs dự đoán (R² = {model.rsquared:.3f})")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT_FIGS}/actual_vs_predicted.png", dpi=150)
plt.close()
print(f"Đã lưu: {OUT_FIGS}/actual_vs_predicted.png")

# -------------------------------------------------------------------
# Biểu đồ 3: So sánh R² giữa OLS và Random Forest
# -------------------------------------------------------------------
if os.path.exists(COMPARISON_FILE):
    comp = pd.read_csv(COMPARISON_FILE)
    plt.figure(figsize=(6, 4))
    plt.bar(comp["model"], comp["r2"], color=["#1f77b4", "#2ca02c"])
    plt.ylabel("R²")
    plt.title("So sánh độ phù hợp giữa OLS và Random Forest")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(f"{OUT_FIGS}/model_r2_comparison.png", dpi=150)
    plt.close()
    print(f"Đã lưu: {OUT_FIGS}/model_r2_comparison.png")
else:
    print(f"⚠ Không thấy {COMPARISON_FILE}, bỏ qua biểu đồ so sánh mô hình.")

# -------------------------------------------------------------------
# Biểu đồ 4: Phân bố giá theo khu vực
# -------------------------------------------------------------------
plt.figure(figsize=(6, 5))
df.boxplot(column="gia_trieu_m2", by="khu_vuc")
plt.title("Phân bố giá/m² theo khu vực")
plt.suptitle("")
plt.ylabel("Giá/m² (triệu đồng)")
plt.tight_layout()
plt.savefig(f"{OUT_FIGS}/price_by_district_boxplot.png", dpi=150)
plt.close()
print(f"Đã lưu: {OUT_FIGS}/price_by_district_boxplot.png")

print("\nHoàn tất Giai đoạn 5 — đã tạo đủ 4 biểu đồ thống kê bổ sung cho báo cáo.")