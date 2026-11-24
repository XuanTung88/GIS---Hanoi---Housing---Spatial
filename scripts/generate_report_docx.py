# -*- coding: utf-8 -*-
"""
Script: generate_report_docx.py
Mục đích: Tự động khởi tạo và biên soạn tài liệu Báo cáo đồ án môn học
          Hệ thống thông tin không gian (GIS) sang định dạng chuẩn Microsoft Word (.docx).
Đề tài: PHÂN TÍCH KHÔNG GIAN VÀ ĐỊNH GIÁ BẤT ĐỘNG SẢN NHÀ Ở TẠI KHU VỰC TRUNG TÂM HÀ NỘI

Cập nhật theo yêu cầu:
1. Cỡ chữ văn bản mặc định là 13pt, chữ trong bảng là 12pt.
2. Số hiệu trang ở footer: chỉ để 1 số thôi, bỏ chữ đi (căn giữa).
3. Bỏ bôi đậm các mục con / gạch đầu dòng trong các tiểu mục, CHỈ bôi đậm đề mục chính (Heading 1, 2, 3).
"""

import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "report"
OUTPUT_FILE = OUTPUT_DIR / "Bao_Cao_Mon_Hoc_GIS_Nhom_BDS_HaNoi.docx"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

doc = Document()

# -------------------------------------------------------------
# CẤU HÌNH TRANG IN KHỔ A4 & CĂN LỀ CHUẨN ĐỒ ÁN (LEFT=3cm ĐỂ ĐÓNG GÁY)
# -------------------------------------------------------------
for s in doc.sections:
    s.page_width = Cm(21.0)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(2.0)
    s.bottom_margin = Cm(2.0)
    s.left_margin = Cm(3.0)
    s.right_margin = Cm(2.0)

# Cấu hình Default Style: Cỡ chữ mặc định 13pt
style_normal = doc.styles['Normal']
font = style_normal.font
font.name = 'Times New Roman'
font.size = Pt(13)
font.color.rgb = RGBColor(20, 20, 20)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="B0C4DE", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_header_footer(doc):
    """Đánh số trang: Loại bỏ chữ rườm rà, chỉ để 1 số duy nhất căn giữa."""
    for sec in doc.sections:
        footer = sec.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ft.paragraph_format.space_before = Pt(0)
        p_ft.paragraph_format.space_after = Pt(0)
        p_ft.text = ""  # Xóa sạch mọi text rườm rà
        
        run_pg = p_ft.add_run()
        run_pg.font.name = "Times New Roman"
        run_pg.font.size = Pt(11)
        run_pg.font.color.rgb = RGBColor(60, 60, 60)
        
        # Chỉ chèn duy nhất mã trường PAGE (số trang)
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        run_pg._r.append(fldSimple)

def add_heading_1(doc, text):
    """Đề mục cấp 1: Bôi đậm."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(15)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 51, 102) # Navy Blue
    return p

def add_heading_2(doc, text):
    """Đề mục cấp 2: Bôi đậm."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(20, 40, 80)
    return p

def add_heading_3(doc, text):
    """Đề mục cấp 3: Bôi đậm."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.italic = True
    run.font.color.rgb = RGBColor(40, 40, 40)
    return p

def add_body_paragraph(doc, text, bold_prefix="", indent=True):
    """Đoạn văn thân bài: Cỡ chữ 13pt, BỎ BÔI ĐẬM mọi mục con."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.3
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.first_line_indent = Cm(1.0)
    else:
        p.paragraph_format.first_line_indent = Cm(0)
    
    full_text = (bold_prefix + text) if bold_prefix else text
    r_body = p.add_run(full_text)
    r_body.font.name = "Times New Roman"
    r_body.font.size = Pt(13)
    r_body.font.bold = False  # Bỏ bôi đậm mục con theo yêu cầu
    return p

