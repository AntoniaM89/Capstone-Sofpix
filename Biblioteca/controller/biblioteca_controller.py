import os
from flask import Blueprint, request, render_template, redirect, url_for, flash
from model.db import get_connection
from model import biblioteca

biblioteca_controller = Blueprint("biblioteca_controller", __name__)

# Vista principal de la biblioteca (formulario + listado)
@biblioteca_controller.route("/", methods=["GET", "POST"])
def gestionar_biblioteca():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener lista de profesores para el selector
        cur.execute("SELECT correo, nom_user, ap_pat_user FROM profesor")
        profesores = cur.fetchall()

        # Si es POST -> Subir archivo
        if request.method == "POST":
            nombre = request.form["nombre"]
            tipo = request.form["tipo"]
            archivo = request.files["contenido"]
            carpeta = request.form["carpeta"]
            profesor_correo = request.form["profesor_correo"]

            if archivo and profesor_correo:
                contenido = archivo.read()
                biblioteca.agregar_archivo(
                    nombre, tipo, contenido, profesor_correo, carpeta
                )
                flash("Archivo subido correctamente", "success")
                return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))
            else:
                flash("Debes seleccionar un archivo y un profesor", "error")

        # Obtener archivos existentes en la biblioteca
        cur.execute(
            "SELECT ID, Nombre, Tipo, Fecha_Subida, profesor_correo, Carpeta FROM biblioteca"
        )
        archivos = cur.fetchall()

        return render_template(
            "biblioteca.html", profesores=profesores, archivos=archivos
        )

    except Exception as e:
        print("Error en gestionar_biblioteca:", e)
        flash(f"Error: {str(e)}", "error")
        return render_template("biblioteca.html", profesores=[], archivos=[])
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# Ruta para eliminar archivo
@biblioteca_controller.route("/eliminar/<int:archivo_id>", methods=["POST"])
def eliminar_archivo(archivo_id):
    try:
        biblioteca.eliminar_archivo(archivo_id)
        flash("Archivo eliminado correctamente", "success")
    except Exception as e:
        flash(f"Error al eliminar archivo: {str(e)}", "error")
    return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))


# Ruta para editar (renombrar) archivo
@biblioteca_controller.route("/editar/<int:archivo_id>", methods=["POST"])
def editar_archivo(archivo_id):
    nuevo_nombre = request.form.get("nuevo_nombre")
    try:
        biblioteca.renombrar_archivo(archivo_id, nuevo_nombre)
        flash("Archivo renombrado correctamente", "success")
    except Exception as e:
        flash(f"Error al renombrar archivo: {str(e)}", "error")
    return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))