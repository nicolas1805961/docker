from flask import Flask
from flask import request
import subprocess
import sys
import os
app = Flask(__name__)

@app.route('/dewarp', methods=['POST'])
def launch_app():
    file = request.files['image']
    first_content = file.read()
    with open('input_file', 'w+') as input_file:
        input_file.write(str(first_content))
    subprocess.run(["python", "dewarp.py", "-d", "input_file", "output.json"])
    with open("output.json", 'r') as file:
        content = file.read()
    return content


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)