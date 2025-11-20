from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from analyze import run_analysis

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/outputs'
ALLOWED_EXT = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return render_template('index.html', error="Please upload a CSV file.")
        if not allowed_file(file.filename):
            return render_template('index.html', error="Only CSV files are allowed.")
        fname = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        file.save(upload_path)

        # clear previous outputs
        for f in os.listdir(app.config['OUTPUT_FOLDER']):
            os.remove(os.path.join(app.config['OUTPUT_FOLDER'], f))

        # Run analysis (creates PNG files in OUTPUT_FOLDER, returns summary dict)
        summary = run_analysis(upload_path, app.config['OUTPUT_FOLDER'])

        # list generated images (for display)
        images = sorted([f for f in os.listdir(app.config['OUTPUT_FOLDER']) if f.lower().endswith('.png')])
        images = [url_for('static', filename=f'outputs/{img}') for img in images]

        return render_template('results.html', images=images, summary=summary)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
