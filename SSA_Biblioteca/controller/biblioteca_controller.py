import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, session
from model.db import get_connection
import model.biblioteca as biblioteca
from model import profesores_mod
import io

biblioteca_controller = Blueprint("biblioteca_controller", __name__)


# ==========================================
# FUNCIÓN DE AYUDA PARA SEGURIDAD
# ==========================================
def check_session():
    # Verifica si el usuario ha iniciado sesión.
    rol = session.get("rol")
    correo = session.get("correo_prof")
    
    if not rol or not correo:
        flash("Debe iniciar sesión primero", "error")
        return None, None, redirect(url_for('login')) 
    
    return rol, correo, None

# ==========================================
# VISTA PRINCIPAL - Gestión de Biblioteca
# ==========================================
@biblioteca_controller.route("/", methods=["GET", "POST"])
def gestionar_biblioteca():
    # --- Verificación de Sesión ---
    rol, correo, response = check_session()
    if response:
        return response
    # --- Fin Verificación ---

    try:
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

            # --- Verificación de Carga ---
            # Un profesor solo puede subir en su propio nombre
            if rol == 'profesor' and profesor_correo != correo:
                flash("No tienes permiso para subir archivos en nombre de otro profesor.", "error")
                return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))
            # --- Fin Verificación ---

            if archivo and profesor_correo:
                nombre = archivo.filename
                tipo = os.path.splitext(nombre)[1][1:] 
                contenido = archivo.read()

                biblioteca.agregar_archivo(nombre, tipo, contenido, profesor_correo, carpeta)
                flash("Archivo subido correctamente", "success")
                return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))
            else:
                flash("Debes seleccionar un archivo y un profesor", "error")

        # === FILTRADO POR ROL ===
        # Obtenemos todos los archivos...
        todos_los_archivos = biblioteca.listar_archivos()
        
        # filtramos según el rol
        if rol == 'admin':
            archivos = todos_los_archivos
        else:
            # El profesor solo ve los suyos Y los que están APROBADOS
            archivos = [
                a for a in todos_los_archivos 
                if a['profesor_correo'] == correo and a['estado'] == 'Aprobado'
            ]
        # === FIN FILTRADO ===
        
        # Obtenemos carpetas únicas de los archivos visibles
        # (Usamos 'set' para evitar duplicados y filtramos Nones o vacíos)
        carpetas_unicas = sorted(list(set(
            a['carpeta'] for a in archivos if a.get('carpeta')
        )))
        
        # Obtenemos estados únicos (solo relevante para el admin)
        estados_unicos = []
        if rol == 'admin':
            estados_unicos = sorted(list(set(
                a['estado'] for a in archivos if a.get('estado')
            )))

        return render_template(
            "Biblioteca/biblioteca.html", 
            profesores=profesores, 
            archivos=archivos,
            rol=rol,
            carpetas_unicas=carpetas_unicas,
            estados_unicos=estados_unicos
        )

    except Exception as e:
        print("Error en gestionar_biblioteca:", e)
        flash(f"Error: {str(e)}", "error")
        return render_template(
            "Biblioteca/biblioteca.html", 
            profesores=[], 
            archivos=[],
            rol=rol if 'rol' in locals() else None,
            carpetas_unicas=[],
            estados_unicos=[]    
        )


# ==========================================
# FUNCIÓN DE AYUDA PARA AUTORIZACIÓN
# ==========================================
def check_file_permission(id_archivo):
    """
    Verifica si el usuario en sesión tiene permiso 
    sobre un archivo específico (o es admin).
    Devuelve (rol, correo, archivo, response)
    """
    rol, correo, response = check_session()
    if response:
        return rol, correo, None, response

    archivo = biblioteca.obtener_archivo(id_archivo)
    if not archivo:
        flash("Archivo no encontrado", "error")
        return rol, correo, None, redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

    # === VERIFICACIÓN DE PERMISOS ===
    if rol != 'admin' and archivo['profesor_correo'] != correo:
        flash("Acceso denegado. No tienes permiso sobre este archivo.", "error")
        return rol, correo, None, redirect(url_for("biblioteca_controller.gestionar_biblioteca"))
    
    return rol, correo, archivo, None


# ==========================================
# DESCARGA DE ARCHIVO
# ==========================================
@biblioteca_controller.route("/descargar/<int:id_archivo>")
def descargar_archivo(id_archivo):
    # --- Verificación de Sesión y Permiso ---
    rol, correo, resultado, response = check_file_permission(id_archivo)
    if response:
        return response
    # --- Fin Verificación ---

    nombre = resultado['nombre']
    tipo = resultado['tipo']
    contenido = resultado['contenido']

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
    # --- Verificación de Sesión y Permiso ---
    rol, correo, archivo, response = check_file_permission(id)
    if response:
        return response
    # --- Fin Verificación ---

    dependencias = False # Tu lógica de dependencias

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


# ==========================================
# EDITAR NOMBRE DE ARCHIVO
# ==========================================
@biblioteca_controller.route("/editar/<int:id>", methods=["POST"])
def editar_nombre_archivo(id):
    # --- Verificación de Sesión y Permiso ---
    rol, correo, archivo_actual, response = check_file_permission(id)
    if response:
        return response
    # --- Fin Verificación ---

    nuevo_nombre_base = request.form.get("nuevo_nombre")

    if not nuevo_nombre_base:
        flash("El nombre no puede estar vacío", "error")
        return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

    try:
        extension = archivo_actual['tipo']
        nuevo_nombre_completo = f"{nuevo_nombre_base}.{extension}"
        
        biblioteca.editar_nombre(id, nuevo_nombre_completo)
        flash("Archivo renombrado correctamente", "success")
        
    except Exception as e:
        print(f"Error al editar nombre: {e}") # Debug
        flash(f"Error al renombrar el archivo: {str(e)}", "error")

    return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

# ==========================================
# ACTUALIZAR ESTADO DE ARCHIVO (SOLO ADMIN)
# ==========================================
@biblioteca_controller.route("/actualizar_estado/<int:id>", methods=["POST"])
def actualizar_estado(id):
    # --- Verificación de Sesión ---
    rol, correo, response = check_session()
    if response:
        return response
    
    # --- Verificación de Permiso (SOLO ADMIN) ---
    if rol != 'admin':
        flash("No tienes permisos para realizar esta acción.", "error")
        return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

    nuevo_estado = request.form.get("estado")

    # Validamos que el estado sea uno de los esperados
    if nuevo_estado not in ['Aprobado', 'Rechazado', 'Pendiente']:
        flash("Estado no válido", "error")
        return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))

    try:
        # Llamamos a la nueva función del modelo
        biblioteca.actualizar_estado_archivo(id, nuevo_estado)
        flash(f"Estado del archivo actualizado a '{nuevo_estado}'", "success")
    except Exception as e:
        print(f"Error al actualizar estado: {e}")
        flash("Error al actualizar el estado", "error")

    # Redirigimos de vuelta a la biblioteca
    return redirect(url_for("biblioteca_controller.gestionar_biblioteca"))