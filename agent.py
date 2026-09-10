import sys
import os
import re
import ollama

# Ensure offline mode is enabled
from offline_guard import enable_offline_mode
enable_offline_mode()

# --- UI Helpers ---
def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==============================================")
    print("      Agent OTG - made by DWE team")
    print("==============================================\n")
    print("Type 'exit' or 'quit' to stop.\n")

# --- Routing Logic ---
from router import classify_prompt

# --- Main Loop ---
def main():
    print_header()
    
    # Read system prompt if exists
    system_prompt_text = "You are a helpful assistant."
    if os.path.exists("system-prompts.txt"):
        with open("system-prompts.txt", "r", encoding="utf-8") as f:
            system_prompt_text = f.read().strip()
    
    # Store simple conversation history
    history = [{"role": "system", "content": system_prompt_text}]
    
    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if user_input.strip().lower() in ["exit", "quit"]:
            break
            
        if not user_input.strip():
            continue
            
        images = []
        final_prompt = user_input
        
        if user_input.strip().lower().startswith('/image '):
            parts = user_input.strip().split(' ', 2)
            if len(parts) >= 2:
                img_path = parts[1].strip('\'"')
                if os.path.exists(img_path):
                    images.append(img_path)
                    final_prompt = parts[2] if len(parts) == 3 else "Describe this image."
                else:
                    print(f"\n[Error]: Image not found at '{img_path}'")
                    continue
            else:
                print("\n[Error]: Please provide an image path. Usage: /image <path> <question>")
                continue
                
        if images:
            history.append({"role": "user", "content": final_prompt, "images": images})
        else:
            history.append({"role": "user", "content": final_prompt})
        
        # Route to appropriate model based on original input
        model_type = classify_prompt(user_input)
        actual_model = model_type 
        
        print(f"\n[Routing to: {model_type} model]")
        print("Agent: ", end="", flush=True)
        
        full_response = ""
        try:
            # Stream the response using ollama
            stream = ollama.chat(
                model=actual_model,
                messages=history,
                stream=True,
            )
            
            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            
            print() # newline after response
            history.append({"role": "assistant", "content": full_response})
            
        except ollama.ResponseError as e:
            print(f"\n[Error from Ollama]: {e}")
            print(f"Please ensure the model '{actual_model}' is installed via 'ollama run {actual_model}'")
            # Remove the failed user prompt from history so it doesn't break future turns
            history.pop()
        except Exception as e:
            print(f"\n[Unexpected Error]: {e}")
            history.pop()

if __name__ == "__main__":
    main()
