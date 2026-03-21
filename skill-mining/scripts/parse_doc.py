"""
parse_doc.py - 解析 Word/PDF/图片文件，提取纯文本内容
用法: python parse_doc.py "文件路径"
依赖: pip install python-docx pymupdf pillow pytesseract
"""

import sys
import os

def parse_docx(path):
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except ImportError:
        return f"[错误] 需要安装 python-docx: pip install python-docx\n文件路径: {path}"

def parse_pdf(path):
    try:
        import fitz  # pymupdf
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        return f"[错误] 需要安装 pymupdf: pip install pymupdf\n文件路径: {path}"

def parse_image(path):
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(path)
        return pytesseract.image_to_string(img, lang='chi_sim+eng')
    except ImportError:
        return f"[错误] 需要安装 pillow 和 pytesseract: pip install pillow pytesseract\n文件路径: {path}"

def parse_file(path):
    if not os.path.exists(path):
        print(f"[错误] 文件不存在: {path}")
        sys.exit(1)

    ext = os.path.splitext(path)[1].lower()

    if ext in ['.docx', '.doc']:
        content = parse_docx(path)
    elif ext == '.pdf':
        content = parse_pdf(path)
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']:
        content = parse_image(path)
    elif ext in ['.txt', '.md']:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    else:
        print(f"[错误] 不支持的文件格式: {ext}")
        sys.exit(1)

    print(content)
    return content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python parse_doc.py <文件路径>")
        sys.exit(1)
    parse_file(sys.argv[1])
