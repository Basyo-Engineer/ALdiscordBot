import fitz  # PyMuPDF
import os

def extract_pdf_content(file_path: str, page_number: int, output_dir: str):
    doc = fitz.open(file_path)

    if page_number < 1 or page_number > len(doc):
        raise ValueError("ページ番号が範囲外です")

    page = doc[page_number - 1]

    # テキスト抽出
    text = page.get_text()

    # 画像抽出
    image_files = []
    for i, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n < 5:  # グレースケールまたはRGB
            img_path = os.path.join(output_dir, f"page{page_number}_img{i+1}.png")
            pix.save(img_path)
        else:  # CMYKなどの場合
            pix = fitz.Pixmap(fitz.csRGB, pix)
            img_path = os.path.join(output_dir, f"page{page_number}_img{i+1}.png")
            pix.save(img_path)
        image_files.append(img_path)

    return text, image_files
