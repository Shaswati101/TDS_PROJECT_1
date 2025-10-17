import os
import google.generativeai as genai

MODEL = "gemini-2.5-flash"

def configure_gemini():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=gemini_api_key)


def generate_html_code(user_prompt: str, attachments, checks) -> str:
    system_prompt = f"""
    You are an expert HTML, CSS, JS developer.
    Your task is to generate a complete, self-contained HTML File based on the user's request.

    **Constraints:**
    1. The output MUST be only raw html, css, js code.
    2. Do NOT include any markdown formatting (e.g., ```python).
    3. Do NOT include any explanatory text, comments, or conversation.
    4. The code must be a single, complete script that can be saved directly to a `index.html` file.
    5. The script must use the plain HTML, CSS, JS framework.
    6. Include all necessary imports.
    7. Consider Attachments from Attachments list if not empty as per user prompt and if its required for the task. 
    8. The user will test the generated code with list of 'checks' when it is executed. 
    9. It is important to generate the code so that give 'checks' should be passed in production.
    10. you can ignore all the checks that are not related to HTML, CSS, JS framework.
    11. The code should be well-formatted.

    **User Request:**
    "{user_prompt}"
    
    **Attachments:**
    "{attachments}"
    
    **Checks**
    "{checks}"

    **Generated HTML, CSS, JS Code:**
    """

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(system_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during Gemini code generation: {e}")
        raise


def generate_read_me(user_prompt: str, html) -> str:
    system_prompt = f"""
    You are an github repository manager.
    Your task is to add professional README.md for the project description and project html file.

    **Constraints:**
    1. The output MUST be only raw README.md content.
    2. Do NOT include any conversation.
    3. The content must be a single, complete script that can be saved directly to a `README.md` file.
    
    **User Prompt:**
    "{user_prompt}"

    ** html file:**
    "{html}"
    """

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(system_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during Gemini code generation: {e}")
        raise


def generate_updated_html_code(code_prompt, existing_code, attachments, checks):
    system_prompt = f"""
        You are an expert HTML, CSS, JS developer.
        Your task is to update given self-contained HTML File based on the user's request.

        **Constraints:**
        1. The output MUST be only raw html, css, js code.
        2. Do NOT include any markdown formatting (e.g., ```python).
        3. Do NOT include any explanatory text, comments, or conversation.
        4. The code must be a single, complete script that can be saved directly to a `index.html` file.
        5. The script must use the plain HTML, CSS, JS.
        6. Include all necessary imports.
        7. Consider Attachments from Attachments list if not empty as per user prompt and if its required for the task. 
        8. The user will test the generated code with list of 'checks' when it is executed. 
        9. It is important to generate the code so that give 'checks' should be passed in production.
        10. you can ignore all the checks that are not related to HTML, CSS, JS framework.
        11. The code should be well-formatted.
        
        **Existing Code:**
        "{existing_code}"

        **User Request:**
        "{code_prompt}"

        **Attachments:**
        "{attachments}"
        
        **Checks**
        "{checks}"

        **Generated HTML, CSS, JS Code:**
        """

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(system_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during Gemini code generation: {e}")
        raise


def generate_updated_read_me(code_prompt, existing_readme, updated_code):
    system_prompt = f"""
       You are an github repository manager.
       Your task is to update existing professional README.md file to also include new changes for updated html code.

       **Constraints:**
       1. The output MUST be only raw README.md content.
       2. Do NOT include any conversation.
       3. The content must be a single, complete script that can be saved directly to a `README.md` file.
       
       **Existing Readme:**
       "{existing_readme}"

       **User Prompt for update:**
       "{code_prompt}"

       **updated html file:**
       "{updated_code}"
       """

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(system_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during Gemini code generation: {e}")
        raise