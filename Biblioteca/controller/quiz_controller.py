from flask import Blueprint, render_template, request, redirect, url_for, flash
from model import quiz
from model.db import get_connection

quiz_controller = Blueprint("quiz_controller", __name__, url_prefix="/quiz")

@quiz_controller.route("/", methods=["GET", "POST"])
def gestionar_quizzes():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT correo, nom_user, seg_nom_user, ap_pat_user FROM profesor")
        profesores = cur.fetchall()  # lista de diccionarios

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
        return render_template("quiz.html", quizzes=quizzes, profesores=profesores)

    except Exception as e:
        print("Error en gestionar_quizzes:", e)
        flash(f"Error: {str(e)}", "error")
        return render_template("quiz.html", quizzes=[], profesores=[])
    finally:
        if cur: cur.close()
        if conn: conn.close()


@quiz_controller.route("/eliminar/<int:id_quiz>", methods=["POST"])
def eliminar(id_quiz):
    quiz.eliminar_quiz(id_quiz)
    flash("🗑 Quiz eliminado correctamente", "success")
    return redirect(url_for("quiz_controller.gestionar_quizzes"))
