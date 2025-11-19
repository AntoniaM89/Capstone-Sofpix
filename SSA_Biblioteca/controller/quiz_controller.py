from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
from model import quiz, quiz_pregunta, biblioteca, profesores_mod
import io

quiz_controller = Blueprint("quiz_controller", __name__)

# ==========================================
# FUNCIÓN DE AYUDA PARA SEGURIDAD
# ==========================================
def check_session():
    """Verifica si el usuario ha iniciado sesión."""
    rol = session.get("rol")
    correo = session.get("correo_prof")
    
    if not rol or not correo:
        flash("Debe iniciar sesión primero", "error")
        return None, None, redirect(url_for('login')) 
    
    return rol, correo, None

# ==========================================
# FUNCIÓN DE VERIFICACIÓN DE PROPIEDAD
# ==========================================
def check_quiz_owner(id_quiz):
    """
    Verifica si el usuario actual es dueño del quiz o es admin.
    Retorna (rol, correo, quiz_data, response)
    """
    rol, correo, response = check_session()
    if response:
        return rol, correo, None, response

    # Obtenemos el quiz de la BD
    quiz_data = quiz.obtener_quiz(id_quiz)
    if not quiz_data:
        flash("Quiz no encontrado", "error")
        return rol, correo, None, redirect(url_for("quiz_controller.gestionar_quizzes"))

    # Validamos permisos
    if rol != 'admin' and quiz_data['profesor_correo'] != correo:
        flash("No tienes permiso para gestionar este quiz", "error")
        return rol, correo, None, redirect(url_for("quiz_controller.gestionar_quizzes"))

    return rol, correo, quiz_data, None


# ==========================================
# VISTA PRINCIPAL - GESTIÓN DE QUIZZES
# ==========================================
@quiz_controller.route("/", methods=["GET", "POST"])
def gestionar_quizzes():   
    # 1. Verificar Sesión
    rol, correo, response = check_session()
    if response:
        return response

    # 2. Cargar lista de profesores (Solo útil si es admin, pero lo cargamos igual)
    if rol == 'admin':
        profesores = profesores_mod.list_profesores()
    elif rol == 'profesor':
        # Si es profe, solo se necesita a sí mismo en la lista (o lo manejamos en el template)
        prof = profesores_mod.get_profesor(correo)
        profesores = [prof] if prof else []
    else:
        profesores = []
    
    # 3. Lógica POST (Crear Quiz)
    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        carpeta = request.form.get("carpeta", "General")
        
        # Lógica de asignación de profesor
        if rol == 'admin':
            profesor_destino = request.form.get("profesor_correo")
        else:
            # Si es profesor, forzamos que sea su propio correo
            profesor_destino = correo

        if titulo and profesor_destino:
            quiz.crear_quiz(titulo, descripcion, profesor_destino, carpeta)
            flash("✅ Quiz creado correctamente", "success")
            return redirect(url_for("quiz_controller.gestionar_quizzes"))
        else:
            flash("❌ Faltan datos obligatorios", "error")

    # 4. Lógica GET (Listar Quizzes con Filtro)
    todos_los_quizzes = quiz.listar_quizzes()

    if rol == 'admin':
        quizzes = todos_los_quizzes
    else:
        # Filtramos en Python: solo los que coincidan con el correo de la sesión
        quizzes = [q for q in todos_los_quizzes if q['profesor_correo'] == correo]

    return render_template(
        "Biblioteca/quiz.html", 
        quizzes=quizzes, 
        profesores=profesores,
        rol=rol,          # Pasamos el rol a la vista
        user_correo=correo # Pasamos el correo actual
    )


# ==========================================
# ELIMINAR QUIZ
# ==========================================
@quiz_controller.route("/eliminar/<int:id_quiz>", methods=["GET", "POST"])
def eliminar(id_quiz):
    # 1. Verificación de seguridad y propiedad
    # (Aprovechamos que esta función nos devuelve los datos del quiz)
    rol, correo, quiz_data, response = check_quiz_owner(id_quiz)
    if response:
        return response

    # 2. Si es POST: El usuario confirmó, procedemos a borrar
    if request.method == "POST":
        try:
            quiz.eliminar_quiz(id_quiz)
            flash("🗑 Quiz eliminado correctamente", "success")
        except Exception as e:
            print(f"Error al eliminar quiz: {e}")
            flash("Error al intentar eliminar el quiz.", "error")
        return redirect(url_for("quiz_controller.gestionar_quizzes"))

    # 3. Si es GET: Mostramos la pantalla de confirmación
    # Reutilizamos tu plantilla 'eliminar_confirmacion.html'
    return render_template(
        "eliminar_confirmacion.html",
        tipo="quiz",                  # Para que el texto diga "el quiz"
        nombre=quiz_data['titulo'],   # Mostramos el título del quiz
        dependencias=False,           # Asumimos que el borrado en cascada lo maneja la BD
        volver=url_for("quiz_controller.gestionar_quizzes")
    )


# ==========================================
# JUGAR QUIZ 
# ==========================================
@quiz_controller.route("/jugar/<int:id_quiz>", methods=["GET"])
def jugar_quiz(id_quiz):
    rol, correo, response = check_session()
    if response:
        return response

    quiz_actual = quiz.obtener_quiz(id_quiz)
    if not quiz_actual:
        flash("Quiz no encontrado", "error")
        return redirect(url_for("quiz_controller.gestionar_quizzes"))

    preguntas = quiz_pregunta.listar_preguntas(id_quiz)
    return render_template("Biblioteca/quiz_jugar.html", quiz=quiz_actual, preguntas=preguntas)


# ==========================================
# SERVIR IMAGEN (Utilidad)
# ==========================================
@quiz_controller.route("/imagen_blob/<int:id_imagen>")
def servir_imagen_blob(id_imagen):
    # Esta ruta suele ser pública para que las etiquetas <img> funcionen
    archivo = biblioteca.obtener_imagen(id_imagen)
    if not archivo:
        return "Imagen no encontrada", 404
    blob_data, tipo_archivo = archivo["contenido"], archivo["tipo"]
    if not blob_data:
        return "Archivo sin datos BLOB", 500
    mimetype = 'image/jpeg'
    if tipo_archivo:
        t = tipo_archivo.lower()
        if t in ['jpg', 'jpeg']: mimetype = 'image/jpeg'
        elif t == 'svg': mimetype = 'image/svg+xml'
        elif t in ['png','gif','webp']: mimetype = f'image/{t}'
    return send_file(io.BytesIO(blob_data), mimetype=mimetype, as_attachment=False)