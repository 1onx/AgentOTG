import re

# --- Configuration ---
CODER_MODEL_NAME = "qwen2.5-coder:latest" 
MAIN_MODEL_NAME = "qwen2.5:7b"
VISION_MODEL_NAME = "qwen2.5vl:7b"

# --- Advanced Regex Routing ---

def is_coding_prompt(prompt: str) -> bool:
    """
    Uses heavy regex to determine if a prompt is related to coding, scripting, or software engineering.
    """
    prompt = prompt.lower()
    
    # Regex 1: Explicit code blocks or backticks (e.g. ```python, `var x`)
    if re.search(r"```[a-z]*", prompt) or re.search(r"`[^`]+`", prompt):
        return True
    
    # Regex 2: Common programming languages and frameworks
    languages_regex = r"\b(python|javascript|typescript|java|c\+\+|cpp|c#|csharp|go|golang|rust|php|ruby|swift|kotlin|dart|r|bash|shell|powershell|html|css|sql|react|vue|angular|svelte|node\.js|express|django|flask|fastapi|spring|laravel)\b"
    if re.search(languages_regex, prompt):
        return True
        
    # Regex 3: Engineering terminology (functions, loops, classes, apis)
    engineering_terms = r"\b(function|method|class|struct|interface|variable|array|list|dict|dictionary|object|loop|for loop|while loop|if statement|switch statement|async|await|promise|callback|api|endpoint|json|xml|yaml|regex|regular expression|database|query|table|row|column)\b"
    if re.search(engineering_terms, prompt):
        return True
        
    # Regex 4: Action verbs paired with coding concepts
    action_coding = r"\b(write|create|build|develop|implement|debug|fix|refactor|optimize|test|compile|deploy)\s+(a|an|the|my)?\s*(script|program|app|application|code|function|class|api|bot|server|website|page|component)\b"
    if re.search(action_coding, prompt):
        return True
        
    # Regex 5: Error and debugging language
    error_regex = r"\b(error|exception|stacktrace|traceback|bug|crash|segfault|null pointer|undefined|typeerror|valueerror|syntaxerror|runtime|compile time|compilation failed)\b"
    if re.search(error_regex, prompt):
        return True

    return False


def classify_prompt(prompt: str) -> str:
    """
    Classifies a user prompt and returns the name of the model to be used.
    If it starts with /image, it routes to the vision model.
    If it passes any of the complex coding regexes, it goes to CODER_MODEL.
    Otherwise, it falls back to the general MAIN_MODEL.
    """
    if prompt.strip().lower().startswith('/image'):
        return VISION_MODEL_NAME
        
    if is_coding_prompt(prompt):
        return CODER_MODEL_NAME
        
    # Default fallback for everything else
    return MAIN_MODEL_NAME
