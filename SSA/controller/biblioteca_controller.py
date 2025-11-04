import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, session
from model.db import get_connection
import model.biblioteca as biblioteca
from model import profesores_mod
import io

biblioteca_controller = Blueprint("biblioteca_controller", __name__)

# ==========================================
# VISTA PRINCIPAL - Gestión de Biblioteca
# ==========================================
@biblioteca_controller.route("/", methods=["GET", "POST"])
def gestionar_biblioteca():
    try:
        rol = session.get("rol")
        correo = session.get("correo_prof")

        if rol == "admin":
            profesores = profesores_mod.list_profesores()
        elif rol == "profesor" and correo:
            prof = profesores_mod.get_profesor(correo)
            profesores = [prof] if prof else []
        else:
            profesores = []

        if request.method == "POST":
            archivo = request.files.get("contenido")
            profesor_correo = request.form.get("profesor_correo")
            carpeta = request.form.get("carpeta", "Home")

            if archivo and profesor_correo:
                nombre = archivo.filename
                tipo = os.path.splitext(nombre)[1][1:] 
                contenido = archivo.read()

                biblioteca.agregar_archivo(nombre, tipo, contenido, profesor_correo, carpeta)
                flash("Archivo subido correctamente", "success")
                return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))
            else:
                flash("Debes seleccionar un archivo y un profesor", "error")

        archivos = biblioteca.listar_archivos()

        return render_template("Biblioteca/biblioteca.html", profesores=profesores, archivos=archivos)

    except Exception as e:
        print("Error en gestionar_biblioteca:", e)
        flash(f"Error: {str(e)}", "error")
        return render_template("Biblioteca/biblioteca.html", profesores=[], archivos=[])



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

    nombre = resultado['nombre']
    tipo = resultado['tipo']
    contenido = resultado['contenido']

    print(f"Descargando {nombre}.{tipo}, {len(contenido)} bytes")  # DEBUG

    if not nombre.lower().endswith(f".{tipo.lower()}"):
        nombre = f"{nombre}.{tipo}"

    buffer = io.BytesIO(contenido)
    response = make_response(buffer.getvalue())
    response.headers.set("Content-Type", "application/octet-stream")
    response.headers.set("Content-Disposition", f"attachment; filename={nombre}")
    return response


# ==========================================
# Eliminar archivo de la biblioteca
# ==========================================
@biblioteca_controller.route("/eliminar/<int:id>", methods=["GET", "POST"])
def delete_archivo(id):
    archivo = biblioteca.obtener_archivo(id)
    if not archivo:
        flash("Archivo no encontrado", "error")
        return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

    dependencias = False

    if request.method == "POST":
        if dependencias:
            flash("No se puede eliminar el archivo por dependencias", "error")
        else:
            biblioteca.eliminar_archivo(id)
            flash("Archivo eliminado correctamente", "success")
        return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

    return render_template(
        "eliminar_confirmacion.html",
        tipo="archivo",
        nombre=archivo['nombre'],
        dependencias=dependencias,
        volver=url_for("biblioteca_controller.gestionar_biblioteca")
    )
