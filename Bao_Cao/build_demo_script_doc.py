# -*- coding: utf-8 -*-
"""
build_demo_script_doc.py
========================
KỊCH BẢN BÁO CÁO CUỐI KỲ MÔN HỌC CÔNG NGHỆ DỮ LIỆU LỚN (BIG DATA)
Trọng tâm:
- Giải thích bản chất từng công nghệ (Hiểu gì về DataNode, NameNode, Spark, Parquet, Kafka, Airflow, ML, Data Mart).
- Áp dụng vào project cụ thể như thế nào.
- Giải quyết triệt để những vấn đề kỹ thuật và thực tiễn gì.
- Lời thoại trực quan, ngắn gọn, nói cái là hiểu liền.
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
OUT_DOCX = os.path.join(BASE_DIR, "Kich_Ban_Demo_Bao_Cao_Cuoi_Ky_BigData.docx")

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
HEX_PROBLEM_BG= "FEF2F2"  # Đỏ nhạt cho giải quyết vấn đề
HEX_URL_BG    = "F1F5F9"  # Xám sáng cho URL

def set_page_margins(section):
    section.top_margin    = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin   = Inches(0.7)
    section.right_margin  = Inches(0.7)

def set_cell_pad(cell, t=50, b=50, l=80, r=80):
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

def set_cell_borders(cell, top=True, bottom=True, left=True, right=True, color="CBD5E1", sz="4"):
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

def add_p(doc, text="", size=10.5, bold=False, italic=False, color=COLOR_DARK, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=2, line_spacing=1.15):
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
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    apply_font_to_run(r, FONT_MAIN, size_pt=12.5, bold=True, color=COLOR_NAVY)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    apply_font_to_run(r, FONT_MAIN, size_pt=11.5, bold=True, color=COLOR_TEAL)
    return p

def add_url_box(doc, page_name, direct_url, secondary_url=None):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.6)
    set_bg(cell, HEX_URL_BG)
    set_cell_pad(cell, t=45, b=45, l=80, r=80)
    set_cell_borders(cell, top=True, bottom=True, left=True, right=True, color="1B365D", sz="6")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(1)
    p.paragraph_format.line_spacing = 1.15
    
    r_tag = p.add_run("[ĐỊNH VỊ GIAO DIỆN & URL TRUY CẬP]\n")
    apply_font_to_run(r_tag, FONT_MAIN, size_pt=9, bold=True, color=COLOR_NAVY)
    
    r_tab = p.add_run(f"• Bấm Tab trên Sidebar: \"{page_name}\"\n")
    apply_font_to_run(r_tab, FONT_MAIN, size_pt=10, bold=True, color=COLOR_TEAL)
    
    r_url = p.add_run(f"• URL Web Dashboard: {direct_url}\n")
    apply_font_to_run(r_url, FONT_CODE, size_pt=9, bold=True, color=COLOR_NAVY)
    
    if secondary_url:
        r_sec = p.add_run(f"• Cổng dịch vụ hạ tầng liên kết: {secondary_url}")
        apply_font_to_run(r_sec, FONT_CODE, size_pt=8.5, bold=False, color=COLOR_MUTED)
    add_p(doc, "", size=2, space_before=0, space_after=1)

def add_callout_box(doc, title, items, box_type="speech"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.6)
    
    if box_type == "speech":
        bg_hex = HEX_ACCENT_BG
        border_color = "0D766E"
        title_color = COLOR_TEAL
        icon_prefix = "[LỜI THOẠI NÓI CÁI HIỂU LIỀN] "
    elif box_type == "action":
        bg_hex = HEX_ACTION_BG
        border_color = "1B365D"
        title_color = COLOR_NAVY
        icon_prefix = "[THAO TÁC MÀN HÌNH] "
    elif box_type == "tech":
        bg_hex = HEX_TECH_BG
        border_color = "D97706"
        title_color = RGBColor(180, 83, 9)
        icon_prefix = "[BẢN CHẤT CÔNG NGHỆ & CÁCH ÁP DỤNG] "
    elif box_type == "problem":
        bg_hex = HEX_PROBLEM_BG
        border_color = "DC2626"
        title_color = RGBColor(185, 28, 28)
        icon_prefix = "[GIẢI QUYẾT VẤN ĐỀ GÌ TRONG BÀI TOÁN?] "
    else:
        bg_hex = HEX_LIGHT_BG
        border_color = "94A3B8"
        title_color = COLOR_DARK
        icon_prefix = "[THÔNG TIN] "

    set_bg(cell, bg_hex)
    set_cell_pad(cell, t=50, b=50, l=80, r=80)
    set_cell_borders(cell, top=True, bottom=True, left=True, right=True, color=border_color, sz="6")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    r_title = p.add_run(icon_prefix + title)
    apply_font_to_run(r_title, FONT_MAIN, size_pt=9.5, bold=True, color=title_color)
    
    for item in items:
        p_c = cell.add_paragraph()
        p_c.paragraph_format.space_before = Pt(1)
        p_c.paragraph_format.space_after  = Pt(1)
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
        set_cell_pad(hdr_cells[c_idx], t=50, b=50, l=60, r=60)
        set_cell_borders(hdr_cells[c_idx], top=True, bottom=True, left=False, right=False, color="1B365D", sz="8")
        p = hdr_cells[c_idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after  = Pt(1)
        r = p.add_run(title)
        apply_font_to_run(r, FONT_MAIN, size_pt=9, bold=True, color=RGBColor(255, 255, 255))
        
    for r_idx, row in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        bg_col = HEX_LIGHT_BG if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row):
            set_bg(row_cells[c_idx], bg_col)
            set_cell_pad(row_cells[c_idx], t=45, b=45, l=60, r=60)
            set_cell_borders(row_cells[c_idx], top=True, bottom=True, left=False, right=False, color="E2E8F0", sz="4")
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 1 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after  = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(str(val))
            apply_font_to_run(r, FONT_MAIN, size_pt=8.5, bold=(c_idx == 0 or c_idx == len(row)-1), color=COLOR_DARK)
            
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
          size=9.5, bold=True, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)

    add_p(doc, "KỊCH BẢN BÁO CÁO & GIẢI TRÌNH CÔNG NGHỆ BIG DATA CUỐI KỲ",
          size=14, bold=True, color=COLOR_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p(doc, "TRỌNG TÂM: BẢN CHẤT CÔNG NGHỆ (DATANODE/NAMENODE, SPARK, KAFKA, AIRFLOW) & GIẢI QUYẾT BÀI TOÁN GÌ",
          size=10, bold=True, color=COLOR_TEAL, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    add_p(doc, "Đề tài: Xây dựng Data Pipeline thu thập, xử lý phân tán và phân tích dữ liệu thị trường chuyển nhượng bóng đá",
          size=9.5, bold=False, italic=True, color=COLOR_DARK, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=6)

    # Khung Thông tin Nhóm
    meta_box = [
        "Giảng viên bộ môn: ThS. Huỳnh Thái Học",
        "Nhóm 5: Đặng Duy Lợi (Trưởng nhóm - 2001230479) | Chu Văn Quốc Trung (2001231010) | Nguyễn Thế Quang (20012307010)",
        "Thời lượng trình bày: 8 đến 10 phút Demo + 3 đến 5 phút trả lời câu hỏi chuyên sâu của Thầy",
        "Web Dashboard: http://localhost:8501 (Tab 1 -> 10) | HDFS NameNode Web UI: http://localhost:9870",
        "Khởi động 1-Click tự động hóa cả 2 máy chủ bằng file CHAY_WEB.bat | GitHub: https://github.com/takachi15/transfermarkt-bigdata-analytics"
    ]
    add_callout_box(doc, "THÔNG TIN BÀI BÁO CÁO", meta_box, box_type="normal")

    # ══════════════════════════════════════════════════════════════════════
    # BẢNG MA TRẬN 7 CÔNG NGHỆ CỐT LÕI
    # ══════════════════════════════════════════════════════════════════════
    add_heading_1(doc, "1. Bảng Ma trận 7 Công nghệ Big Data: Bản chất & Vấn đề giải quyết")
    add_p(doc, "Bảng tóm tắt để người nghe và giảng viên nắm bắt ngay lập tức giá trị kỹ thuật của đề tài:")

    matrix_data = [
        ("1. Hadoop HDFS\n(NameNode & DataNode)", "NameNode giữ metadata cây thư mục;\n3 DataNode lưu các khối 128MB (Rep=3).", "Quản lý 12 CSV Data Lake (872.5 MB,\n7.5M dòng) tại /football_project/.", "Chống mất dữ liệu (hỏng 1-2 node vẫn còn);\nXóa nghẽn I/O đọc song song cho Spark."),
        ("2. Apache Spark\n(PySpark Engine)", "Tính toán phân tán In-Memory (Tungsten);\nTối ưu truy vấn bằng Catalyst Optimizer.", "16 Cores CPU song song làm sạch 50k cầu thủ\nvà chạy 4 truy vấn Spark SQL đa chiều.", "Nhanh gấp 16.0 lần Pandas (0.78s vs 12.45s);\nKhông bị tràn RAM sập máy khi dữ liệu lớn."),
        ("3. Apache Parquet\n(Snappy Columnar)", "Lưu trữ dạng cột nén Snappy; Chỉ đọc đúng\ncột cần tính, bỏ qua các cột thừa.", "Xuất cleaned_players.parquet (1.41 MB)\ncho tầng Machine Learning và Web.", "Tiết kiệm 97.7% dung lượng ổ đĩa (18.7M -> 1.4M);\nTăng tốc độ I/O nạp dữ liệu vào mô hình."),
        ("4. Machine Learning\n(MLlib & Scikit)", "K-Means gom cụm không giám sát (k=3);\nRandom Forest biến đổi log1p(y) chống lệch.", "Phân khúc 3 đẳng cấp cầu thủ (Silhouette 0.64);\nDự đoán giá R²=84.7% & Scouting Engine.", "Xóa bỏ định giá cầu thủ bằng cảm tính;\nTự động phát hiện cầu thủ giá hời (Undervalued)."),
        ("5. Apache Kafka\n(Speed Layer)", "Message Broker Publish/Subscribe thời gian thực,\nchịu tải hàng ngàn tin/giây, độ trễ mili-giây.", "Cổng 9092, topic football_transfers bắt sóng\ncác tin chuyển nhượng mới phát sinh dạng JSON.", "Giải quyết độ trễ: Cập nhật biến động giá tức thì\nmà không phải chạy lại toàn bộ mẻ dữ liệu lịch sử."),
        ("6. Apache Airflow\n(Orchestration)", "Điều phối lập lịch tự động chuỗi công việc\ndưới dạng đồ thị có hướng không chu trình (DAG).", "DAG transfermarkt_pipeline gồm 7 task\ntuần tự chạy qua 5 container Docker Compose.", "Loại bỏ thao tác thủ công dễ quên/sai sót;\nTự động kiểm tra điều kiện, ghi log & xử lý lỗi."),
        ("7. SQLite Data Mart\n(Serving Layer)", "CSDL Serving phục vụ dữ liệu đã tính toán sẵn\n(Pre-computed) có đánh chỉ mục tối ưu.", "football_analytics.db lưu 5 bảng quan hệ\nphục vụ hiển thị trên Streamlit UI.", "Giúp Web phản hồi dưới 10ms, không gây đơ web\nvà không chiếm dụng tài nguyên tính toán của Spark.")
    ]
    add_table_data(doc, ["Công nghệ cốt lõi", "Tôi hiểu gì về nó? (Bản chất)", "Áp dụng vào project ra sao?", "Giải quyết vấn đề gì trong bài toán?"], matrix_data, [1.4, 1.8, 1.8, 1.6])

    # ══════════════════════════════════════════════════════════════════════
    # KỊCH BẢN CHI TIẾT THEO 10 BƯỚC GIAO DIỆN
    # ══════════════════════════════════════════════════════════════════════
    add_heading_1(doc, "2. Kịch bản chi tiết từng bước Demo (Đi thẳng vào Công nghệ & Giải quyết vấn đề)")

    # ── BƯỚC 1 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Bước 1: Tổng quan đề tài & Khởi chạy 1-Click (1 phút | Đặng Duy Lợi)")
    add_url_box(doc, "1. Bản đồ Kiến trúc & Tổng quan", "http://localhost:8501")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Mở trình duyệt Chrome/Edge đang chạy URL: http://localhost:8501 (Nhấn F11 bật Toàn màn hình).",
        "2. Chỉ tay vào 4 thẻ số liệu Big Data nền tảng: HDFS (872.5 MB), Spark 4.2 (16 Cores), Kafka (Port 9092), Airflow (7 Tasks SUCCESS).",
        "3. Cuộn nhẹ chỉ vào sơ đồ 5 lớp công nghệ Lambda Architecture."
    ], box_type="action")

    add_callout_box(doc, "LỜI THOẠI NÓI CÁI HIỂU LIỀN", [
        "\"Kính chào Thầy Huỳnh Thái Học và các bạn! Nhóm 5 xin báo cáo bài tập lớn môn Công nghệ Dữ liệu lớn với đề tài: Xây dựng Data Pipeline phân tích thị trường chuyển nhượng bóng đá quốc tế.\"",
        "\"Bài toán thực tế nhóm giải quyết: Trước đây dữ liệu bóng đá cực kỳ rời rạc và việc định giá cầu thủ chủ yếu dựa trên cảm tính. Nhóm đã ứng dụng đầy đủ 7 công nghệ Big Data phân tán để tự động hóa trọn vẹn vòng đời dữ liệu: từ lưu trữ HDFS, tính toán phân tán Spark, bắt tin thời gian thực Kafka, điều phối Airflow đến phục vụ trực quan trên Web.\"",
        "\"Toàn bộ hệ thống được nhóm đóng gói 1-Click tự động khởi chạy cả 2 máy chủ Web Dashboard (8501) và HDFS NameNode (9870) qua file CHAY_WEB.bat. Sau đây nhóm xin đi sâu vào từng công nghệ cốt lõi!\""
    ], box_type="speech")

    # ── BƯỚC 2 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Bước 2: Giải trình HDFS NameNode & DataNode (1.5 phút | Đặng Duy Lợi)")
    add_url_box(doc, "2. Quản trị dữ liệu HDFS Data Lake",
                "http://localhost:8501/?page=Quản+trị+dữ+liệu+HDFS+Data+Lake",
                secondary_url="Giao diện độc lập: http://localhost:9870/#tab-datanode")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Trên Sidebar, bấm chọn menu: '2. Quản trị dữ liệu HDFS Data Lake'.",
        "2. Bấm vào tab con: 'Giám sát Cụm 3 DataNodes (Live Cluster)' -> Chỉ vào 3 thẻ xanh lá của 3 DataNodes và sơ đồ phân bổ 18 khối dữ liệu.",
        "3. (Nếu Thầy yêu cầu mở cổng 9870): Bấm vào nút 'Mở http://localhost:9870' để chuyển sang giao diện gốc NameNode Web UI.",
        "4. Bấm sang tab con: 'Trích xuất Schema & Khối Dữ liệu Mẫu' -> Chọn bảng game_lineups.csv (3.18 Triệu dòng)."
    ], box_type="action")

    add_callout_box(doc, "BẢN CHẤT CÔNG NGHỆ: HIỂU GÌ VỀ NAMENODE & DATANODE?", [
        "• NameNode (Master Node, cổng 9820 / Web UI 9870): Là 'Bộ não chỉ huy', chỉ lưu trữ Siêu dữ liệu (Metadata) trong bộ nhớ RAM: quản lý cây thư mục /football_project/, lưu bảng ánh xạ xem khối dữ liệu nào nằm ở DataNode nào, và liên tục lắng nghe nhịp tim (Heartbeat) của các DataNode.",
        "• DataNode (Worker Nodes, cổng 9864-9866): Là 'Kho chứa dữ liệu vật lý', không lưu file thông thường mà lưu các khối nhị phân (Binary Blocks) kích thước 128 MB (như blk_1073741825) kèm tệp kiểm tra toàn vẹn .meta.",
        "• Áp dụng trong project: Cụm gồm 1 NameNode và 3 Live DataNodes, lưu trữ trọn vẹn 12 tệp CSV Transfermarkt (872.5 MB, 7.5 triệu dòng) được chia thành 18 Blocks với Replication factor = 3 (Tổng dung lượng lưu trên 3 DataNode là ~2.58 GB)."
    ], box_type="tech")

    add_callout_box(doc, "GIẢI QUYẾT VẤN ĐỀ GÌ TRONG BÀI TOÁN?", [
        "1. Chống mất mát dữ liệu (Fault Tolerance): Ổ cứng máy chủ có thể hỏng bất cứ lúc nào. Nhờ cơ chế nhân bản 3 lần trên 3 DataNode độc lập, nếu lỡ có 1 hoặc 2 DataNode bị mất điện hay hỏng ổ cứng, dữ liệu giải đấu và cầu thủ vẫn nguyên vẹn 100%!",
        "2. Xóa bỏ nghẽn cổ chai I/O đĩa cứng (Storage Bottleneck): Thay vì bắt 1 ổ cứng đơn lẻ phải đọc tuần tự 872 MB, NameNode phân bổ các khối cho 3 DataNode cấp phát đồng thời cho cụm Spark đọc song song (Data Locality).",
        "3. Khả năng mở rộng ngang (Horizontal Scalability): Khi bổ sung dữ liệu các mùa giải mới lên hàng chục triệu dòng, nhóm chỉ cần cắm thêm DataNode mới vào mạng mà không phải đập đi xây lại hệ thống."
    ], box_type="problem")

    add_callout_box(doc, "LỜI THOẠI NÓI CÁI HIỂU LIỀN", [
        "\"Thưa Thầy, ở tầng Data Lake, nhóm ứng dụng mô hình phân tán của Hadoop HDFS gồm 1 NameNode và 3 DataNode:\"",
        "\"NameNode chạy ở cổng 9820 đóng vai trò bộ não, giữ metadata trong RAM để điều phối. Còn 3 DataNode đóng vai trò kho chứa, lưu trữ trực tiếp các khối nhị phân 128MB. Toàn bộ 12 tệp CSV nặng 872.5 MB được chia thành 18 blocks và nhân bản 3 lần sang cả 3 DataNode.\"",
        "\"Kiến trúc này giải quyết 2 vấn đề sống còn: Thứ nhất là chống mất dữ liệu — nếu 1-2 DataNode bị sập ổ cứng thì dữ liệu vẫn còn nguyên. Thứ hai là xóa bỏ nghẽn I/O — 3 DataNode sẽ phát dữ liệu đồng thời cho Spark xử lý song song thay vì bắt 1 ổ cứng phải đọc tuần tự!\""
    ], box_type="speech")

    # ── BƯỚC 3 ───────────────────────────────────────────────────────────
    add_heading_2(doc, "Bước 3: Giải trình Apache Spark & Benchmark vs Pandas (1.5 phút | Đặng Duy Lợi)")
    add_url_box(doc, "3. Benchmark hiệu năng Spark vs Pandas", "http://localhost:8501/?page=Benchmark+hiệu+năng+Spark+vs+Pandas")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu: '3. Benchmark hiệu năng Spark vs Pandas'.",
        "2. Bấm nút màu đỏ: 'Chạy kiểm tra tốc độ đọc 200,000 bản ghi'.",
        "3. Chỉ tay vào biểu đồ cột so sánh: Spark (0.78s) vs Pandas (12.45s)."
    ], box_type="action")

    add_callout_box(doc, "BẢN CHẤT CÔNG NGHỆ & GIẢI QUYẾT VẤN ĐỀ", [
        "• Bản chất: Apache Spark 4.2 sử dụng cơ chế tính toán trong bộ nhớ RAM (In-Memory Computing) thông qua RDD/DataFrame và bộ tối ưu hóa truy vấn Catalyst Optimizer.",
        "• Vấn đề giải quyết: Thư viện Pandas truyền thống chỉ chạy đơn luồng (1 core CPU duy nhất) nên mất tận 12.45 giây trên 200,000 dòng và sẽ bị tràn RAM (Out-Of-Memory) khi quét bảng lớn 3.2 triệu dòng. Trong khi đó, Spark tự chia dữ liệu thành 16 phân vùng, chạy song song trên 16 luồng CPU chỉ tốn 0.78 giây (nhanh gấp 16 lần) và không bao giờ bị nghẽn RAM."
    ], box_type="problem")

    add_callout_box(doc, "LỜI THOẠI NÓI CÁI HIỂU LIỀN", [
        "\"Tại sao nhóm phải dùng Spark mà không dùng Pandas? Thực nghiệm trực tiếp cho thấy: Trên 200 nghìn dòng dữ liệu, Pandas chạy đơn luồng mất 12.45 giây, trong khi Spark tận dụng 16 luồng CPU chạy song song chỉ mất 0.78 giây — nhanh gấp 16 lần!\"",
        "\"Quan trọng hơn, khi dữ liệu tăng lên hàng chục triệu dòng, Pandas sẽ bị tràn RAM sập máy, còn Spark nhờ kiến trúc phân tán In-Memory sẽ chia nhỏ ra xử lý mượt mà!\""
    ], box_type="speech")

    # ── BƯỚC 4 & 5 ────────────────────────────────────────────────────────
    add_heading_2(doc, "Bước 4 & 5: PySpark ETL, Định dạng Parquet & Spark SQL (1.5 phút | Chu Văn Quốc Trung)")
    add_url_box(doc, "4. Tổng quan thị trường (PySpark ETL) & 5. Phân tích Spark SQL",
                "http://localhost:8501/?page=Tổng+quan+thị+trường",
                secondary_url="http://localhost:8501/?page=Phân+tích+Spark+SQL")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu '4. Tổng quan thị trường (PySpark ETL)' -> Tích chọn 'Chỉ lấy niên độ gần nhất (2023 - Nay)' xem thẻ 22,751 cầu thủ.",
        "2. Bấm menu '5. Phân tích Spark SQL' -> Bấm chuyển đổi 4 tab: Top 15 siêu sao, Vị trí thi đấu, Quốc gia, Độ tuổi vàng. Thử nút 'Trang tiếp ▶'."
    ], box_type="action")

    add_callout_box(doc, "BẢN CHẤT CÔNG NGHỆ & GIẢI QUYẾT VẤN ĐỀ", [
        "• PySpark ETL (02_data_cleaning.py): Giải quyết vấn đề dữ liệu rác/khuyết tật — Tự động điền trung vị chiều cao, tính lại tuổi chuẩn từ ngày sinh, loại bỏ 9,400 bản ghi thiếu giá trị, lọc ra đúng 40,749 bản ghi sạch.",
        "• Định dạng Apache Parquet (Snappy Columnar): Giải quyết vấn đề lãng phí tài nguyên lưu trữ — File thô players.csv nặng 18.72 MB được nén thành cleaned_players.parquet chỉ còn 1.41 MB (tiết kiệm 97.7% dung lượng ổ cứng) và chỉ đọc đúng các cột số khi huấn luyện AI.",
        "• Spark SQL (03_spark_analysis.py): Đăng ký TempView thực thi truy vấn phân tán đa chiều, tích hợp bộ phân trang Enterprise lưu trạng thái vào URL query params."
    ], box_type="problem")

    add_callout_box(doc, "LỜI THOẠI NÓI CÁI HIỂU LIỀN", [
        "\"Em chào Thầy và các bạn, em là Quốc Trung. PySpark ETL đã làm sạch hơn 50 nghìn hồ sơ thô thành 40,749 bản ghi sạch. Dữ liệu được lưu dưới dạng Parquet nén Snappy chỉ 1.4 MB — giúp tiết kiệm đến 97.7% ổ cứng và tăng tốc độ đọc dữ liệu.\"",
        "\"Ở phần Spark SQL, nhóm chạy phân tán 4 góc nhìn: Top 15 siêu sao đắt nhất như Haaland, Mbappe giá 180-200 triệu Euro; vị trí Tiền đạo áp đảo giá trị; và độ tuổi vàng đạt đỉnh phong độ là 25 đến 28 tuổi!\""
    ], box_type="speech")

    # ── BƯỚC 6 & 7 ────────────────────────────────────────────────────────
    add_heading_2(doc, "Bước 6 & 7: Machine Learning phân tán & Săn cầu thủ giá hời (2 phút | Chu Văn Quốc Trung)")
    add_url_box(doc, "6. Phân cụm K-Means & 7. Dự đoán định giá (ML & XAI)",
                "http://localhost:8501/?page=Phân+cụm+K-Means",
                secondary_url="http://localhost:8501/?page=Dự+đoán+định+giá+(ML)")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu '6. Phân cụm K-Means' -> Chỉ vào biểu đồ 3 cụm và điểm Silhouette Score k=3 đạt 0.6429.",
        "2. Bấm menu '7. Dự đoán định giá (ML & XAI)': Gõ tên 'Erling Haaland' xem giá dự đoán và 5 bước giải trình Explainable AI.",
        "3. Cuộn xuống tính năng 'Săn cầu thủ theo Ngân sách (Scouting Engine)': Kéo ngân sách về 35 triệu EUR, chọn Tiền đạo, xem các cầu thủ 'Kèo hời'."
    ], box_type="action")

    add_callout_box(doc, "BẢN CHẤT CÔNG NGHỆ & GIẢI QUYẾT VẤN ĐỀ", [
        "• PySpark MLlib K-Means: Thử nghiệm Silhouette từ k=2 đến k=6, xác định k=3 là tối ưu (Score 0.6429) -> Giải quyết bài toán phân đoạn thị trường: chia đúng 3 đẳng cấp: Siêu sao (30M €), Trụ cột (1.2M €), Phổ thông (400k €).",
        "• Random Forest Regressor: Áp dụng phép biến đổi logarit chuẩn hóa ln(1+y) -> Giải quyết vấn đề lệch phải (Right-skewness) cực nặng của giá cầu thủ, nâng độ chính xác R² từ dưới 60% lên đạt 84.68% (file rf_model.joblib).",
        "• Scouting Engine: Giải quyết bài toán kinh tế của các CLB — AI tự động quét 40 nghìn hồ sơ để tìm ra những cầu thủ có thực lực vượt trội nhưng đang bị thị trường định giá thấp (Undervalued), giúp CLB mua cầu thủ giỏi với chi phí tiết kiệm hàng chục triệu Euro!"
    ], box_type="problem")

    add_callout_box(doc, "LỜI THOẠI NÓI CÁI HIỂU LIỀN", [
        "\"Để giải quyết bài toán định giá cầu thủ bằng cảm tính, nhóm áp dụng 2 thuật toán Machine Learning:\"",
        "\"Thứ nhất, K-Means k=3 phân đoạn cầu thủ thành 3 đẳng cấp rõ rệt với điểm Silhouette 0.64. Thứ hai, Random Forest dự đoán giá trị chuyển nhượng đạt độ chính xác R2 = 84.7%, kèm giải trình XAI 5 bước.\"",
        "\"Đặc biệt, tính năng Săn cầu thủ giá hời giúp các CLB chỉ với ngân sách 35 triệu Euro có thể tìm ra những viên ngọc quý đang bị thị trường định giá thấp, mang lại giá trị kinh tế thực tế rất cao!\""
    ], box_type="speech")

    # ── BƯỚC 8, 9, 10 ─────────────────────────────────────────────────────
    add_heading_2(doc, "Bước 8, 9 & 10: Kafka Streaming, Airflow DAG & CSDL Data Mart (2 phút | Nguyễn Thế Quang)")
    add_url_box(doc, "8. Kafka Streaming -> 9. Airflow Workflow -> 10. CSDL Data Mart",
                "http://localhost:8501/?page=Dòng+dữ+liệu+Kafka+Streaming",
                secondary_url="Airflow UI: http://localhost:8080 | SQLite Mart: http://localhost:8501/?page=Truy+vấn+CSDL+Data+Mart")

    add_callout_box(doc, "THAO TÁC MÀN HÌNH", [
        "1. Bấm menu '8. Dòng dữ liệu Kafka Streaming': Xem bảng tin JSON giao dịch nhảy số trực tiếp (> 707 triệu Euro).",
        "2. Bấm menu '9. Điều phối Airflow Workflow': Chỉ vào sơ đồ 7 task tuần tự báo xanh 100% SUCCESS trong 2m 10s.",
        "3. Bấm menu '10. Truy vấn CSDL Data Mart': Chọn câu query mẫu 'Top 10 cầu thủ có giá trị cao nhất' -> Bấm Thực thi SQL xem bảng hiện tức thì dưới 10ms."
    ], box_type="action")

    add_callout_box(doc, "BẢN CHẤT CÔNG NGHỆ & GIẢI QUYẾT VẤN ĐỀ", [
        "• Apache Kafka (Speed Layer): Giải quyết bài toán độ trễ thời gian thực — Trong kỳ chuyển nhượng, các thương vụ phát sinh từng giờ. Nếu dùng Spark xử lý mẻ thì phải chạy lại cả 872 MB rất tốn tài nguyên. Kafka topic football_transfers cổng 9092 bắt ngay các bản tin mới và cập nhật lên màn hình trong tích tắc!",
        "• Apache Airflow (Orchestration): Giải quyết bài toán vận hành thủ công dễ lỗi — Tự động hóa toàn bộ Data Pipeline 7 bước bằng Docker Compose, tự kiểm tra điều kiện tiên quyết và ghi log.",
        "• SQLite Data Mart (Serving Layer): Giải quyết bài toán nghẽn tải Web — Toàn bộ kết quả tính toán phân tán được nạp sẵn vào CSDL football_analytics.db có đánh chỉ mục, giúp Web phản hồi dưới 10ms mà không làm đơ cụm máy chủ Spark."
    ], box_type="problem")

    add_callout_box(doc, "LỜI THOẠI NÓI CÁI HIỂU LIỀN", [
        "\"Em chào Thầy và các bạn, em là Thế Quang, phụ trách Kafka, Airflow và CSDL:\"",
        "\"1. Với Kafka: Giải quyết bài toán tin chuyển nhượng nóng sốt từng giờ. Producer bắn tin qua cổng 9092, Consumer bắt ngay để cập nhật lên web mà không cần chạy lại cả kho dữ liệu cũ.\"",
        "\"2. Với Airflow: Giải quyết bài toán tự động hóa — gom cả quy trình 7 bước vào 1 DAG chạy trên Docker, toàn bộ 7 task đều báo xanh 100% SUCCESS trong 2 phút 10 giây.\"",
        "\"3. Với SQLite Data Mart: Giúp Web phản hồi tức thì dưới 10 mili-giây mà không làm nghẽn máy chủ tính toán Spark.\"",
        "\"Tóm lại, đề tài của nhóm đã vận dụng đầy đủ 7 công nghệ Big Data, giải quyết trọn vẹn bài toán từ lưu trữ, xử lý, streaming đến AI và phục vụ người dùng. Nhóm 5 xin cảm ơn Thầy và các bạn đã lắng nghe ạ!\""
    ], box_type="speech")

    # ══════════════════════════════════════════════════════════════════════
    # BỘ CÂU HỎI VẤN ĐÁP ĂN ĐIỂM TUYỆT ĐỐI (TOP 6 Q&A)
    # ══════════════════════════════════════════════════════════════════════
    add_heading_1(doc, "3. Bộ câu hỏi vấn đáp cốt lõi của Giảng viên & Cách trả lời ngắn gọn (Hiểu liền, ăn điểm ngay)")

    qa_list = [
        ("Câu 1 (Trọng tâm): Em hiểu DataNode và NameNode là gì? Trong bài em áp dụng thế nào và nó giải quyết vấn đề gì?",
         "Trả lời ngắn gọn ăn điểm ngay: Dạ thưa Thầy, trong HDFS: (1) NameNode là Master quản lý Metadata (cây thư mục /football_project/, ánh xạ block) tại cổng 9820/9870. (2) DataNode là Workers trực tiếp lưu trữ các khối nhị phân 128MB trên đĩa vật lý. Cụm của nhóm có 1 NameNode và 3 DataNodes lưu 18 blocks của 12 file CSV (872.5 MB) với Replication factor = 3 (tổng 2.58 GB). Kiến trúc này giải quyết 3 vấn đề lớn: Chống mất dữ liệu (hỏng 1-2 DataNode vẫn an toàn), Xóa nghẽn I/O (3 DataNode cấp dữ liệu cho Spark đọc song song), và Mở rộng quy mô chỉ cần cắm thêm DataNode mới ạ!"),

        ("Câu 2: Dữ liệu chưa tới 1GB thì có thực sự cần đến Hadoop/Spark không hay chỉ cần Pandas là đủ?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, dữ liệu của nhóm có gần 7.5 triệu dòng, bảng thi đấu gần 3.2 triệu dòng. Thực nghiệm đo đạc thực tế: Pandas chạy đơn luồng mất 12.45 giây, trong khi Spark chia 16 luồng song song chỉ mất 0.78 giây (nhanh gấp 16 lần). Quan trọng hơn, khi dữ liệu tăng lên hàng chục triệu dòng, Pandas sẽ bị sập vì tràn RAM (Out-Of-Memory), còn Spark chỉ cần gắn thêm DataNode/Worker là chạy bình thường ạ."),

        ("Câu 3: Tại sao đề tài lại dùng thêm SQLite mà không cho Web Dashboard truy vấn trực tiếp từ Spark hoặc HDFS?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, theo nguyên lý Lambda Architecture, Spark và HDFS xử lý dữ liệu lớn theo mẻ nên mỗi lần chạy mất 5-10 giây để khởi động JVM, nếu người dùng lướt web mà chờ lâu sẽ bị đơ web. Vì vậy Spark tính toán trước rồi lưu kết quả vào CSDL SQLite (Serving Layer) để người dùng lướt web mượt mà dưới 10 mili-giây mà không chiếm tài nguyên máy chủ Spark ạ."),

        ("Câu 4: Phân cụm K-Means tại sao nhóm lại chọn k=3 mà không phải k=4 hay k=5?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, nhóm chọn k=3 vì 2 lý do: Về toán học, nhóm đã chạy thử nghiệm Silhouette từ k=2 đến 6 thì k=3 đạt điểm cao nhất là 0.6429. Về thực tế bóng đá, k=3 chia rất đúng 3 phân khúc: Siêu sao thế giới (~30 triệu Euro), Cầu thủ trụ cột các giải lớn (~1.2 triệu Euro), và Cầu thủ trẻ tiềm năng / giải đấu phổ thông (~400 nghìn Euro) ạ."),

        ("Câu 5: Tại sao trong mô hình Random Forest phải biến đổi log1p cho giá trị cầu thủ?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, giá trị cầu thủ bị lệch phải cực kỳ nặng nề: hơn 80% cầu thủ có giá dưới vài triệu Euro, nhưng một số ít siêu sao lại có giá lên tới gần 200 triệu Euro. Nếu để nguyên thì thuật toán chỉ tập trung học siêu sao và đoán sai hết nhóm phổ thông. Phép biến đổi ln(1 + y) giúp đưa giá trị về dạng phân phối chuẩn, giúp mô hình học đều và nâng độ chính xác R2 từ dưới 60% lên đạt 84.7% ạ."),

        ("Câu 6: Apache Kafka trong bài làm nhiệm vụ gì và dữ liệu streaming đi về đâu?",
         "Trả lời ngắn gọn: Dạ thưa Thầy, Spark dùng để xử lý dữ liệu lịch sử theo mẻ, còn Kafka dùng để truyền tải các thương vụ chuyển nhượng mới phát sinh theo thời gian thực (Speed Layer). Producer phát bản tin chuyển nhượng qua cổng 9092, Consumer bắt lấy tin tức thì và ghi vào CSDL Data Mart để cập nhật ngay lên Dashboard cho người dùng xem mà không phải chạy lại toàn bộ mẻ dữ liệu lịch sử 872 MB ạ.")
    ]

    for q, a in qa_list:
        add_p(doc, q, size=10, bold=True, color=COLOR_NAVY, space_before=5, space_after=1)
        add_p(doc, a, size=9.5, bold=False, italic=False, color=COLOR_DARK, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=5)

    # Lưu tệp DOCX
    doc.save(OUT_DOCX)
    print(f"[HOÀN THÀNH] ĐÃ TẠO TỆP KỊCH BẢN MỚI TẠI: {OUT_DOCX}")

if __name__ == "__main__":
    build_demo_document()
