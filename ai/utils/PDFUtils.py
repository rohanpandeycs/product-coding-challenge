import os
from pathlib import Path


class PDFUtils:

    @staticmethod
    def save_images(images):
        # Create a directory to save the images
        current_directory = os.path.dirname(os.path.abspath(__file__))
        save_dir = os.path.join(current_directory, '..', 'output', 'PdfToImages')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save each image to the directory
        saved_image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(save_dir, f'image_{i}.jpeg')
            image.save(image_path, 'JPEG')
            saved_image_paths.append(image_path)
            print(f"Page {i + 1} saved as image: {image_path}")
        return saved_image_paths

    @staticmethod
    def output_to_folder(markdown_content):
        # Create a directory to save the images
        current_directory = os.path.dirname(os.path.abspath(__file__))
        save_dir = os.path.join(current_directory, '..', 'output', 'OutputMarkDown')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        output_path = Path(save_dir) / f"financial_summary.md"
        with open(output_path, 'w') as f:
            for content in markdown_content:
                f.write(content)
        print(f"Financial summary saved to {output_path}")
