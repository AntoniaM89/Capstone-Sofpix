import os
import threading
import webview
from flask import Flask, render_template
from controller.biblioteca_controller import biblioteca_controller
from controller.download_manager import descargar_archivo_local 
from controller.quiz_controller import quiz_controller

# ==========================
# Configuración de Flask
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "view", "templates"),
    static_folder=os.path.join(BASE_DIR, "view", "static")
)

app.secret_key = "clave-ultra-secreta"  

# ==========================
# Rutas principales
# ==========================
@app.route("/")
def index():
    return render_template("index.html")

# Registrar blueprints
app.register_blueprint(biblioteca_controller, url_prefix="/biblioteca")
app.register_blueprint(quiz_controller, url_prefix="/quiz")

# ==========================
# API para PyWebView
# ==========================
class API:
    """
    Métodos expuestos a la app de escritorio para PyWebView
    """
    def descargar(self, id_archivo):
        """
        Descargar un archivo de la base de datos y guardarlo
        en la carpeta Descargas del cliente.
        """
        ruta = descargar_archivo_local(id_archivo)
        return {"ok": ruta is not None, "ruta": ruta}


# ==========================
# Función para ejecutar Flask en un hilo
# ==========================
def run_flask():
    # debug=False y use_reloader=False para que PyWebView no cree hilos duplicados
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


# ==========================
# Inicio de la app de escritorio con PyWebView
# ==========================
if __name__ == "__main__":
    # Ejecutar Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Crear la ventana de PyWebView
    api = API()
    window = webview.create_window(
        "Sofpix - Biblioteca",
        "http://127.0.0.1:5000/",
        width=1000,
        height=700,
        js_api=api
    )
    webview.start()
