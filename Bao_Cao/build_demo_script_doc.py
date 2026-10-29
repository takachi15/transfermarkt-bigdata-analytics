# -*- coding: utf-8 -*-
"""
build_demo_script_doc.py
========================
Kịch bản thuyết trình và Demo trực quan, đơn giản, dễ hiểu cho BÁO CÁO CUỐI KỲ MÔN HỌC.
Môn học: Công nghệ Dữ liệu lớn (Big Data Technologies)
Giảng viên: ThS. Huỳnh Thái Học
Nhóm 5 thực hiện.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DOCX = os.path.join(BASE_DIR, "Kich_Ban_Demo_Bao_Ve_Website_BigData.docx")
OUT_DOCX_FRIENDLY = os.path.join(BASE_DIR, "Kich_Ban_Demo_Bao_Cao_Cuoi_Ky_BigData.docx")

FONT_MAIN = "Times New Roman"
FONT_CODE = "Consolas"

COLOR_NAVY = RGBColor(27, 54, 93)     # #1B365D
COLOR_TEAL = RGBColor(13, 118, 110)   # #0D766E
COLOR_DARK = RGBColor(30, 41, 59)     # #1E293B
COLOR_MUTED = RGBColor(100, 116, 139) # #64748B

HEX_NAVY_BG   = "1B365D"
HEX_LIGHT_BG  = "F8FAFC"
HEX_ACCENT_BG = "F0FDF4"  # Xanh dịu cho lời thoại
HEX_ACTION_BG = "EFF6FF"  # Xanh dương nhạt cho thao tác
HEX_TECH_BG   = "FEF3C7"  # Vàng nhạt cho công nghệ
HEX_URL_BG    = "F1F5F9"  # Xám sáng cho URL

def set_page_margins(section):
    section.top_margin    = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin   = Inches(0.75)
    section.right_margin  = Inches(0.75)

def set_cell_pad(cell, t=60, b=60, l=90, r=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', t), ('w:bottom', b), ('w:left', l), ('w:right', r)]:
        node = parse_xml(f'<{m} {nsdecls("w")} w:w="{val}" w:type="dxa"/>')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_borders(cell, top=True, bottom=True, left=True, right=True, color="D0D5DD", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    sides = [('top', top), ('bottom', bottom), ('left', left), ('right', right)]
    for side_name, enabled in sides:
        if enabled:
            b_xml = f'<w:{side_name} {nsdecls("w")} w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        else:
            b_xml = f'<w:{side_name} {nsdecls("w")} w:val="none"/>'
        tcBorders.append(parse_xml(b_xml))
    tcPr.append(tcBorders)

def apply_font_to_run(run, font_name=FONT_MAIN, size_pt=11, bold=False, italic=False, color=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(
        f'<w:rFonts {nsdecls("w")} '
        f'w:ascii="{font_name}" '
        f'w:hAnsi="{font_name}" '
        f'w:eastAsia="{font_name}" '
        f'w:cs="{font_name}"/>'
    )
    rPr.append(rFonts)

def configure_document_styles(doc):
    styles = doc.styles
    for style_name in ['Normal', 'Heading 1', 'Heading 2', 'Heading 3']:
        try:
            s = styles[style_name]
            s.font.name = FONT_MAIN
            rPr = s._element.get_or_add_rPr()
            rFonts = parse_xml(
                f'<w:rFonts {nsdecls("w")} '
                f'w:ascii="{FONT_MAIN}" '
                f'w:hAnsi="{FONT_MAIN}" '
                f'w:eastAsia="{FONT_MAIN}" '
                f'w:cs="{FONT_MAIN}"/>'
            )
            rPr.append(rFonts)
        except Exception:
            pass

def add_p(doc, text="", size=11, bold=False, italic=False, color=COLOR_DARK, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=2, line_spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        apply_font_to_run(r, FONT_MAIN, size_pt=size, bold=bold, italic=italic, color=color)
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(13)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    apply_font_to_run(r, FONT_MAIN, size_pt=13, bold=True, color=COLOR_NAVY)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    apply_font_to_run(r, FONT_MAIN, size_pt=11.5, bold=True, color=COLOR_TEAL)
    return p

def add_url_box(doc, page_name, direct_url, secondary_url=None):
    """Hộp định vị Tab và URL rõ ràng, trực quan"""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_bg(cell, HEX_URL_BG)
    set_cell_pad(cell, t=50, b=50, l=90, r=90)
    set_cell_borders(cell, top=True, bottom=True, left=True, right=True, color="1B365D", sz="6")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    r_tag = p.add_run("[ĐỊNH VỊ GIAO DIỆN & URL TRUY CẬP]\n")
    apply_font_to_run(r_tag, FONT_MAIN, size_pt=9.5, bold=True, color=COLOR_NAVY)
    
    r_tab = p.add_run(f"• Bấm Tab trên Sidebar: \"{page_name}\"\n")
    apply_font_to_run(r_tab, FONT_MAIN, size_pt=10, bold=True, color=COLOR_TEAL)
    
    r_url = p.add_run(f"• Đường dẫn trực tiếp: {direct_url}\n")
    apply_font_to_run(r_url, FONT_CODE, size_pt=9, bold=True, color=COLOR_NAVY)
    
    if secondary_url:
        r_sec = p.add_run(f"• Cổng dịch vụ phụ: {secondary_url}")
        apply_font_to_run(r_sec, FONT_CODE, size_pt=8.5, bold=False, color=COLOR_MUTED)
    add_p(doc, "", size=2, space_before=0, space_after=1)

def add_callout_box(doc, title, items, box_type="speech"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    
    if box_type == "speech":
        bg_hex = HEX_ACCENT_BG
        border_color = "0D766E"
        title_color = COLOR_TEAL
        icon_prefix = "[LỜI THOẠI NÓI CÁI HIỂU LIỀN] "
    elif box_type == "action":
        bg_hex = HEX_ACTION_BG
        border_color = "1B365D"
        title_color = COLOR_NAVY
        icon_prefix = "[THAO TÁC MÀN HÌNH & CHUỘT] "
    elif box_type == "tech":
        bg_hex = HEX_TECH_BG
        border_color = "D97706"
        title_color = RGBColor(180, 83, 9)
        icon_prefix = "[TỪ KHÓA BIG DATA ĂN ĐIỂM] "
    else:
        bg_hex = HEX_LIGHT_BG
        border_color = "94A3B8"
        title_color = COLOR_DARK
        icon_prefix = "[THÔNG TIN] "

    set_bg(cell, bg_hex)
    set_cell_pad(cell, t=60, b=60, l=90, r=90)
    set_cell_borders(cell, top=True, bottom=True, left=True, right=True, color=border_color, sz="6")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    r_title = p.add_run(icon_prefix + title)
    apply_font_to_run(r_title, FONT_MAIN, size_pt=10, bold=True, color=title_color)
    
    for item in items:
        p_c = cell.add_paragraph()
        p_c.paragraph_format.space_before = Pt(1)
        p_c.paragraph_format.space_after  = Pt(2)
        p_c.paragraph_format.line_spacing = 1.15
        p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_item = p_c.add_run(item)
        apply_font_to_run(r_item, FONT_MAIN, size_pt=9.5, bold=False, italic=(box_type == "speech"), color=COLOR_DARK)
    add_p(doc, "", size=2, space_before=0, space_after=1)

def add_table_data(doc, headers, rows_data, col_widths=None):
    table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr_cells = table.rows[0].cells
    for c_idx, title in enumerate(headers):
        set_bg(hdr_cells[c_idx], HEX_NAVY_BG)
        set_cell_pad(hdr_cells[c_idx], t=60, b=60, l=70, r=70)
        set_cell_borders(hdr_cells[c_idx], top=True, bottom=True, left=False, right=False, color="1B365D", sz="8")
        p = hdr_cells[c_idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after  = Pt(1)
        r = p.add_run(title)
        apply_font_to_run(r, FONT_MAIN, size_pt=9.5, bold=True, color=RGBColor(255, 255, 255))
        
    for r_idx, row in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        bg_col = HEX_LIGHT_BG if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row):
            set_bg(row_cells[c_idx], bg_col)
            set_cell_pad(row_cells[c_idx], t=50, b=50, l=70, r=70)
            set_cell_borders(row_cells[c_idx], top=True, bottom=True, left=False, right=False, color="E2E8F0", sz="4")
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 1 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after  = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(str(val))
            apply_font_to_run(r, FONT_MAIN, size_pt=9, bold=(c_idx == 0 or c_idx == len(row)-1), color=COLOR_DARK)
            
    if col_widths:
        for row in table.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)
    add_p(doc, "", size=2, space_before=0, space_after=2)

def build_demo_document():
    doc = docx.Document()
    sec = doc.sections[0]
    set_page_margins(sec)
    configure_document_styles(doc)

    # ══════════════════════════════════════════════════════════════════════
    # TIÊU ĐỀ BÁO CÁO CUỐI KỲ MÔN HỌC
    # ══════════════════════════════════════════════════════════════════════
    add_p(doc, "TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)\nKHOA CÔNG NGHỆ THÔNG TIN — BỘ MÔN KHOA HỌC DỮ LIỆU",
          size=10, bold=True, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=6)

    add_p(doc, "KỊCH BẢN THUYẾT TRÌNH & DEMO BÁO CÁO CUỐI KỲ",
          size=15, bold=True, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    add_p(doc, "HỌC PHẦN: CÔNG NGHỆ DỮ LIỆU LỚN (BIG DATA TECHNOLOGIES)",
          size=11, bold=True, color=COLOR_TEAL, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    add_p(doc, "Đề tài: Xây dựng Data Pipeline thu thập, xử lý phân tán và phân tích dữ liệu thị trường chuyển nhượng bóng đá",
          size=10, bold=False, italic=True, color=COLOR_DARK, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)

    # Khung Thông tin Nhóm môn học
    meta_box = [
        "Giảng viên bộ môn: ThS. Huỳnh Thái Học",
        "Nhóm sinh viên thực hiện (Nhóm 5):",
        "  1. Đặng Duy Lợi (Trưởng nhóm - MSSV: 2001230479) - Phụ trách Tổng quan, HDFS, Spark Benchmark",
        "  2. Chu Văn Quốc Trung (MSSV: 2001231010) - Phụ trách PySpark ETL, Spark SQL, Machine Learning",
        "  3. Nguyễn Thế Quang (MSSV: 20012307010) - Phụ trách Kafka Streaming, Airflow DAG, CSDL Data Mart",
        "Thời lượng trình bày trước lớp: 8 đến 10 phút Demo + 3 đến 5 phút trả lời câu hỏi của Thầy",
        "Web Dashboard: http://localhost:8501 (Khởi động 1-Click bằng file CHAY_WEB.bat)",
        "GitHub Repository chính thức: https://github.com/takachi15/transfermarkt-bigdata-analytics"
    ]
    add_callout_box(doc, "THÔNG TIN BÀI BÁO CÁO CUỐI KỲ", meta_box, box_type="normal")

    # ══════════════════════════════════════════════════════════════════════
    # 1. BẢNG PHÂN CÔNG THỜI GIAN & TAB GIAO DIỆN
    # ══════════════════════════════════════════════════════════════════════
    add_heading_1(doc, "1. Bảng phân công thời gian và Tab giao diện trực quan")
    add_p(doc, "Bảng tra cứu nhanh giúp nhóm phối hợp nhịp nhàng: người thuyết trình nói đến đâu, bạn ngồi máy tính bấm ngay Tab và URL đó:")

    timeline_data = [
        ("Phần 1: Mở đầu\n(00:00 - 01:00 | 60s)", "Trang chủ / Header", "http://localhost:8501", "Đặng Duy Lợi"),
        ("Phần 2: Kiến trúc & HDFS\n(01:00 - 02:30 | 90s)", "Bản đồ ứng dụng Big Data\nQuản trị dữ liệu HDFS Data Lake", "http://localhost:8501/?page=Bản+đồ+ứng+dụng+Big+Data\nhttp://localhost:8501/?page=Quản+trị+dữ+liệu+HDFS+Data+Lake", "Đặng Duy Lợi"),
        ("Phần 3: Benchmark Spark vs Pandas\n(02:30 - 04:00 | 90s)", "Benchmark hiệu năng Spark vs Pandas", "http://localhost:8501/?page=Benchmark+hiệu+năng+Spark+vs+Pandas", "Đặng Duy Lợi"),
        ("Phần 4: PySpark ETL & Spark SQL\n(04:00 - 05:30 | 90s)", "Tổng quan thị trường\nPhân tích Spark SQL", "http://localhost:8501/?page=Tổng+quan+thị+trường\nhttp://localhost:8501/?page=Phân+tích+Spark+SQL", "Chu Văn Quốc Trung"),
        ("Phần 5: Machine Learning & Săn cầu thủ\n(05:30 - 07:30 | 120s)", "Phân cụm K-Means\nDự đoán định giá (ML)", "http://localhost:8501/?page=Phân+cụm+K-Means\nhttp://localhost:8501/?page=Dự+đoán+định+giá+(ML)", "Chu Văn Quốc Trung"),
        ("Phần 6: Kafka Streaming & Airflow\n(07:30 - 08:30 | 60s)", "Dòng dữ liệu Kafka Streaming\nĐiều phối Airflow Workflow", "http://localhost:8501/?page=Dòng+dữ+liệu+Kafka+Streaming\nhttp://localhost:8501/?page=Điều+phối+Airflow+Workflow", "Nguyễn Thế Quang"),
        ("Phần 7: CSDL Data Mart & Kết luận\n(08:30 - 09:30 | 60s)", "Truy vấn CSDL Data Mart", "http://localhost:8501/?page=Truy+vấn+CSDL+Data+Mart", "Nguyễn Thế Quang"),
        ("Phần 8: Trả lời câu hỏi của Thầy\n(09:30 - 14:00 | 5 phút)", "Toàn bộ Dashboard & Terminal Logs", "Cổng 8501, 9870, 8080", "Cả 3 thành viên")
    ]
    add_table_data(doc, ["Phân đoạn & Thời gian", "Bấm Tab trên Sidebar", "Địa chỉ URL tương ứng", "Thành viên nói"], timeline_data, [1.7, 1.8, 1.9, 1.1])

    # ══════════════════════════════════════════════════════════════════════
    # 2. KỊCH BẢN CHI TIẾT TỪNG PHÂN ĐOẠN (NÓI CÁI HIỂU LIỀN)
    # ══════════════════════════════════════════════════════════════════════
    add_heading_1(doc, "2. Kịch bản chi tiết từng phân đoạn (Đơn giản, trực quan, nói cái hiểu liền)")

    # ── PHẦN 1 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Phần 1: Mở đầu & Khởi chạy hệ thống 1-Click (1 phút | Đặng Duy Lợi)")
    add_url_box(doc, "Trang chủ Web Dashboard", "http://localhost:8501")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Mở trình duyệt Chrome/Edge đang chạy URL: http://localhost:8501.",
        "2. Bấm phím F11 để bật Toàn màn hình (Full Screen) cho đẹp và gọn gàng.",
        "3. Chỉ tay vào Header chính và 4 ô trạng thái xanh: HDFS (872.5 MB), Spark 4.2 Engine, Kafka Port 9092, Airflow 7 Tasks OK."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI MẪU (NÓI TỰ NHIÊN, DỄ HIỂU)", [
        "\"Kính chào Thầy Huỳnh Thái Học và các bạn trong lớp! Hôm nay Nhóm 5 xin báo cáo bài tập lớn cuối kỳ môn Công nghệ Dữ liệu lớn với đề tài: 'Xây dựng Data Pipeline phân tích thị trường chuyển nhượng bóng đá'.\"",
        "\"Trước đây dữ liệu bóng đá rất rời rạc, các câu lạc bộ thường định giá cầu thủ bằng cảm tính. Nhóm em đã giải quyết bài toán này bằng một hệ thống Big Data hoàn chỉnh từ đầu đến cuối: thu thập 7.5 triệu dòng dữ liệu vào HDFS, dùng Apache Spark xử lý phân tán siêu tốc, Apache Kafka bắt tin chuyển nhượng thời gian thực, Apache Airflow lên lịch tự động và hiển thị trực quan lên Web Dashboard này.\"",
        "\"Toàn bộ hệ sinh thái đã được nhóm đóng gói tự động hóa 1-Click qua file CHAY_WEB.bat. Sau đây em xin bắt đầu trình diễn từng phân hệ!\""
    ], box_type="speech")

    # ── PHẦN 2 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Phần 2: Kiến trúc Lambda 5 lớp & Kho dữ liệu HDFS (1.5 phút | Đặng Duy Lợi)")
    add_url_box(doc, "Bản đồ ứng dụng Big Data & Quản trị dữ liệu HDFS Data Lake",
                "http://localhost:8501/?page=Bản+đồ+ứng+dụng+Big+Data",
                secondary_url="http://localhost:8501/?page=Quản+trị+dữ+liệu+HDFS+Data+Lake (HDFS Web UI: http://localhost:9870)")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Trên Sidebar bên trái, bấm chọn menu: 'Bản đồ ứng dụng Big Data' -> Chỉ vào sơ đồ 5 lớp công nghệ.",
        "2. Tiếp tục bấm chọn menu: 'Quản trị dữ liệu HDFS Data Lake'.",
        "3. Tại ô chọn bảng, lần lượt bấm chọn 'game_lineups.csv' và 'players.csv' để xem số dòng và bảng dữ liệu mẫu."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI MẪU (NÓI CÁI HIỂU LIỀN)", [
        "\"Thưa Thầy và các bạn, hệ thống của nhóm được thiết kế theo đúng kiến trúc Lambda 5 lớp chuẩn trong Big Data: Tầng 1 Lưu trữ HDFS -> Tầng 2 Xử lý mẻ Spark -> Tầng 3 Xử lý luồng Kafka -> Tầng 4 Điều phối Airflow -> Tầng 5 Web Data Mart.\"",
        "\"Tại Tầng lưu trữ HDFS: Nhóm lưu trữ trọn vẹn 12 bảng dữ liệu thô với hơn 7.49 triệu dòng, tổng dung lượng 872.5 MB, cấu hình Block size 128MB và nhân bản 3 lần an toàn.\"",
        "\"Như Thầy và các bạn thấy trên màn hình: bảng game_lineups chứa gần 3.2 triệu dòng lịch sử thi đấu, và bảng trung tâm players gồm hơn 50 nghìn cầu thủ với 26 cột thông tin. Toàn bộ dữ liệu lớn này đã nằm sẵn trên HDFS để cấp phát cho tầng tính toán phía sau!\""
    ], box_type="speech")

    add_callout_box(doc, "Ý CHÍNH CẦN NHỚ", [
        "• Quy mô dữ liệu: 12 file CSV, 7.497.433 bản ghi thô, 872.5 MB.",
        "• Kiến trúc: Lambda 5 tầng, HDFS Block size 128MB, Replication factor 3."
    ], box_type="tech")

    # ── PHẦN 3 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Phần 3: Benchmark Spark 4.2 vs Pandas - Trả lời: Sao phải dùng Big Data? (1.5 phút | Đặng Duy Lợi)")
    add_url_box(doc, "Benchmark hiệu năng Spark vs Pandas", "http://localhost:8501/?page=Benchmark+hiệu+năng+Spark+vs+Pandas")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm chọn menu: 'Benchmark hiệu năng Spark vs Pandas'.",
        "2. Bấm chuột vào nút màu đỏ: 'Chạy kiểm tra tốc độ đọc 200,000 bản ghi'.",
        "3. Đợi 1 giây thanh tiến trình chạy xong, chỉ tay vào biểu đồ cột so sánh thời gian."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI MẪU (NÓI CÁI HIỂU LIỀN)", [
        "\"Nhiều bạn sẽ thắc mắc: 'Dữ liệu chưa tới 1GB thì sao không dùng thư viện Pandas cho tiện, cần chi cài đặt Hadoop với Spark phức tạp?'. Nhóm em xin trả lời bằng thực nghiệm đo đạc trực tiếp trên máy:\"",
        "\"Khi quét và tính toán trên 200,000 dòng dữ liệu của bảng game_lineups: Thư viện Pandas chỉ chạy được trên 1 lõi CPU duy nhất và mất tận 12.45 giây.\"",
        "\"Trong khi đó, Apache Spark 4.2 tự động chia nhỏ dữ liệu thành 16 phân vùng, tận dụng song song 16 luồng CPU phần cứng, hoàn thành chỉ trong 0.78 giây — tức là Spark chạy nhanh gấp 16 lần so với Pandas!\"",
        "\"Điều cốt lõi là: Khi dữ liệu tăng lên 10 triệu hay 50 triệu dòng, Pandas sẽ bị tràn RAM và sập máy, còn Spark chỉ cần gắn thêm máy (mở rộng ngang) là chạy bình thường!\""
    ], box_type="speech")

    add_callout_box(doc, "Ý CHÍNH CẦN NHỚ", [
        "• Pandas: Chạy đơn luồng (1 core), tốn 12.45 giây.",
        "• Spark 4.2: Chạy song song 16 partitions trên 16 cores, chỉ tốn 0.78 giây (Nhanh gấp 16 lần)."
    ], box_type="tech")

    # ── PHẦN 4 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Phần 4: PySpark ETL, Bộ lọc Niên độ & Spark SQL (1.5 phút | Chu Văn Quốc Trung)")
    add_url_box(doc, "Tổng quan thị trường & Phân tích Spark SQL",
                "http://localhost:8501/?page=Tổng+quan+thị+trường",
                secondary_url="http://localhost:8501/?page=Phân+tích+Spark+SQL")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu: 'Tổng quan thị trường' -> Tích vào ô 'Chỉ lấy niên độ gần nhất (2023 - Nay)', chỉ vào thẻ thống kê: 22,751 cầu thủ đang đá với tổng định giá 16.5 tỷ Euro.",
        "2. Bấm menu: 'Phân tích Spark SQL' -> Bấm chuyển giữa 4 tab: Top 15 siêu sao, Vị trí thi đấu, Quốc gia, Độ tuổi. Bấm thử nút 'Trang tiếp ▶' trên bảng phân trang."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI MẪU (NÓI CÁI HIỂU LIỀN)", [
        "\"Chào Thầy và các bạn, em là Chu Văn Quốc Trung, phụ trách phần PySpark ETL, Spark SQL và Machine Learning.\"",
        "\"Thứ nhất, về làm sạch dữ liệu lớn: File thô có hơn 50 nghìn cầu thủ nhưng nhiều người bị thiếu giá tiền, thiếu chiều cao. PySpark đã tự động điền trung vị chiều cao, tính lại tuổi từ ngày sinh và lọc ra đúng 40,749 cầu thủ chuẩn, lưu vào file nén Parquet chỉ còn 1.4 MB — giúp tiết kiệm đến 97% dung lượng lưu trữ so với file gốc.\"",
        "\"Thứ hai, nhóm thiết kế thêm Bộ lọc niên độ 2023 - Nay để loại bỏ những cầu thủ đã giải nghệ từ 20 năm trước, giữ lại đúng 22 nghìn cầu thủ đang thi đấu thực tế.\"",
        "\"Thứ ba, ở phần Spark SQL: Nhóm dùng Spark SQL chạy phân tán 4 truy vấn: tìm ra Top 15 siêu sao đắt nhất thế giới như Haaland, Mbappe giá 180 đến 200 triệu Euro; vị trí Tiền đạo luôn áp đảo về giá trị; và độ tuổi vàng đạt đỉnh giá trị là từ 25 đến 28 tuổi. Bảng dữ liệu có phân trang thông minh lưu trạng thái vào URL, khi bấm F5 vẫn giữ nguyên trang đang xem!\""
    ], box_type="speech")

    add_callout_box(doc, "Ý CHÍNH CẦN NHỚ", [
        "• Làm sạch: 50.149 dòng thô -> 40.749 dòng sạch (Parquet nén Snappy chỉ 1.4 MB).",
        "• Niên độ: Lọc 22.751 cầu thủ đang thi đấu (2023 - Nay).",
        "• Spark SQL: Top 15 siêu sao, phân tích vị trí, quốc gia, độ tuổi vàng 25-28."
    ], box_type="tech")

    # ── PHẦN 5 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Phần 5: Machine Learning - K-Means & Săn cầu thủ giá hời (2 phút | Chu Văn Quốc Trung)")
    add_url_box(doc, "Phân cụm K-Means & Dự đoán định giá (ML)",
                "http://localhost:8501/?page=Phân+cụm+K-Means",
                secondary_url="http://localhost:8501/?page=Dự+đoán+định+giá+(ML)")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu: 'Phân cụm K-Means' -> Chỉ vào biểu đồ 3 cụm màu sắc và điểm Silhouette Score k=3 đạt 0.6429.",
        "2. Bấm menu: 'Dự đoán định giá (ML)':",
        "   - Tại ô chọn cầu thủ: Gõ tên 'Erling Haaland' (hoặc chọn 'Lamine Yamal') -> Xem AI dự đoán giá và 5 bước giải thích XAI.",
        "   - Cuộn xuống tính năng 'Săn cầu thủ theo Ngân sách (Scouting Engine)': Kéo thanh ngân sách về 35 triệu EUR, chọn Vị trí 'Attack', tích ô 'Chỉ tìm cầu thủ Kèo hời' -> Xem danh sách cầu thủ hiện ra."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI MẪU (NÓI CÁI HIỂU LIỀN)", [
        "\"Tiếp theo là phần thông minh nhất của đồ án: Ứng dụng Machine Learning phân tán để giải quyết bài toán định giá cầu thủ.\"",
        "\"1. Về Phân cụm K-Means: Nhóm đã thử nghiệm Silhouette từ k=2 đến k=6 và chọn k=3 tối ưu nhất với điểm Silhouette đạt 0.6429. Thuật toán tự chia cầu thủ làm 3 phân khúc rất chuẩn: Cụm Siêu sao thế giới (giá trung bình gần 30 triệu Euro), Cụm Cầu thủ trụ cột (1.2 triệu Euro) và Cụm Cầu thủ tiềm năng/phổ thông (400 nghìn Euro).\"",
        "\"2. Về Dự đoán giá chuyển nhượng bằng Random Forest: Do giá cầu thủ bị lệch rất mạnh (đa số cầu thủ giá rẻ, chỉ vài người giá cực cao), nhóm dùng phép biến đổi logarit chuẩn hóa y = ln(1 + market_value), giúp mô hình đạt độ chính xác R2 = 84.7%. Ví dụ khi chọn Erling Haaland, AI dự đoán khoảng 175 triệu Euro — rất sát thực tế. Hệ thống còn có Explainable AI giải thích rõ 5 lý do tại sao cầu thủ này có giá đó.\"",
        "\"3. Đặc biệt là tính năng Săn cầu thủ giá hời: Ví dụ một CLB có ngân sách 35 triệu Euro, công cụ sẽ quét toàn bộ 40 nghìn hồ sơ để tìm ra những cầu thủ có tài năng vượt trội nhưng đang bị thị trường định giá thấp, giúp CLB mua được cầu thủ giỏi với giá rẻ!\""
    ], box_type="speech")

    add_callout_box(doc, "Ý CHÍNH CẦN NHỚ", [
        "• K-Means: k=3 tối ưu, Silhouette Score = 0.6429 (3 phân khúc cầu thủ rõ rệt).",
        "• Random Forest Regressor: R2 = 84.68%, biến đổi log1p(y) triệt tiêu độ lệch phải.",
        "• Tính năng thực tế: Explainable AI (XAI 5 bước) & Scouting Engine săn cầu thủ giá hời."
    ], box_type="tech")

    # ── PHẦN 6 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Phần 6: Kafka Streaming & Điều phối Airflow DAG (1 phút | Nguyễn Thế Quang)")
    add_url_box(doc, "Dòng dữ liệu Kafka Streaming & Điều phối Airflow Workflow",
                "http://localhost:8501/?page=Dòng+dữ+liệu+Kafka+Streaming",
                secondary_url="http://localhost:8501/?page=Điều+phối+Airflow+Workflow (Airflow UI: http://localhost:8080)")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu: 'Dòng dữ liệu Kafka Streaming' -> Xem các dòng tin JSON giao dịch phát trực tiếp thời gian thực (15 thương vụ, tổng 707 triệu Euro).",
        "2. Bấm menu: 'Điều phối Airflow Workflow' -> Chỉ vào sơ đồ 7 task tuần tự và trạng thái 100% SUCCESS màu xanh lá."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI MẪU (NÓI CÁI HIỂU LIỀN)", [
        "\"Chào Thầy và các bạn, em là Nguyễn Thế Quang, phụ trách mảng Streaming Kafka, điều phối Airflow và CSDL Data Mart.\"",
        "\"Thứ nhất, với Apache Kafka: Trong kỳ chuyển nhượng luôn có những thương vụ đột xuất diễn ra từng giờ. Để xử lý dữ liệu thời gian thực, nhóm dùng Kafka chạy ở cổng 9092. Producer liên tục phát sóng các bản tin chuyển nhượng mới dạng JSON, Consumer bắt lấy và cập nhật tức thì lên hệ thống với tổng giá trị theo dõi hơn 707 triệu Euro mà không phải chạy lại toàn bộ dữ liệu lịch sử cũ.\"",
        "\"Thứ hai, với Apache Airflow: Toàn bộ quy trình 7 bước (từ HDFS -> Spark làm sạch -> Spark SQL -> K-Means -> Random Forest -> Lưu vào CSDL) được nhóm gom vào 1 DAG tự động trên Airflow, triển khai bằng Docker Compose. Toàn bộ 7 task đều chạy thành công 100% SUCCESS trong 2 phút 10 giây!\""
    ], box_type="speech")

    add_callout_box(doc, "Ý CHÍNH CẦN NHỚ", [
        "• Kafka Streaming: Topic football_transfers cổng 9092, đẩy tin tức thì.",
        "• Apache Airflow: DAG 7 tasks tự động hóa 100% SUCCESS, hoàn thành trong 2m 10s."
    ], box_type="tech")

    # ── PHẦN 7 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Phần 7: CSDL Data Mart & Kết luận (1 phút | Nguyễn Thế Quang)")
    add_url_box(doc, "Truy vấn CSDL Data Mart", "http://localhost:8501/?page=Truy+vấn+CSDL+Data+Mart")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu: 'Truy vấn CSDL Data Mart'.",
        "2. Tại ô chọn truy vấn mẫu, chọn: 'Top 10 cầu thủ có giá trị cao nhất' -> Bấm nút 'Thực thi truy vấn SQL' -> Kết quả hiện ra ngay lập tức."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI MẪU (NÓI CÁI HIỂU LIỀN)", [
        "\"Cuối cùng là Tầng phục vụ Web (Serving Layer). Sau khi Spark tính toán dữ liệu lớn xong, kết quả được lưu vào CSDL SQLite Data Mart football_analytics.db. Nhờ vậy trang web phản hồi cực nhanh dưới 10 mili-giây mà không làm nghẽn máy chủ Spark.\"",
        "\"Tóm lại: Bài tập lớn cuối kỳ của Nhóm 5 đã vận dụng đầy đủ cả 5 công nghệ cốt lõi của Big Data: Hadoop HDFS, Apache Spark, Apache Kafka, Apache Airflow và Machine Learning. Hệ thống chạy ổn định 100%, có thể chạy lại bất cứ lúc nào và có ý nghĩa ứng dụng thực tế cao.\"",
        "\"Nhóm 5 chúng em xin chân thành cảm ơn Thầy Huỳnh Thái Học và các bạn đã chú ý lắng nghe. Nhóm em rất mong nhận được câu hỏi và góp ý từ Thầy ạ!\""
    ], box_type="speech")

    # ══════════════════════════════════════════════════════════════════════
    # 3. 5 CÂU HỎI THẦY HAY HỎI & CÁCH TRẢ LỜI NGẮN GỌN (ĂN ĐIỂM NGAY)
    # ══════════════════════════════════════════════════════════════════════
    add_heading_1(doc, "3. Top 5 câu hỏi Thầy hay hỏi & Cách trả lời ngắn gọn (Hiểu liền, ăn điểm ngay)")

    qa_list = [
        ("Câu 1: Tại sao đề tài lại dùng thêm SQLite mà không cho Web truy vấn trực tiếp từ Spark hoặc HDFS?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, Spark và HDFS được thiết kế để xử lý dữ liệu lớn theo mẻ. Mỗi lần chạy một câu lệnh trên Spark mất từ 5 đến 10 giây để khởi động JVM, nếu người dùng lướt web mà chờ lâu như vậy thì web sẽ bị đơ. Vì vậy theo mô hình Lambda, Spark tính toán trước rồi lưu kết quả vào CSDL SQLite (Serving Layer) để người dùng lướt web mượt mà dưới 10 mili-giây mà không tốn tài nguyên máy chủ ạ."),
        
        ("Câu 2: Dữ liệu chưa tới 1GB thì có thực sự cần đến Hadoop/Spark không hay chỉ cần Pandas là đủ?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, dữ liệu của nhóm có gần 7.5 triệu dòng. Khi chạy thử nghiệm thực tế trên bảng 200,000 dòng, Pandas chạy đơn luồng mất 12.45 giây, trong khi Spark chia 16 luồng song song chỉ mất 0.78 giây (nhanh gấp 16 lần). Quan trọng hơn, Spark có khả năng mở rộng ngang: khi dữ liệu tăng lên 10 triệu hay 50 triệu dòng, Pandas sẽ bị sập vì tràn RAM, còn Spark chỉ cần gắn thêm máy là chạy bình thường ạ."),
        
        ("Câu 3: Phân cụm K-Means tại sao nhóm lại chọn k=3 mà không phải k=4 hay k=5?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, nhóm chọn k=3 vì 2 lý do: Thứ nhất về toán học, nhóm đã chạy thử nghiệm Silhouette từ k=2 đến 6 thì k=3 đạt điểm cao nhất là 0.6429. Thứ hai về thực tế bóng đá, k=3 chia rất đúng 3 nhóm: Siêu sao thế giới (giá ~30 triệu Euro), Cầu thủ trụ cột các giải lớn (~1.2 triệu Euro), và Cầu thủ trẻ tiềm năng / giải đấu phổ thông (~400 nghìn Euro) ạ."),
        
        ("Câu 4: Tại sao trong mô hình Random Forest phải biến đổi log1p cho giá trị cầu thủ?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, trong bóng đá giá trị cầu thủ bị lệch rất nặng: đa số cầu thủ chỉ vài trăm nghìn đến vài triệu Euro, nhưng một số ít siêu sao lại có giá lên tới gần 200 triệu Euro. Nếu để nguyên thì thuật toán chỉ tập trung học siêu sao và đoán sai hết nhóm phổ thông. Phép biến đổi ln(1 + y) giúp nén giá trị về dạng phân phối chuẩn, giúp mô hình học đều và nâng độ chính xác R2 từ dưới 60% lên đạt 84.7% ạ."),
        
        ("Câu 5: Apache Kafka trong bài làm nhiệm vụ gì và dữ liệu streaming đi về đâu?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, Spark dùng để xử lý dữ liệu lịch sử theo mẻ, còn Kafka dùng để truyền tải các thương vụ chuyển nhượng mới phát sinh theo thời gian thực (Speed Layer). Producer phát bản tin chuyển nhượng qua cổng 9092, Consumer bắt lấy tin tức thì và ghi vào CSDL Data Mart để cập nhật ngay lên Dashboard cho người dùng xem ạ.")
    ]

    for q, a in qa_list:
        add_p(doc, q, size=10.5, bold=True, color=COLOR_NAVY, space_before=5, space_after=1)
        add_p(doc, a, size=10, bold=False, italic=False, color=COLOR_DARK, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=5)

    # ══════════════════════════════════════════════════════════════════════
    # 4. 4 MẸO NHỎ ĐỂ BÁO CÁO MƯỢT MÀ VÀ ĐẠT ĐIỂM CAO
    # ══════════════════════════════════════════════════════════════════════
    add_heading_1(doc, "4. Bốn mẹo nhỏ để nhóm báo cáo tự tin và đạt điểm tối đa")
    tips = [
        "Phối hợp nhịp nhàng giữa người nói và người bấm máy: Người ngồi máy tính chuyển Tab trước 3 giây khi bạn mình chuẩn bị nói đến phần đó. Khi bạn nói đến Spark Benchmark, bấm nút chạy ngay để kết quả hiện ra đúng lúc.",
        "Nói ngắn gọn, rõ ràng, không đọc thuộc lòng: Mỗi phần chỉ cần nắm đúng 3 ý: Trang này làm gì? Dùng công nghệ Big Data nào? Con số nổi bật là gì?",
        "Tự tin trả lời câu hỏi của Thầy: Luôn mở đầu bằng 'Dạ thưa Thầy...', trả lời thẳng vào trọng tâm trong 2-3 câu, không lan man lý thuyết.",
        "Hệ thống đã chạy sẵn và an toàn 100%: Dữ liệu và mô hình AI đã được nhóm lưu sẵn offline trên máy, hoàn toàn không phụ thuộc vào mạng Internet trường học nên cứ an tâm trình diễn!"
    ]
    for idx, tip in enumerate(tips):
        add_p(doc, f"• Mẹo {idx+1}: {tip}", size=10, space_before=1, space_after=3)

    # Lưu tệp DOCX cả 2 tên để tiện dùng và tương thích 100%
    doc.save(OUT_DOCX)
    doc.save(OUT_DOCX_FRIENDLY)
    print(f"[HOÀN THÀNH] ĐÃ TẠO TỆP KỊCH BẢN DEMO BÁO CÁO CUỐI KỲ TẠI:\n - {OUT_DOCX}\n - {OUT_DOCX_FRIENDLY}")

if __name__ == "__main__":
    build_demo_document()
