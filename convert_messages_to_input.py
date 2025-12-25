import json


def convert_messages_to_input(messages: list):
    result = {}
    input_messages = []

    for msg in messages:
        role = msg.get("role")
        if role == "system":
            result["instructions"] = msg.get("content")
        elif role in ["user", "assistant", "developer"]:
            # Xử lý với TH content chỉ là string
            if isinstance(msg.get("content"), str):
                input_messages.append({"role": role, "content": msg.get("content")})
            # Xử lý với TH content là list
            elif isinstance(msg.get("content"), list):
                content_blocks = []
                for block in msg.get("content"):
                    block_type = block.get("type")
                    # Xử lý với text
                    if block_type == "text":
                        content_blocks.append(
                            {"type": "input_text", "text": block.get("text")}
                        )
                    # Xử lý với image_url thông thường và base64
                    elif block_type == "image_url":
                        content_blocks.append(
                            {
                                "type": "input_image",
                                "image_url": block.get("image_url").get("url"),
                            }
                        )
                    # Xử lý với image
                    elif block_type == "image":
                        content_blocks.append(
                            {"type": "input_image", "image": block.get("image")}
                        )
                    # Các loại block khác giữ nguyên
                    else:
                        content_blocks.append(block)
                input_messages.append({"role": role, "content": content_blocks})

    if input_messages:
        result["input"] = input_messages

    return result


def convert_structured_outputs(response_format: dict):
    if not response_format:
        return {}

    json_schema = response_format.get("json_schema", {})

    result_format = {"type": "json_schema"}
    result_format.update(json_schema)

    return {"format": result_format}


def convert_tools(tools: list):
    if not tools:
        return []

    result = []
    for tool in tools:
        if tool.get("type") == "function":
            function_def = tool.get("function", {})
            result.append(
                {
                    "type": "function",
                    "name": function_def.get("name"),
                    "description": function_def.get("description"),
                    "parameters": function_def.get("parameters"),
                }
            )
        else:
            result.append(tool)

    return result


if __name__ == "__main__":
    print("=== Convert Chat Completions to Responses ===")
    print("\nChọn loại conversion:")
    print("1. Convert Messages to Input")
    print("2. Convert Tools")
    print("3. Convert Structured Outputs (Response Format)")

    choice = input("\nNhập lựa chọn của bạn (1-3): ").strip()

    print("\nNhập JSON input messages:")
    print("Ví dụ:")

    if choice == "1":
        print(
            '[{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "Hello"}]'
        )
    elif choice == "2":
        print(
            '[{"type": "function", "function": {"name": "get_weather", "description": "Get weather", "parameters": {...}}}]'
        )
    elif choice == "3":
        print(
            '{"type": "json_schema", "json_schema": {"name": "person", "strict": true, "schema": {...}}}'
        )
    else:
        print("Lựa chọn không hợp lệ!")
        exit(1)

    print("\nNhập JSON của bạn:")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)

    json_input = "\n".join(lines)

    # Tự động chuyển Python syntax sang JSON syntax
    json_input = (
        json_input.replace("True", "true")
        .replace("False", "false")
        .replace("None", "null")
    )

    try:
        data = json.loads(json_input)
    except json.JSONDecodeError as e:
        # Loại bỏ dấu phẩy dư thừa
        import re

        json_input_cleaned = re.sub(r",(\s*[}\]])", r"\1", json_input)
        try:
            data = json.loads(json_input_cleaned)
            print("(Đã tự động loại bỏ dấu phẩy dư thừa)")
        except json.JSONDecodeError:
            print(f"\nLỗi parse JSON: {e}")
            print("\nLưu ý: JSON chuẩn yêu cầu:")
            print("  - true/false/null (viết thường)")
            print("  - Không có dấu phẩy thừa sau phần tử cuối cùng")
            exit(1)

    print("\n=== Kết quả convert ===")

    if choice == "1":
        result = convert_messages_to_input(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif choice == "2":
        result = convert_tools(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif choice == "3":
        result = convert_structured_outputs(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
