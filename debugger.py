import subprocess
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables!")


genai.configure(api_key=api_key)

def run_cpp_code(code: str):
    with open("program.cpp", "w") as f:
        f.write(code)

   
    exe_file = "program.exe" if os.name == "nt" else "program.out"

   
    compile_process = subprocess.run(
        ["g++", "program.cpp", "-o", exe_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if compile_process.returncode != 0:
        return None, compile_process.stderr  
    else:
        
        run_process = subprocess.run(
            [exe_file] if os.name == "nt" else ["./" + exe_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return run_process.stdout, run_process.stderr



def ask_gemini_to_debug(code, error):
    prompt = f"""
    The following C++ code has an error.

    Code:
    {code}

    Error:
    {error}

    👉 Explain the error clearly and suggest a corrected version of the code.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":
    
    cpp_code = """
    #include <iostream>
    using namespace std;
    int main() {
        cout << "Hello World"
        return 0;
    }
    """

    output, error = run_cpp_code(cpp_code)

    if error:
        print("❌ Compilation/Runtime Error:\n", error)
        suggestion = ask_gemini_to_debug(cpp_code, error)
        print("\n🤖 Gemini Debugger Suggestion:\n", suggestion)
    else:
        if output.strip():
            print("✅ Program Output:\n", output)
        else:
            print("✅ Program ran successfully with no output.")
