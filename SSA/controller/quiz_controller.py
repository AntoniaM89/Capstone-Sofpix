from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from model import quiz, quiz_pregunta, biblioteca, profesores_mod
import io

quiz_controller = Blueprint("quiz_controller", __name__)

@quiz_controller.route("/", methods=["GET", "POST"])
def gestionar_quizzes():   
    profesores = profesores_mod.list_profesores()
    
    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        profesor_correo = request.form["profesor_correo"]
        carpeta = request.form.get("carpeta", "General")

        if titulo and profesor_correo:
            quiz.crear_quiz(titulo, descripcion, profesor_correo, carpeta)
            flash("✅ Quiz creado correctamente", "success")
            return redirect(url_for("quiz_controller.gestionar_quizzes"))
        else:
            flash("❌ Debes ingresar título y profesor", "error")

    quizzes = quiz.listar_quizzes()
    return render_template("Biblioteca/quiz.html", quizzes=quizzes, profesores=profesores)

@quiz_controller.route("/eliminar/<int:id_quiz>", methods=["POST"])
def eliminar(id_quiz):
    quiz.eliminar_quiz(id_quiz)
    flash("🗑 Quiz eliminado correctamente", "success")
    return redirect(url_for("quiz_controller.gestionar_quizzes"))

@quiz_controller.route("/jugar/<int:id_quiz>", methods=["GET"])
def jugar_quiz(id_quiz):
    quiz_actual = quiz.obtener_quiz(id_quiz)
    preguntas = quiz_pregunta.listar_preguntas(id_quiz)
    return render_template("Biblioteca/quiz_jugar.html", quiz=quiz_actual, preguntas=preguntas)

@quiz_controller.route("/imagen_blob/<int:id_imagen>")
def servir_imagen_blob(id_imagen):
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
