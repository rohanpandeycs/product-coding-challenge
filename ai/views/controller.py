from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pdf2image import convert_from_bytes
from ..utils.PDFUtils import PDFUtils
from ..utils.AIUtils import AIUtils


@csrf_exempt  # This decorator is used to exempt CSRF verification for this view.
def extract_financial_details(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf_file = request.FILES['pdf']
        # Create an instance of the class
        ai_util = AIUtils()
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_file.read(), dpi=200, fmt='jpeg')
            saved_image_paths = PDFUtils.save_images(images)
            image_urls = ai_util.encode_images_to_base64(saved_image_paths)
            content = ai_util.images_to_markdown_text(image_urls)
            PDFUtils.output_to_folder(content)  # write to file

            return JsonResponse({'financial_summary': content})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Please provide a PDF file using POST request.'}, status=405)