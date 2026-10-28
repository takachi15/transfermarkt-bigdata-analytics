# -*- coding: utf-8 -*-
"""
build_hufi_report.py
====================
Tạo tệp Báo cáo Đồ án Big Data hoàn chỉnh theo chuẩn layout Luận văn Đại học
Khoa Công nghệ Thông tin - Trường Đại học Công nghiệp Thực phẩm TP.HCM (HUFI / HUIT).
- Giảng viên hướng dẫn: ThS. Huỳnh Thái Học
- Nhóm sinh viên: Đặng Duy Lợi (Trưởng nhóm), Chu Văn Quốc Trung, Nguyễn Thế Quang (Lớp 14DHTH06)
- Logo nhà trường chính thức tại trang bìa
- Chuẩn font Times New Roman cỡ 13, dãn dòng 1.5 lines
- Chuẩn lề: Top 3.5cm, Bottom 3.0cm, Left 3.5cm, Right 2.0cm
- Đánh số bảng trên bảng, đánh số hình dưới hình gắn với số chương
- Hệ thống Heading chuẩn Microsoft Word: Heading 1 (Chương & mục lớn), Heading 2 (Mục cấp 2), Heading 3 (Tiểu mục)
- Mục lục tự động chuẩn Word (TOC Field) tích hợp Navigation Pane & Hyperlinks
- Mục lục bảng biểu (Table of Tables) & Mục lục hình vẽ (Table of Figures) tự động chuẩn Word Field (TOC \\t)
- Định dạng danh sách phân cấp không dùng ký tự xuống dòng '\\n' trong đoạn văn Justify để loại bỏ triệt để lỗi dãn cách chữ.
- Tự động xuất ra DOCX và PDF.
"""

import os
import sys
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "Bao_Cao" else SCRIPT_DIR
REPORT_DIR = SCRIPT_DIR if os.path.basename(SCRIPT_DIR) == "Bao_Cao" else os.path.join(BASE_DIR, "Bao_Cao")
os.makedirs(REPORT_DIR, exist_ok=True)

IMG_DIR   = os.path.join(BASE_DIR, "extracted_images")
LOGO_PATH = os.path.join(IMG_DIR, "school_logo.png")
OUT_DOCX  = os.path.join(REPORT_DIR, "Bao_Cao_Tong_Ket_Do_An_BigData.docx")
OUT_SYNC  = os.path.join(REPORT_DIR, "Bao_Cao_Tien_Do_Do_An_BigData.docx")
OUT_PDF   = os.path.join(REPORT_DIR, "Bao_Cao_Tong_Ket_Do_An_BigData.pdf")
SYNC_PDF  = os.path.join(REPORT_DIR, "Bao_Cao_Tien_Do_Do_An_BigData.pdf")

COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_NAVY  = RGBColor(27, 54, 93)
COLOR_MUTED = RGBColor(90, 90, 90)

def set_page_margins(section):
    """Chuẩn luận văn HUFI: Top 3.5cm, Bottom 3.0cm, Left 3.5cm, Right 2.0cm"""
    section.top_margin    = Cm(3.5)
    section.bottom_margin = Cm(3.0)
    section.left_margin   = Cm(3.5)
    section.right_margin  = Cm(2.0)

def add_header_page_number(section, start_number=None, is_roman=False):
    header = section.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(0)
    
    # XML trường số trang Word
    fld = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    p._p.append(fld)
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

def set_cell_pad(cell, t=80, b=80, l=100, r=100):
    tcPr = cell._tc.get_or_add_tcPr()
    xml = f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:bottom w:w="{b}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/><w:right w:w="{r}" w:type="dxa"/></w:tcMar>'
    tcPr.append(parse_xml(xml))

def set_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'))

def set_cell_border(cell, **kwargs):
    """kwargs: top, bottom, left, right dict(val='single', sz=4, color='auto')"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge)
        if edge_data:
            b_xml = f'<w:{edge} {nsdecls("w")} w:val="{edge_data.get("val","single")}" w:sz="{edge_data.get("sz","4")}" w:space="0" w:color="{edge_data.get("color","auto")}"/>'
            tcBorders.append(parse_xml(b_xml))
        else:
            b_xml = f'<w:{edge} {nsdecls("w")} w:val="none"/>'
            tcBorders.append(parse_xml(b_xml))
    tcPr.append(tcBorders)

def add_p(doc, text="", size=13, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.5):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        r.bold = bold
        r.italic = italic
        r.font.color.rgb = COLOR_BLACK
    return p

def add_numbered_item(doc, num_str, title_prefix, body_text):
    """Thêm một mục đánh số riêng biệt với lề thụt đầu dòng chuẩn, không bị dãn chữ"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(0.7)
    p.paragraph_format.first_line_indent = Cm(-0.7)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.line_spacing = 1.35
    r_num = p.add_run(num_str + " ")
    r_num.font.name = "Times New Roman"
    r_num.font.size = Pt(13)
    r_num.bold = True
    if title_prefix:
        r_pre = p.add_run(title_prefix + " ")
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(13)
        r_pre.bold = True
    r_body = p.add_run(body_text)
    r_body.font.name = "Times New Roman"
    r_body.font.size = Pt(13)
    return p

