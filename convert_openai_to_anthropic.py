import json


def convert_messages(messages: list):
    result = {}
    input_messages = []
    system_parts = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        # Claude không có role developer nên sẽ chuyển developer thành phần của system prompt có priority cao hơn system
        if role == "developer":
            # Developer có priority cao nhất -> thêm vào đầu với emphasis
            system_parts.insert(0, {"priority": "critical", "content": content})

        elif role == "system":
            # System message -> thêm vào sau developer
            system_parts.append({"priority": "normal", "content": content})

        elif role in ["user", "assistant"]:
            # Xử lý content string
            if isinstance(content, str):
                input_messages.append({"role": role, "content": content})

            # Xử lý content list (multi-modal)
            elif isinstance(content, list):
                content_blocks = []

                for block in content:
                    block_type = block.get("type")

                    # Xử lý text block
                    if block_type == "text":
                        content_blocks.append(
                            {"type": "text", "text": block.get("text", "")}
                        )

                    # Xử lý image_url
                    elif block_type == "image_url":
                        image_url_data = block.get("image_url", {})
                        url = (
                            image_url_data.get("url")
                            if isinstance(image_url_data, dict)
                            else image_url_data
                        )

                        # Kiểm tra xem là base64 hay URL
                        # Nếu là base64
                        if url and url.startswith("data:"):
                            # Format: data:image/jpeg;base64,<base64_data>
                            try:
                                media_type = url.split(";")[0].split(":")[1]
                                base64_data = url.split(",")[1]
                                content_blocks.append(
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": media_type,
                                            "data": base64_data,
                                        },
                                    }
                                )
                            except (IndexError, ValueError):
                                print(
                                    f"Warning: Invalid base64 image format: {url[:50]}..."
                                )
                        # Nếu là URL thông thường
                        else:
                            content_blocks.append(
                                {"type": "image", "source": {"type": "url", "url": url}}
                            )

                    # Xử lý image block
                    elif block_type == "image":
                        content_blocks.append(block)

                    # Các loại block khác
                    else:
                        content_blocks.append(block)

                if content_blocks:
                    input_messages.append({"role": role, "content": content_blocks})
        else:
            print(f"Warning: Unknown role '{role}' - skipping message")

    # Build system prompt
    if system_parts:
        system_prompt_parts = []

        # Thêm critical instructions (developer) trước
        critical_parts = [
            p["content"] for p in system_parts if p["priority"] == "critical"
        ]
        if critical_parts:
            system_prompt_parts.append(
                "CRITICAL INSTRUCTIONS (HIGHEST PRIORITY):\n"
                + "\n\n".join(critical_parts)
            )

        # Thêm normal instructions (system) sau
        normal_parts = [p["content"] for p in system_parts if p["priority"] == "normal"]
        if normal_parts:
            system_prompt_parts.append("\n\n".join(normal_parts))

        result["system"] = "\n\n---\n\n".join(system_prompt_parts)

    if input_messages:
        result["messages"] = input_messages

    return result


def convert_tools(tools: list):
    if not tools:
        return []

    result = []
    for tool in tools:
        if tool.get("type") == "function":
            function_def = tool.get("function", {})
            result.append(
                {
                    "name": function_def.get("name"),
                    "description": function_def.get("description"),
                    "input_schema": function_def.get("parameters"),
                }
            )
        else:
            result.append(tool)

    return result


def convert_structured_outputs(response_format: dict):
    if not response_format:
        return {}

    json_schema = response_format.get("json_schema", {})
    schema = json_schema.get("schema", {})

    return {"type": "json_schema", "schema": schema}


if __name__ == "__main__":
    print("=== Convert Messages OpenAI to Anthropic ===")
    print("\nChọn loại conversion:")
    print("1. Convert Messages")
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
        result = convert_messages(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif choice == "2":
        result = convert_tools(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif choice == "3":
        result = convert_structured_outputs(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
