from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import ollama
import json

# Ensure offline mode is enabled
from offline_guard import enable_offline_mode
enable_offline_mode()

from router import classify_prompt

app = FastAPI(title="Agent OTG", description="Simple routing agent API")

class AskRequest(BaseModel):
    prompt: str

def ollama_stream(model_name: str, prompt: str, images: list = None):
    """Generator to stream ollama responses to the client."""
    
    # Read system prompt if exists
    system_prompt_text = "You are a helpful assistant."
    import os
    if os.path.exists("system-prompts.txt"):
        with open("system-prompts.txt", "r", encoding="utf-8") as f:
            system_prompt_text = f.read().strip()
            
    try:
        messages = [
            {"role": "system", "content": system_prompt_text},
            {"role": "user", "content": prompt}
        ]
        
        if images:
            messages[1]["images"] = images
            
        stream = ollama.chat(
            model=model_name,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
    except ollama.ResponseError as e:
        yield f"\n[Error from Ollama]: {e}"
    except Exception as e:
        yield f"\n[Unexpected Error]: {e}"

@app.post("/ask")
async def ask_question(req: AskRequest):
    model_type = classify_prompt(req.prompt)
    
    images = None
    final_prompt = req.prompt
    
    if req.prompt.strip().lower().startswith('/image '):
        import os
        parts = req.prompt.strip().split(' ', 2)
        if len(parts) >= 2:
            img_path = parts[1].strip('\'"')
            if os.path.exists(img_path):
                images = [img_path]
                final_prompt = parts[2] if len(parts) == 3 else "Describe this image."
            else:
                return StreamingResponse(iter([f"[Error]: Image not found at '{img_path}'"]), media_type="text/plain")
    
    # Return a streaming response
    return StreamingResponse(
        ollama_stream(model_type, final_prompt, images),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
