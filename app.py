from flask import Flask, render_template, request, send_file, flash
import os
from werkzeug.utils import secure_filename
from test import process_csv
from pathlib import Path
import urllib.parse

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flashing messages

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename_with_unicode(filename):
    # Keep Chinese characters while removing potentially dangerous characters
    # Get the name and extension
    name, ext = os.path.splitext(filename)
    # Replace dangerous characters but keep Chinese characters
    safe_name = "".join(c for c in name if c.isalnum() or c.isspace() or ord(c) > 127)
    return f"{safe_name}{ext}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return render_template('upload.html')
        
        file = request.files['file']
        
        # If no file selected
        if file.filename == '':
            flash('No file selected')
            return render_template('upload.html')
        
        if file and allowed_file(file.filename):
            # Secure the filename while preserving Chinese characters
            filename = secure_filename_with_unicode(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the uploaded file
            file.save(filepath)
            
            try:
                # Process the CSV file
                process_csv(filepath)
                
                # Generate the processed filename
                processed_filepath = str(Path(filepath).parent / f"{Path(filepath).stem}new{Path(filepath).suffix}")
                
                if os.path.exists(processed_filepath):
                    # Return the processed file with proper encoding in filename
                    return send_file(
                        processed_filepath,
                        as_attachment=True,
                        download_name=f"{Path(filepath).stem}new{Path(filepath).suffix}",
                        mimetype='text/csv'
                    )
                else:
                    flash('Error processing file')
            except Exception as e:
                flash(f'Error: {str(e)}')
            finally:
                # Clean up uploaded and processed files
                if os.path.exists(filepath):
                    os.remove(filepath)
                if os.path.exists(processed_filepath):
                    os.remove(processed_filepath)
        else:
            flash('Invalid file type. Please upload a CSV file.')
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True) 