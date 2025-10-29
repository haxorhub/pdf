from flask import Flask, request, send_file
from PyPDF2 import PdfMerger, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>PDF Index Merger (by Pawan Vishwakarma)</h2>
    <form action="/merge" method="post" enctype="multipart/form-data">
      <input type="file" name="pdfs" multiple required><br><br>
      <button type="submit">Merge PDFs with Index</button>
    </form>
    '''

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    uploaded_files = request.files.getlist('pdfs')
    if not uploaded_files:
        return "No PDFs uploaded!", 400

    merger = PdfMerger()
    index_lines = ["Index Page", ""]

    page_counter = 1
    pdf_buffers = []

    for f in uploaded_files:
        pdf_bytes = io.BytesIO(f.read())
        pdf_buffers.append(pdf_bytes)
        try:
            reader = PdfReader(pdf_bytes)
            total_pages = len(reader.pages)
        except:
            total_pages = 1

        index_lines.append(f"{f.filename} — starts at page {page_counter}")
        page_counter += total_pages

    # Create index PDF
    index_pdf = io.BytesIO()
    c = canvas.Canvas(index_pdf, pagesize=A4)
    y = 800
    for line in index_lines:
        c.drawString(50, y, line)
        y -= 20
    c.showPage()
    c.save()
    index_pdf.seek(0)

    # Merge index + uploaded PDFs
    merger.append(index_pdf)
    for buf in pdf_buffers:
        buf.seek(0)
        merger.append(buf)

    final = io.BytesIO()
    merger.write(final)
    merger.close()
    final.seek(0)

    return send_file(final, download_name="merged_with_index.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run()
