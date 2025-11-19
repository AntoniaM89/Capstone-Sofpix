import threading
import webview
from app import app

def start_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Lanzar Flask
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Abrir pywebview apuntando a Flask con tamaño mínimo
    webview.create_window(
        "SSA Sofpix",
        "http://127.0.0.1:5000",
        width=800,
        height=800,
        min_size=(800, 800)  # tamaño mínimo de ventana
    )
    webview.start()
