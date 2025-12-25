from openai import OpenAI
import os
import base64

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image = encode_image("./anh_troi_mua.jpg")


# Upload image file to get file ID
def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result.id


file_id = create_file("anh_troi_mua.jpg")


input_messages = [
    {
        "role": "user",
        "content": [
            # # image URL
            {"type": "input_text", "text": "Mô tả ngắn gọn bức ảnh này"},
            {
                "type": "input_image",
                "image_url": "https://tse3.mm.bing.net/th/id/OIP._EB0pGhVR69V-nZ83-9VbAHaEs?cb=ucfimg2&ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3",
            },
            # # Base64 image
            # {
            #     "type": "input_image",
            #     "image_url": f"data:image/jpeg;base64,{base64_image}"
            # },
            # # File ID image
            # {
            #     "type": "input_image",
            #     "file_id": file_id,
            # },
        ],
    }
]

response = client.responses.create(model="gpt-4o-mini", input=input_messages)

print(response.output_text)
