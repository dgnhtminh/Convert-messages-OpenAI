from openai import OpenAI
import os
import base64

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # File URL
response = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Phân tích bức thư và tóm tắt ngắn gọn những điểm chính.",
                },
                {
                    "type": "input_file",
                    "file_url": "https://www.berkshirehathaway.com/letters/2024ltr.pdf",
                },
            ],
        },
    ],
)

print(response.output_text)


# # Uploading files
# file = client.files.create(file=open("file.pdf", "rb"), purpose="user_data")

# print("File ID:", file.id)

# response = client.responses.create(
#     model="gpt-5",
#     input=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "input_file",
#                     "file_id": file.id,
#                 },
#                 {
#                     "type": "input_text",
#                     "text": "Trong file có bao nhiêu câu hỏi lý thuyết và bao nhiêu câu hỏi bài tập?",
#                 },
#             ],
#         }
#     ],
# )

# print(response.output_text)


# # Base64
# with open("file.pdf", "rb") as f:
#     data = f.read()

# base64_string = base64.b64encode(data).decode("utf-8")

# response = client.responses.create(
#     model="gpt-5",
#     input=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "input_file",
#                     "filename": "file.pdf",
#                     "file_data": f"data:application/pdf;base64,{base64_string}",
#                 },
#                 {
#                     "type": "input_text",
#                     "text": "Trong file có bao nhiêu câu hỏi lý thuyết và bao nhiêu câu hỏi bài tập?",
#                 },
#             ],
#         },
#     ],
# )

# print(response.output_text)
