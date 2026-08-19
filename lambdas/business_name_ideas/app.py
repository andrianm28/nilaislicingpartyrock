import json
import os
import boto3
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
REGION = os.environ.get("AWS_REGION", "ap-southeast-5")

bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)


def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST,OPTIONS"
    return response


@app.route("/generate", methods=["OPTIONS"])
def options():
    resp = Response("", status=200)
    return add_cors_headers(resp)


@app.route("/generate", methods=["POST"])
def generate_names():
    data = request.get_json(force=True)

    industry = data.get("industry", "")
    name_style = data.get("name_style", "Modern")
    keywords = data.get("keywords", "")

    prompt = f"""You are a branding expert and creative naming consultant. A user wants business name ideas with the following details:

Industry or Business Type: {industry}
Keywords or Themes: {keywords}
Desired Name Style: {name_style}

Generate exactly 10 creative, unique, and memorable business names tailored to their industry and style preference. Incorporate the provided keywords or themes where relevant. For each name, provide a brief 1-2 sentence explanation of why it works — covering the meaning, tone, and appeal. Format the output as a numbered list. Aim for variety: mix short punchy names, compound words, invented words, and evocative phrases."""

    # Build messages
    messages = []

    # Handle file upload if present
    content_blocks = []
    file_data = data.get("file_data")
    file_mime = data.get("file_mime")

    if file_data and file_mime:
        if file_mime.startswith("image/"):
            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": file_mime,
                    "data": file_data
                }
            })
        else:
            content_blocks.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": file_mime,
                    "data": file_data
                }
            })

    content_blocks.append({"type": "text", "text": prompt})
    messages.append({"role": "user", "content": content_blocks})

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": messages
    })

    def generate():
        try:
            response = bedrock_runtime.invoke_model_with_response_stream(
                modelId=BEDROCK_MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=body
            )

            for event in response["body"]:
                chunk = event.get("chunk")
                if chunk:
                    chunk_data = json.loads(chunk["bytes"].decode("utf-8"))
                    if chunk_data.get("type") == "content_block_delta":
                        delta = chunk_data.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield delta.get("text", "")
        except Exception as e:
            yield f"\n\nError: {str(e)}"

    resp = Response(stream_with_context(generate()), content_type="text/plain; charset=utf-8")
    return add_cors_headers(resp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
