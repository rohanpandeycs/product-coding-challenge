import base64
import os
import requests

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class AIUtils:
    @staticmethod
    def encode_images_to_base64(saved_image_paths):
        # List to store the image URLs
        image_urls = []

        # Iterate over each image path
        for image_path in saved_image_paths:
            # Read the image data from the file
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()

            # Encode the image data to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # Construct the image URL
            image_url = f"data:image/jpeg;base64,{base64_image}"

            # Append the image URL to the list
            image_urls.append({'url': image_url})

        return image_urls

    @staticmethod
    def images_to_markdown_text(image_urls):
        # Call OpenAI API to extract financial details
        api_key = os.getenv('API_KEY')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        # To cut payload costs, we can lower image definition using parameters, but this may reduce model accuracy.
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract 1. Account owner name 2. Portfolio value for the user in the file in "
                                    "form of a markdown text. Now retrieve Name and cost basis of each page "
                                    "containing holdings for this user from images which contains holding into "
                                    "single tabular view. Do not explain the output, just return it. Include all "
                                    "holding rows and don't miss. Convert tables to markdown tables. Don't include "
                                    "any other data other than what is asked."
                        }
                    ]
                }
            ],
            "max_tokens": 1200
        }

        # Add the image URLs to the payload
        for image_url in image_urls:
            payload['messages'][0]['content'].append({
                "type": "image_url",
                "image_url": image_url
            })
        try:
             response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
             response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 500:
                print(f"Server encountered an error. Status code: {response.status_code}, Reason: {response.text}")
            else:
                print(f"HTTP Error occurred: {err}")
        except requests.exceptions.RequestException as e:
            # For non-HTTP errors like connection errors
            print(f"Error during requests to openai: {e}")
        
        if response.ok:
            return response.json()['choices'][0]['message']['content']
