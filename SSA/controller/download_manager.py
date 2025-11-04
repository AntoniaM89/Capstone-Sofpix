import os
import re
import requests
from pathlib import Path

def descargar_archivo_local(id_archivo):
    """Descarga un archivo desde el servidor Flask y lo guarda en la carpeta Descargas"""
    url = f"http://127.0.0.1:5000/biblioteca/descargar/{id_archivo}"
    response = requests.get(url)

    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition", "")
        match = re.search(r'filename="?([^";]+)"?', content_disposition)
        filename = match.group(1) if match else "archivo_descargado"

        _, ext = os.path.splitext(filename)
        if not ext:
            content_type = response.headers.get("Content-Type", "")
            if "pdf" in content_type:
                ext = ".pdf"
            elif "word" in content_type or "doc" in content_type:
                ext = ".docx"
            elif "image" in content_type:
                ext = ".jpg"
            elif "text" in content_type:
                ext = ".txt"
            filename += ext

        # Carpeta Descargas
        downloads_folder = str(Path.home() / "Downloads")
        os.makedirs(downloads_folder, exist_ok=True)

        # Evitar sobrescribir archivos existentes
        base, ext = os.path.splitext(filename)
        ruta_destino = os.path.join(downloads_folder, filename)
        counter = 1
        while os.path.exists(ruta_destino):
            ruta_destino = os.path.join(downloads_folder, f"{base}({counter}){ext}")
            counter += 1

        # Guardar archivo
        with open(ruta_destino, "wb") as f:
            f.write(response.content)

        print(f"Archivo guardado en {ruta_destino}")
        return ruta_destino

    else:
        print(f"Error al descargar: {response.status_code}")
        return None