from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .forms import UploadFileForm
from pdf2docx import Converter
import tempfile
import os
from io import BytesIO
from docx2pdf import convert
import fitz  # PyMuPDF

# Dictionnaire global pour stocker la progression de la conversion
conversion_progress = {}

def SizeCalc(fichier):
    file_size = fichier.size

    if file_size < 1024:
        file_size_formatted = f"{file_size} octets"
    elif file_size < 1024 * 1024:
        file_size_formatted = f"{file_size / 1024:.2f} Ko"
    else:
        file_size_formatted = f"{file_size / (1024 * 1024):.2f} Mo"

    return file_size_formatted

def index(request):
    poids = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            FileToConvert = request.FILES['pdf_file']
            poids = SizeCalc(FileToConvert)
            print(poids)
            file_id = str(FileToConvert.size) + FileToConvert.name  # Identifiant unique du fichier
            conversion_progress[file_id] = 0

            if FileToConvert.name.endswith("pdf"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf.write(FileToConvert.read())
                    temp_pdf_path = temp_pdf.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                    temp_docx_path = temp_docx.name

                try:
                    # Utilisation de PyMuPDF pour obtenir le nombre de pages
                    pdf_document = fitz.open(temp_pdf_path)
                    total_pages = pdf_document.page_count
                    pdf_document.close()

                    cv = Converter(temp_pdf_path)
                    for page in range(total_pages):
                        cv.convert(temp_docx_path, start=page, end=page+1)
                        conversion_progress[file_id] = int((page + 1) / total_pages * 100)
                    cv.close()
                    conversion_progress[file_id] = 100  # Conversion terminée
                except Exception as e:
                    conversion_progress[file_id] = -1  # Erreur
                    print(f"Erreur de conversion PDF vers DOCX : {e}")
                    return JsonResponse({'error': str(e)}, status=500)

                with open(temp_docx_path, 'rb') as docx_file:
                    docx_io = BytesIO(docx_file.read())

                docx_io.seek(0)
                os.remove(temp_pdf_path)
                os.remove(temp_docx_path)

                response = HttpResponse(docx_io, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename={FileToConvert.name.replace(".pdf", ".docx")}'
                return response

            elif FileToConvert.name.endswith("docx"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                    temp_docx.write(FileToConvert.read())
                    temp_docx_path = temp_docx.name

                temp_pdf_path = temp_docx_path.replace(".docx", ".pdf")
                convert(temp_docx_path, temp_pdf_path)

                with open(temp_pdf_path, 'rb') as pdf_file:
                    pdf_io = BytesIO(pdf_file.read())

                pdf_io.seek(0)
                os.remove(temp_docx_path)
                os.remove(temp_pdf_path)

                response = HttpResponse(pdf_io, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename={FileToConvert.name.replace(".docx", ".pdf")}'
                return response

            return JsonResponse({'file_id': file_id})
    else:
        form = UploadFileForm()
    return render(request, 'index.html', {'form': form, 'taille': poids})

def get_progress(request, file_id):
    progress = conversion_progress.get(file_id, 0)
    return JsonResponse({'progress': progress})
