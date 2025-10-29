from flask import Flask, request, send_file
from PyPDF2 import PdfMerger
import io

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>PDF Index Merger</h2>
    <form action="/merge" method="post" enctype="multipart/form-data">
      <input type="file" name="pdfs" multiple><br><br>
      <button type="submit">Merge PDFs</button>
    </form>
    '''

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    uploaded_files = request.files.getlist('pdfs')
    merger = PdfMerger()

    index_text = "Index Page\n\n"
    page_num = 1

    pdf_buffers = []
    for f in uploaded_files:
        pdf_buffer = io.BytesIO(f.read())
        merger.append(pdf_buffer)
        pdf_buffers.append(pdf_buffer)
        index_text += f"{f.filename} — starts at page {page_num}\n"
        try:
            reader = PdfReader(pdf_buffer)
            page_num += len(reader.pages)
        except:
            page_num += 1

    index_pdf = io.BytesIO()
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    c = canvas.Canvas(index_pdf, pagesize=A4)
    for i, line in enumerate(index_text.splitlines()):
        c.drawString(50, 800 - 15*i, line)
    c.showPage()
    c.save()
    index_pdf.seek(0)

    final = io.BytesIO()
    merger_with_index = PdfMerger()
    merger_with_index.append(index_pdf)
    for buf in pdf_buffers:
        buf.seek(0)
        merger_with_index.append(buf)
    merger_with_index.write(final)
    final.seek(0)

    return send_file(final, download_name="merged_with_index.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run()
