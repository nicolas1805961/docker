from flask import Flask
from flask import request
import subprocess
import shutil
app = Flask(__name__)

@app.route('/dewarp', methods=['POST'])
def launch_app():
    file = request.files['image']
    file.save('input_file')
    subprocess.run(["python", "dewarp.py", "-d", "input_file", "output.json"])
    with open("output.json", 'r') as file:
        content = file.read()
    return content


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded = True, debug=True)