def add_bullet_item(doc, text, bold_prefix=""):
    """Mục gạch đầu dòng: Cỡ chữ 13pt, BỎ BÔI ĐẬM mọi mục con."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.25
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(-0.5)
    p.paragraph_format.left_indent = Cm(1.2)
    
    full_text = (bold_prefix + text) if bold_prefix else text
    r_body = p.add_run(full_text)
    r_body.font.name = "Times New Roman"
    r_body.font.size = Pt(13)
    r_body.font.bold = False  # Bỏ bôi đậm mục con theo yêu cầu
    return p

def add_figure_image(doc, img_rel_path, caption, width_inch=5.2):
    img_full_path = PROJECT_ROOT / img_rel_path
    if img_full_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(7)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_full_path), width=Inches(width_inch))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(7)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(11)
        r_cap.font.italic = True
        r_cap.font.bold = False
        r_cap.font.color.rgb = RGBColor(60, 60, 60)
    else:
        print(f"Warning: Image not found at {img_full_path}")

def add_placeholder_box(doc, title, note_text, height_pt=120):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(5.8)
    set_cell_background(cell, "F8F9FA")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="dashed" w:sz="6" w:space="0" w:color="003366"/>
            <w:bottom w:val="dashed" w:sz="6" w:space="0" w:color="003366"/>
            <w:left w:val="dashed" w:sz="6" w:space="0" w:color="003366"/>
            <w:right w:val="dashed" w:sz="6" w:space="0" w:color="003366"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(height_pt // 3)
    p.paragraph_format.space_after = Pt(2)
    r1 = p.add_run(f"📷 [{title}]\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(12)
    r1.font.bold = False
    r1.font.color.rgb = RGBColor(0, 51, 102)
    
    r2 = p.add_run(f"({note_text})")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(120, 120, 120)
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(3)
    p_cap.paragraph_format.space_after = Pt(7)
    rc = p_cap.add_run(title)
    rc.font.name = "Times New Roman"
    rc.font.size = Pt(11)
    rc.font.italic = True
    rc.font.bold = False
    rc.font.color.rgb = RGBColor(60, 60, 60)

def add_table_custom(doc, headers, data, col_widths=None):
    """Bảng dữ liệu: Cỡ chữ trong bảng là 12pt."""
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="B0C4DE", sz="6", val="single")
    
    # Header Row: Cỡ chữ 12pt
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "003366")
        set_cell_margins(hdr_cells[i], top=80, bottom=80, left=90, right=90)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(12)  # Cỡ chữ bảng 12
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
    
    # Data Rows: Cỡ chữ 12pt
    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        bg_color = "F9FBFD" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            row_cells[col_idx].text = str(text)
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=50, bottom=50, left=70, right=70)
            p = row_cells[col_idx].paragraphs[0]
            if col_idx in [0, 1] and len(headers) > 4:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif col_idx in [len(headers) - 1, len(headers) - 2]:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)  # Cỡ chữ bảng 12
                r.font.bold = False  # Bỏ bôi đậm trong nội dung ô
                r.font.color.rgb = RGBColor(30, 30, 30)

    # Set Column widths
    if col_widths and len(col_widths) == len(headers):
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)
                
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)
    return table

print("[+] Bắt đầu tạo nội dung tài liệu Word cập nhật...")

# =============================================================
# 1. TRANG BÌA CHÍNH (COVER PAGE)
# =============================================================
p_uni = doc.add_paragraph()
p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_uni.paragraph_format.space_before = Pt(10)
p_uni.paragraph_format.space_after = Pt(2)
r = p_uni.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\nTRƯỜNG ĐẠI HỌC CÔNG NGHỆ / KHOA HỌC TỰ NHIÊN\n")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.font.bold = True

r_fac = p_uni.add_run("KHOA CÔNG NGHỆ THÔNG TIN - BỘ MÔN HỆ THỐNG THÔNG TIN\n")
r_fac.font.name = "Times New Roman"
r_fac.font.size = Pt(12.5)
r_fac.font.bold = True
r_fac.font.color.rgb = RGBColor(0, 51, 102)

p_line = doc.add_paragraph()
p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_line.paragraph_format.space_before = Pt(0)
p_line.paragraph_format.space_after = Pt(36)
r_line = p_line.add_run("-----------------------***-----------------------")
r_line.font.bold = True

p_logo = doc.add_paragraph()
p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_logo.paragraph_format.space_before = Pt(10)
p_logo.paragraph_format.space_after = Pt(30)
r_type = p_logo.add_run("BÁO CÁO KẾT THÚC HỌC PHẦN\nHỆ THỐNG THÔNG TIN KHÔNG GIAN (GIS)\n")
r_type.font.name = "Times New Roman"
r_type.font.size = Pt(16)
r_type.font.bold = True
r_type.font.color.rgb = RGBColor(180, 0, 0)

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(10)
p_title.paragraph_format.space_after = Pt(30)
r_tit = p_title.add_run("ĐỀ TÀI:\nPHÂN TÍCH KHÔNG GIAN VÀ ĐỊNH GIÁ BẤT ĐỘNG SẢN NHÀ Ở\nTẠI KHU VỰC TRUNG TÂM HÀ NỘI\n")
r_tit.font.name = "Times New Roman"
r_tit.font.size = Pt(18)
r_tit.font.bold = True
r_tit.font.color.rgb = RGBColor(0, 51, 102)

r_sub = p_title.add_run("(Ứng dụng QGIS, PostGIS, Kinh tế lượng Hedonic và Nền tảng WebGIS Tương tác)")
r_sub.font.name = "Times New Roman"
r_sub.font.size = Pt(13)
r_sub.font.italic = True
r_sub.font.bold = False
r_sub.font.color.rgb = RGBColor(80, 80, 80)

p_info = doc.add_paragraph()
p_info.alignment = WD_ALIGN_PARAGRAPH.LEFT
p_info.paragraph_format.space_before = Pt(50)
p_info.paragraph_format.space_after = Pt(40)
p_info.paragraph_format.left_indent = Cm(3.5)

r_sv = p_info.add_run("Sinh viên thực hiện  :  NHÓM SINH VIÊN NGHIÊN CỨU\n"
                      "Mã số sinh viên      :  Học kỳ 7 - Chuyên ngành GIS / CNTT\n"
                      "Lớp học phần         :  Hệ thống thông tin địa lý (GIS)\n"
                      "Giảng viên hướng dẫn :  TS. GIẢNG VIÊN PHỤ TRÁCH MÔN HỌC\n")
r_sv.font.name = "Times New Roman"
r_sv.font.size = Pt(12.5)
r_sv.font.bold = True

p_loc = doc.add_paragraph()
p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_loc.paragraph_format.space_before = Pt(40)
p_loc.paragraph_format.space_after = Pt(0)
r_loc = p_loc.add_run("HÀ NỘI – NĂM 2026")
r_loc.font.name = "Times New Roman"
r_loc.font.size = Pt(12)
r_loc.font.bold = True

doc.add_page_break()

# =============================================================
# 2. PHIẾU CHẤM ĐIỂM BÁO CÁO CHUYÊN ĐỀ
# =============================================================
p_eval_title = doc.add_paragraph()
p_eval_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_eval_title.paragraph_format.space_before = Pt(10)
p_eval_title.paragraph_format.space_after = Pt(14)
r_ev = p_eval_title.add_run("PHIẾU ĐÁNH GIÁ KẾT QUẢ BÁO CÁO HỌC PHẦN")
r_ev.font.name = "Times New Roman"
r_ev.font.size = Pt(14)
r_ev.font.bold = True
r_ev.font.color.rgb = RGBColor(0, 51, 102)

add_body_paragraph(doc, "Tên đề tài: PHÂN TÍCH KHÔNG GIAN VÀ ĐỊNH GIÁ BẤT ĐỘNG SẢN NHÀ Ở TẠI KHU VỰC TRUNG TÂM HÀ NỘI", bold_prefix="1. ", indent=False)
add_body_paragraph(doc, "Họ và tên sinh viên / Nhóm thực hiện: Nhóm sinh viên thực hiện đồ án GIS", bold_prefix="2. ", indent=False)
add_body_paragraph(doc, "Cán bộ chấm 1: .....................................................................   Chữ ký: ...............................", bold_prefix="3. ", indent=False)
add_body_paragraph(doc, "Cán bộ chấm 2: .....................................................................   Chữ ký: ...............................", bold_prefix="4. ", indent=False)

eval_headers = ["STT", "Nội dung / Tiêu chí đánh giá", "Điểm tối đa", "Điểm CB 1", "Điểm CB 2"]
eval_data = [
    ["1", "Tổng quan đề tài, tính cấp thiết và mục tiêu nghiên cứu", "1.0", "", ""],
    ["2", "Nắm vững lý thuyết GIS, các mô hình dữ liệu (Vector, Raster)", "1.5", "", ""],
    ["3", "Kỹ năng thu thập, xử lý và làm sạch dữ liệu không gian OSM, Chợ Tốt", "1.5", "", ""],
    ["4", "Thực hiện thành thạo công cụ QGIS (IDW, Hotspot Gi*, Local Moran's I)", "2.0", "", ""],
    ["5", "Xây dựng mô hình kinh tế lượng Hedonic OLS và Học máy Random Forest", "1.5", "", ""],
    ["6", "Xây dựng ứng dụng WebGIS tương tác, truy vấn bán kính động PostGIS", "1.5", "", ""],
    ["7", "Hình thức trình bày báo cáo đúng quy chuẩn, cấu trúc mạch lạc", "1.0", "", ""],
    ["", "TỔNG CỘNG", "10.0", "", ""]
]
add_table_custom(doc, eval_headers, eval_data, col_widths=[0.6, 3.1, 0.8, 0.9, 0.9])

add_body_paragraph(doc, "NHẬN XÉT VÀ ĐÁNH GIÁ CỦA CÁN BỘ CHẤM:", bold_prefix="5. ", indent=False)
add_body_paragraph(doc, "........................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................", indent=False)

doc.add_page_break()

# =============================================================
# 3. LỜI CẢM ƠN (3/4 TRANG)
# =============================================================
p_ack = doc.add_paragraph()
p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_ack.paragraph_format.space_before = Pt(10)
p_ack.paragraph_format.space_after = Pt(16)
r_ack = p_ack.add_run("LỜI CẢM ƠN")
r_ack.font.name = "Times New Roman"
r_ack.font.size = Pt(15)
r_ack.font.bold = True
r_ack.font.color.rgb = RGBColor(0, 51, 102)

add_body_paragraph(doc, "Để hoàn thành báo cáo chuyên đề kết thúc học phần Hệ thống thông tin không gian (GIS) với đề tài: \"Phân tích không gian và định giá bất động sản nhà ở tại khu vực trung tâm Hà Nội\", chúng em xin bày tỏ lòng biết ơn chân thành và sâu sắc nhất tới quý Thầy, Cô giáo trong Bộ môn Hệ thống thông tin, Khoa Công nghệ Thông tin đã tận tình truyền đạt những kiến thức nền tảng quý báu về khoa học địa lý, xử lý dữ liệu không gian và kinh tế lượng ứng dụng trong suốt quá trình học tập.")

add_body_paragraph(doc, "Đặc biệt, chúng em xin gửi lời cảm ơn sâu sắc tới Giảng viên phụ trách học phần, Thầy/Cô đã dành nhiều thời gian quý báu để định hướng phương pháp luận, hướng dẫn cách tiếp cận các công cụ mã nguồn mở hiện đại như phần mềm QGIS, hệ quản trị cơ sở dữ liệu không gian PostGIS, các thuật toán không gian SciPy cKDTree, cũng như cách thức xây dựng mô hình định giá vi mô Hedonic. Những lời chỉ dẫn tận tâm và các góp ý học thuật sắc bén của Thầy/Cô là kim chỉ nam giúp chúng em tháo gỡ nhiều rào cản kỹ thuật phức tạp trong quá trình phân tích không gian và phát triển ứng dụng WebGIS.")

add_body_paragraph(doc, "Chúng em cũng xin chân thành cảm ơn các bạn sinh viên trong lớp học phần đã luôn đồng hành, trao đổi và chia sẻ kinh nghiệm xử lý dữ liệu thực tế. Mặc dù đã dành trọn vẹn tâm huyết và nỗ lực để hoàn thiện báo cáo một cách khoa học, chỉn chu nhất, song do kiến thức và kinh nghiệm thực tiễn còn bước đầu trau dồi, cuốn báo cáo khó tránh khỏi những thiếu sót nhất định. Nhóm nghiên cứu rất mong nhận được những nhận xét, góp ý quý báu của quý Thầy/Cô để đồ án được hoàn thiện sâu sắc hơn.")

p_sign = doc.add_paragraph()
p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
p_sign.paragraph_format.space_before = Pt(20)
p_sign.paragraph_format.space_after = Pt(0)
r_sig = p_sign.add_run("Hà Nội, tháng 11 năm 2026\nNhóm sinh viên thực hiện đề tài\n(Ký và ghi rõ họ tên)")
r_sig.font.name = "Times New Roman"
r_sig.font.size = Pt(12)
r_sig.font.italic = True
r_sig.font.bold = False

doc.add_page_break()

# =============================================================
# 4. TÓM TẮT ĐỀ TÀI / LỜI MỞ ĐẦU (3/4 TRANG)
# =============================================================
p_abs = doc.add_paragraph()
p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_abs.paragraph_format.space_before = Pt(10)
p_abs.paragraph_format.space_after = Pt(16)
r_abs = p_abs.add_run("TÓM TẮT ĐỀ TÀI")
r_abs.font.name = "Times New Roman"
r_abs.font.size = Pt(15)
r_abs.font.bold = True
r_abs.font.color.rgb = RGBColor(0, 51, 102)

add_body_paragraph(doc, "Bất động sản nhà ở tại khu vực trung tâm Thủ đô Hà Nội (đặc biệt là 3 quận lõi lịch sử: Ba Đình, Hoàn Kiếm, Đống Đa) mang tính đặc thù cao với mật độ cư dân dày đặc, mạng lưới hạ tầng phức hợp và sự phân hóa giá đất sâu sắc. Định giá bất động sản truyền thống thường chủ yếu dựa trên các đặc tính vật lý đơn thuần (diện tích, số tầng) mà thiếu đi công cụ định lượng khoa học phản ánh tác động của vị trí không gian và khả năng tiếp cận hệ sinh thái tiện ích đô thị xung quanh.")

add_body_paragraph(doc, "Báo cáo này nghiên cứu và hiện thực hóa một quy trình khoa học dữ liệu không gian khép kín (Spatial Data Science Pipeline) tích hợp giữa GIS, Kinh tế lượng không gian và Học máy để giải quyết bài toán lượng giá nhà đất đô thị. Nghiên cứu khai thác dữ liệu đa nguồn gồm 121 tin rao bất động sản hợp lệ gắn tọa độ thực tế và 7 lớp tiện ích công cộng trích xuất từ OpenStreetMap (với hơn 1,000 thực thể trường học, bệnh viện, công viên, siêu thị, chợ dân sinh, trạm xe buýt và hồ cảnh quan). Thông qua thuật toán tìm kiếm đa chiều SciPy cKDTree, nghiên cứu đã lượng hóa chính xác cự ly hình học và mật độ tiện ích trong các vùng đệm đi bộ (300m, 500m, 1,000m).")

add_body_paragraph(doc, "Trên nền tảng QGIS, nghiên cứu đã thiết lập bản đồ bề mặt nội suy giá liên tục IDW, xác định 26 điểm cực nóng giá trị cao tại Hoàn Kiếm qua thống kê Getis-Ord Gi*, và nhận diện các điểm ngoại lai không gian đặc thù (nhà mặt phố kinh doanh trong vùng giá thấp và nhà ngõ sâu trong vùng lõi) qua Local Moran's I (LISA). Mô hình định giá Hedonic OLS đạt R² = 0.407, chỉ ra mối liên hệ có ý nghĩa thống kê cao giữa giá nhà với vị trí Hoàn Kiếm (+202 triệu VNĐ/m²), nhà mặt phố (+88 triệu VNĐ/m²) và khoảng cách tới hồ nước (mỗi mét xa hồ làm giá giảm ~209,000 VNĐ/m²). Đồng thời, nhóm nghiên cứu đã thiết kế và phát triển thành công nền tảng WebGIS tương tác full-stack (Node.js/Express + PostGIS + Leaflet.js + Chart.js) hỗ trợ truy vấn bán kính động linh hoạt và hiển thị dashboard thống kê trực quan.")

doc.add_page_break()

# =============================================================
# 5. DANH MỤC TỪ VIẾT TẮT, BẢNG BIỂU & HÌNH VẼ
# =============================================================
add_heading_1(doc, "DANH MỤC CÁC TỪ VIẾT TẮT")
abbr_headers = ["Từ viết tắt", "Thuật ngữ tiếng Anh", "Ý nghĩa tiếng Việt"]
abbr_data = [
    ["GIS", "Geographic Information System", "Hệ thống thông tin địa lý / không gian"],
    ["OSM", "OpenStreetMap", "Nền tảng dữ liệu bản đồ mở toàn cầu"],
    ["QGIS", "Quantum GIS", "Phần mềm mã nguồn mở biên tập và phân tích GIS"],
    ["PostGIS", "Spatial Extension for PostgreSQL", "Phần mở rộng cơ sở dữ liệu không gian cho PostgreSQL"],
    ["IDW", "Inverse Distance Weighting", "Phương pháp nội suy khoảng cách nghịch đảo có trọng số"],
    ["LISA", "Local Indicators of Spatial Association", "Chỉ số liên kết không gian cục bộ (Local Moran's I)"],
    ["OLS", "Ordinary Least Squares", "Phương pháp bình phương bé nhất thông thường"],
    ["RF", "Random Forest", "Thuật toán học máy Rừng ngẫu nhiên"],
    ["WGS 84", "World Geodetic System 1984", "Hệ quy chiếu tọa độ trắc địa elipsoid quốc tế (EPSG:4326)"],
    ["UTM", "Universal Transverse Mercator", "Hệ tọa độ phẳng phép chiếu hình trụ ngang (EPSG:32648)"],
    ["CV", "Cross-Validation", "Kỹ thuật kiểm định chéo đánh giá mô hình"],
    ["MAE", "Mean Absolute Error", "Sai số tuyệt đối trung bình"]
]
add_table_custom(doc, abbr_headers, abbr_data, col_widths=[1.2, 2.4, 2.7])

add_heading_1(doc, "DANH MỤC CÁC BẢNG BIỂU")
tbl_list_headers = ["Ký hiệu bảng", "Tên bảng biểu", "Trang"]
tbl_list_data = [
    ["Bảng 1.1", "Ma trận so sánh đặc tính mô hình dữ liệu Vector và Raster", "10"],
    ["Bảng 2.1", "Danh mục các thư viện Python chuyên dụng trong dự án", "14"],
    ["Bảng 3.1", "Quy mô thu thập dữ liệu 7 nhóm tiện ích đô thị từ OSM", "17"],
    ["Bảng 3.2", "Cấu trúc trường dữ liệu bảng housing trong cơ sở dữ liệu", "19"],
    ["Bảng 3.3", "Kết quả phân nhóm điểm nóng - điểm lạnh Getis-Ord Gi*", "22"],
    ["Bảng 3.4", "Kết quả phân tích tự tương quan không gian cục bộ Local Moran's I", "23"],
    ["Bảng 3.5", "Bảng kết quả ước lượng mô hình hồi quy OLS Hedonic", "26"],
    ["Bảng 3.6", "Bảng so sánh độ phù hợp giữa OLS và Random Forest", "27"],
    ["Bảng 3.7", "Danh mục các điểm cuối (Endpoints) của hệ thống RESTful API", "29"]
]
add_table_custom(doc, tbl_list_headers, tbl_list_data, col_widths=[1.3, 4.2, 0.8])

add_heading_1(doc, "DANH MỤC CÁC HÌNH VẼ")
fig_list_headers = ["Ký hiệu hình", "Tên hình minh họa", "Trang"]
fig_list_data = [
    ["Hình 1.1", "Bản đồ ranh giới hành chính khu vực nghiên cứu 3 quận trung tâm", "9"],
    ["Hình 2.1", "Sơ đồ kiến trúc luồng dữ liệu không gian tổng thể của đề tài", "15"],
    ["Hình 3.1", "Phân bố 121 điểm bất động sản khảo sát trên hệ tọa độ mét UTM 48N", "18"],
    ["Hình 3.2", "Bản đồ bề mặt nội suy giá đất liên tục IDW tại 3 quận trung tâm", "21"],
    ["Hình 3.3", "Bản đồ phân tích điểm nóng (Hot Spot Analysis - Getis-Ord Gi*)", "22"],
    ["Hình 3.4", "Bản đồ tự tương quan không gian cục bộ LISA (Local Moran's I)", "24"],
    ["Hình 3.5", "Kết quả phép truy vấn thuộc tính (Select by Expression) trên QGIS", "24"],
    ["Hình 3.6", "Kết quả phép truy vấn cự ly không gian (Select within Distance)", "25"],
    ["Hình 3.7", "Kết quả thực hiện phép ghép thuộc tính không gian (Spatial Join)", "25"],
    ["Hình 3.8", "Biểu đồ hệ số hồi quy OLS kèm đánh dấu mức ý nghĩa thống kê", "26"],
    ["Hình 3.9", "Biểu đồ phân tán so sánh giá thực tế vs giá dự đoán của mô hình OLS", "27"],
    ["Hình 3.10", "Biểu đồ hộp (Boxplot) phân bố đơn giá nhà đất theo 3 quận", "28"],
    ["Hình 3.11", "Biểu đồ xếp hạng mức độ quan trọng của biến trong Random Forest", "28"],
    ["Hình 4.1", "Giao diện Bản đồ WebGIS tương tác và điều khiển phân lớp tiện ích", "30"],
    ["Hình 4.2", "Giao diện bộ lọc bất động sản và công cụ truy vấn bán kính động", "31"],
    ["Hình 4.3", "Giao diện phân hệ Báo cáo phân tích mô hình kinh tế lượng", "31"],
    ["Hình 4.4", "Giao diện phân hệ Thư viện bản đồ chuyên đề QGIS độ phân giải cao", "32"]
]
add_table_custom(doc, fig_list_headers, fig_list_data, col_widths=[1.3, 4.2, 0.8])

doc.add_page_break()

# Thêm Header & Footer: Chỉ để duy nhất 1 số trang căn giữa, không có chữ
add_header_footer(doc)

# =============================================================
# CHƯƠNG 1: TỔNG QUAN VỀ HỆ THỐNG THÔNG TIN KHÔNG GIAN (GIS)
# =============================================================
add_heading_1(doc, "CHƯƠNG 1: TỔNG QUAN VỀ HỆ THỐNG THÔNG TIN KHÔNG GIAN (GIS)")

add_heading_2(doc, "1.1. Đặt vấn đề và lý do chọn đề tài")
add_body_paragraph(doc, "Trong nền kinh tế thị trường hiện đại, bất động sản luôn là một trong những tài sản có giá trị kinh tế đặc biệt lớn và đóng vai trò huyết mạch trong cơ cấu tài sản xã hội. Tại các đô thị đặc biệt như Thủ đô Hà Nội, đất đai không chỉ đơn thuần là không gian sinh tồn mà còn là nguồn lực tài chính mang tính chiến lược. Thị trường bất động sản nhà ở tại khu vực trung tâm Hà Nội — cụ thể là ba quận lõi lịch sử gồm Ba Đình, Hoàn Kiếm và Đống Đa — luôn chứng kiến mức biến động giá rất phức tạp, mặt bằng giá đất thuộc nhóm đắt đỏ nhất cả nước và có sự phân hóa cục bộ cực kỳ mạnh mẽ giữa các tuyến phố, ngõ hẻm và các phân khu chức năng.")

add_body_paragraph(doc, "Về mặt kinh tế học đô thị, giá trị của một căn nhà được hình thành từ sự kết hợp của hai nhóm yếu tố chính: (1) Các đặc tính vật lý nội tại của công trình (như diện tích sử dụng, số tầng xây dựng, kết cấu kiến trúc, độ rộng mặt tiền); và (2) Các yếu tố ngoại ứng không gian bắt nguồn từ vị trí địa lý (như cự ly tiếp cận trường học, bệnh viện, công viên cây xanh, hồ điều hòa, chợ dân sinh, siêu thị và hệ thống giao thông công cộng). Tuy nhiên, trên thực tế tại Việt Nam, các phương pháp định giá bất động sản truyền thống (như phương pháp so sánh trực tiếp, phương pháp chi phí) thường mang nặng tính chủ quan của chuyên viên thẩm định giá, thiếu các mô hình toán học lượng hóa và đặc biệt là chưa khai thác được sức mạnh to lớn của Hệ thống thông tin địa lý (GIS) trong việc phân tích các mối tương quan không gian đa biến.")

add_body_paragraph(doc, "Sự phát triển mạnh mẽ của khoa học dữ liệu không gian (Spatial Data Science) và công nghệ WebGIS mở ra cơ hội đột phá để tiếp cận bài toán lượng giá nhà đất theo hướng khách quan, minh bạch và khoa học. Xuất phát từ bối cảnh thực tiễn trên, nhóm nghiên cứu đã lựa chọn đề tài: \"Phân tích không gian và định giá bất động sản nhà ở tại khu vực trung tâm Hà Nội\" làm đề tài báo cáo môn học Hệ thống thông tin không gian (GIS). Đề tài hướng tới việc tích hợp dữ liệu bản đồ mở (OpenStreetMap), dữ liệu giao dịch bất động sản thực tế và các thuật toán GIS tiên tiến nhằm giải mã quy luật địa tô và xây dựng nền tảng hỗ trợ ra quyết định thông minh.")

add_heading_2(doc, "1.2. Mục tiêu nghiên cứu và phạm vi thực hiện")
add_heading_3(doc, "1.2.1. Mục tiêu nghiên cứu")
add_bullet_item(doc, "Ứng dụng các công cụ GIS mã nguồn mở để thu thập, chuẩn hóa và xây dựng cơ sở dữ liệu địa không gian đa tầng tích hợp giữa tin rao bất động sản và hệ thống tiện ích dịch vụ công cộng tại khu vực trung tâm thành phố.", bold_prefix="Mục tiêu dữ liệu: ");
add_bullet_item(doc, "Vận dụng các thuật toán hình học tính toán (như cấu trúc cây nhị phân đa chiều cKDTree) để lượng hóa chính xác cự ly trắc địa từ từng căn nhà tới các tiện ích đô thị gần nhất và đo lường mật độ tiện ích trong các bán kính đi bộ.", bold_prefix="Mục tiêu đặc trưng không gian: ");
add_bullet_item(doc, "Thực hiện các phân tích không gian chuyên sâu trên phần mềm QGIS: thiết lập bản đồ bề mặt nội suy giá liên tục (IDW), định vị các cực tập trung giá trị cao/thấp (Getis-Ord Gi*) và nhận diện các điểm dị biệt không gian cục bộ (Local Moran's I).", bold_prefix="Mục tiêu phân tích GIS: ");
add_bullet_item(doc, "Xây dựng mô hình định giá kinh tế lượng vi mô Hedonic OLS và mô hình học máy Random Forest để xác định các yếu tố địa lý có ý nghĩa thống kê chi phối giá nhà đất.", bold_prefix="Mục tiêu kinh tế lượng: ");
add_bullet_item(doc, "Thiết kế và triển khai ứng dụng WebGIS tương tác full-stack phục vụ người dùng cuối tra cứu thông tin, lọc đa tiêu chí và thực hiện các phép truy vấn không gian bán kính động trực tiếp trên trình duyệt.", bold_prefix="Mục tiêu ứng dụng: ");

add_heading_3(doc, "1.2.2. Phạm vi thực hiện")
add_body_paragraph(doc, "Phạm vi không gian của đề tài giới hạn tại 3 quận nội thành trung tâm của Thủ đô Hà Nội: Quận Hoàn Kiếm, Quận Ba Đình và Quận Đống Đa. Đây là khu vực có tính chất lịch sử lâu đời, mật độ dân cư và hoạt động kinh tế thương mại sầm uất nhất thành phố, là môi trường lý tưởng để kiểm nghiệm các quy luật tương quan địa không gian. Về phạm vi dữ liệu, đề tài tập trung vào phân khúc nhà ở riêng lẻ (nhà mặt phố và nhà ngõ hẻm), không bao gồm căn hộ chung cư cao tầng do chung cư có đặc thù định giá theo tầng cao và tiện ích nội khu tòa nhà.")

add_figure_image(doc, "data/raw/region.png", "Hình 1.1: Bản đồ ranh giới hành chính khu vực nghiên cứu 3 quận trung tâm Hà Nội", width_inch=4.8)

add_heading_2(doc, "1.3. Khái niệm và các thành phần cốt lõi của GIS")
add_heading_3(doc, "1.3.1. Khái niệm Hệ thống thông tin không gian (GIS)")
add_body_paragraph(doc, "Hệ thống thông tin không gian (Geographic Information System - GIS) là một hệ thống tích hợp bao gồm phần cứng, phần mềm, dữ liệu không gian, con người và quy trình tác nghiệp, được thiết kế nhằm thu thập, lưu trữ, cập nhật, thao tác, phân tích và trực quan hóa mọi dạng thông tin mang thuộc tính địa lý trên bề mặt Trái Đất. Điểm khác biệt căn bản giữa GIS và các hệ thống thông tin quản lý (MIS) truyền thống là GIS gắn kết chặt chẽ dữ liệu thuộc tính (Attribute data - các đại lượng mô tả \"Cái gì?\") với dữ liệu không gian (Spatial data - tọa độ xác định \"Ở đâu?\") thông qua một hệ tọa độ quy chiếu thống nhất.")

add_heading_3(doc, "1.3.2. Năm thành phần cốt lõi của hệ thống GIS trong đề tài")
add_bullet_item(doc, "Bao gồm máy trạm tính toán phục vụ xử lý dữ liệu nặng trong QGIS, máy chủ phục vụ API Node.js và các thiết bị đầu cuối của người dùng truy cập WebGIS qua giao thức HTTP.", bold_prefix="1. Phần cứng (Hardware): ");
add_bullet_item(doc, "Phần mềm GIS máy trạm (QGIS 3.x), Hệ quản trị cơ sở dữ liệu không gian (PostgreSQL / PostGIS), môi trường lập trình Python (GeoPandas, SciPy, Statsmodels), và nền tảng WebGIS (Express.js, Leaflet.js, Chart.js).", bold_prefix="2. Phần mềm (Software): ");
add_bullet_item(doc, "Là \"linh hồn\" của GIS. Trong đề tài gồm dữ liệu vector ranh giới hành chính, dữ liệu mạng lưới tiện ích OpenStreetMap, và bảng thuộc tính tin rao bất động sản gắn tọa độ WGS84.", bold_prefix="3. Dữ liệu (Data): ");
add_bullet_item(doc, "Bao gồm các nhà phân tích dữ liệu không gian, sinh viên nghiên cứu, chuyên viên định giá và người dùng cuối tra cứu thông tin bất động sản.", bold_prefix="4. Con người (People): ");
add_bullet_item(doc, "Quy trình chuẩn hóa tọa độ, sửa lỗi đa giác, tính toán ma trận cự ly, nội suy bề mặt raster, phân tích điểm nóng, huấn luyện mô hình kinh tế lượng và triển khai WebGIS.", bold_prefix="5. Quy trình & Phương pháp (Methods): ");

add_heading_2(doc, "1.4. Các loại dữ liệu không gian và thuộc tính ứng dụng trong đề tài")
add_body_paragraph(doc, "Trong khoa học GIS, dữ liệu địa lý được biểu diễn dưới hai mô hình cơ bản là Vector và Raster. Trong phạm vi đề tài này, cả hai mô hình đều được ứng dụng đồng bộ để giải quyết các bài toán chuyên biệt:")

add_body_paragraph(doc, "Mô hình dữ liệu Vector biểu diễn các đối tượng thế giới thực thông qua các tọa độ hình học rời rạc (Điểm, Đường, Vùng). Trong đề tài, mô hình Vector đóng vai trò chủ đạo: (1) Lớp Điểm (Point) đại diện cho 121 vị trí bất động sản khảo sát và hơn 1,000 tiện ích đô thị (trường học, bệnh viện, trạm xe buýt); (2) Lớp Đường (LineString) mô tả mạng lưới giao thông đường bộ; (3) Lớp Vùng (Polygon/MultiPolygon) đại diện cho ranh giới hành chính 3 quận và diện tích mặt nước hồ điều hòa.", bold_prefix="1. Mô hình dữ liệu Vector: ");

add_body_paragraph(doc, "Mô hình dữ liệu Raster tổ chức không gian thành một lưới ô vuông (pixel/cell) liên tục, trong đó mỗi ô chứa một giá trị định lượng phản ánh thuộc tính bề mặt. Trong đề tài, mô hình Raster được sinh ra từ thuật toán nội suy khoảng cách nghịch đảo (IDW) và lưu dưới định dạng GeoTIFF (tệp Clipped_mask.tif). Lớp Raster này mô tả bề mặt giá đất biến thiên liên tục trên toàn địa bàn nghiên cứu.", bold_prefix="2. Mô hình dữ liệu Raster: ");

add_body_paragraph(doc, "Mỗi đối tượng không gian vector đều liên kết chặt chẽ với một bản ghi thuộc tính phi không gian trong bảng cơ sở dữ liệu. Bảng thuộc tính bất động sản lưu trữ các biến kinh tế - kỹ thuật quan trọng như: giá bán (VNĐ), diện tích sàn (m²), đơn giá (triệu VNĐ/m²), số tầng cao, hình thái tiếp cận đường (mặt phố hay trong ngõ) và địa chỉ chi tiết.", bold_prefix="3. Dữ liệu thuộc tính (Attribute Data): ");

tbl1_headers = ["Tiêu chí so sánh", "Mô hình dữ liệu Vector", "Mô hình dữ liệu Raster"]
tbl1_data = [
    ["Bản chất hình học", "Tập hợp các cặp tọa độ rời rạc (Point, Line, Polygon)", "Lưới ma trận ô vuông (Pixel/Cell) có kích thước cố định"],
    ["Cấu trúc lưu trữ", "GeoJSON, ESRI Shapefile, GeoPackage, PostGIS Geometry", "GeoTIFF (.tif), ESRI Grid, ASCII Raster"],
    ["Độ chính xác vị trí", "Rất cao, bảo toàn nguyên vẹn ranh giới và hình dạng", "Phụ thuộc vào kích thước ô lưới (độ phân giải không gian)"],
    ["Ứng dụng trong đề tài", "Lớp 121 nhà ở, 7 lớp tiện ích OSM, ranh giới 3 quận", "Lớp bề mặt nội suy giá liên tục IDW (Clipped_mask.tif)"],
    ["Phép tính không gian", "Truy vấn bán kính cKDTree, buffer, spatial join", "Đại số bản đồ (Map Algebra), phân tích độ dốc giá"]
]
add_table_custom(doc, tbl1_headers, tbl1_data, col_widths=[1.5, 2.4, 2.4])

add_heading_2(doc, "1.5. Chức năng cơ bản của GIS và sự vận dụng trong đề tài")
add_body_paragraph(doc, "Hệ thống GIS thực hiện năm chức năng cơ bản và đã được hiện thực hóa trọn vẹn trong toàn bộ chu trình phát triển của đề tài:")

add_bullet_item(doc, "Thu thập tự động dữ liệu tin rao từ API Chợ Tốt và trích xuất dữ liệu bản đồ mở qua Overpass API (OSM Turbo). Làm sạch và loại bỏ các bản ghi trùng lặp, thiếu tọa độ.", bold_prefix="1. Thu thập & Tiền xử lý (Data Acquisition): ");
add_bullet_item(doc, "Tổ chức lưu trữ dữ liệu vector trong GeoPackage (.gpkg) trên máy trạm và cơ sở dữ liệu quan hệ không gian PostGIS trên máy chủ, tối ưu hóa chỉ mục R-Tree (GiST).", bold_prefix="2. Lưu trữ & Quản lý (Data Storage): ");
add_bullet_item(doc, "Thực hiện các câu lệnh truy vấn lọc theo thuộc tính (Select by Expression) và truy vấn quan hệ vị trí (Select by Location / Select within distance 500m) trên QGIS và WebGIS.", bold_prefix="3. Truy vấn không gian (Spatial Query): ");
add_bullet_item(doc, "Ứng dụng thuật toán cKDTree đo cự ly tiện ích, phân tích bề mặt nội suy IDW, kiểm định tương quan không gian Getis-Ord Gi* và Local Moran's I (LISA) xác định cấu trúc phân cụm thị trường.", bold_prefix="4. Phân tích không gian (Spatial Analysis): ");
add_bullet_item(doc, "Biên tập bản đồ chuyên đề theo chuẩn mực cartography trên QGIS Print Layout và xuất bản giao diện WebGIS tương tác đa lớp trên nền tảng Leaflet.js.", bold_prefix="5. Trực quan hóa & Hiển thị (Cartographic Visualization): ");

doc.add_page_break()

# =============================================================
# CHƯƠNG 2: CÔNG NGHỆ VÀ CÔNG CỤ TRIỂN KHAI
# =============================================================
add_heading_1(doc, "CHƯƠNG 2: CÔNG NGHỆ VÀ CÔNG CỤ TRIỂN KHAI")

add_heading_2(doc, "2.1. Giới thiệu phần mềm GIS chuyên nghiệp QGIS (Quantum GIS)")
add_body_paragraph(doc, "QGIS (tiền thân là Quantum GIS) là một trong những phần mềm Hệ thống thông tin địa lý mã nguồn mở (Open Source GIS) phổ biến và mạnh mẽ nhất thế giới hiện nay. Được bảo trợ bởi Tổ chức Địa không gian Mã nguồn mở (OSGeo), QGIS cung cấp một môi trường máy trạm hoàn chỉnh hỗ trợ xem, biên tập, xử lý, phân tích dữ liệu không gian và xuất bản bản đồ chất lượng cao.")

add_body_paragraph(doc, "Trong phạm vi đề tài, QGIS (phiên bản 3.28 LTR) đóng vai trò là môi trường phân tích không gian trung tâm với các chức năng nổi bật:")
add_bullet_item(doc, "Quản lý và đồng bộ hóa các lớp dữ liệu vector đa nguồn trên hệ quy chiếu chuẩn UTM Zone 48N (EPSG:32648). Khắc phục các lỗi hình học (geometry errors) của đa giác ranh giới hành chính.", bold_prefix="Quản lý và biên tập dữ liệu: ");
add_bullet_item(doc, "Tích hợp thư viện GDAL/OGR và GRASS GIS cho phép thực hiện thuật toán nội suy IDW (Inverse Distance Weighting) từ 121 điểm khảo sát bất động sản ra bề mặt raster độ phân giải cao và cắt khớp chính xác theo ranh giới 3 quận (Clip raster by mask layer).", bold_prefix="Nội suy không gian chuyên sâu: ");
add_bullet_item(doc, "Cung cấp các công cụ kiểm định thống kê địa lý nâng cao: Phân tích điểm nóng (Hot Spot Analysis - Getis-Ord Gi*) và Thống kê tự tương quan không gian cục bộ (Univariate Local Moran's I) để phân loại các cụm giá trị.", bold_prefix="Thống kê không gian (Spatial Statistics): ");
add_bullet_item(doc, "Thực hiện phép nối thuộc tính dựa trên vị trí hình học (Join Attributes by Location) để ghép nhãn phân cụm thống kê từ lớp phân tích ngược trở lại bảng thuộc tính nhà ở, tạo tiền đề cho việc xây dựng mô hình kinh tế lượng.", bold_prefix="Ghép nối không gian (Spatial Join): ");

add_heading_2(doc, "2.2. Hệ quản trị cơ sở dữ liệu không gian PostGIS / PostgreSQL")
add_body_paragraph(doc, "PostgreSQL là một trong những hệ quản trị cơ sở dữ liệu quan hệ đối tượng (ORDBMS) mã nguồn mở mạnh mẽ và tin cậy nhất hiện nay. PostGIS là phần mở rộng không gian chính thức của PostgreSQL, biến PostgreSQL thành một hệ quản trị cơ sở dữ liệu không gian đẳng cấp doanh nghiệp đáp ứng đầy đủ tiêu chuẩn Simple Features for SQL của Hiệp hội Địa không gian Mở (OGC).")

add_body_paragraph(doc, "Các ưu thế kỹ thuật vượt trội của PostGIS được vận dụng trong đề tài bao gồm:")
add_bullet_item(doc, "Hỗ trợ kiểu dữ liệu GEOMETRY và GEOGRAPHY cho phép lưu trữ các đối tượng hình học với hệ quy chiếu xác định (SRID=4326).", bold_prefix="Kiểu dữ liệu hình học bản địa: ");
add_bullet_item(doc, "Hỗ trợ cây chỉ mục Generalized Search Tree (GiST) dựa trên thuật toán R-Tree. Nhờ GiST Index, các câu lệnh truy vấn tìm kiếm bất động sản lân cận giảm độ phức tạp từ O(N) xuống O(log N), mang lại tốc độ phản hồi tính bằng mili-giây.", bold_prefix="Chỉ mục không gian GiST (Spatial Indexing): ");
add_bullet_item(doc, "Hệ thống hơn 1,000 hàm toán tử không gian mạnh mẽ. Đề tài khai thác triệt để hàm ST_DWithin (truy vấn khoảng cách thực trên mặt cầu elipsoid), hàm ST_AsGeoJSON (chuyển đổi hình học sang định dạng GeoJSON chuẩn hóa trả về cho WebGIS) và hàm ST_MakePoint.", bold_prefix="Toán tử không gian SQL: ");

add_heading_2(doc, "2.3. Môi trường lập trình và các thư viện phân tích dữ liệu không gian")
add_body_paragraph(doc, "Bên cạnh các phần mềm GIS máy trạm, ngôn ngữ lập trình Python (v3.12) được sử dụng để xây dựng các kịch bản tự động hóa xử lý dữ liệu lớn, tính toán cự ly hình học và mô hình hóa kinh tế lượng:")

tbl2_headers = ["Phân nhóm thư viện", "Tên thư viện Python", "Chức năng & Ứng dụng cụ thể trong đề tài"]
tbl2_data = [
    ["Xử lý địa không gian", "GeoPandas & Shapely", "Đọc/ghi GeoPackage, GeoJSON, thao tác hình học Point/Polygon, chuyển đổi hệ quy chiếu sang EPSG:32648."],
    ["Thuật toán cự ly tối ưu", "SciPy (cKDTree)", "Xây dựng cây tìm kiếm nhị phân k-chiều tính cự ly ngắn nhất từ nhà tới 7 tiện ích và đếm mật độ buffer 300m/500m/1km."],
    ["Thu thập dữ liệu", "Requests & Regex", "Gửi HTTP request cào dữ liệu từ API Chợ Tốt; trích xuất số tầng, phân loại nhà mặt phố/hẻm."],
    ["Kinh tế lượng vi mô", "Statsmodels (OLS)", "Ước lượng mô hình hồi quy OLS Hedonic, tính toán hệ số p-value, t-statistic, R², F-statistic, kiểm định đa cộng tuyến."],
    ["Học máy (Machine Learning)", "Scikit-learn (Random Forest)", "Huấn luyện mô hình Random Forest Regressor 300 cây, kiểm định chéo 5-fold CV, tính toán mức độ quan trọng đặc trưng."],
    ["Trực quan hóa thống kê", "Matplotlib", "Vẽ biểu đồ hệ số OLS, biểu đồ phân tán Actual vs Predicted, Boxplot phân bố giá, biểu đồ cột so sánh R²."]
]
add_table_custom(doc, tbl2_headers, tbl2_data, col_widths=[1.4, 1.7, 3.2])

add_heading_2(doc, "2.4. Kiến trúc hệ thống tổng thể và luồng luân chuyển dữ liệu")
add_body_paragraph(doc, "Kiến trúc hệ thống của đề tài được thiết kế theo mô hình 4 tầng phân tách độc lập (4-Tier Architecture) bảo đảm tính module hóa, độ ổn định và khả năng mở rộng cao:")

add_bullet_item(doc, "Chứa dữ liệu tin rao Chợ Tốt (CSV), các lớp tiện ích OpenStreetMap (GeoJSON), ranh giới 3 quận (GPKG) và cơ sở dữ liệu quan hệ không gian PostGIS.", bold_prefix="1. Tầng dữ liệu (Data Tier): ");
add_bullet_item(doc, "Chịu trách nhiệm thực hiện các tác vụ tính toán nặng bao gồm QGIS Processing Toolbox (IDW, Getis-Ord Gi*, LISA) và các kịch bản Python (cKDTree, OLS, Random Forest).", bold_prefix="2. Tầng phân tích & Tính toán (Analysis Engine Tier): ");
add_bullet_item(doc, "Xây dựng trên nền Node.js (Express), cung cấp các RESTful API (/api/housing, /api/amenities, /api/stats). Tích hợp cơ chế Smart Fallback Engine tự động tính khoảng cách Haversine khi chưa có kết nối PostGIS.", bold_prefix="3. Tầng dịch vụ & API (Service/API Tier): ");
add_bullet_item(doc, "Giao diện Dashboard tương tác người dùng xây dựng bằng Leaflet.js (hiển thị bản đồ đa lớp, truy vấn bán kính động) và Chart.js (trực quan hóa biểu đồ kinh tế lượng).", bold_prefix="4. Tầng trình diễn (Presentation Tier - WebGIS): ");

add_figure_image(doc, "outputs/query/housing_full.png", "Hình 2.1: Lớp dữ liệu 121 điểm bất động sản khảo sát phân bố trên nền bản đồ 3 quận trung tâm", width_inch=5.0)

doc.add_page_break()

# =============================================================
# CHƯƠNG 3: PHÂN TÍCH VÀ XÂY DỰNG HỆ THỐNG
# =============================================================
add_heading_1(doc, "CHƯƠNG 3: PHÂN TÍCH VÀ XÂY DỰNG HỆ THỐNG")

add_heading_2(doc, "3.1. Khảo sát khu vực nghiên cứu và thu thập dữ liệu")
add_heading_3(doc, "3.1.1. Đặc điểm khu vực 3 quận trung tâm Hà Nội")
add_body_paragraph(doc, "Ba quận trung tâm Hà Nội (Hoàn Kiếm, Ba Đình, Đống Đa) đại diện cho lõi đô thị lịch sử với các đặc trưng không gian điển hình: Quận Hoàn Kiếm là trung tâm hành chính - du lịch - thương mại với Khu phố cổ và Hồ Gươm, giá đất luôn đứng đầu cả nước; Quận Ba Đình là trung tâm chính trị ngoại giao với nhiều mảng xanh, hồ nước lớn (Hồ Tây, Trúc Bạch); Quận Đống Đa là quận có mật độ dân số cao nhất với hệ thống ngõ ngách chằng chịt và mạng lưới trường đại học, bệnh viện dày đặc.")

add_heading_3(doc, "3.1.2. Thu thập dữ liệu tiện ích công cộng từ OpenStreetMap")
add_body_paragraph(doc, "Dữ liệu hạ tầng và tiện ích đô thị được khai thác thông qua công cụ Overpass Turbo trên nền OpenStreetMap (OSM) bằng ngôn ngữ truy vấn Overpass QL. Dữ liệu sau khi trích xuất được lưu dưới định dạng GeoJSON chuẩn hóa tại thư mục data/raw/amenities_osm/:")

tbl3_headers = ["Nhóm tiện ích", "Thẻ truy vấn OSM (Tag)", "Số lượng đối tượng", "Vai trò kinh tế trong định giá bất động sản"]
tbl3_data = [
    ["Trường học", "amenity=school", "153 điểm", "Đo lường mức độ tiếp cận giáo dục phổ thông; yếu tố gia tăng giá trị nhà ở đối với hộ gia đình."],
    ["Bệnh viện / Y tế", "amenity=hospital", "54 điểm", "Đo lường sự thuận tiện chăm sóc sức khỏe; mật độ bệnh viện tuyến trung ương cao tại vùng lõi."],
    ["Công viên / Cây xanh", "leisure=park", "89 đối tượng", "Đại diện cho chất lượng môi trường vi khí hậu, không gian nghỉ dưỡng và rèn luyện thể chất."],
    ["Siêu thị bán lẻ", "shop=supermarket", "79 điểm", "Phản ánh tiện nghi thương mại hiện đại và mức sống tiêu dùng của khu vực dân cư."],
    ["Chợ dân sinh", "shop=marketplace", "39 điểm", "Đặc trưng văn hóa sinh hoạt truyền thống; thuận tiện nhưng tiềm ẩn tiếng ồn và ùn tắc giao thông."],
    ["Trạm dừng xe buýt", "highway=bus_stop", "462 điểm", "Phản ánh mật độ giao thông công cộng, năng lực kết nối di chuyển của cư dân không sở hữu ô tô."],
    ["Hồ nước / Cảnh quan", "natural=water", "124 đối tượng", "Tạo lập giá trị cảnh quan \"view hồ\" đắt giá và điều hòa vi khí hậu đô thị (Hồ Gươm, Trúc Bạch...)."]
]
add_table_custom(doc, tbl3_headers, tbl3_data, col_widths=[1.3, 1.4, 1.0, 2.6])

add_heading_3(doc, "3.1.3. Thu thập và làm sạch dữ liệu tin rao bất động sản")
add_body_paragraph(doc, "Dữ liệu bất động sản được thu thập tự động từ nền tảng Chợ Tốt (Nhà Tốt) thông qua script Python scripts/01_crawl_housing_3districts.py. Quá trình tiền xử lý dữ liệu bao gồm các bước kiểm tra nghiêm ngặt: loại bỏ tin đăng thiếu tọa độ (vĩ độ/kinh độ bằng 0 hoặc null); loại bỏ các tin có diện tích hoặc giá bất hợp lý; trích xuất số tầng từ tiêu đề bài đăng qua biểu thức chính quy (Regex); và phân loại hình thái nhà (Mặt phố / Hẻm). Kết quả thu được bộ dữ liệu sạch gồm 121 tin bất động sản độc lập.")

add_figure_image(doc, "outputs/figures/housing_utm.png", "Hình 3.1: Phân bố 121 điểm bất động sản khảo sát trên hệ tọa độ phẳng mét UTM 48N", width_inch=4.8)

add_heading_2(doc, "3.2. Thiết kế cơ sở dữ liệu không gian")
add_heading_3(doc, "3.2.1. Chuẩn hóa hệ quy chiếu không gian (CRS)")
add_body_paragraph(doc, "Toàn bộ dữ liệu thu thập ban đầu ở hệ tọa độ trắc địa WGS 84 (EPSG:4326) được chuyển đổi sang hệ tọa độ phẳng phép chiếu hình trụ ngang UTM Zone 48N (EPSG:32648) bằng thư viện GeoPandas và phần mềm QGIS. Việc chuyển đổi này là bắt buộc để đơn vị đo khoảng cách chuyển sang mét (m), bảo đảm tính chuẩn xác khi đo bán kính vùng đệm.")

add_heading_3(doc, "3.2.2. Thiết kế cấu trúc bảng cơ sở dữ liệu PostGIS")
add_body_paragraph(doc, "Cơ sở dữ liệu detai_gis được thiết kế gồm hai bảng không gian chính: bảng housing (lưu trữ bất động sản) và bảng amenities (lưu trữ hệ thống tiện ích):")

tbl4_headers = ["Tên trường (Field)", "Kiểu dữ liệu SQL", "Ràng buộc", "Mô tả ý nghĩa nghiệp vụ"]
tbl4_data = [
    ["id", "VARCHAR(50)", "PRIMARY KEY", "Mã định danh duy nhất của tin đăng bất động sản."],
    ["khu_vuc", "VARCHAR(50)", "NOT NULL", "Địa bàn hành chính quận (Ba Đình, Đống Đa, Hoàn Kiếm)."],
    ["gia", "NUMERIC(15,2)", "NOT NULL", "Tổng giá bán niêm yết (đồng)."],
    ["gia_trieu_m2", "NUMERIC(10,2)", "NOT NULL", "Đơn giá trên một mét vuông (triệu VNĐ/m²) - Biến mục tiêu Y."],
    ["dien_tich", "NUMERIC(8,2)", "NOT NULL", "Diện tích sàn sử dụng thực tế (m²)."],
    ["so_tang", "INTEGER", "DEFAULT 1", "Số tầng cao của căn nhà."],
    ["loai_nha", "VARCHAR(30)", "NOT NULL", "Phân loại vị trí: Mặt phố kinh doanh hoặc Trong hẻm/ngõ."],
    ["dia_chi", "TEXT", "NULL", "Địa chỉ chi tiết của căn nhà."],
    ["geom", "GEOMETRY(Point, 4326)", "INDEX GIST", "Hình học điểm không gian của căn nhà."]
]
add_table_custom(doc, tbl4_headers, tbl4_data, col_widths=[1.3, 1.6, 1.2, 2.2])

add_heading_2(doc, "3.3. Quy trình trích xuất đặc trưng không gian (Spatial Feature Engineering)")
add_body_paragraph(doc, "Để đưa các yếu tố ngoại ứng không gian vào mô hình định giá, kịch bản Python scripts/03_spatial_analysis.py đã hiện thực hóa thuật toán cây nhị phân k-chiều (cKDTree) để sinh ra hai nhóm biến không gian quan trọng:")
add_bullet_item(doc, "Khoảng cách Euclid hình học tính bằng mét từ từng căn nhà tới thực thể tiện ích gần nhất thuộc 7 nhóm (dist_school_m, dist_hospital_m, dist_park_m, dist_supermarket_m, dist_marketplace_m, dist_bus_stop_m, dist_water_lakes_m).", bold_prefix="Nhóm biến cự ly gần nhất: ");
add_bullet_item(doc, "Số lượng tiện ích hiện diện bên trong các vòng tròn bán kính đệm 300m, 500m và 1,000m bao quanh căn nhà (sinh ra 21 trường thuộc tính count_*).", bold_prefix="Nhóm biến mật độ vùng đệm (Buffer Density): ");

add_body_paragraph(doc, "Kết quả của bước này đã mở rộng bảng dữ liệu ban đầu thành bảng dữ liệu hoàn chỉnh housing_with_spatial_features.csv gồm 121 dòng và 40 cột thuộc tính giàu thông tin.")

add_heading_2(doc, "3.4. Phân tích thống kê không gian nâng cao trên QGIS")
add_heading_3(doc, "3.4.1. Nội suy bề mặt giá liên tục (Inverse Distance Weighting - IDW)")
add_body_paragraph(doc, "Thuật toán IDW giả định rằng giá trị của điểm cần dự báo chịu ảnh hưởng của các điểm quan sát lân cận tỷ lệ nghịch với lũy thừa khoảng cách giữa chúng:")

add_body_paragraph(doc, "Công thức toán học của phương pháp IDW:\nZ_hat(s_0) = [ SUM( Z(s_i) / (d_i)^p ) ] / [ SUM( 1 / (d_i)^p ) ]\nTrong đó: Z(s_i) là giá nhà tại điểm khảo sát s_i; d_i là khoảng cách từ điểm s_0 đến s_i; tham số lũy thừa khoảng cách chọn p = 2.", bold_prefix="Phương trình toán học: ", indent=False)

add_figure_image(doc, "outputs/figures/map_idw_price.png", "Hình 3.2: Bản đồ bề mặt nội suy giá đất liên tục IDW tại 3 quận trung tâm Hà Nội", width_inch=5.0)

add_heading_3(doc, "3.4.2. Phân tích điểm nóng (Hot Spot Analysis - Getis-Ord Gi*)")
add_body_paragraph(doc, "Công cụ Getis-Ord Gi* trên QGIS thực hiện kiểm định giả thuyết thống kê để xác định các cụm không gian có giá trị cao bất thường (Hot Spot) hoặc giá trị thấp bất thường (Cold Spot) với độ tin cậy thống kê 90%, 95% và 99%:")

tbl5_headers = ["Phân loại cụm Getis-Ord Gi*", "Mức ý nghĩa thống kê", "Ngưỡng Z-score", "Số điểm (N=121)", "Phân bố địa bàn đặc trưng"]
tbl5_data = [
    ["Điểm cực nóng (Hotspot 99%)", "p < 0.01", "Z > +2.58", "26 điểm", "Tập trung 100% tại Hoàn Kiếm (Khu phố cổ, Hồ Gươm)."],
    ["Điểm nóng (Hotspot 90-95%)", "p < 0.10", "+1.65 < Z <= +2.58", "0 điểm", "Khu vực chuyển tiếp không gian hẹp."],
    ["Không có ý nghĩa thống kê", "p >= 0.10", "-1.65 <= Z <= +1.65", "63 điểm", "Phân bố rải rác khu vực Ba Đình và Đống Đa."],
    ["Điểm cực lạnh (Coldspot 99%)", "p < 0.01", "Z < -2.58", "32 điểm", "Tập trung dày đặc tại khu vực ngõ hẻm quận Đống Đa."]
]
add_table_custom(doc, tbl5_headers, tbl5_data, col_widths=[1.7, 1.0, 1.0, 0.8, 1.8])

add_figure_image(doc, "outputs/figures/GI_output.png", "Hình 3.3: Bản đồ phân tích điểm nóng (Hot Spot Analysis - Getis-Ord Gi*)", width_inch=5.0)

add_heading_3(doc, "3.4.3. Phân tích tự tương quan không gian cục bộ (Local Moran's I - LISA)")
add_body_paragraph(doc, "Local Moran's I đo lường mức độ tương đồng giữa giá trị của một căn nhà với các căn nhà lân cận và phân loại thành 4 nhóm liên kết không gian:")

tbl6_headers = ["Loại hình liên kết LISA", "Diễn giải đặc tính không gian", "Số điểm (N=121)", "Đặc trưng kinh tế thực tế"]
tbl6_data = [
    ["High-High (Cụm nóng)", "Giá cao nằm trong khu vực lân cận giá cao", "19 điểm", "Bất động sản lõi phố cổ Hoàn Kiếm, giá trị thương mại lớn."],
    ["Low-Low (Cụm lạnh)", "Giá thấp nằm trong khu vực lân cận giá thấp", "32 điểm", "Bất động sản trong ngõ cụt Đống Đa (Khâm Thiên, Trung Phụng)."],
    ["High-Low (Dị biệt loại 1)", "Giá cao nằm lọt giữa khu vực giá thấp", "15 điểm", "Nhà mặt phố kinh doanh lớn nằm trên các trục xuyên tâm huyết mạch."],
    ["Low-High (Dị biệt loại 2)", "Giá thấp nằm lọt giữa khu vực giá cao", "17 điểm", "Nhà ngõ hẹp, diện tích nhỏ hoặc chung sổ xen lẫn tại Hoàn Kiếm."],
    ["Không có ý nghĩa", "Không có tự tương quan không gian rõ rệt", "38 điểm", "Giá dao động ngẫu nhiên quanh mức trung bình khu vực."]
]
add_table_custom(doc, tbl6_headers, tbl6_data, col_widths=[1.5, 2.0, 0.8, 2.0])

add_figure_image(doc, "outputs/figures/moran_output.png", "Hình 3.4: Bản đồ tự tương quan không gian cục bộ LISA (Local Moran's I)", width_inch=5.0)

add_heading_3(doc, "3.4.4. Truy vấn không gian và Phép ghép thuộc tính (Spatial Join)")
add_body_paragraph(doc, "Đề tài thực nghiệm các phép truy vấn không gian phức tạp trên QGIS: (1) Truy vấn biểu thức Select by Expression (`\"gia_trieu_m2\" > 250 OR \"dist_school_m\" < 300`) lọc được 104 / 121 bản ghi (85.95%); (2) Truy vấn Select within distance (bán kính 500m quanh bệnh viện) chọn được 59 / 121 bản ghi (48.76%); (3) Phép Spatial Join gộp nhãn phân cụm và Z-score vào lớp nhà để tạo bảng dữ liệu huấn luyện housing_model_ready.csv.")

add_figure_image(doc, "outputs/query/filter_gia.png", "Hình 3.5: Kết quả phép truy vấn thuộc tính (Select by Expression) trên QGIS", width_inch=4.6)
add_figure_image(doc, "outputs/query/filter_location.png", "Hình 3.6: Kết quả phép truy vấn cự ly không gian quanh cơ sở y tế trong bán kính 500m", width_inch=4.6)
add_figure_image(doc, "outputs/query/spatial_join.png", "Hình 3.7: Kết quả thực hiện phép ghép thuộc tính không gian (Spatial Join) gộp kết quả phân tích", width_inch=4.6)

add_heading_2(doc, "3.5. Xây dựng mô hình định giá kinh tế lượng Hedonic")
add_heading_3(doc, "3.5.1. Cơ sở lý thuyết mô hình giá ẩn Hedonic")
add_body_paragraph(doc, "Mô hình Hedonic giả định giá của một hàng hóa không đồng nhất (như nhà ở) bằng tổng giá trị của các đặc tính cấu thành nên nó. Phương trình hồi quy có dạng:\nPrice_i = beta_0 + SUM(beta_k * Structural_ik) + SUM(gamma_m * Location_im) + SUM(theta_j * Environmental_ij) + e_i")

add_heading_3(doc, "3.5.2. Ước lượng mô hình OLS (Ordinary Least Squares)")
add_body_paragraph(doc, "Mô hình OLS được ước lượng trên 121 quan sát sạch thông qua thư viện statsmodels. Kết quả kiểm định F-statistic = 4.795 (p = 5.58e-07) chứng minh toàn bộ mô hình có ý nghĩa thống kê vượt trội, giải thích được 40.7% độ biến thiên của đơn giá nhà đất (R² = 0.407, Adj. R² = 0.322):")

tbl7_headers = ["Tên biến độc lập", "Hệ số beta", "Sai số chuẩn", "t-statistic", "p-value", "Ý nghĩa thống kê & Diễn giải kinh tế"]
tbl7_data = [
    ["const (Hệ số chặn)", "393.80", "87.15", "4.518", "0.000", "Mức giá cơ sở nền tảng của thị trường."],
    ["dist_water_lakes_m", "-0.2093", "0.104", "-2.012", "0.047*", "Có ý nghĩa (p < 0.05): Cách xa hồ 1m giá giảm ~209.000 VNĐ/m²."],
    ["khu_vuc_Hoàn Kiếm", "+202.39", "78.59", "2.575", "0.011*", "Có ý nghĩa (p < 0.05): Giá nhà Hoàn Kiếm cao hơn Ba Đình ~202 triệu/m²."],
    ["loai_nha_Mặt phố", "+87.99", "36.74", "2.395", "0.018*", "Có ý nghĩa (p < 0.05): Nhà mặt tiền kinh doanh đắt hơn nhà hẻm ~88 triệu/m²."],
    ["dist_marketplace_m", "-0.1273", "0.084", "-1.519", "0.132", "Gần chợ dân sinh giá có xu hướng cao hơn nhưng chưa đạt mức 5%."],
    ["dist_park_m", "-0.1040", "0.089", "-1.169", "0.245", "Khoảng cách tới công viên có hệ số âm."],
    ["dien_tich", "+0.4021", "0.294", "1.369", "0.174", "Diện tích có quan hệ đồng biến nhẹ với đơn giá."],
    ["so_tang", "+8.7705", "7.283", "1.204", "0.231", "Số tầng cao đóng góp gia tăng giá trị sử dụng."],
    ["khu_vuc_Đống Đa", "-23.43", "55.83", "-0.420", "0.676", "Chênh lệch giá giữa Đống Đa và Ba Đình không đáng kể."]
]
add_table_custom(doc, tbl7_headers, tbl7_data, col_widths=[1.5, 0.8, 0.8, 0.8, 0.7, 1.7])

add_figure_image(doc, "outputs/figures/ols_coefficients.png", "Hình 3.8: Biểu đồ hệ số hồi quy OLS kèm đánh dấu các biến có ý nghĩa thống kê (màu đỏ, p < 0.05)", width_inch=5.0)
add_figure_image(doc, "outputs/figures/actual_vs_predicted.png", "Hình 3.9: Biểu đồ phân tán so sánh giá thực tế vs giá dự đoán của mô hình OLS (R² = 0.407)", width_inch=4.6)
add_figure_image(doc, "outputs/figures/price_by_district_boxplot.png", "Hình 3.10: Biểu đồ hộp (Boxplot) phân bố đơn giá nhà đất theo 3 quận trung tâm Hà Nội", width_inch=4.6)

add_heading_3(doc, "3.5.3. Mô hình học máy Random Forest Regressor")
add_body_paragraph(doc, "Mô hình Random Forest Regressor (300 cây, max_depth=6) được huấn luyện trên 36 biến không gian và thuộc tính vật lý. Kết quả kiểm định chéo 5-fold CV đạt R² trung bình = 0.092 (MAE = 148.5 triệu/m²). Do quy mô mẫu N = 121 tương đối nhỏ so với số biến, mô hình phi tuyến gặp hiện tượng quá khớp (overfitting) trên tập train. Tuy nhiên, bảng xếp hạng độ quan trọng đặc trưng (Feature Importance) vẫn tái khẳng định cự ly tới hồ nước, quận Hoàn Kiếm và nhà mặt phố là 3 biến quan trọng nhất.")

tbl8_headers = ["Mô hình thử nghiệm", "Quy mô quan sát (N)", "Số lượng biến độc lập", "Hệ số xác định (R²)", "Đánh giá khả năng tổng quát"]
tbl8_data = [
    ["Hồi quy OLS Hedonic (Tập biến gọn)", "121", "15", "0.407", "Rất tốt trên cỡ mẫu nhỏ, hệ số trực quan, giải thích rõ ràng."],
    ["Random Forest (5-fold CV, toàn bộ biến)", "121", "36", "0.092", "Dễ bị quá khớp do số biến lớn hơn nhiều so với quy mô mẫu."]
]
add_table_custom(doc, tbl8_headers, tbl8_data, col_widths=[1.8, 0.9, 1.1, 0.9, 1.6])

add_figure_image(doc, "outputs/figures/rf_feature_importance.png", "Hình 3.11: Biểu đồ xếp hạng mức độ quan trọng của biến trong mô hình Random Forest", width_inch=5.0)
add_figure_image(doc, "outputs/figures/model_r2_comparison.png", "Hình 3.12: Biểu đồ so sánh độ phù hợp R² giữa mô hình OLS và Random Forest", width_inch=4.5)

add_heading_2(doc, "3.6. Thiết kế và phát triển nền tảng WebGIS trực quan hóa tương tác")
add_body_paragraph(doc, "Để trực quan hóa các kết quả phân tích đến người dùng, nhóm nghiên cứu đã xây dựng ứng dụng WebGIS hoàn chỉnh tại thư mục webapp/ theo kiến trúc phân tầng:")

add_body_paragraph(doc, "Backend được phát triển bằng Node.js / Express cung cấp các RESTful API phục vụ dữ liệu GeoJSON cho frontend. Điểm sáng kỹ thuật của backend là cơ chế Smart Fallback Engine: khi có PostgreSQL/PostGIS, hệ thống tận dụng các hàm ST_DWithin; khi chưa cấu hình cơ sở dữ liệu, server tự động kích hoạt bộ tính toán không gian bộ nhớ trong dùng công thức Haversine, đảm bảo ứng dụng luôn chạy mượt mà 100% trong mọi môi trường triển khai.", bold_prefix="Cơ chế Smart Fallback Backend: ");

tbl9_headers = ["Phương thức", "Đường dẫn API (Endpoint)", "Tham số truy vấn (Query Params)", "Mô tả chức năng nghiệp vụ"]
tbl9_data = [
    ["GET", "/api/status", "Không", "Kiểm tra trạng thái server và chế độ cơ sở dữ liệu (PostGIS hay Fallback)."],
    ["GET", "/api/housing", "district, houseType, minPrice, maxPrice, minArea, maxArea", "Lấy danh sách 121 bất động sản kết hợp bộ lọc thuộc tính đa tiêu chí."],
    ["GET", "/api/housing/nearby", "lat, lon, radius (mặc định 500m)", "Truy vấn không gian tìm kiếm các căn nhà nằm trong bán kính quanh tọa độ chỉ định."],
    ["GET", "/api/housing/:id", "id", "Lấy chi tiết thuộc tính của một căn nhà cụ thể."],
    ["GET", "/api/amenities", "Không", "Lấy danh mục 7 nhóm tiện ích đô thị kèm số lượng thống kê."],
    ["GET", "/api/amenities/:type", "type (school, hospital, park, bus_stop...)", "Trả về lớp GeoJSON FeatureCollection của loại tiện ích yêu cầu."],
    ["GET", "/api/boundaries", "Không", "Trả về ranh giới hành chính đa giác 3 quận trung tâm."],
    ["GET", "/api/stats", "Không", "Cung cấp bảng số liệu so sánh mô hình kinh tế lượng OLS và Random Forest."]
]
add_table_custom(doc, tbl9_headers, tbl9_data, col_widths=[0.7, 1.6, 1.7, 2.3])

doc.add_page_break()

# =============================================================
# CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ
# =============================================================
add_heading_1(doc, "CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ")

add_heading_2(doc, "4.1. Giao diện và chức năng hoàn thiện của hệ thống WebGIS")
add_body_paragraph(doc, "Hệ thống WebGIS đã được triển khai hoàn chỉnh tại địa chỉ http://localhost:3000. Giao diện ứng dụng được thiết kế theo phong cách Modern Geographic Dashboard với tông màu khoa học, tương thích hoàn hảo trên các độ phân giải màn hình máy tính và thiết bị di động. Hệ thống bao gồm 3 phân hệ chính:")

add_heading_3(doc, "4.1.1. Phân hệ Bản đồ không gian tương tác (Map View)")
add_body_paragraph(doc, "Phân hệ bản đồ là trung tâm tương tác của ứng dụng WebGIS, tích hợp thư viện Leaflet.js với nhiều tính năng nâng cao:")
add_bullet_item(doc, "Cho phép người dùng lựa chọn 4 lớp bản đồ nền chuyên nghiệp: OpenStreetMap tiêu chuẩn, Carto Positron (nền sáng tinh giản), Carto Dark (nền tối tương phản cao) và Ảnh vệ tinh Esri World Imagery.", bold_prefix="Hỗ trợ 4 lớp bản đồ nền (Base Maps): ");
add_bullet_item(doc, "121 điểm nhà được hiển thị dưới dạng CircleMarker với màu sắc phân cấp theo đơn giá: Xanh lá (< 150 triệu/m²), Vàng (150-300 triệu/m²), Cam (300-500 triệu/m²) và Đỏ (> 500 triệu/m²). Nhấp vào điểm hiển thị Popup đầy đủ thông tin giá bán, diện tích, số tầng, loại nhà và liên kết tin đăng gốc.", bold_prefix="Phân cấp màu sắc bất động sản: ");
add_bullet_item(doc, "Cho phép bật/tắt độc lập 7 lớp tiện ích đô thị (Trường học, Bệnh viện, Công viên, Siêu thị, Chợ, Trạm xe buýt, Hồ nước) với các biểu tượng FontAwesome chuyên biệt.", bold_prefix="Điều khiển phân lớp tiện ích (Layer Control): ");
add_bullet_item(doc, "Cho phép bật lớp phủ raster nội suy IDW xuất từ QGIS lên đúng vị trí địa lý với thanh trượt điều chỉnh độ trong suốt (opacity).", bold_prefix="Chồng phủ bề mặt nội suy IDW: ");

add_placeholder_box(doc, "Hình 4.1: Giao diện Bản đồ WebGIS tương tác và điều khiển phân lớp tiện ích", "Sinh viên tự chụp ảnh màn hình giao diện bản đồ khi chạy ứng dụng và chèn thay thế khung này", height_pt=130)

add_heading_3(doc, "4.1.2. Chức năng bộ lọc đa tiêu chí và Truy vấn bán kính động")
add_body_paragraph(doc, "Hệ thống trang bị hai công cụ tìm kiếm và lọc dữ liệu không gian mạnh mẽ:")
add_bullet_item(doc, "Cho phép người dùng lọc đồng thời theo quận (Hoàn Kiếm, Ba Đình, Đống Đa), phân loại nhà (Mặt phố, Hẻm), khoảng giá bán (từ - đến tỷ VNĐ) và khoảng diện tích sàn. Bản đồ tự động cập nhật lại các điểm thỏa mãn điều kiện theo thời gian thực.", bold_prefix="Bộ lọc thuộc tính đa tiêu chí: ");
add_bullet_item(doc, "Người dùng nhấp chuột vào bất kỳ vị trí nào trên bản đồ hoặc chọn một tiện ích cụ thể, chọn cự ly bán kính đệm (300m, 500m, 1,000m, 2,000m). Hệ thống lập tức vẽ vòng tròn buffer trực quan và truy vấn backend (qua ST_DWithin hoặc Haversine fallback) để trả về danh sách các căn nhà nằm lọt trong phạm vi.", bold_prefix="Truy vấn bán kính không gian động (Spatial Radius Query): ");

add_placeholder_box(doc, "Hình 4.2: Giao diện bộ lọc bất động sản và công cụ truy vấn bán kính động", "Sinh viên tự chụp ảnh màn hình thao tác lọc nhà và vẽ vòng tròn bán kính trên WebGIS", height_pt=130)

add_heading_3(doc, "4.1.3. Phân hệ Báo cáo phân tích mô hình kinh tế lượng (Analytics View)")
add_body_paragraph(doc, "Nhấp nút \"Phân Tích Mô Hình\" trên thanh tiêu đề, giao diện chuyển sang màn hình Dashboard phân tích kinh tế lượng tích hợp thư viện Chart.js:")
add_bullet_item(doc, "Các thẻ số liệu KPI hiển thị nhanh quy mô mẫu (121 tin), hệ số R² OLS (0.407), hệ số R² Random Forest (0.092) và mức độ chênh lệch giá giữa các quận.", bold_prefix="Thẻ chỉ số tổng hợp (Summary Cards): ");
add_bullet_item(doc, "Biểu đồ thanh ngang hiển thị giá trị các hệ số beta của mô hình Hedonic OLS, trong đó các cột hệ số có ý nghĩa thống kê (p < 0.05) như khoảng cách tới hồ nước, quận Hoàn Kiếm, nhà mặt phố được đánh dấu nổi bật bằng màu đỏ cảnh báo.", bold_prefix="Biểu đồ hệ số hồi quy OLS tương tác: ");
add_bullet_item(doc, "Biểu đồ hộp phân bố giá trực quan hóa độ phân tán giá trị bất động sản giữa Hoàn Kiếm (trung vị ~502 triệu/m²), Ba Đình (~321 triệu/m²) và Đống Đa (~245 triệu/m²).", bold_prefix="Biểu đồ Boxplot phân bố giá: ");

add_placeholder_box(doc, "Hình 4.3: Giao diện phân hệ Báo cáo phân tích mô hình kinh tế lượng", "Sinh viên tự chụp ảnh màn hình phân hệ Analytics Dashboard trên trình duyệt", height_pt=130)

add_heading_3(doc, "4.1.4. Phân hệ Thư viện bản đồ chuyên đề QGIS (Gallery View)")
add_body_paragraph(doc, "Nhấp nút \"Bản Đồ QGIS\", người dùng được tiếp cận thư viện bản đồ chuyên đề chất lượng cao xuất từ QGIS: bản đồ Hot Spot Getis-Ord Gi*, bản đồ LISA Local Moran's I, bản đồ nội suy IDW, và các bản đồ truy vấn không gian. Người dùng có thể nhấp vào từng bản đồ để mở cửa sổ phóng to (Modal zoom) và đọc thuyết minh ý nghĩa địa lý chi tiết.")

add_placeholder_box(doc, "Hình 4.4: Giao diện phân hệ Thư viện bản đồ chuyên đề QGIS độ phân giải cao", "Sinh viên tự chụp ảnh màn hình phân hệ Gallery trưng bày các bản đồ QGIS", height_pt=130)

add_heading_2(doc, "4.2. Đánh giá ưu điểm của hệ thống")
add_bullet_item(doc, "Xây dựng được quy trình khép kín từ trích xuất dữ liệu thô, chuẩn hóa hình học đa giác, tính toán ma trận cự ly tối ưu qua cKDTree O(log N), phân tích thống kê không gian trên QGIS, đến mô hình hóa định giá và xuất bản WebGIS.", bold_prefix="1. Tính toàn diện và đồng bộ khoa học: ");
add_bullet_item(doc, "Hệ thống WebGIS được thiết kế thông minh với cơ chế Fallback Engine. Ứng dụng không bị phụ thuộc cứng vào cơ sở dữ liệu PostgreSQL mà có khả năng tự động tính toán khoảng cách mặt cầu Haversine trên dữ liệu GeoJSON nội bộ, đảm bảo tính khả dụng tuyệt đối khi chấm bài hoặc trình diễn.", bold_prefix="2. Khả năng vận hành độc lập, linh hoạt: ");
add_bullet_item(doc, "Mô hình OLS đạt độ tin cậy thống kê cao (p(F) < 0.001, R² = 0.407), phát hiện và lượng hóa chính xác giá trị của cảnh quan hồ nước (-209 nghìn đ/m² cho mỗi mét xa hồ), thương hiệu địa lý Hoàn Kiếm (+202 triệu/m²) và ưu thế mặt phố (+88 triệu/m²).", bold_prefix="3. Ý nghĩa thực tiễn của mô hình định giá: ");
add_bullet_item(doc, "Giao diện Dashboard trực quan, thẩm mỹ, phân lớp rõ ràng, hỗ trợ đầy đủ các thao tác chuyên nghiệp của một WebGIS thương mại.", bold_prefix="4. Trải nghiệm người dùng (UI/UX) hiện đại: ");

add_heading_2(doc, "4.3. Đánh giá hạn chế kỹ thuật và bài học kinh nghiệm")
add_bullet_item(doc, "Quy mô 121 bản ghi tuy đủ để thiết lập mô hình hồi quy OLS cơ bản nhưng vẫn còn khiêm tốn đối với các thuật toán học máy phức tạp như Random Forest, dẫn đến hiện tượng quá khớp và suy giảm R² trên tập kiểm định chéo CV.", bold_prefix="1. Hạn chế về cỡ mẫu khảo sát: ");
add_bullet_item(doc, "Việc đưa trực tiếp các đại lượng kiểm định không gian cục bộ phái sinh từ chính giá bán (Z-score, p-value của LISA) vào vế phải phương trình OLS đã làm nảy sinh hiện tượng đa cộng tuyến mạnh (Condition Number = 8.26e+04). Bài học kinh nghiệm là chỉ nên đưa các kết quả phân cụm dưới dạng biến nhị phân phân vùng (dummy regimes).", bold_prefix="2. Hiện tượng đa cộng tuyến nội sinh: ");
add_bullet_item(doc, "Dữ liệu cào từ tin rao trực tuyến chưa phản ánh được các thuộc tính vi mô cốt lõi của bất động sản trong ngõ Hà Nội như: bề rộng mặt ngõ trước nhà (ngõ ba gác hay ngõ ô tô tránh nhau), khoảng cách tới trục đường chính, hình dáng thửa đất (nở hậu hay thóp hậu) và tình trạng pháp lý (sổ đỏ riêng hay sổ chung).", bold_prefix="3. Thiếu vắng các biến vi mô thửa đất: ");

add_heading_2(doc, "4.4. Đề xuất định hướng phát triển tiếp theo")
add_bullet_item(doc, "Áp dụng phương pháp Hồi quy trọng số địa lý (Geographically Weighted Regression - GWR) cho phép các hệ số beta biến thiên linh hoạt theo tọa độ không gian (u_i, v_i), giải quyết triệt để vấn đề bất đồng nhất không gian (Spatial Heterogeneity).", bold_prefix="1. Nâng cấp mô hình không gian GWR: ");
add_bullet_item(doc, "Áp dụng dạng hàm logarit bán phần (Semi-log model: ln(Price)) để chuẩn hóa phân phối giá đất lệch phải, giảm thiểu sai số dự báo ở phân khúc nhà cao cấp.", bold_prefix="2. Chuẩn hóa hàm định giá Semi-log: ");
add_bullet_item(doc, "Tích hợp máy chủ bản đồ chuyên nghiệp GeoServer kết hợp kỹ thuật phân mảnh Vector Tiles (MVT) qua thư viện Mapbox GL JS / MapLibre GL để tối ưu hóa hiệu năng hiển thị hàng chục nghìn điểm dữ liệu bất động sản trong thời gian thực.", bold_prefix="3. Nâng cấp hạ tầng WebGIS phân tán: ");

doc.add_page_break()

# =============================================================
# KẾT LUẬN VÀ KIẾN NGHỊ
# =============================================================
add_heading_1(doc, "KẾT LUẬN VÀ KIẾN NGHỊ")

add_heading_2(doc, "1. Kết luận tổng kết đề tài")
add_body_paragraph(doc, "Báo cáo chuyên đề học phần Hệ thống thông tin không gian (GIS) với đề tài: \"Phân tích không gian và định giá bất động sản nhà ở tại khu vực trung tâm Hà Nội\" đã hoàn thành xuất sắc toàn bộ các mục tiêu lý thuyết và thực tiễn đề ra. Thông qua quá trình thực hiện đồ án, nhóm sinh viên đã làm chủ được các kỹ thuật nền tảng của khoa học địa không gian hiện đại:")

add_body_paragraph(doc, "Thứ nhất, đồ án đã chứng minh vị trí địa lý và khả năng tiếp cận hạ tầng đô thị là yếu tố chi phối mang tính quyết định đến giá trị bất động sản. Các phân tích thống kê không gian trên QGIS đã làm sáng tỏ cấu trúc phân hóa giá đất: Hoàn Kiếm đóng vai trò cực tăng trưởng nóng với mức giá cao vượt trội; cảnh quan hồ nước tạo ra phần bù kinh tế bền vững cho bất động sản nội đô; trong khi các ngõ cụt tại Đống Đa hình thành nên các dải giá trị lạnh tương đối.")

add_body_paragraph(doc, "Thứ hai, việc kết hợp giữa công nghệ GIS và kinh tế lượng vi mô Hedonic đã mở ra một hướng tiếp cận khách quan, định lượng hóa sự tác động của từng tiện ích công cộng tới giá đất, khắc phục các hạn chế cảm tính của phương pháp định giá truyền thống.")

add_body_paragraph(doc, "Thứ ba, đồ án đã hiện thực hóa thành công một sản phẩm ứng dụng WebGIS tương tác hoàn chỉnh, có khả năng chạy độc lập, đáp ứng đầy đủ các nhu cầu tra cứu thông tin, lọc đa tiêu chí, truy vấn bán kính không gian và phân tích biểu đồ thống kê trực quan.")

add_heading_2(doc, "2. Kiến nghị ứng dụng thực tế")
add_bullet_item(doc, "Có thể ứng dụng mô hình IDW và phân tích điểm nóng để xây dựng Bảng giá đất đô thị hàng năm sát với giá thị trường thực tế, hỗ trợ công tác tính thuế sử dụng đất, lập quy hoạch hạ tầng công cộng và đền bù giải phóng mặt bằng công bằng, minh bạch.", bold_prefix="Đối với cơ quan quản lý đô thị: ");
add_bullet_item(doc, "Có thể ứng dụng mô hình Hedonic OLS và công cụ cKDTree để tự động hóa định giá tài sản thế chấp nhanh chóng, chính xác dựa trên tọa độ vị trí và khoảng cách tới các tiện ích đã được số hóa.", bold_prefix="Đối với các tổ chức tín dụng và ngân hàng: ");
add_bullet_item(doc, "Nền tảng WebGIS cung cấp công cụ tra cứu minh bạch, giúp người mua nhà dễ dàng đánh giá môi trường sống, khoảng cách đi bộ tới trường học, bệnh viện, công viên trước khi ra quyết định giao dịch.", bold_prefix="Đối với người dân và nhà đầu tư: ");

doc.add_page_break()

# =============================================================
# TÀI LIỆU THAM KHẢO
# =============================================================
add_heading_1(doc, "TÀI LIỆU THAM KHẢO")

refs = [
    "[1] Rosen, S. (1974). Hedonic prices and implicit markets: product differentiation in pure competition. Journal of Political Economy, 82(1), 34-55.",
    "[2] Anselin, L. (1995). Local indicators of spatial association—LISA. Geographical Analysis, 27(2), 93-115.",
    "[3] Getis, A., & Ord, J. K. (1992). The analysis of spatial association by use of distance statistics. Geographical Analysis, 24(3), 189-206.",
    "[4] Shekhar, S., & Xiong, H. (Eds.). (2008). Encyclopedia of GIS. Springer Science & Business Media.",
    "[5] QGIS Development Team. (2024). QGIS Geographic Information System User Guide. Open Source Geospatial Foundation Project. https://docs.qgis.org/",
    "[6] Obe, R. O., & Hsu, L. S. (2021). PostGIS in Action (3rd ed.). Manning Publications.",
    "[7] Gillies, S., & Contributors. (2023). Shapely: manipulation and analysis of geometric objects. https://shapely.readthedocs.io/",
    "[8] Jordahl, K., et al. (2023). GeoPandas: Python tools for geographic data. https://geopandas.org/",
    "[9] Virtanen, P., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods, 17(3), 261-272.",
    "[10] Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with python. Proceedings of the 9th Python in Science Conference.",
    "[11] Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825-2830.",
    "[12] OpenStreetMap Contributors. (2024). Planet dump [Data file from world wide web]. https://planet.openstreetmap.org/",
    "[13] Bộ Tài nguyên và Môi trường. (2020). Thông tư quy định kỹ thuật về xây dựng cơ sở dữ liệu địa lý quốc gia tỷ lệ 1:2.000, 1:5.000. Hà Nội.",
    "[14] Hoàng Triều Ân. (2018). Giáo trình Hệ thống thông tin địa lý (GIS). Nhà xuất bản Đại học Quốc gia Hà Nội."
]

for ref in refs:
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.space_before = Pt(2)
    p_ref.paragraph_format.space_after = Pt(4)
    p_ref.paragraph_format.line_spacing = 1.25
    p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_ref.paragraph_format.first_line_indent = Cm(-0.8)
    p_ref.paragraph_format.left_indent = Cm(0.8)
    r_rf = p_ref.add_run(ref)
    r_rf.font.name = "Times New Roman"
    r_rf.font.size = Pt(13)

doc.add_page_break()

# =============================================================
# PHỤ LỤC
# =============================================================
add_heading_1(doc, "PHỤ LỤC BÁO CÁO")

add_heading_2(doc, "Phụ lục 1: Toàn văn kết quả báo cáo OLS Regression Results")
add_body_paragraph(doc, "Báo cáo chi tiết trích xuất trực tiếp từ gói statsmodels của Python lưu tại outputs/tables/ols_summary.txt:")

ols_txt_path = PROJECT_ROOT / "outputs" / "tables" / "ols_summary.txt"
if ols_txt_path.exists():
    with open(ols_txt_path, "r", encoding="utf-8") as f:
        ols_raw = f.read()
    
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(4)
    p_code.paragraph_format.space_after = Pt(6)
    p_code.paragraph_format.line_spacing = 1.0
    r_c = p_code.add_run(ols_raw)
    r_c.font.name = "Courier New"
    r_c.font.size = Pt(8.5)
    r_c.font.color.rgb = RGBColor(40, 40, 40)

add_heading_2(doc, "Phụ lục 2: Trích đoạn mã nguồn thuật toán Haversine Smart Fallback Engine")
add_body_paragraph(doc, "Đoạn mã JavaScript triển khai tại webapp/backend/src/db.js phục vụ tính toán không gian nội suy bộ nhớ khi không có kết nối cơ sở dữ liệu PostGIS:")

js_code = """// Hàm tính khoảng cách trắc địa Haversine (mét) giữa 2 tọa độ WGS84
function haversineDistanceMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Bán kính Trái Đất (mét)
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// Truy vấn bất động sản trong bán kính R mét
async function getNearbyHousing(lat, lon, radiusMeters) {
  const centerLat = parseFloat(lat);
  const centerLon = parseFloat(lon);
  const radius = parseFloat(radiusMeters);
  
  const allHouses = await getHousing({});
  const filtered = allHouses.features.filter(f => {
    const [hLon, hLat] = f.geometry.coordinates;
    const dist = haversineDistanceMeters(centerLat, centerLon, hLat, hLon);
    f.properties.distance_meters = Math.round(dist);
    return dist <= radius;
  });
  
  filtered.sort((a, b) => a.properties.distance_meters - b.properties.distance_meters);
  return { type: 'FeatureCollection', features: filtered };
}"""

p_js = doc.add_paragraph()
p_js.paragraph_format.space_before = Pt(4)
p_js.paragraph_format.space_after = Pt(6)
p_js.paragraph_format.line_spacing = 1.0
r_js = p_js.add_run(js_code)
r_js.font.name = "Courier New"
r_js.font.size = Pt(8.5)
r_js.font.color.rgb = RGBColor(0, 51, 102)

# Lưu tệp Word cuối cùng
doc.save(str(OUTPUT_FILE))
print(f"[V] XUẤT BÁO CÁO THÀNH CÔNG TẠI:\n -> {OUTPUT_FILE}")
