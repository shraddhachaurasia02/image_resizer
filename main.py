from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import cv2

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Required for flashing messages

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

def process_image(filename, format, scale):
    try:
        # Construct the image path
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img = cv2.imread(img_path)

        if img is None:
            flash('Error: Image could not be loaded')
            return None

        # Convert to grayscale if the format is "cgray"
        if format == "cgray":
            imgprocessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            extension = filename.split('.')[-1].lower()
        else:
            imgprocessed = img
            extension = format.lower()

        # Ensure that the new format is one of the allowed formats
        if extension not in ALLOWED_EXTENSIONS:
            flash(f'Error: Unsupported format "{extension}"')
            return None

        # Resize the image if scale is provided
        if scale:
            scale = float(scale)
            width = int(imgprocessed.shape[1] * (scale / 100))
            height = int(imgprocessed.shape[0] * (scale / 100))
            imgprocessed = cv2.resize(imgprocessed, (width, height))

        # Construct the new filename with the correct extension
        new_filename = filename.split('.')[0] + '.' + extension

        # Save the processed image
        new_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        result = cv2.imwrite(new_filepath, imgprocessed)

        if result:
            flash(f'Image successfully processed and saved as {new_filename}')
            return new_filename  # Return the new filename for downloading
        else:
            flash(f'Error: Could not save image as {new_filename}')
            return None

    except Exception as e:
        flash(f'Error: {str(e)}')
        return None


@app.route('/upload', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        format = request.form.get("format")
        scale = request.form.get("scale")
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('home'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            new_filename = process_image(filename, format, scale)
            return render_template("index.html", new_filename=new_filename)
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)

