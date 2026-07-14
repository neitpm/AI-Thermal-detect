import re
import os
import sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def add_p_border_bottom(paragraph):
    pPr = paragraph._element.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="4F81BD"/></w:pBdr>')
    pPr.append(pBdr)

def add_formatted_text(paragraph, text):
    # Regex to find bold **text** or inline code `code` or bold-italic ***text***
    # Let's split by bold-italic, bold, and code.
    pattern = r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`)'
    tokens = re.split(pattern, text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('***') and token.endswith('***'):
            run = paragraph.add_run(token[3:-3])
            run.bold = True
            run.italic = True
        elif token.startswith('**') and token.endswith('**'):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith('*') and token.endswith('*'):
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        elif token.startswith('`') and token.endswith('`'):
            run = paragraph.add_run(token[1:-1])
            run.font.name = 'Courier New'
            run.font.size = Pt(9.5)
            # Add light gray color to run text
            run.font.color.rgb = RGBColor(180, 50, 50)
        else:
            paragraph.add_run(token)

def convert_md_to_docx(md_path, docx_path):
    doc = Document()
    
    # Configure page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Set default style to Times New Roman
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(30, 30, 30)

    # Color definitions
    PRIMARY_COLOR = RGBColor(31, 78, 121)    # #1F4E79 Dark Blue
    SECONDARY_COLOR = RGBColor(89, 89, 89)   # #595959 Dark Gray

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    in_mermaid_block = False
    code_content = []
    code_lang = ""

    for line in lines:
        stripped = line.strip()
        
        # Check for code blocks
        if stripped.startswith('```'):
            if in_code_block:
                # End of code block
                if in_mermaid_block:
                    in_mermaid_block = False
                    in_code_block = False
                    code_content = []
                    continue

                # Add a table with 1 cell to act as a shaded box for code
                table = doc.add_table(rows=1, cols=1)
                table.autofit = False
                table.columns[0].width = Inches(6.5)
                cell = table.cell(0, 0)
                set_cell_background(cell, "F2F2F2") # Light gray background
                
                # Set cell padding (margins)
                tcPr = cell._element.get_or_add_tcPr()
                tcMar = OxmlElement('w:tcMar')
                for margin_name in ['top', 'left', 'bottom', 'right']:
                    node = OxmlElement(f'w:{margin_name}')
                    node.set(qn('w:w'), '120')
                    node.set(qn('w:type'), 'dxa')
                    tcMar.append(node)
                tcPr.append(tcMar)
                
                # Add borders
                tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/><w:left w:val="single" w:sz="18" w:space="0" w:color="1F4E79"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/></w:tcBorders>')
                tcPr.append(tcBorders)

                # Write code lines
                p = cell.paragraphs[0]
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                
                code_text = "".join(code_content)
                run = p.add_run(code_text.rstrip('\n'))
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(40, 40, 40)
                
                # Add spacing paragraph after table
                p_after = doc.add_paragraph()
                p_after.paragraph_format.space_before = Pt(0)
                p_after.paragraph_format.space_after = Pt(6)
                
                in_code_block = False
                code_content = []
            else:
                # Start of code block
                in_code_block = True
                code_lang = stripped[3:].strip()
                if code_lang.lower() == 'mermaid':
                    in_mermaid_block = True
                else:
                    in_mermaid_block = False
            continue

        if in_code_block:
            if not in_mermaid_block:
                code_content.append(line)
            continue

        # Ignore empty lines or generate small spacing
        if not stripped:
            continue

        # Check for images
        image_match = re.match(r'^!\[(.*?)\]\((.*?)\)', stripped)
        if image_match:
            alt_text = image_match.group(1)
            img_path = image_match.group(2)
            
            # If path starts with file:///, strip it
            if img_path.startswith("file:///"):
                img_path = img_path[8:]
                
            # If path is relative, make it absolute relative to md_file directory
            if not os.path.isabs(img_path):
                img_path = os.path.join(os.path.dirname(os.path.abspath(md_path)), img_path)
                
            if os.path.exists(img_path):
                # Add picture
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.space_before = Pt(12)
                run = p.add_run()
                run.add_picture(img_path, width=Inches(5.8))
                
                # Add caption
                if alt_text:
                    p_cap = doc.add_paragraph()
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_cap.paragraph_format.space_before = Pt(2)
                    p_cap.paragraph_format.space_after = Pt(12)
                    run_cap = p_cap.add_run(f"Hình: {alt_text}")
                    run_cap.italic = True
                    run_cap.font.size = Pt(9.5)
                    run_cap.font.color.rgb = RGBColor(100, 100, 100)
            else:
                print(f"[WARNING] Image path not found: {img_path}")
            continue

        # Horizontal Rule
        if stripped == '---':
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(12)
            add_p_border_bottom(p)
            continue

        # Headings
        if stripped.startswith('# '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[2:])
            run.bold = True
            run.font.size = Pt(18)
            run.font.color.rgb = PRIMARY_COLOR
            add_p_border_bottom(p)
            continue

        if stripped.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[3:])
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = PRIMARY_COLOR
            continue

        if stripped.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[4:])
            run.bold = True
            run.font.size = Pt(12)
            run.font.color.rgb = SECONDARY_COLOR
            continue

        if stripped.startswith('#### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[5:])
            run.bold = True
            run.italic = True
            run.font.size = Pt(11)
            run.font.color.rgb = SECONDARY_COLOR
            continue

        # Bullet lists and Numbered lists
        # Check indentation levels
        leading_spaces = len(line) - len(line.lstrip(' '))
        indent_level = leading_spaces // 4
        
        list_match = re.match(r'^[\s]*([\*\-\+])[\s]+(.*)', line)
        num_match = re.match(r'^[\s]*([0-9]+\.)[\s]+(.*)', line)

        if list_match:
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.space_before = Pt(0)
            content = list_match.group(2)
            add_formatted_text(p, content)
        elif num_match:
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.space_before = Pt(0)
            content = num_match.group(2)
            add_formatted_text(p, content)
        else:
            # Normal paragraph
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_text(p, line.strip())

    # Save document
    doc.save(docx_path)
    print(f"[CONVERTER SUCCESS] Đã tạo file word thành công tại: {docx_path}")

if __name__ == '__main__':
    md_file = "/home/admin-khai/Desktop/smart_camera_edge_system/HOSO_KY_THUAT_DU_AN.md"
    docx_file = "/home/admin-khai/Desktop/smart_camera_edge_system/HOSO_KY_THUAT_DU_AN.docx"
    convert_md_to_docx(md_file, docx_file)
