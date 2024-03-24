import base64
import os
import requests
import time

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class AIUtils:

    def __init__(self):
        pass

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

    def images_to_markdown_text(self, image_urls):

        if not image_urls:
            return []

        # Execute initial request to retrieve 1. Account owner name 2. Portfolio value
        payload = self.__create_initial_request_for_account_info(image_urls[0])
        first_response = self.__make_api_request(payload).json()['choices'][0]['message']['content']
        print(first_response)

        payloads = []
        if len(image_urls) > 6:  # Break the requests into batches
            for i in range(1, len(image_urls), 6):
                batch_urls = image_urls[i:i + 6]
                payloads.append(self.__create_batch_request(batch_urls))
        else:
            payloads.append(self.__create_batch_request(image_urls))

        batch_response = self.__send_batch_requests(payloads)
        batch_response.insert(0, first_response)
        return batch_response

    @staticmethod
    def __create_initial_request_for_account_info(image_url):
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract 1. Account owner name 2. Portfolio value for the user in the file in "
                                    "form of a markdown text. Do not explain the output, just return it. Don't include "
                                    "any other data other than what is asked."
                        },
                        {
                            "type": "image_url",
                            "image_url": image_url
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        return payload
    
    @staticmethod
    def __make_api_request(payload):
        # Call OpenAI API to extract financial details
        api_key = os.getenv('API_KEY')
        open_ai_vision_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        try:
            response = requests.post(open_ai_vision_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for HTTP errors
        except requests.exceptions.HTTPError as err:
            if response.status_code == 500:
                print(f"Server encountered an error. Status code: {response.status_code}, Reason: {response.text}, "
                      f"error: {err}")
                return None
            else:
                print(f"HTTP Error occurred: {err}")
                return None
        except requests.exceptions.RequestException as err:
            print(f"Error during requests to openai: {err}")
            return None

        if response.ok:
            return response
        
    @staticmethod
    def __create_batch_request(image_urls):
        prompt = """
        Extract holdings data from Fidelity 1099 statement for the user.

        ---

        Fidelity 1099 Statement:

        Holdings:

        Please extract the holdings data from the Fidelity 1099 statement. The 
        extracted data should include the name of each holding,and the cost basis.
        
        Example Output:
        | Description | Quantity | Price Per Unit | Ending Value | Total Cost Basis | Unrealized Gain/Loss |
        |-------------|----------|----------------|--------------|------------------|----------------------|
        | DOUBLELINE TOTAL RETURN BOND FD CL I (DBLTX) | 1,015.328 | $11.190 | $11,361.52 | $7,536.91* | $3,824.61 |

        Instructions for OpenAI:

        Please analyze the provided Fidelity 1099 statement and extract the holdings data. Ensure that 
        the extracted data is accurate and formatted appropriately. Do not explain the output, just return it. 
        Convert tables to markdown tables. Don't include " "any other data other than what is asked."""
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
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

        return payload

    def __send_batch_requests(self, payloads, max_requests_per_minute=5, retry_attempts=3):
        delay = 60 / max_requests_per_minute  # Calculate delay between requests
        all_responses = []
        for payload in payloads:
            for attempt in range(retry_attempts):
                response = self.__make_api_request(payload)
                if response:
                    all_responses.append(response.json()['choices'][0]['message']['content'])
                    break  # Break out of retry loop if successful response
                else:
                    print(f"Retrying request {attempt + 1}/{retry_attempts}")
                    time.sleep(4 ** attempt)  # Exponential backoff for retries
            else:
                print("Request failed after multiple attempts.")
                continue  # Move to the next payload if request fails
            time.sleep(delay)  # Throttle requests to stay within OpenAI rate limit 
        return all_responses