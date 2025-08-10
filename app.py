import os
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import difflib # Import difflib for comparison

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey_for_flash_messages'  # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

GEMINI_MODELS = [
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash-001", 
    "gemini-2.5-flash",

    # Add other models you might want to test
]

def generate_diff_html(text1, text2):
    """Generates HTML with highlighted differences between two texts.
    text1 is considered the 'expected' or 'base' for diffing (removed lines are from text1).
    text2 is considered the 'actual' or 'new' for diffing (added lines are from text2).
    """
    d = difflib.Differ()
    diff = list(d.compare(text1.splitlines(keepends=True), text2.splitlines(keepends=True)))
    
    html_diff = []
    for line in diff:
        if line.startswith('+ '):
            html_diff.append(f'<span class="diff-added">{line}</span>')
        elif line.startswith('- '):
            html_diff.append(f'<span class="diff-removed">{line}</span>')
        elif line.startswith('? '):
            # This line indicates intra-line changes, we'll just show it for context
            html_diff.append(f'<span class="diff-info">{line}</span>')
        else:
            html_diff.append(f'<span>{line}</span>')
    return '<pre>' + ''.join(html_diff) + '</pre>'


@app.route('/', methods=['GET', 'POST'])
def index():
    results_table_data = [] 
    selected_model = request.form.get('gemini_model', "gemini-pro") 

    if request.method == 'POST':
        api_key = request.form.get('api_key')
        selected_model = request.form.get('gemini_model') 

        if not api_key:
            flash('Please set your Gemini API Key.', 'error')
            return redirect(request.url)

        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            flash(f"Error configuring Gemini API: {e}", 'error')
            return redirect(request.url)

        # --- Handle two system message files ---
        system_message_1 = None
        if 'system_message_file_1' in request.files:
            system_file_1 = request.files['system_message_file_1']
            if system_file_1 and allowed_file(system_file_1.filename):
                filename_1 = secure_filename(system_file_1.filename)
                filepath_1 = os.path.join(app.config['UPLOAD_FOLDER'], filename_1)
                system_file_1.save(filepath_1)
                with open(filepath_1, 'r', encoding='utf-8') as f:
                    system_message_1 = f.read()
            elif system_file_1.filename != '':
                flash('Invalid file type for System Message 1. Only .txt allowed.', 'error')
                return redirect(request.url)
        
        system_message_2 = None
        if 'system_message_file_2' in request.files:
            system_file_2 = request.files['system_message_file_2']
            if system_file_2 and allowed_file(system_file_2.filename):
                filename_2 = secure_filename(system_file_2.filename)
                filepath_2 = os.path.join(app.config['UPLOAD_FOLDER'], filename_2)
                system_file_2.save(filepath_2)
                with open(filepath_2, 'r', encoding='utf-8') as f:
                    system_message_2 = f.read()
            elif system_file_2.filename != '':
                flash('Invalid file type for System Message 2. Only .txt allowed.', 'error')
                return redirect(request.url)

        if not system_message_1 or not system_message_2:
            flash('Please upload both System Message 1 and System Message 2 files.', 'error')
            return redirect(request.url)

        # Process input files
        input_files_list = request.files.getlist('input_message_files')

        if not input_files_list:
            flash('Please upload at least one input message file.', 'error')
            return redirect(request.url)
        
        # Read input file contents
        raw_input_messages = []
        for input_file in input_files_list:
            if input_file and allowed_file(input_file.filename):
                input_filename = secure_filename(input_file.filename)
                input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
                input_file.save(input_filepath)
                with open(input_filepath, 'r', encoding='utf-8') as f:
                    raw_input_messages.append(f.read())
            elif input_file.filename != '':
                flash(f'Invalid file type for input message: {input_file.filename}. Only .txt allowed.', 'error')
                return redirect(request.url)

        try:
            temperature = float(request.form.get('temperature', 1.0))
            top_p = float(request.form.get('top_p', 0.95))
            top_k = int(request.form.get('top_k', 40))
        except ValueError:
            flash('Invalid value for temperature, top_p, or top_k. Please enter numbers.', 'error')
            return redirect(request.url)

        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": 8192,
        }

        try:
            model = genai.GenerativeModel(model_name=selected_model)
        except Exception as e:
            flash(f"Error initializing Gemini model '{selected_model}': {e}", 'error')
            return redirect(request.url)

        # --- Run each input against both system prompts and compare ---
        for input_content in raw_input_messages:
            output_sys1_content = ""
            output_sys2_content = ""
            comparison_diff_html = ""
            status = "Error" # Default status

            try:
                # Run with System Prompt 1
                chat_sys1 = model.start_chat(history=[
                    {"role": "user", "parts": [system_message_1]},
                    {"role": "model", "parts": ["Understood."]} 
                ])
                response_sys1 = chat_sys1.send_message(input_content, generation_config=generation_config)
                output_sys1_content = response_sys1.text

                # Run with System Prompt 2
                chat_sys2 = model.start_chat(history=[
                    {"role": "user", "parts": [system_message_2]},
                    {"role": "model", "parts": ["Understood."]} 
                ])
                response_sys2 = chat_sys2.send_message(input_content, generation_config=generation_config)
                output_sys2_content = response_sys2.text

                # Compare the two outputs
                if output_sys1_content.strip() == output_sys2_content.strip():
                    status = "Match"
                    comparison_diff_html = '<span class="diff-match">Outputs Match!</span>'
                else:
                    status = "Mismatch"
                    # Compare output_sys1_content (base) with output_sys2_content (new)
                    comparison_diff_html = generate_diff_html(output_sys1_content, output_sys2_content)

            except Exception as e:
                flash(f"Error processing input: '{input_content[:50]}...' - {e}", 'error')
                output_sys1_content = f"Error: {e}"
                output_sys2_content = f"Error: {e}"
                comparison_diff_html = '<span class="diff-error">Error during generation or comparison.</span>'
            
            results_table_data.append({
                "input_content": input_content,
                "output_sys1_content": output_sys1_content,
                "output_sys2_content": output_sys2_content,
                "comparison_diff_html": comparison_diff_html,
                "status": status
            })

    return render_template('index.html', 
                           results_table_data=results_table_data, 
                           gemini_models=GEMINI_MODELS, 
                           selected_model=selected_model)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
