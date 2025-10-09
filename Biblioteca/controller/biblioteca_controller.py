import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from model.db import get_connection
import model.biblioteca as biblioteca
import io

biblioteca_controller = Blueprint("biblioteca_controller", __name__)

# ==========================================
# VISTA PRINCIPAL - Gestión de Biblioteca
# ==========================================
@biblioteca_controller.route("/", methods=["GET", "POST"])
def gestionar_biblioteca():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Lista de profesores para el selector
        cur.execute("SELECT correo, nom_user, ap_pat_user FROM profesor")
        profesores = cur.fetchall()
        # Soporte para DictCursor
        if profesores and isinstance(profesores[0], dict):
            # convertir a lista de tuplas para compatibilidad con el template
            profesores = [(p['correo'], p['nom_user'], p['ap_pat_user']) for p in profesores]

        # Subida de archivo
        if request.method == "POST":
            archivo = request.files.get("contenido")
            profesor_correo = request.form.get("profesor_correo")
            carpeta = request.form.get("carpeta", "Home")

            if archivo and profesor_correo:
                nombre = archivo.filename
                tipo = os.path.splitext(nombre)[1][1:]  # sin el punto
                contenido = archivo.read()

                biblioteca.agregar_archivo(nombre, tipo, contenido, profesor_correo, carpeta)
                flash("Archivo subido correctamente", "success")
                return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))
            else:
                flash("Debes seleccionar un archivo y un profesor", "error")

        # Archivos ya cargados
        cur.execute(
            "SELECT ID, Nombre, Tipo, Fecha_Subida, profesor_correo, Carpeta FROM biblioteca"
        )
        archivos = cur.fetchall()
        # Soporte para DictCursor
        if archivos and isinstance(archivos[0], dict):
            archivos = [
                (a['ID'], a['Nombre'], a['Tipo'], a['Fecha_Subida'], a['profesor_correo'], a['Carpeta'])
                for a in archivos
            ]

        return render_template("biblioteca.html", profesores=profesores, archivos=archivos)

    except Exception as e:
        print("Error en gestionar_biblioteca:", e)
        flash(f"Error: {str(e)}", "error")
        return render_template("biblioteca.html", profesores=[], archivos=[])
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ==========================================
# DESCARGA DE ARCHIVO
# ==========================================
@biblioteca_controller.route("/descargar/<int:id_archivo>")
def descargar_archivo(id_archivo):
    resultado = biblioteca.obtener_archivo(id_archivo)
    if not resultado:
        print(f"Archivo {id_archivo} no encontrado en la base de datos")
        flash("Archivo no encontrado", "error")
        return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

    nombre, tipo, contenido = resultado
    print(f"Descargando {nombre}.{tipo}, {len(contenido)} bytes")  # DEBUG

    if not nombre.lower().endswith(f".{tipo.lower()}"):
        nombre = f"{nombre}.{tipo}"

    buffer = io.BytesIO(contenido)
    response = make_response(buffer.getvalue())
    response.headers.set("Content-Type", "application/octet-stream")
    response.headers.set("Content-Disposition", f"attachment; filename={nombre}")
    return response
