"""
PDF 转 Markdown 工具
使用方法：python pdf_to_markdown.py <PDF文件路径> [输出目录]
"""

import sys
import re
from pathlib import Path


def clean_text(text: str) -> str:
    """清理提取的文本"""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()
    return text


def extract_title_from_pdf(doc) -> str:
    """尝试从PDF元数据或第一页提取标题"""
    if doc.metadata.get('title'):
        return doc.metadata['title']

    try:
        first_page = doc[0]
        text = first_page.get_text()
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                return line
    except:
        pass

    return ""


def pdf_to_markdown(pdf_path: str, output_dir: str = None) -> str:
    """将PDF转换为Markdown"""

    try:
        import fitz
    except ImportError:
        print("需要安装 pymupdf: pip install pymupdf")
        sys.exit(1)

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)

    if output_dir is None:
        output_dir = pdf_file.parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"正在转换: {pdf_file.name}")

    doc = fitz.open(pdf_path)
    title = extract_title_from_pdf(doc)

    markdown_content = []

    if title:
        markdown_content.append(f"# {title}\n")

    markdown_content.append(f"*来源: {pdf_file.name}*\n")
    markdown_content.append(f"*页数: {len(doc)}*\n")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        text = clean_text(text)

        if text.strip():
            markdown_content.append(f"\n## 第 {page_num + 1} 页\n")
            markdown_content.append(text)

    doc.close()

    output_file = output_dir / f"{pdf_file.stem}.md"
    output_file.write_text('\n'.join(markdown_content), encoding='utf-8')

    print(f"转换完成: {output_file.name}")
    return str(output_file)


def batch_convert(input_dir: str, output_dir: str = None) -> list:
    """批量转换目录下所有PDF文件"""
    import fitz

    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"目录不存在: {input_dir}")
        return []

    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"目录下没有PDF文件: {input_dir}")
        return []

    results = []
    for pdf_file in pdf_files:
        try:
            result = pdf_to_markdown(str(pdf_file), output_dir)
            results.append(result)
        except Exception as e:
            print(f"转换失败 {pdf_file.name}: {e}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  单文件: python pdf_to_markdown.py <PDF文件路径> [输出目录]")
        print("  批量:   python pdf_to_markdown.py --batch <目录路径> [输出目录]")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("请提供输入目录")
            sys.exit(1)
        input_dir = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        results = batch_convert(input_dir, output_dir)
        print(f"\n批量转换完成，共 {len(results)} 个文件")
    else:
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        pdf_to_markdown(pdf_path, output_dir)
