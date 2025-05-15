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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    body {
      margin: 0;
      font-family: 'Poppins', sans-serif;
      background: #121014;
      color: #ddd;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
      min-height: 100vh;
    }
    h2 {
      color: #b58cff;
      text-shadow: 0 0 10px #9b59b6;
      margin-bottom: 30px;
    }
    .dropzone {
      border: 3px dashed #b58cff;
      border-radius: 12px;
      padding: 40px;
      text-align: center;
      margin-bottom: 25px;
      font-weight: 600;
      font-size: 1.2rem;
      color: #b58cff;
      cursor: pointer;
      background: #1e172f;
      transition: border-color 0.4s ease, box-shadow 0.4s ease;
      user-select: none;
      animation: pulse 3s ease-in-out infinite;
    }
    .dropzone:hover {
      border-color: #9b59b6;
      box-shadow: 0 0 15px #9b59b6;
      animation-play-state: paused;
    }
    @keyframes pulse {
      0%, 100% {
        box-shadow: 0 0 15px #b58cff55;
      }
      50% {
        box-shadow: 0 0 30px #b58cffaa;
      }
    }
    #progressBar {
      width: 100%;
      background: #2c2540;
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 20px;
      height: 22px;
      box-shadow: inset 0 0 8px #000;
    }
    #progressBar div {
      height: 100%;
      width: 0;
      background: linear-gradient(90deg, #b58cff, #9b59b6);
      text-align: center;
      color: white;
      font-weight: 600;
      line-height: 22px;
      transition: width 0.3s ease;
      box-shadow: 0 0 8px #9b59b6;
    }
    input[type="text"] {
      padding: 10px 15px;
      border-radius: 8px;
      border: none;
      font-size: 1rem;
      width: 150px;
      background: #2c2540;
      color: #ddd;
      box-shadow: inset 0 0 5px #000;
      margin-left: 10px;
      transition: box-shadow 0.3s ease;
    }
    input[type="text"]:focus {
      outline: none;
      box-shadow: 0 0 12px #9b59b6;
      background: #3a2e5c;
    }
    button {
      background: #b58cff;
      border: none;
      color: #121014;
      padding: 12px 30px;
      font-size: 1.1rem;
      font-weight: 700;
      border-radius: 12px;
      cursor: pointer;
      box-shadow: 0 0 12px #b58cff;
      transition: background 0.4s ease, box-shadow 0.4s ease;
      user-select: none;
    }
    button:hover {
      background: #9b59b6;
      box-shadow: 0 0 20px #9b59b6;
    }
    #downloadLink {
      display: none;
      margin-top: 25px;
      color: #b58cff;
      font-weight: 700;
      font-size: 1.1rem;
      text-decoration: none;
      box-shadow: 0 0 12px #b58cff;
      padding: 10px 25px;
      border-radius: 12px;
      background: #1e172f;
      transition: background 0.3s ease, box-shadow 0.3s ease;
    }
    #downloadLink:hover {
      background: #3a2e5c;
      box-shadow: 0 0 25px #9b59b6;
    }
  </style>
</head>
<body>
  <h2>Upload File and Set Target Size</h2>
  <div class="dropzone" id="dropzone">Drop file here or click to upload</div>
  <input type="file" id="fileInput" style="display: none;">
  <br>
  Target Size (MB):
  <input type="text" id="size_mb" placeholder="Enter size in MB"><br><br>
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
      dropzone.style.borderColor = '#9b59b6';
      dropzone.style.boxShadow = '0 0 25px #9b59b6';
    });
    dropzone.addEventListener('dragleave', () => {
      dropzone.style.borderColor = '#b58cff';
      dropzone.style.boxShadow = 'none';
    });
    dropzone.addEventListener('drop', e => {
      e.preventDefault();
      selectedFile = e.dataTransfer.files[0];
      dropzone.textContent = selectedFile.name;
      dropzone.style.borderColor = '#b58cff';
      dropzone.style.boxShadow = 'none';
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

        return send_file(filepath, as_attachment=True, download_name=filename)

    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True)
