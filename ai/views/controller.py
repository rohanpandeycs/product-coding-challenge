from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pdf2image import convert_from_bytes
from ..utils.PDFUtils import PDFUtils
from ..utils.AIUtils import AIUtils


@csrf_exempt  # This decorator is used to exempt CSRF verification for this view. Be cautious when using it.
def extract_financial_details(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf_file = request.FILES['pdf']
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_file.read(), dpi=200, fmt='jpeg')
            saved_image_paths = PDFUtils.save_images(images)
            image_urls = AIUtils.encode_images_to_base64(saved_image_paths)
            concatenated_content = ""
            if len(image_urls) > 10:
                for i in range(0, len(image_urls), 10):
                    batch_urls = image_urls[i:i+10]
                    print(f"Performing request {i-10} to openAi")
                    content = AIUtils.images_to_markdown_text(batch_urls)
                    concatenated_content += content
            else:
                content = AIUtils.images_to_markdown_text(image_urls)
            PDFUtils.output_to_folder(concatenated_content)  # write to file
            content=concatenated_content
            return JsonResponse({'financial_summary': content})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Please provide a PDF file using POST request.'}, status=405)