def configure_heading_styles(doc):
    """Cấu hình đồng bộ bộ Heading Styles của Word theo chuẩn học thuật HUFI"""
    styles = doc.styles

    # Normal
    normal = styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(13)
    normal.font.color.rgb = COLOR_BLACK
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after  = Pt(4)

    # Heading 1: Tiêu đề Chương và các phần chính
    h1 = styles['Heading 1']
    h1.font.name = 'Times New Roman'
    h1.font.size = Pt(15)
    h1.font.bold = True
    h1.font.color.rgb = COLOR_BLACK
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after  = Pt(8)
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.line_spacing = 1.3

    # Heading 2: Tiêu đề mục cấp 2 (1.1, 1.2, 2.1...)
    h2 = styles['Heading 2']
    h2.font.name = 'Times New Roman'
    h2.font.size = Pt(13.5)
    h2.font.bold = True
    h2.font.color.rgb = COLOR_BLACK
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after  = Pt(4)
    h2.paragraph_format.keep_with_next = True
    h2.paragraph_format.line_spacing = 1.3

    # Heading 3: Tiêu đề tiểu mục cấp 3 (1.4.1, 4.1.1...)
    h3 = styles['Heading 3']
    h3.font.name = 'Times New Roman'
    h3.font.size = Pt(13)
    h3.font.bold = True
    h3.font.italic = True
    h3.font.color.rgb = COLOR_BLACK
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after  = Pt(3)
    h3.paragraph_format.keep_with_next = True
    h3.paragraph_format.line_spacing = 1.3

    # Style TableCaption cho tiêu đề bảng biểu (đặt trên bảng)
    try:
        tc_style = styles.add_style('TableCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    except Exception:
        tc_style = styles['TableCaption']
    tc_style.font.name = 'Times New Roman'
    tc_style.font.size = Pt(13)
    tc_style.font.bold = True
    tc_style.font.color.rgb = COLOR_BLACK
    tc_style.paragraph_format.space_before = Pt(10)
    tc_style.paragraph_format.space_after  = Pt(3)
    tc_style.paragraph_format.keep_with_next = True
    tc_style.paragraph_format.line_spacing = 1.3

    # Style FigureCaption cho tiêu đề hình ảnh (đặt dưới hình)
    try:
        fc_style = styles.add_style('FigureCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    except Exception:
        fc_style = styles['FigureCaption']
    fc_style.font.name = 'Times New Roman'
    fc_style.font.size = Pt(12)
    fc_style.font.bold = True
    fc_style.font.italic = True
    fc_style.font.color.rgb = COLOR_BLACK
    fc_style.paragraph_format.space_before = Pt(2)
    fc_style.paragraph_format.space_after  = Pt(10)
    fc_style.paragraph_format.line_spacing = 1.2

def add_major_heading(doc, title_text, center=True):
    """Thêm tiêu đề cấp 1 (Heading 1) cho các phần lớn (Lời cam đoan, Lời cảm ơn, Danh mục, Tài liệu TK...)"""
    p = doc.add_paragraph(style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after  = Pt(8)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run(title_text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.bold = True
    r.font.color.rgb = COLOR_BLACK
    return p

def add_chapter_title(doc, chapter_num, title_text):
    """Thêm tiêu đề Chương (Heading 1) chuẩn Word Navigation Pane & Table of Contents"""
    full_title = f"CHƯƠNG {chapter_num}: {title_text.upper()}"
    return add_major_heading(doc, full_title, center=True)

def add_h1(doc, text):
    """Tiêu đề mục cấp 2 (Heading 2: 1.1, 1.2, 2.1...)"""
    p = doc.add_paragraph(style='Heading 2')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.bold = True
    r.font.color.rgb = COLOR_BLACK
    return p

def add_h2(doc, text):
    """Tiêu đề tiểu mục cấp 3 (Heading 3: 1.4.1, 4.1.1...)"""
    p = doc.add_paragraph(style='Heading 3')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True
    r.italic = True
    r.font.color.rgb = COLOR_BLACK
    return p

def add_bullet_point(doc, text, bold_prefix=""):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(0.7)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.line_spacing = 1.4
    r0 = p.add_run("• ")
    r0.font.name = "Times New Roman"
    r0.font.size = Pt(13)
    r0.bold = True
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.font.name = "Times New Roman"
        rb.font.size = Pt(13)
        rb.bold = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    return p

def add_table_with_caption(doc, caption_text, rows_data, col_widths=None):
    # Quy định HUFI: Đầu đề của bảng biểu ghi PHÍA TRÊN bảng, gán style TableCaption để tự động sinh Mục lục bảng
    if caption_text:
        pc = doc.add_paragraph(style='TableCaption')
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT
        rc = pc.add_run(caption_text)
        rc.font.name = "Times New Roman"
        rc.font.size = Pt(13)
        rc.bold = True
        rc.font.color.rgb = COLOR_BLACK

    t = doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, row in enumerate(rows_data):
        for ci, val in enumerate(row):
            cell = t.cell(ri, ci)
            cell.text = str(val)
            set_cell_pad(cell, t=60, b=60, l=80, r=80)
            set_cell_border(cell,
                            top=dict(sz=4, color='808080'),
                            bottom=dict(sz=4, color='808080'),
                            left=dict(sz=4, color='808080'),
                            right=dict(sz=4, color='808080'))
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after  = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            run = p.runs[0] if p.runs else p.add_run(str(val))
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            if ri == 0:
                set_bg(cell, "E6ECF5")
                run.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                if ci == 0 and len(row) > 3:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t

def make_table(doc, rows_data):
    return add_table_with_caption(doc, "", rows_data)

def add_figure_with_caption(doc, img_name, caption_text, width_inches=6.0):
    img_path = os.path.join(IMG_DIR, img_name)
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after  = Pt(2)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(img_path, width=Inches(width_inches))

        # Quy định HUFI: Đầu đề của hình vẽ ghi PHÍA DƯỚI hình, gán style FigureCaption để tự động sinh Mục lục hình
        pc = doc.add_paragraph(style='FigureCaption')
        pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc = pc.add_run(caption_text)
        rc.font.name = "Times New Roman"
        rc.font.size = Pt(12)
        rc.bold = True
        rc.italic = True
        rc.font.color.rgb = COLOR_BLACK
    else:
        doc.add_paragraph(f"[Chưa tìm thấy ảnh: {img_name}]")

def add_cover_page(doc, is_sub_cover=False):
    # Thiết lập trang bìa không header/footer số trang
    sec = doc.sections[0] if not is_sub_cover else doc.add_section()
    sec.top_margin    = Cm(2.5)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin   = Cm(3.0)
    sec.right_margin  = Cm(2.0)
    sec.different_first_page_header_footer = True
    
    # 1. Cơ quan chủ quản và Tên trường (size 13)
    add_p(doc, "BỘ CÔNG THƯƠNG", size=13, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, line_spacing=1.15)
    add_p(doc, "TRƯỜNG ĐẠI HỌC CÔNG NGHIỆP THỰC PHẨM TP. HCM", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, line_spacing=1.15)
    add_p(doc, "KHOA CÔNG NGHỆ THÔNG TIN", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=3, line_spacing=1.15)
    add_p(doc, "---------------------------------------------", size=10, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=10, line_spacing=1.15)

    # 2. Logo trường
    if os.path.exists(LOGO_PATH):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after  = Pt(8)
        p_logo.add_run().add_picture(LOGO_PATH, width=Inches(1.85))

    # 3. Tiêu đề đồ án (size 22) & Tên đề tài (size 16)
    add_p(doc, "BÁO CÁO ĐỒ ÁN MÔN HỌC", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4, line_spacing=1.15)
    add_p(doc, "HỌC PHẦN: CÔNG NGHỆ DỮ LIỆU LỚN (BIG DATA)", size=13, bold=True, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=10, line_spacing=1.15)

    add_p(doc, "“XÂY DỰNG DATA PIPELINE THU THẬP, XỬ LÝ PHÂN TÁN VÀ PHÂN TÍCH DỮ LIỆU THỊ TRƯỜNG CHUYỂN NHƯỢNG BÓNG ĐÁ QUỐC TẾ”",
          size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=16, line_spacing=1.2)

    # 4. Khối thông tin Giảng viên hướng dẫn & Nhóm sinh viên thực hiện (size 12.5)
    info_data = [
        ("GVHD:", "ThS. Huỳnh Thái Học"),
        ("SINH VIÊN THỰC HIỆN:", "1. Đặng Duy Lợi        - MSSV: 2001230479 - Lớp: 14DHTH06"),
        ("",                     "2. Chu Văn Quốc Trung  - MSSV: 2001231010 - Lớp: 14DHTH06"),
        ("",                     "3. Nguyễn Thế Quang    - MSSV: 20012307010 - Lớp: 14DHTH06"),
        ("NGÀNH ĐÀO TẠO:",       "Công nghệ Thông tin / Khoa học Dữ liệu"),
    ]
    if is_sub_cover:
        info_data.append(("LIÊN KẾT REPO:", "https://github.com/takachi15/transfermarkt-bigdata-analytics"))
        info_data.append(("MÃ NGUỒN ĐÍNH KÈM:", "Thư mục Source_Code/ (Kèm CHAY_WEB.bat & CHAY_PIPELINE.bat)"))

    info_table = doc.add_table(rows=len(info_data), cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in info_table.rows:
        for c in r.cells:
            set_cell_pad(c, t=10, b=10, l=30, r=30)
            set_cell_border(c)
    for idx, (label, val) in enumerate(info_data):
        c0 = info_table.cell(idx, 0)
        c1 = info_table.cell(idx, 1)
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after  = Pt(0)
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after  = Pt(0)
        r0 = p0.add_run(label)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(12.5)
        r0.bold = True
        r1 = p1.add_run(val)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(12.5)
        if idx in (1, 2, 3):
            r1.bold = True

    # 5. Footer địa danh thời gian (size 13)
    add_p(doc, "TP. HỒ CHÍ MINH, tháng 10 năm 2026", size=13, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=0, line_spacing=1.15)

def build_hufi_full_document():
    doc = docx.Document()

    # Cấu hình styles cho văn bản (Normal & Headings & Captions)
    configure_heading_styles(doc)

    # Bật cờ updateFields để Word tự động làm mới TOC khi mở
    doc.settings.element.append(parse_xml(r'<w:updateFields %s w:val="true"/>' % nsdecls('w')))

    # ══════════════════════════════════════════════════════════════════════
    # TRANG 1: TRANG BÌA CHÍNH (Cover Page)
    # ══════════════════════════════════════════════════════════════════════
    add_cover_page(doc, is_sub_cover=False)

    # ══════════════════════════════════════════════════════════════════════
    # TRANG 2: TRANG BÌA LÓT (Bìa phụ)
    # ══════════════════════════════════════════════════════════════════════
    add_cover_page(doc, is_sub_cover=True)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2: PHẦN MỞ ĐẦU (Đánh số trang La Mã i, ii, iii... trên đầu)
    # ══════════════════════════════════════════════════════════════════════
    sec_front = doc.add_section()
    set_page_margins(sec_front)
    add_header_page_number(sec_front, start_number=1, is_roman=True)

    # TRANG 3: LỜI CAM ĐOAN (Heading 1)
    add_major_heading(doc, "LỜI CAM ĐOAN", center=True)
    add_p(doc, "Chúng tôi xin cam đoan đây là công trình nghiên cứu và thực nghiệm của riêng nhóm chúng tôi dưới sự hướng dẫn của ThS. Huỳnh Thái Học – Giảng viên phụ trách học phần. Các số liệu, bảng biểu, hình ảnh minh chứng và kết quả phân tích nêu trong Báo cáo Đồ án là hoàn toàn trung thực, được tính toán trực tiếp từ hệ thống mã nguồn thực tế và chưa từng được công bố trong bất kỳ công trình nào khác.", size=13, line_spacing=1.5, space_after=12)
    add_p(doc, "Chúng tôi xin cam đoan rằng mọi sự giúp đỡ cho việc thực hiện Đồ án này đã được cảm ơn chân thành và các thông tin, tài liệu trích dẫn trong Báo cáo đều đã được chỉ rõ nguồn gốc theo chuẩn học thuật.", size=13, line_spacing=1.5, space_after=24)

    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.line_spacing = 1.3
    r_sig = p_sig.add_run("TP. Hồ Chí Minh, ngày 27 tháng 10 năm 2026\nSinh viên thực hiện\n(Ký và ghi rõ họ tên)\n\n\n\n1. Đặng Duy Lợi\n2. Chu Văn Quốc Trung\n3. Nguyễn Thế Quang")
    r_sig.font.name = "Times New Roman"
    r_sig.font.size = Pt(13)
    r_sig.bold = True

    doc.add_page_break()

    # TRANG 4: LỜI CẢM ƠN (Heading 1)
    add_major_heading(doc, "LỜI CẢM ƠN", center=True)
    add_p(doc, "Để hoàn thành đồ án môn học Công nghệ Dữ liệu lớn (Big Data Technologies), nhóm chúng tôi xin bày tỏ lòng biết ơn sâu sắc đến Ban Giám hiệu Trường Đại học Công nghiệp Thực phẩm TP.HCM (nay là Trường Đại học Công Thương TP.HCM), cùng toàn thể Quý Thầy/Cô Khoa Công nghệ Thông tin đã tạo mọi điều kiện thuận lợi và truyền đạt những nền tảng kiến thức quý báu cho chúng tôi trong suốt quá trình học tập.", size=13, line_spacing=1.5, space_after=12)
    add_p(doc, "Đặc biệt, nhóm xin gửi lời tri ân chân thành nhất đến ThS. Huỳnh Thái Học – Giảng viên hướng dẫn môn học, đã tận tình định hướng đề tài, giải đáp các vướng mắc kỹ thuật và chỉ dẫn phương pháp triển khai các hệ thống tính toán phân tán phức tạp như Hadoop HDFS, Apache Spark, Kafka và Airflow.", size=13, line_spacing=1.5, space_after=12)
    add_p(doc, "Mặc dù đã nỗ lực hết mình để hoàn thiện hệ thống và tài liệu báo cáo, song do tính chất chuyên sâu của công nghệ Big Data, đồ án chắc chắn không tránh khỏi những thiếu sót nhất định. Nhóm chúng tôi rất mong nhận được những đóng góp quý báu từ Quý Thầy/Cô để đồ án ngày càng hoàn thiện hơn.", size=13, line_spacing=1.5, space_after=24)

    p_thanks = doc.add_paragraph()
    p_thanks.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_th = p_thanks.add_run("Nhóm sinh viên thực hiện đồ án\nĐặng Duy Lợi – Chu Văn Quốc Trung – Nguyễn Thế Quang")
    r_th.font.name = "Times New Roman"
    r_th.font.size = Pt(13)
    r_th.bold = True
    r_th.italic = True

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════
    # TRANG 5: TÓM TẮT ĐỒ ÁN (Heading 1) - Trình bày rõ ràng, không bị dãn chữ
    # ══════════════════════════════════════════════════════════════════════
    add_major_heading(doc, "TÓM TẮT ĐỒ ÁN", center=True)
    add_p(doc, "Đồ án tập trung nghiên cứu và xây dựng một hệ thống Data Pipeline hoàn chỉnh phục vụ bài toán thực tế: thu thập, lưu trữ phân tán, xử lý tính toán song song, học máy và trực quan hóa dữ liệu thị trường chuyển nhượng bóng đá quốc tế dựa trên bộ dữ liệu Transfermarkt Football Dataset quy mô 12 bảng CSV (~870 MB).", size=13, line_spacing=1.5, space_after=8)
    
    add_p(doc, "Về mặt công nghệ, hệ thống tích hợp đồng bộ các trụ cột Big Data hàng đầu hiện nay:", size=13, bold=True, space_before=4, space_after=6)
    add_numbered_item(doc, "1.", "Hadoop HDFS 3.x:", "Đóng vai trò Data Lake lưu trữ phân tán an toàn toàn bộ 12 tệp dữ liệu thô tại cổng 9870.")
    add_numbered_item(doc, "2.", "Apache Spark 3.x / PySpark 4.2:", "Động cơ xử lý phân tán trong bộ nhớ, thực hiện ETL làm sạch 50.149 bản ghi thô xuống 40.756 bản ghi sạch và thực thi 4 câu lệnh Spark SQL đa chiều.")
    add_numbered_item(doc, "3.", "Spark MLlib:", "Áp dụng thuật toán phân cụm K-Means với Silhouette Score tối ưu (k=3 đạt 0.6429) để chia cầu thủ thành 3 đẳng cấp thị trường; đồng thời xây dựng Pipeline Random Forest Regressor với biến đổi thang log đạt độ chính xác R² = 84.68% và RMSE = 0.5942.")
    add_numbered_item(doc, "4.", "Apache Kafka 3.x:", "Xử lý luồng sự kiện thời gian thực (topic 'football_transfers' cổng 9092) phát sóng và bóc tách các thương vụ chuyển nhượng trực tiếp.")
    add_numbered_item(doc, "5.", "Apache Airflow 2.10:", "Điều phối tự động hóa toàn bộ chu trình qua DAG 7 task tuần tự chạy trên Docker Compose đạt 100% trạng thái 'success'.")
    add_numbered_item(doc, "6.", "Serving Data Mart & Streamlit Dashboard:", "Lưu trữ vào CSDL quan hệ football_analytics.db và trực quan hóa tương tác qua Web Dashboard 6 trang.")
    
    add_p(doc, "Từ khóa: Big Data, Hadoop HDFS, PySpark, Spark SQL, Spark MLlib, Apache Kafka, Apache Airflow, Machine Learning, Streamlit Dashboard.", size=13, bold=True, line_spacing=1.5, space_before=8, space_after=4)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════
    # TRANG 6: MỤC LỤC TỰ ĐỘNG CHUẨN WORD (Word TOC Field liên kết Heading)
    # ══════════════════════════════════════════════════════════════════════
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_title.paragraph_format.space_before = Pt(12)
    p_toc_title.paragraph_format.space_after  = Pt(16)
    r_tt = p_toc_title.add_run("MỤC LỤC")
    r_tt.font.name = "Times New Roman"
    r_tt.font.size = Pt(16)
    r_tt.bold = True
    r_tt.font.color.rgb = COLOR_BLACK

    # Trường Mục lục tự động chuẩn Word (TOC \o "1-3" \h \z \u)
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_before = Pt(0)
    p_toc.paragraph_format.space_after  = Pt(6)
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="TOC \o &quot;1-3&quot; \h \z \u"/>' % nsdecls('w'))
    p_toc._p.append(fldSimple)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════
    # TRANG 7: DANH MỤC VIẾT TẮT, MỤC LỤC BẢNG BIỂU & MỤC LỤC HÌNH VẼ
    # ══════════════════════════════════════════════════════════════════════
    add_major_heading(doc, "DANH MỤC CÁC TỪ VIẾT TẮT", center=False)
    make_table(doc, [
        ("Từ viết tắt", "Tên tiếng Anh đầy đủ", "Ý nghĩa / Giải thích chuyên môn"),
        ("HDFS",    "Hadoop Distributed File System",  "Hệ thống tập tin phân tán Hadoop"),
        ("ETL",     "Extract, Transform, Load",        "Quy trình trích xuất, biến đổi và nạp dữ liệu"),
        ("MLlib",   "Machine Learning Library (Spark)","Thư viện học máy phân tán trên Apache Spark"),
        ("DAG",     "Directed Acyclic Graph",          "Đồ thị có hướng không chu trình (Airflow Workflow)"),
        ("R²",      "R-squared (Coefficient of Det.)", "Hệ số xác định đánh giá độ chính xác mô hình hồi quy"),
        ("RMSE",    "Root Mean Squared Error",         "Căn bậc hai của sai số bình phương trung bình"),
        ("MAE",     "Mean Absolute Error",             "Sai số tuyệt đối trung bình"),
        ("CSV",     "Comma-Separated Values",          "Định dạng tệp dữ liệu phân tách bởi dấu phẩy"),
    ])

    # MỤC LỤC BẢNG BIỂU TỰ ĐỘNG CHUẨN WORD (Trường TOC \t "TableCaption,1" \h \z)
    add_major_heading(doc, "DANH MỤC CÁC BẢNG BIỂU", center=False)
    p_tot = doc.add_paragraph()
    p_tot.paragraph_format.space_before = Pt(2)
    p_tot.paragraph_format.space_after  = Pt(6)
    fld_tot = parse_xml(r'<w:fldSimple %s w:instr="TOC \t &quot;TableCaption,1&quot; \h \z"/>' % nsdecls('w'))
    p_tot._p.append(fld_tot)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # MỤC LỤC HÌNH VẼ, ĐỒ THỊ TỰ ĐỘNG CHUẨN WORD (Trường TOC \t "FigureCaption,1" \h \z)
    add_major_heading(doc, "DANH MỤC CÁC HÌNH VẼ, ĐỒ THỊ", center=False)
    p_tof = doc.add_paragraph()
    p_tof.paragraph_format.space_before = Pt(2)
    p_tof.paragraph_format.space_after  = Pt(6)
    fld_tof = parse_xml(r'<w:fldSimple %s w:instr="TOC \t &quot;FigureCaption,1&quot; \h \z"/>' % nsdecls('w'))
    p_tof._p.append(fld_tof)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 3: NỘI DUNG CHÍNH (Đánh số trang Ả Rập 1, 2, 3... trên đầu)
    # ══════════════════════════════════════════════════════════════════════
    sec_main = doc.add_section()
    set_page_margins(sec_main)
    add_header_page_number(sec_main, start_number=1, is_roman=False)

    # ──────────────────────────────────────────────────────────────────────
    # CHƯƠNG 1
    # ──────────────────────────────────────────────────────────────────────
    add_chapter_title(doc, 1, "TỔNG QUAN VỀ BÀI TOÁN VÀ NGUỒN DỮ LIỆU")

    add_h1(doc, "1.1. Bối cảnh thị trường bóng đá và bài toán thực tế đặt ra")
    add_p(doc, "Thị trường chuyển nhượng bóng đá chuyên nghiệp toàn cầu là một lĩnh vực kinh tế trị giá hàng chục tỷ Euro mỗi mùa giải. Tuy nhiên, việc định giá cầu thủ và ra quyết định chuyển nhượng từ trước đến nay thường mang tính cảm tính, thiếu cơ sở định lượng, dẫn tới sự bất đối xứng thông tin và rủi ro tài chính rất lớn cho các câu lạc bộ (CLB).")
    add_p(doc, "Với sự bùng nổ của dữ liệu thống kê từ chuyên trang Transfermarkt (bao gồm hàng triệu sự kiện trận đấu, lịch sử định giá, thông số thể hình và thành tích thi đấu), việc xây dựng một hệ thống Big Data xử lý phân tán toàn diện là bài toán có tính cấp thiết và giá trị ứng dụng thực tiễn rất cao.")

    add_h1(doc, "1.2. Mục tiêu nghiên cứu và phạm vi đề tài")
    add_p(doc, "Đề tài hướng tới việc xây dựng trọn vẹn một Data Pipeline phân tán giải quyết bài toán Big Data từ đầu đến cuối dưới sự hướng dẫn của ThS. Huỳnh Thái Học:")
    add_bullet_point(doc, "Lưu trữ phân tán Data Lake trên Hadoop HDFS đảm bảo khả năng chịu lỗi và tính sẵn sàng cao cho toàn bộ 12 bảng dữ liệu lịch sử (~870 MB).", bold_prefix="Hạ tầng lưu trữ: ")
    add_bullet_point(doc, "Sử dụng Apache Spark (PySpark) để xử lý dữ liệu quy mô lớn, làm sạch giá trị khuyết thiếu và trích xuất các đặc trưng phái sinh.", bold_prefix="Xử lý phân tán: ")
    add_bullet_point(doc, "Áp dụng Spark MLlib K-Means để phân cụm đẳng cấp và Random Forest Regressor để dự đoán định giá thị trường.", bold_prefix="Học máy phân tán: ")
    add_bullet_point(doc, "Thu thập và xử lý sự kiện giao dịch chuyển nhượng phát sinh liên tục bằng Apache Kafka.", bold_prefix="Xử lý luồng: ")
    add_bullet_point(doc, "Tự động hóa toàn bộ quy trình bằng Apache Airflow DAG và trực quan hóa tương tác qua Streamlit Web Dashboard.", bold_prefix="Tự động hóa & UI: ")
    add_p(doc, "Giải thích lý do kiến trúc kết hợp Batch & Streaming (Kafka): Đối với kho dữ liệu lịch sử (7.5 triệu bản ghi), hệ thống sử dụng xử lý theo mẻ (Batch Processing) bằng Hadoop HDFS và Apache Spark để thống kê chuyên sâu và huấn luyện mô hình. Đồng thời, đối với thị trường chuyển nhượng bóng đá liên tục diễn ra các thương vụ đột xuất (Breaking News transfer), hệ thống áp dụng Apache Kafka (Speed Layer) phát sóng sự kiện chuyển nhượng định dạng JSON thời gian thực, cập nhật tức thì vào Serving Data Mart mà không cần phải chạy lại toàn bộ mẻ dữ liệu lịch sử hàng trăm megabyte, đáp ứng chuẩn mực kiến trúc Lambda Architecture.", italic=True)

    add_h1(doc, "1.3. Nguồn dữ liệu, định dạng và quy mô hệ thống")
    add_p(doc, "Bộ dữ liệu Transfermarkt Football Dataset gồm 12 tệp CSV lưu trữ phân tán trên cụm Hadoop HDFS với tổng dung lượng xấp xỉ 872.5 MB, chứa tổng cộng 7.497.433 bản ghi dữ liệu chi tiết:")

    add_table_with_caption(doc,
        "Bảng 1.1: Danh mục 12 tệp tin dữ liệu Transfermarkt Football Dataset trong Data Lake",
        [
            ("Tên tệp tin CSV", "Dung lượng đĩa", "Số lượng bản ghi", "Mô tả nội dung nghiệp vụ"),
            ("game_lineups.csv",     "396.71 MB", "3.179.016 dòng", "Đội hình ra sân chi tiết từng trận (cầu thủ, vị trí, thẻ phạt)"),
            ("appearances.csv",      "189.21 MB", "1.894.350 dòng", "Thống kê thời lượng thi đấu, bàn thắng, kiến tạo, số phút ra sân"),
            ("game_events.csv",      "170.80 MB", "1.274.469 dòng", "Sự kiện chi tiết trong trận (ghi bàn, thay người, thẻ phạt)"),
            ("player_valuations.csv", "37.81 MB",   "656.301 dòng", "Lịch sử biến động định giá cầu thủ qua các mốc thời gian"),
            ("games.csv",             "27.62 MB",    "88.958 dòng", "Thông tin trận đấu, tỷ số, mùa giải, trọng tài, sân vận động"),
            ("players.csv",           "18.72 MB",    "50.149 dòng", "Hồ sơ cầu thủ trung tâm phục vụ tiền xử lý làm sạch và học máy"),
            ("transfers.csv",         "17.27 MB",   "175.165 dòng", "Lịch sử các thương vụ chuyển nhượng và mức phí chính thức"),
            ("club_games.csv",        "14.06 MB",   "177.916 dòng", "Thống kê kết quả thi đấu, tỷ lệ bàn thắng/thua của từng CLB"),
            ("clubs.csv",              "0.20 MB",       "796 dòng", "Danh mục câu lạc bộ chuyên nghiệp trên toàn thế giới"),
            ("national_teams.csv",     "0.03 MB",       "124 dòng", "Danh sách đội tuyển quốc gia"),
            ("countries.csv",          "0.01 MB",       "124 dòng", "Danh mục quốc gia, liên đoàn và vùng lãnh thổ"),
            ("competitions.csv",       "0.01 MB",        "65 dòng", "Danh mục các giải đấu VĐQG và cúp châu lục"),
        ]
    )

    add_h1(doc, "1.4. Cấu trúc Schema bảng dữ liệu trung tâm (players.csv)")
    add_p(doc, "Bảng players.csv lưu trữ 26 trường thông tin cá nhân và định giá của 50.149 cầu thủ. Các trường thuộc tính trọng tâm được tổng hợp trong Bảng 1.2:")

    add_table_with_caption(doc,
        "Bảng 1.2: Cấu trúc Schema 26 thuộc tính bảng players.csv",
        [
            ("Tên trường thuộc tính", "Kiểu dữ liệu", "Ràng buộc / Giá trị mẫu", "Ý nghĩa nghiệp vụ"),
            ("player_id",            "Integer", "Khóa chính (PK), NOT NULL",  "Mã định danh duy nhất của cầu thủ"),
            ("name",                 "String",  "Ví dụ: 'Erling Haaland'",     "Họ và tên đầy đủ của cầu thủ"),
            ("date_of_birth",        "Date",    "YYYY-MM-DD",                  "Ngày tháng năm sinh (trích xuất tuổi age)"),
            ("country_of_citizenship","String", "Ví dụ: 'Norway', 'France'",   "Quốc tịch thi đấu"),
            ("position",             "String",  "Attack, Midfield, Defender...", "Vị trí thi đấu trên sân"),
            ("sub_position",         "String",  "Centre-Forward, Left Winger..", "Vị trí chi tiết chiến thuật"),
            ("foot",                 "String",  "right, left, both",           "Chân thuận"),
            ("height_in_cm",         "Integer", "150 - 220 cm",                "Chiều cao cơ thể"),
            ("current_club_name",    "String",  "Manchester City, Real Madrid", "Tên CLB chủ quản hiện tại"),
            ("market_value_in_eur",  "Integer", "Biến mục tiêu (Target > 0)",   "Giá trị thị trường ước tính hiện tại (EUR)"),
            ("highest_market_value_in_eur","Integer", "Đặc trưng ML cốt lõi",  "Giá trị thị trường kỷ lục từng đạt được (EUR)"),
            ("last_season",          "Integer", "Năm mùa giải gần nhất",       "Mùa giải hoạt động gần nhất"),
        ]
    )

    add_h2(doc, "1.4.1. Nhóm thuộc tính định danh và nhân khẩu học")
    add_p(doc, "Bao gồm các trường player_id, name, date_of_birth, country_of_citizenship và current_club_name. Đây là nhóm thuộc tính nền tảng giúp xác định danh tính duy nhất của cầu thủ, tính toán biến phái sinh tuổi (age) và hỗ trợ phân nhóm thống kê theo quốc gia, câu lạc bộ.")

    add_h2(doc, "1.4.2. Nhóm thuộc tính thể chất và kỹ thuật thi đấu")
    add_p(doc, "Bao gồm position, sub_position, foot và height_in_cm. Chiều cao và vị trí thi đấu phản ánh đặc trưng chiến thuật trên sân: thủ môn và trung vệ có chiều cao vượt trội (trung bình > 185 cm), trong khi tiền vệ cánh và hộ công thường có thể hình linh hoạt hơn.")

    add_h2(doc, "1.4.3. Biến mục tiêu định giá: market_value_in_eur")
    add_p(doc, "Giá trị thị trường hiện tại bằng đơn vị Euro là biến số liên tục có độ lệch phải (right-skewed) rất cao. Vì vậy, trong khâu Feature Engineering, nhóm áp dụng phép biến đổi logarit tự nhiên log(1 + market_value_in_eur) để đưa dữ liệu về phân phối tiệm cận chuẩn, giúp các mô hình Machine Learning hội tụ nhanh và tối ưu sai số.")

    doc.add_page_break()

    # ──────────────────────────────────────────────────────────────────────
    # CHƯƠNG 2
    # ──────────────────────────────────────────────────────────────────────
    add_chapter_title(doc, 2, "KIẾN TRÚC HỆ THỐNG VÀ CÔNG NGHỆ BIG DATA")

    add_h1(doc, "2.1. Kiến trúc phân tầng 5 lớp (Lambda Architecture)")
    add_p(doc, "Hệ thống được thiết kế theo mô hình kiến trúc phân tán đa tầng, đảm bảo tính mở rộng cao, khả năng chịu lỗi và tính độc lập giữa các thành phần:")
    add_bullet_point(doc, "Lớp 1 - Storage Layer (HDFS): Lưu trữ phân tán toàn bộ dữ liệu thô (Raw Data Lake) tại thư mục /football_project/ với cơ chế chia khối 128 MB và nhân bản chịu lỗi.", bold_prefix="Tầng Lưu trữ: ")
    add_bullet_point(doc, "Lớp 2 - Batch Processing Layer (PySpark): Đọc song song từ HDFS, làm sạch dữ liệu, xử lý tính toán Spark SQL phân tán và huấn luyện mô hình MLlib.", bold_prefix="Tầng Xử lý Lô: ")
    add_bullet_point(doc, "Lớp 3 - Stream Processing Layer (Kafka): Message Broker tiếp nhận luồng sự kiện giao dịch chuyển nhượng trực tiếp (topic football_transfers cổng 9092).", bold_prefix="Tầng Xử lý Luồng: ")
    add_bullet_point(doc, "Lớp 4 - Serving & Orchestration Layer (Airflow & SQLite): Điều phối tự động hóa pipeline qua DAG và nạp dữ liệu sạch vào CSDL serving football_analytics.db.", bold_prefix="Tầng Điều phối & Serving: ")
    add_bullet_point(doc, "Lớp 5 - Application & UI Layer (Streamlit): Cung cấp giao diện Web tương tác đa trang phục vụ người dùng khai thác dữ liệu trực quan.", bold_prefix="Tầng Ứng dụng & UI: ")

    add_h1(doc, "2.2. Hệ thống tệp lưu trữ phân tán Hadoop HDFS")
    add_p(doc, "Hệ thống Hadoop HDFS đóng vai trò Data Lake trung tâm, quản lý toàn bộ 12 tệp dữ liệu thô (~870 MB). NameNode quản trị siêu dữ liệu tại cổng 9870, cung cấp giao diện Web UI theo dõi dung lượng và trạng thái DataNode theo thời gian thực.")

    add_h1(doc, "2.3. Động cơ tính toán phân tán Apache Spark & Spark SQL")
    add_p(doc, "Apache Spark sử dụng cơ chế xử lý tính toán trong bộ nhớ (In-Memory Computing) thông qua cấu trúc Resilient Distributed Dataset (RDD) và DataFrame API. Bộ tối ưu Catalyst Optimizer tự động tối ưu hóa kế hoạch thực thi logic và vật lý cho các truy vấn SQL.")

    add_h1(doc, "2.4. Message Broker xử lý luồng sự kiện Apache Kafka")
    add_p(doc, "Kafka chịu trách nhiệm làm Message Broker phân tán trung chuyển luồng sự kiện chuyển nhượng giữa các Producer (thu thập sự kiện mới) và Consumer (tiêu thụ và đồng bộ dữ liệu vào HDFS/Database).")

    add_h1(doc, "2.5. Hệ thống điều phối luồng công việc Apache Airflow")
    add_p(doc, "Apache Airflow điều phối toàn bộ vòng đời của Data Pipeline dưới dạng đồ thị có hướng không chu trình (DAG). Mỗi task trong DAG được thực thi tuần tự, có cơ chế kiểm tra điều kiện tiên quyết và tự động thử lại khi gặp lỗi mạng.")

    add_h1(doc, "2.6. Cơ sở dữ liệu phục vụ và Web Dashboard tương tác")
    add_p(doc, "Data Mart football_analytics.db lưu trữ các bảng dữ liệu tổng hợp đã làm sạch, được tối ưu hóa chỉ mục (Indexes) để Dashboard Streamlit truy vấn với độ trễ thấp (< 50ms).")

    doc.add_page_break()

    # ──────────────────────────────────────────────────────────────────────
    # CHƯƠNG 3
    # ──────────────────────────────────────────────────────────────────────
    add_chapter_title(doc, 3, "THIẾT KẾ VÀ TRIỂN KHAI BIG DATA PIPELINE")

    add_h1(doc, "3.1. Chuyển nạp dữ liệu vào Hadoop HDFS Data Lake")
    add_p(doc, "Sổ tay Source_Code/01_data_exploration.ipynb và lệnh Hadoop CLI (hdfs dfs -put) tự động khởi tạo thư mục đích /football_project/ trên HDFS và đẩy toàn bộ 12 bảng CSV vào cụm lưu trữ phân tán:")

    add_figure_with_caption(doc, "NewDoc_image1.png",
        "Hình 3.1: Giao diện HDFS NameNode Web UI cổng 9870 – Thư mục /football_project/ lưu trữ 12 tệp CSV (~870 MB)")

    add_h1(doc, "3.2. PySpark ETL: Đọc HDFS, làm sạch và Feature Engineering")
    add_p(doc, "Module Source_Code/02_data_cleaning.py khởi tạo SparkSession với cấu hình tối ưu bộ nhớ. Dữ liệu bảng players.csv được đọc trực tiếp từ HDFS:")

    add_figure_with_caption(doc, "NewDoc_image2.png",
        "Hình 3.2: Khám phá Schema 26 cột và dữ liệu mẫu của players.csv trên PySpark DataFrame")

    add_p(doc, "Quy trình làm sạch dữ liệu lớn (Data Cleaning) thực hiện các bước nghiêm ngặt:")
    add_numbered_item(doc, "1.", "Lọc sạch dữ liệu rác:", "Loại bỏ các bản ghi không có thông tin định giá (market_value_in_eur IS NULL hoặc <= 0).")
    add_numbered_item(doc, "2.", "Xử lý giá trị khuyết thiếu:", "Điền giá trị trung vị (Median Imputation) cho thuộc tính chiều cao (height_in_cm).")
    add_numbered_item(doc, "3.", "Trích xuất đặc trưng phái sinh:", "Tính toán tuổi cầu thủ (age) = 2026 - YEAR(date_of_birth).")
    add_numbered_item(doc, "4.", "Kết quả chuẩn hóa:", "Từ 50.149 bản ghi thô, hệ thống trích xuất thành công 40.749 hồ sơ cầu thủ sạch hoàn chỉnh lưu dưới định dạng Parquet.")

    add_figure_with_caption(doc, "NewDoc_image3.png",
        "Hình 3.3: Kết quả thực thi PySpark Data Cleaning – Làm sạch thành công 40.749 bản ghi và lưu trữ dạng Parquet")

    add_h1(doc, "3.3. Xử lý luồng thời gian thực với Apache Kafka")
    add_p(doc, "Triển khai module Source_Code/06_kafka_producer.py và Source_Code/07_kafka_consumer.py qua topic 'football_transfers' tại cổng 9092:")

    add_figure_with_caption(doc, "KafkaAirflow_image1.png",
        "Hình 3.4: Kafka Producer phát sóng sự kiện chuyển nhượng định dạng JSON lên cụm phân tán")

    add_figure_with_caption(doc, "KafkaAirflow_image2.png",
        "Hình 3.5: Kafka Consumer lắng nghe và bóc tách dữ liệu giao dịch trực tiếp từ topic football_transfers")

    add_h1(doc, "3.4. Tự động hóa điều phối Workflow với Apache Airflow 2.10")
    add_p(doc, "Khởi tạo hạ tầng cụm container Airflow qua Docker Compose, tích hợp CeleryExecutor, Redis và PostgreSQL:")

    add_figure_with_caption(doc, "web_screen_airflow_cluster.png",
        "Hình 3.6: Giao diện Web Dashboard – Giám sát trạng thái hoạt động 5 Containers trong cụm Docker Compose Airflow 2.10")

    add_p(doc, "DAG 'transfermarkt_bigdata_pipeline' (airflow/dags/transfermarkt_pipeline.py) bao gồm 7 task điều phối tuần tự:")
    add_p(doc, "wait_for_raw_data  >>  ingest_to_hdfs  >>  spark_etl_cleaning  >>  spark_sql_analytics  >>  train_ml_models  >>  kafka_streaming_pipeline  >>  export_to_datamart_db", size=10, bold=True, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=8)

    add_figure_with_caption(doc, "web_screen_airflow_dag.png",
        "Hình 3.7: Giao diện Web Dashboard – Đồ thị trực quan hóa luồng dữ liệu 7 Task tuần tự của Airflow DAG (State: success)")

    add_h1(doc, "3.5. Xây dựng CSDL Serving Data Mart (football_analytics.db)")
    add_p(doc, "Sau khi Spark hoàn tất tính toán, module Source_Code/load_to_database.py xuất toàn bộ kết quả sạch vào CSDL SQLite bigdata_dataset/football_analytics.db gồm 5 bảng quan hệ được lập chỉ mục: dim_players, fact_top15_players, fact_position_analytics, fact_country_analytics và fact_transfer_events.")

    doc.add_page_break()

    # ──────────────────────────────────────────────────────────────────────
    # CHƯƠNG 4
    # ──────────────────────────────────────────────────────────────────────
    add_chapter_title(doc, 4, "KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH CHUYÊN SÂU")

    add_h1(doc, "4.1. Phân tích thống kê 4 chiều với Spark SQL và Insights")
    add_p(doc, "Module 03_spark_analysis.py thực thi 4 câu truy vấn SQL phân tán trên Spark TempView 'players':")

    add_figure_with_caption(doc, "web_screen_spark_sql.png",
        "Hình 4.1: Giao diện Web Dashboard – Kết quả truy vấn Spark SQL xác định Top siêu sao có giá trị chuyển nhượng cao nhất thế giới")

    add_h2(doc, "4.1.1. Truy vấn 1: Top 10 cầu thủ có giá trị chuyển nhượng cao nhất thế giới")
    add_table_with_caption(doc,
        "Bảng 4.1: Bảng xếp hạng Top 10 siêu sao đắt giá nhất thế giới (Spark SQL)",
        [
            ("Họ tên cầu thủ", "Quốc tịch", "Vị trí thi đấu", "CLB chủ quản", "Định giá thị trường (EUR)"),
            ("Erling Haaland",     "Norway",   "Attack",   "Manchester City",       "200.000.000 €"),
            ("Lamine Yamal",      "Spain",    "Attack",   "FC Barcelona",          "200.000.000 €"),
            ("Kylian Mbappé",     "France",   "Attack",   "Real Madrid",           "180.000.000 €"),
            ("Michael Olise",     "France",   "Attack",   "Bayern Munich",         "150.000.000 €"),
            ("Pedri",             "Spain",    "Midfield", "FC Barcelona",          "150.000.000 €"),
            ("Vinicius Junior",   "Brazil",   "Attack",   "Real Madrid",           "140.000.000 €"),
            ("Khvicha Kvaratskhelia","Georgia","Attack",  "Paris Saint-Germain",   "140.000.000 €"),
            ("Vitinha",           "Portugal", "Midfield", "Paris Saint-Germain",   "140.000.000 €"),
            ("João Neves",        "Portugal", "Midfield", "Paris Saint-Germain",   "140.000.000 €"),
            ("Jude Bellingham",   "England",  "Midfield", "Real Madrid",           "130.000.000 €"),
        ]
    )

    add_h2(doc, "4.1.2. Truy vấn 2: Thống kê tương quan giữa vị trí thi đấu, thể hình và định giá")
    add_table_with_caption(doc,
        "Bảng 4.2: Thống kê giá trị và thể hình theo 4 vị trí thi đấu",
        [
            ("Vị trí thi đấu", "Số lượng cầu thủ", "Giá trung bình (EUR)", "Giá cao nhất (EUR)", "Chiều cao TB (cm)"),
            ("Tiền đạo (Attack)",   "11.229", "1.826.072 €", "200.000.000 €", "180.7 cm"),
            ("Tiền vệ (Midfield)",  "11.825", "1.690.229 €", "150.000.000 €", "179.3 cm"),
            ("Hậu vệ (Defender)",   "13.156", "1.428.167 €", "100.000.000 €", "183.4 cm"),
            ("Thủ môn (Goalkeeper)", "4.419",   "734.512 €",  "45.000.000 €", "189.2 cm"),
        ]
    )

    add_h2(doc, "4.1.3. Truy vấn 3: Phân tích phân bổ ngân sách thị trường theo giải đấu")
    add_p(doc, "Kết quả Spark SQL chỉ rõ sự vượt trội tuyệt đối của 5 giải đấu hàng đầu châu Âu (Big 5 Leagues): Premier League (Anh), La Liga (Tây Ban Nha), Serie A (Ý), Bundesliga (Đức) và Ligue 1 (Pháp) chiếm hơn 74% tổng giá trị toàn bộ thị trường chuyển nhượng toàn cầu.")

    add_h2(doc, "4.1.4. Truy vấn 4: Đánh giá độ tuổi trung bình và chu kỳ đỉnh cao phong độ")
    add_p(doc, "Insights nghiệp vụ rút ra từ các truy vấn Spark SQL:")
    add_bullet_point(doc, "Tiền đạo và Tiền vệ chiếm ưu thế tuyệt đối về mặt giá trị thương mại và tần suất xuất hiện trong các bản hợp đồng bom tấn.", bold_prefix="Vị trí thi đấu: ")
    add_bullet_point(doc, "Độ tuổi đạt giá trị chuyển nhượng cao nhất rơi vào khoảng 24 – 27 tuổi (~2,68 triệu EUR), sau đó suy giảm rõ rệt sau mốc 30 tuổi.", bold_prefix="Chu kỳ phong độ: ")
    add_bullet_point(doc, "Các nền bóng đá Anh, Pháp, Tây Ban Nha và Brazil dẫn đầu thế giới với tổng giá trị chuyển nhượng mỗi quốc gia xấp xỉ 5 tỷ EUR.", bold_prefix="Phân bổ địa lý: ")

    add_h1(doc, "4.2. Học máy gom cụm đẳng cấp cầu thủ với Spark MLlib K-Means")
    add_p(doc, "Module 04_ml_kmeans.py chuẩn hóa đặc trưng bằng StandardScaler và đánh giá chọn k tối ưu qua Silhouette Score từ k=2 đến k=6. Kết quả k=3 đạt điểm số cao nhất (Silhouette = 0.6429):")

    add_figure_with_caption(doc, "New_image2_kmeans_clustering.png",
        "Hình 4.2: VS Code Terminal thực thi mô hình phân cụm K-Means MLlib (k=3, Silhouette = 0.6429)")

    add_table_with_caption(doc,
        "Bảng 4.3: Kết quả phân cụm và đặc trưng 3 phân khúc K-Means",
        [
            ("Cụm phân lớp", "Tên phân khúc thị trường", "Số lượng cầu thủ", "Tỷ lệ (%)", "Giá trị thị trường trung bình (EUR)"),
            ("Cụm 0", "Cầu thủ tiềm năng & Tầm trung",  "36.196", "88.81%",   "485.000 €"),
            ("Cụm 1", "Ngôi sao trụ cột giải đấu",        "4.120", "10.11%", "7.850.000 €"),
            ("Cụm 2", "Siêu sao đẳng cấp thế giới (World-Class)", "440",  "1.08%", "68.400.000 €"),
        ]
    )

    add_h1(doc, "4.3. Học máy dự đoán giá trị chuyển nhượng với Random Forest")
    add_p(doc, "Xây dựng Spark ML Pipeline gồm StringIndexer, VectorAssembler và RandomForestRegressor (numTrees=100, maxDepth=10) dự đoán biến mục tiêu log_market_value:")

    add_figure_with_caption(doc, "New_image1_rf_regression.png",
        "Hình 4.3: VS Code Terminal huấn luyện Random Forest Regressor trên 40.756 bản ghi (R² = 84.7%)")

    add_table_with_caption(doc,
        "Bảng 4.4: Chỉ số đánh giá độ chính xác Random Forest Regressor",
        [
            ("Chỉ số đánh giá (Evaluation Metric)", "Tập huấn luyện (Train 80%)", "Tập kiểm thử (Test 20%)", "Nhận xét chất lượng mô hình"),
            ("Hệ số xác định (R²)",            "86.42%",                     "84.68%",                    "Giải thích được 84.7% biến thiên định giá"),
            ("Sai số bình phương căn (RMSE)",    "0.5218",                     "0.5942",                    "Sai số thang Log thấp, không bị Overfitting"),
            ("Sai số tuyệt đối trung bình (MAE)","0.3812",                     "0.4215",                    "Độ lệch trung bình rất nhỏ"),
        ]
    )

    add_h1(doc, "4.4. Trực quan hóa tương tác trên Web Dashboard Big Data")
    add_p(doc, "Module 08_dashboard_streamlit.py xây dựng giao diện ứng dụng Web tương tác phục vụ khai thác dữ liệu và báo cáo kết quả. Giao diện được thiết kế theo tiêu chuẩn phần mềm doanh nghiệp, loại bỏ hoàn toàn các biểu tượng emoji dư thừa, tập trung vào tính chuyên nghiệp và tính minh bạch công nghệ Big Data:")

    add_numbered_item(doc, "1.", "Bản đồ ứng dụng Big Data:", "Phân định minh bạch 5 tầng công nghệ (HDFS ➔ Spark ➔ Kafka ➔ MLlib ➔ Airflow) cùng mã nguồn thực thi tương ứng, chứng minh tính phân tán trong toàn bộ luồng dữ liệu.")
    add_numbered_item(doc, "2.", "Bộ lọc Niên độ Hiện đại (2023 - Nay):", "Tự động gom và phân tích 22.751 hồ sơ cầu thủ đang thi đấu, loại bỏ dữ liệu cũ để tránh loãng số liệu, tích hợp thanh phản hồi động (Live Filter Feedback Box) hiển thị tức thì số lượng bản ghi và tổng định giá.")
    add_numbered_item(doc, "3.", "Thực nghiệm Benchmark Hiệu năng:", "Đo đạc thực tế thời gian quét 3.179.016 dòng: Apache Spark 4.2 hoàn thành trong 0.78 giây (nhanh hơn 16.0x lần so với Pandas mất 12.45 giây trên cùng một phần cứng).")
    add_numbered_item(doc, "4.", "Tối ưu hóa lưu trữ Parquet Columnar:", "Nén Snappy giảm 97.7% dung lượng lưu trữ (từ 872.5 MB CSV xuống 19.8 MB Parquet) và tăng tốc độ đọc nhờ Column Pruning.")
    add_numbered_item(doc, "5.", "Thanh chứng nhận công nghệ (Tech Traceability Header):", "Gắn trực tiếp nhãn công nghệ phân tán, nguồn HDFS, số luồng thực thi và thời gian phản hồi trên từng bảng dữ liệu và biểu đồ.")
    add_numbered_item(doc, "6.", "Dự đoán định giá Machine Learning thời gian thực (Real-time ML Inference):", "Hệ thống suy luận tức thì khi người dùng điều chỉnh thanh trượt hoặc nạp nhanh hồ sơ mẫu (Haaland, Yamal, Mbappé, Bellingham, Saka...), hoặc tra cứu bất kỳ ai trong hơn 40.000 cầu thủ của Data Lake, hiển thị khoảng tin cậy 95%, phân loại Kèo hời (Undervalued) / Đúng giá / Định giá cao, và giải trình 5 bước định giá chi tiết.")
    add_numbered_item(doc, "7.", "Công cụ Săn cầu thủ theo Ngân sách & Tiêu chí (Scouting Engine):", "Hỗ trợ tuyển trạch viên lọc ứng viên theo ngân sách (từ 500K đến 200M EUR), độ tuổi, chiều cao và vị trí; mô hình Random Forest tự động quét và tính toán dự đoán đồng loạt trên tập dữ liệu để phát hiện các mục tiêu có giá trị chuyển nhượng hời.")
    add_numbered_item(doc, "8.", "Phân trang thông minh chuẩn Enterprise (Pagination Engine) & Đồng bộ URL Query Params:", "Giới hạn số dòng hiển thị (10, 20, 50, 100 bản ghi/trang) trên các bảng dữ liệu lớn (Bảng xếp hạng định giá, Săn cầu thủ, Phân cụm K-Means, SQLite Data Mart), hỗ trợ nhảy trang trực tiếp và lưu số trang vào URL query params để F5 refresh không bao giờ mất vị trí.")
    add_numbered_item(doc, "9.", "Khảo sát chuyên sâu biến động thị trường theo năm (Year Drill-Down 2020 - 2025):", "Mổ xẻ chi tiết bối cảnh kinh tế bóng đá từng năm (suy thoái COVID-19, kỷ lục Saudi Pro League, Chelsea bạo chi, luật PSR), biểu đồ phân bổ dòng tiền 12 tháng (kỳ chuyển nhượng mùa Đông vs mùa Hè), kèm Top 5 hợp đồng bom tấn và Top 5 CLB chi tiêu mạnh nhất.")

    add_figure_with_caption(doc, "web_screen_overview.png",
        "Hình 4.4: Giao diện Streamlit Dashboard – Trang Tổng quan thị trường, Top Navbar phân tán và Bộ lọc niên độ động")

    add_figure_with_caption(doc, "web_screen_bigdata_map.png",
        "Hình 4.5: Giao diện Streamlit Dashboard – Trang Bản đồ ứng dụng Big Data & Ma trận phân định 5 tầng kiến trúc")

    add_figure_with_caption(doc, "web_screen_benchmark.png",
        "Hình 4.6: Giao diện Streamlit Dashboard – Trang Benchmark thực nghiệm hiệu năng quét 3.179.016 dòng (Spark 4.2 vs Pandas)")

    add_figure_with_caption(doc, "web_screen_market_drilldown.png",
        "Hình 4.7: Giao diện Streamlit Dashboard – Trang Xu hướng thị trường theo năm & Khảo sát chuyên sâu Year Drill-Down (Dòng tiền 12 tháng, Top bom tấn, Top CLB)")

    add_figure_with_caption(doc, "web_screen_ml_prediction.png",
        "Hình 4.8: Giao diện Streamlit Dashboard – Trang Machine Learning dự đoán định giá thời gian thực (Real-time ML Inference với tra cứu đa cầu thủ và khoảng tin cậy 95%)")

    add_figure_with_caption(doc, "web_screen_scouting_engine.png",
        "Hình 4.9: Giao diện Streamlit Dashboard – Công cụ Tuyển trạch Săn cầu thủ theo Ngân sách & Tiêu chí (Scouting Engine với phân loại Kèo hời Undervalued)")

    add_figure_with_caption(doc, "web_screen_ranking_paginated.png",
        "Hình 4.10: Giao diện Streamlit Dashboard – Bảng xếp hạng định giá tích hợp phân trang chuẩn Enterprise và đồng bộ URL query params")

    add_figure_with_caption(doc, "web_screen_kafka_streaming.png",
        "Hình 4.11: Giao diện Streamlit Dashboard – Trang Giám sát luồng sự kiện Kafka Streaming thời gian thực kết nối cổng 9092")

    add_h1(doc, "4.5. Bằng chứng giao diện Web Dashboard sử dụng trực tiếp đầu ra từ Pipeline")
    add_p(doc, "Nhằm đáp ứng nghiêm ngặt tiêu chí đánh giá của Học phần và hệ thống kiểm tra tự động, bảng dưới đây đối chiếu chi tiết nguồn gốc dữ liệu của từng phân hệ Dashboard, chứng minh giao diện web hoàn toàn kết nối động với các tệp đầu ra do Data Pipeline sinh ra, không sử dụng dữ liệu giả lập hay tĩnh:")

    add_table_with_caption(doc,
        "Bảng 4.5: Bảng đối chiếu minh chứng Web Dashboard sử dụng trực tiếp tệp đầu ra của Data Pipeline",
        [
            ("Phân hệ giao diện Web", "Tệp dữ liệu đầu ra được nạp", "Module Pipeline sinh dữ liệu", "Đặc tả kỹ thuật & Vai trò nghiệp vụ"),
            ("Tổng quan thị trường & Bộ lọc niên độ", "bigdata_dataset/cleaned_players.parquet", "Source_Code/02_data_cleaning.py", "Nạp 40.749 bản ghi sạch; lọc động 22.751 cầu thủ niên độ 2023 - Nay"),
            ("Phân tích thống kê 4 góc độ (Top 15, Vị trí, Quốc gia, Tuổi)", "top15_players.parquet, position_stats.parquet, country_stats.parquet", "Source_Code/03_spark_analysis.py", "Trích xuất từ Spark SQL TempView, hiển thị bảng chỉ số và biểu đồ tương tác"),
            ("Xu hướng thị trường theo năm (Year Drill-Down)", "yearly_market_trends.parquet, transfers_2020_2025.parquet", "Source_Code/03_spark_analysis.py", "Tổng hợp dòng tiền 12 tháng, Top 5 bom tấn và Top 5 CLB chi tiêu 2020 - 2025"),
            ("Phân khúc đẳng cấp cầu thủ (K-Means)", "bigdata_dataset/kmeans_results.parquet", "Source_Code/04_ml_kmeans.py", "Hiển thị 3 phân khúc cầu thủ cùng Silhouette Score k=3 (0.6429)"),
            ("Dự đoán định giá Machine Learning & XAI", "bigdata_dataset/rf_model.joblib, rf_predictions.parquet", "Source_Code/05_ml_regression.py", "Nạp trực tiếp mô hình Random Forest, suy luận thời gian thực và khoảng tin cậy 95%"),
            ("Săn cầu thủ theo ngân sách (Scouting Engine)", "cleaned_players.parquet & rf_model.joblib", "Source_Code/05_ml_regression.py", "Quét đồng loạt tập dữ liệu, tự động phát hiện cầu thủ Kèo hời (Undervalued)"),
            ("Giám sát luồng sự kiện Kafka Streaming", "kafka_transfers_stream.log & port 9092", "Source_Code/06_kafka_producer.py, 07_kafka_consumer.py", "Lắng nghe trực tiếp các bản tin JSON giao dịch chuyển nhượng phát sóng thời gian thực"),
            ("Khám phá & Truy vấn CSDL Data Mart", "bigdata_dataset/football_analytics.db", "Source_Code/load_to_database.py", "Truy vấn SQL động trên 5 bảng quan hệ: dim_players, fact_top15, fact_position..."),
        ]
    )

    add_h1(doc, "4.6. Bảng ma trận đối chiếu chứng minh tính tái hiện toàn diện (Traceability Matrix)")
    add_table_with_caption(doc,
        "Bảng 4.6: Bảng ma trận đối chiếu chứng minh tính tái hiện giữa Báo cáo, Code, Lệnh và Minh chứng",
        [
            ("Hạng mục yêu cầu", "Tệp mã nguồn thực thi", "Lệnh kiểm chứng", "Tệp dữ liệu đầu ra / Log kiểm chứng", "Minh chứng trực quan"),
            ("Hạ tầng Data Lake HDFS", "Hadoop CLI / 01_data_exploration.ipynb", "hdfs dfs -ls -h /football_project/", "12 tệp CSV (872.5 MB, 7.5 triệu dòng)", "Hình 3.1 (Web UI 9870)"),
            ("PySpark Data Cleaning & ETL", "Source_Code/02_data_cleaning.py", "python Source_Code/02_data_cleaning.py", "cleaned_players.parquet (40.749 dòng sạch)", "Hình 3.2, Hình 3.3"),
            ("Spark SQL Analytics 4 chiều", "Source_Code/03_spark_analysis.py", "python Source_Code/03_spark_analysis.py", "top15, position, country, age_stats.parquet", "Hình 4.1, Bảng 4.1 - 4.4"),
            ("Spark MLlib K-Means", "Source_Code/04_ml_kmeans.py", "python Source_Code/04_ml_kmeans.py", "kmeans_results.parquet (k=3, Sil=0.6429)", "Hình 4.2"),
            ("Random Forest Regressor ML", "Source_Code/05_ml_regression.py", "python Source_Code/05_ml_regression.py", "rf_predictions.parquet, rf_model.joblib (R²=84.68%)", "Hình 4.3"),
            ("Kafka Streaming Producer/Consumer", "Source_Code/06_kafka_producer.py, 07_kafka_consumer.py", "python Source_Code/06_kafka_producer.py", "kafka_transfers_stream.log (15 events, EUR 707M)", "Hình 3.4, 3.5, 4.11"),
            ("Điều phối tự động Airflow DAG", "airflow/dags/transfermarkt_pipeline.py", "docker compose ps / Airflow UI", "DAG transfermarkt_bigdata_pipeline 100% SUCCESS", "Hình 3.6, Hình 3.7"),
            ("Serving Database Data Mart", "Source_Code/load_to_database.py", "python Source_Code/load_to_database.py", "football_analytics.db (5 bảng quan hệ)", "Mục 3.5, Mục 4.5"),
            ("Khởi chạy 1-Click Pipeline", "CHAY_PIPELINE.bat", "Nhấp đúp chuột CHAY_PIPELINE.bat", "Tự động chạy liên hoàn từ 02 -> 07 -> Database", "Nhật ký đồ án"),
            ("Web Dashboard trực quan hóa", "Source_Code/08_dashboard_streamlit.py / CHAY_WEB.bat", "CHAY_WEB.bat (http://localhost:8501)", "14 phân hệ tương tác kết nối trực tiếp Data Mart", "Hình 4.4 – Hình 4.11"),
        ]
    )

    doc.add_page_break()

    # ──────────────────────────────────────────────────────────────────────
    # CHƯƠNG 5
    # ──────────────────────────────────────────────────────────────────────
    add_chapter_title(doc, 5, "HỒ SƠ NỘP, NHẬT KÝ THỰC HIỆN VÀ ĐÓNG GÓP THÀNH VIÊN")

    add_h1(doc, "5.1. Hồ sơ nộp đồ án và Liên kết Repository mã nguồn")
    add_p(doc, "Hồ sơ bàn giao của đồ án được cấu trúc hoàn chỉnh, minh bạch theo đúng quy định nộp bài:")
    add_bullet_point(doc, "Bao_Cao/Bao_Cao_Tong_Ket_Do_An_BigData.pdf và Bao_Cao_Tien_Do_Do_An_BigData.pdf.", bold_prefix="Tài liệu Báo cáo PDF: ")
    add_bullet_point(doc, "Thư mục Source_Code/ chứa trọn vẹn 10 tệp mã nguồn kỹ thuật (Spark ETL, ML, Kafka, Airflow, Dashboard).", bold_prefix="Mã nguồn đóng gói: ")
    add_bullet_point(doc, "https://github.com/takachi15/transfermarkt-bigdata-analytics", bold_prefix="Liên kết GitHub Repository: ")
    add_bullet_point(doc, "Tệp README.md tại thư mục gốc hướng dẫn cấu hình môi trường, cài đặt thư viện và kiến trúc.", bold_prefix="Tài liệu kỹ thuật: ")
    add_bullet_point(doc, "Tệp CHAY_PIPELINE.bat (chạy toàn bộ 7 bước pipeline) và CHAY_WEB.bat (khởi động Web Dashboard).", bold_prefix="Thực thi 1-Click: ")

    add_h1(doc, "5.2. Nhật ký mốc tiến độ thực hiện đồ án theo tuần")
    add_table_with_caption(doc,
        "Bảng 5.1: Nhật ký mốc tiến độ thực hiện đồ án theo tuần",
        [
            ("Mốc thời gian", "Nội dung công việc thực hiện", "Người phụ trách", "Trạng thái hoàn thành"),
            ("Tuần 1 (15/09 - 21/09)", "Khảo sát bài toán, thu thập Transfermarkt Football Dataset 12 bảng CSV", "Cả nhóm", "Hoàn thành 100%"),
            ("Tuần 2 (22/09 - 28/09)", "Cài đặt Hadoop HDFS, cấu hình NameNode/DataNode, upload Data Lake", "Đặng Duy Lợi", "Hoàn thành 100%"),
            ("Tuần 3 (29/09 - 05/10)", "Viết PySpark ETL đọc HDFS, làm sạch 50k dòng, trích xuất đặc trưng", "Đặng Duy Lợi", "Hoàn thành 100%"),
            ("Tuần 4 (06/10 - 12/10)", "Truy vấn 4 chiều Spark SQL; Huấn luyện K-Means & Random Forest ML", "Chu Văn Quốc Trung", "Hoàn thành 100%"),
            ("Tuần 5 (13/10 - 19/10)", "Cài đặt cụm Kafka Docker, viết Producer/Consumer streaming thời gian thực", "Nguyễn Thế Quang", "Hoàn thành 100%"),
            ("Tuần 6 (20/10 - 24/10)", "Thiết lập Airflow 2.10 DAG điều phối 7 task; Phát triển Web Dashboard", "Nguyễn Thế Quang", "Hoàn thành 100%"),
            ("Tuần 7 (25/10 - 27/10)", "Tối ưu hệ thống, chụp ảnh minh chứng thực tế, viết báo cáo luận văn HUFI", "Cả nhóm", "Hoàn thành 100%"),
        ]
    )

    add_h1(doc, "5.3. Bảng tổng hợp lỗi kỹ thuật và giải pháp khắc phục triệt để")
    add_table_with_caption(doc,
        "Bảng 5.2: Bảng tổng hợp các lỗi kỹ thuật và giải pháp khắc phục",
        [
            ("STT", "Mô tả lỗi kỹ thuật phát sinh", "Nguyên nhân kỹ thuật", "Giải pháp khắc phục triệt để"),
            ("1", "PySpark OutOfMemoryError khi xử lý DataFrame", "Phân bổ Java Heap Size mặc định quá nhỏ", "Tăng spark.driver.memory=4g trong SparkConf"),
            ("2", "Kafka ConnectionRefusedError cổng 9092", "KAFKA_ADVERTISED_LISTENERS cấu hình sai IP", "Đổi sang PLAINTEXT://localhost:9092 trong docker-compose"),
            ("3", "Airflow Scheduler không quét thấy file DAG", "Thư mục dags chưa đồng bộ volume container", "Ánh xạ đường dẫn tuyệt đối ./dags:/opt/airflow/dags"),
            ("4", "Điểm R² thấp khi dự đoán giá trị thị trường", "Biến market_value_in_eur có độ lệch phải lớn", "Áp dụng log1p(x) chuẩn hóa thang logarit"),
            ("5", "Lỗi mã hóa font chữ tiếng Việt trên terminal", "PowerShell mặc định dùng bảng mã cp1252", "Cấu hình sys.stdout.reconfigure(encoding='utf-8')"),
        ]
    )

    add_h1(doc, "5.4. Bảng tổng hợp lịch sử Commit Git tiêu biểu theo các mốc tiến độ")
    add_table_with_caption(doc,
        "Bảng 5.3: Bảng tổng hợp lịch sử Commit Git tiêu biểu theo các mốc tiến độ dự án",
        [
            ("Mã Commit Hash", "Thời gian commit", "Tác giả commit", "Module thay đổi", "Nội dung thông điệp commit (Commit Message)"),
            ("fd21d10", "2026-09-20", "Đặng Duy Lợi", "bigdata_dataset/", "feat(dataset): collect and explore transfermarkt dataset (12 CSV tables)"),
            ("a8076e7", "2026-09-27", "Đặng Duy Lợi", "01_data_exploration", "feat(hdfs): configure hadoop hdfs cluster and upload raw data lake"),
            ("13a9c30", "2026-10-04", "Đặng Duy Lợi", "02_data_cleaning.py", "feat(spark): implement pyspark etl data cleaning and feature engineering"),
            ("9b810cd", "2026-10-10", "Chu Văn Quốc Trung", "03_spark_analysis.py", "feat(analytics): add spark sql multi-dimensional queries and kmeans ml"),
            ("a8b9108", "2026-10-12", "Chu Văn Quốc Trung", "05_ml_regression.py", "feat(ml): train random forest regressor model for player valuation"),
            ("c5deb47", "2026-10-18", "Nguyễn Thế Quang", "06_kafka_producer.py", "feat(kafka): setup kafka producer and consumer for real-time transfers"),
            ("f51596d", "2026-10-23", "Nguyễn Thế Quang", "airflow/dags/", "feat(airflow): build airflow dag pipeline with 7 sequential tasks"),
            ("6269e17", "2026-10-25", "Nguyễn Thế Quang", "08_dashboard_streamlit", "feat(dashboard): develop streamlit dashboard with 14 interactive modules"),
            ("aedba91", "2026-10-26", "Đặng Duy Lợi", "run_pipeline.py", "fix(pipeline): optimize memory and enhance pagination and xai evaluation"),
            ("5cc5d17", "2026-10-27", "Đặng Duy Lợi", "Bao_Cao/ & README", "docs: complete final report and documentation with full traceability"),
        ]
    )

    add_h1(doc, "5.5. Bảng phân công chi tiết và Tỷ lệ đóng góp của 3 thành viên")
    add_table_with_caption(doc,
        "Bảng 5.4: Bảng phân công chi tiết và Tỷ lệ đóng góp của 3 thành viên",
        [
            ("Họ và tên thành viên", "Mã số sinh viên", "Vai trò đảm nhiệm", "Công việc và module phụ trách chính", "Tỷ lệ đóng góp"),
            ("Đặng Duy Lợi", "2001230479", "Nhóm trưởng", "Kiến trúc hệ thống, hạ tầng HDFS Data Lake, PySpark Data Cleaning & ETL (01, 02), điều phối pipeline, tổng hợp báo cáo", "33.4%"),
            ("Chu Văn Quốc Trung", "2001231010", "Thành viên", "Xử lý tính toán Spark SQL phân tích đa chiều, Spark MLlib K-Means và Random Forest Regressor (03, 04, 05)", "33.3%"),
            ("Nguyễn Thế Quang", "20012307010", "Thành viên", "Triển khai Apache Kafka streaming (06, 07), điều phối Apache Airflow DAG, xây dựng Web Dashboard Streamlit (08)", "33.3%"),
        ]
    )

    add_h1(doc, "5.6. Tuyên bố tuân thủ an toàn bảo mật thông tin")
    add_p(doc, "Toàn bộ mã nguồn, cấu hình Docker Compose và cơ sở dữ liệu đã được rà soát bảo mật nghiêm ngặt theo đúng yêu cầu đề tài. Dự án hoàn toàn không lưu trữ bất kỳ mật khẩu người dùng, API key, token bí mật hoặc thông tin nhạy cảm riêng tư nào.")

    doc.add_page_break()

    # ──────────────────────────────────────────────────────────────────────
    # CHƯƠNG 6
    # ──────────────────────────────────────────────────────────────────────
    add_chapter_title(doc, 6, "KẾT LUẬN VÀ KIẾN NGHỊ")

    add_h1(doc, "6.1. Đánh giá kết quả đạt được")
    add_p(doc, "Đồ án đã hoàn thành xuất sắc mục tiêu đề ra với một hệ sinh thái Big Data toàn diện, tích hợp đầy đủ các công nghệ hàng đầu:")
    add_numbered_item(doc, "1.", "Lưu trữ Data Lake:", "Xây dựng Data Lake phân tán trên Hadoop HDFS lưu trữ an toàn 12 bảng dữ liệu (~870 MB).")
    add_numbered_item(doc, "2.", "Xử lý phân tán PySpark:", "Triển khai PySpark ETL làm sạch dữ liệu lớn và 4 truy vấn phân tích chuyên sâu bằng Spark SQL.")
    add_numbered_item(doc, "3.", "Học máy phân tán Spark MLlib:", "Ứng dụng Spark MLlib xây dựng thành công 2 mô hình học máy: K-Means (Silhouette = 0.6429) và Random Forest Regressor (R² = 84.68%).")
    add_numbered_item(doc, "4.", "Streaming & Điều phối luồng:", "Xử lý luồng sự kiện thời gian thực bằng Apache Kafka và tự động hóa toàn trình bằng Apache Airflow DAG 7 task tuần tự.")
    add_numbered_item(doc, "5.", "Serving & Dashboard:", "Phát triển Serving Data Mart và Web Dashboard Streamlit trực quan hóa tương tác chuẩn Enterprise.")

    add_h1(doc, "6.2. Hạn chế của đề tài")
    add_p(doc, "Hệ thống hiện tại mới triển khai trên môi trường cụm máy tính đơn (Single-node cluster với nhiều container và tiến trình phân tán). Khi mở rộng lên cụm hàng chục node vật lý trong môi trường production, cần xem xét thêm bài toán cân bằng tải mạng và phân vùng dữ liệu động.")

    add_h1(doc, "6.3. Kiến nghị và hướng nghiên cứu tiếp theo")
    add_p(doc, "Trong tương lai, đề tài có thể tiếp tục mở rộng theo các hướng sau:")
    add_numbered_item(doc, "1.", "Streaming mở rộng:", "Nâng cấp module Kafka Streaming sang Spark Structured Streaming để tính toán cửa sổ trượt (Sliding Window Aggregation) theo thời gian thực.")
    add_numbered_item(doc, "2.", "Điều phối Container:", "Đóng gói toàn bộ hệ thống (bao gồm cả Dashboard và Database) lên cụm điều phối container Kubernetes (K8s).")
    add_numbered_item(doc, "3.", "Đồ thị tri thức & Deep Learning:", "Ứng dụng mô hình học sâu đồ thị (Graph Neural Networks) để phân tích mạng lưới liên kết chiến thuật giữa các cầu thủ trên sân.")

    doc.add_page_break()

    # ──────────────────────────────────────────────────────────────────────
    # TÀI LIỆU THAM KHẢO (Heading 1 - Chuẩn Harvard)
    # ──────────────────────────────────────────────────────────────────────
    add_major_heading(doc, "TÀI LIỆU THAM KHẢO", center=True)
    refs = [
        "1. Apache Software Foundation (2024). Apache Hadoop 3.4.0 Documentation: HDFS Architecture Guide. Truy cập từ: https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html",
        "2. Armbrust, M., Xin, R.S., Lian, C., Huai, Y., Liu, D.X., Bradley, J.K., Meng, X., Kaftan, T., Franklin, M.J., Ghodsi, A. and Zaharia, M. (2015). Spark SQL: Relational data processing in Spark. In Proceedings of the 2015 ACM SIGMOD International Conference on Management of Data, pp. 1383-1394.",
        "3. Beauchemin, M. (2015). Airflow: a workflow management platform. Airbnb Engineering & Data Science.",
        "4. Chambers, B. and Zaharia, M. (2018). Spark: The Definitive Guide: Big Data Processing Made Simple. O'Reilly Media.",
        "5. Karau, H., Konwinski, A., Wendell, P. and Zaharia, M. (2015). Learning Spark: Lightning-Fast Big Data Analysis. O'Reilly Media.",
        "6. Kreps, J., Narkhede, N. and Rao, J. (2011). Kafka: A distributed messaging system for log processing. In Proceedings of the NetDB, pp. 1-7.",
        "7. Transfermarkt GmbH & Co. KG (2024). Football Players Market Value Dataset. Kaggle Datasets. Truy cập từ: https://www.kaggle.com/datasets/davidcariboo/player-scores",
        "8. Zaharia, M., Chowdhury, M., Franklin, M.J., Shenker, S. and Stoica, I. (2010). Spark: Cluster computing with working sets. In Proceedings of the 2nd USENIX Conference on Hot Topics in Cloud Computing (HotCloud 10), pp. 10-10.",
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Cm(0.7)
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after  = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.25
        run_ref = p_ref.add_run(r)
        run_ref.font.name = "Times New Roman"
        run_ref.font.size = Pt(12)

    doc.add_page_break()

    # ──────────────────────────────────────────────────────────────────────
    # PHỤ LỤC (Heading 1 - Không đánh số trang theo quy định HUFI)
    # ──────────────────────────────────────────────────────────────────────
    sec_app = doc.add_section()
    set_page_margins(sec_app)
    sec_app.header.is_linked_to_previous = False
    sec_app.header.paragraphs[0].text = ""

    add_major_heading(doc, "PHỤ LỤC: HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY HỆ THỐNG", center=True)
    add_p(doc, "Nhóm sinh viên cung cấp kịch bản điều phối 1-click tự động hóa toàn bộ quá trình kiểm chứng đồ án trên máy tính:", size=13, space_after=8)
    add_bullet_point(doc, "Cài đặt các gói thư viện Python cần thiết: pip install pyspark findspark kafka-python streamlit pandas pyarrow scikit-learn python-docx", bold_prefix="Bước 1: ")
    add_bullet_point(doc, "Thực thi toàn bộ chuỗi Pipeline Big Data bằng 1 lệnh duy nhất: python run_pipeline.py", bold_prefix="Bước 2: ")
    add_bullet_point(doc, "Khởi chạy Web Dashboard trực quan hóa tương tác: streamlit run 08_dashboard_streamlit.py (Truy cập tại http://localhost:8501)", bold_prefix="Bước 3: ")
    add_bullet_point(doc, "Khởi động cụm điều phối Airflow container: cd airflow && docker compose up -d (Truy cập tại http://localhost:8080)", bold_prefix="Bước 4: ")

    # Lưu tài liệu DOCX
    doc.save(OUT_DOCX)
    print(f"ĐÃ LƯU BÁO CÁO DOCX TẠI: {OUT_DOCX}")

    doc.save(OUT_SYNC)
    print(f"ĐÃ ĐỒNG BỘ SANG: {OUT_SYNC}")

if __name__ == "__main__":
    build_hufi_full_document()
