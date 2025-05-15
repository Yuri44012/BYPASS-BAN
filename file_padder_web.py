from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_FORM = """
<!doctype html>
<html>
<head>
  <title>File Padder</title>
  <style>
    .dropzone {
      border: 2px dashed #ccc;
      padding: 30px;
      text-align: center;
      margin-bottom: 20px;
    }
    #progressBar {
      width: 100%%;
      background: #eee;
    }
    #progressBar div {
      height: 20px;
      width: 0;
      background: green;
      text-align: center;
      color: white;
    }
    #downloadLink {
      display: none;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <h2>Upload File and Set Target Size</h2>
  <div class="dropzone" id="dropzone">Drop file here or click to upload</div>
  <input type="file" id="fileInput" style="display: none;">
  <br>
  Target Size (MB): <input type="text" id="size_mb"><br><br>
  <button onclick="uploadFile()">Upload</button>
  <div id="progressBar"><div></div></div>
  <a id="downloadLink" href="#" download>Download Modified File</a>
  <script>
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const downloadLink = document.getElementById('downloadLink');
    let selectedFile;

    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', e => {
      e.preventDefault();
      dropzone.style.borderColor = 'green';
    });
    dropzone.addEventListener('dragleave', () => {
      dropzone.style.borderColor = '#ccc';
    });
    dropzone.addEventListener('drop', e => {
      e.preventDefault();
      selectedFile = e.dataTransfer.files[0];
      dropzone.textContent = selectedFile.name;
    });
    fileInput.addEventListener('change', e => {
      selectedFile = e.target.files[0];
      dropzone.textContent = selectedFile.name;
    });

    function uploadFile() {
      const sizeMb = document.getElementById('size_mb').value;
      if (!selectedFile || !sizeMb) {
        alert('Please select a file and enter a size.');
        return;
      }
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('size_mb', sizeMb);

      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/', true);
      xhr.responseType = 'blob';

      xhr.upload.onprogress = function(e) {
        const percent = (e.loaded / e.total) * 100;
        document.querySelector('#progressBar div').style.width = percent + '%';
        document.querySelector('#progressBar div').textContent = Math.floor(percent) + '%';
      };

      xhr.onload = function() {
        if (xhr.status === 200) {
          const blob = new Blob([xhr.response]);
          const url = window.URL.createObjectURL(blob);
          downloadLink.href = url;
          downloadLink.download = selectedFile.name;
          downloadLink.style.display = 'inline-block';
          downloadLink.textContent = 'Download ' + selectedFile.name;
        } else {
          alert('Error uploading file.');
        }
      };
      xhr.send(formData);
    }
  </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        size_mb = request.form.get('size_mb')

        if not file or not size_mb:
            return "Invalid file or size."

        try:
            size_mb = float(size_mb)
        except ValueError:
            return "Size must be a number."

        if size_mb <= 0:
            return "Size must be greater than zero."

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        target_bytes = int(size_mb * 1024 * 1024)
        current_size = os.path.getsize(filepath)
        padding_needed = target_bytes - current_size

        if padding_needed > 0:
            with open(filepath, 'ab') as f:
                f.write(b"\x00" * padding_needed)

        return send_file(filepath, as_attachment=True)

    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True)
