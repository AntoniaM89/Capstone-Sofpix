import os

def make_dirs():
    dirs = [
        "controller",
        "model",
        "view/templates",
        "view/static/js",
        "view/static/css",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    with open("app.py", "w") as f:
        f.write(
            '''import webview
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def start_webview():
    webview.create_window("Mi App MVC", app, width=1000, height=700)
    webview.start()

if __name__ == '__main__':
    start_webview()
'''
        )

    with open("view/templates/index.html", "w") as f:
        f.write("<h1>Hola, PyWebView + MVC</h1>")

    with open("requirements.txt", "w") as f:
        f.write("pywebview\nflask\n")

    print("✅ Proyecto creado con éxito")

if __name__ == "__main__":
    make_dirs()
