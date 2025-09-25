import os
import threading
import webview
from flask import Flask, render_template
from controller.biblioteca_controller import biblioteca_controller

# ==========================
# Configuración de Flask
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "view", "templates"),
    static_folder=os.path.join(BASE_DIR, "view", "static")
)

# Necesario para manejar sesiones y mensajes flash
app.secret_key = "clave-ultra-secreta"  
# Puedes usar algo más seguro generado con os.urandom(24)

# ==========================
# Rutas principales
# ==========================
@app.route("/")
def index():
    return render_template("index.html")

# Registrar blueprint de biblioteca
app.register_blueprint(biblioteca_controller, url_prefix="/biblioteca")

# ==========================
# Función para ejecutar Flask en un hilo
# ==========================
def run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

# ==========================
# Inicio de la app de escritorio con PyWebView
# ==========================
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # PyWebView abre la ventana con la app Flask
    webview.create_window("Sofpix - Biblioteca", "http://127.0.0.1:5000/", width=1000, height=700)
    webview.start()


# Rutas Biblioteca
@app.route('/biblioteca/subir', methods=['POST'])
def subir():
    return biblioteca_controller.subir_archivo()

@app.route('/biblioteca/listar', methods=['GET'])
def listar():
    return biblioteca_controller.listar()

@app.route('/biblioteca/descargar/<int:id_archivo>', methods=['GET'])
def descargar(id_archivo):
    return biblioteca_controller.descargar_archivo(id_archivo)