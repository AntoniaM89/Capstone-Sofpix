from flask import Blueprint, render_template, request, redirect, url_for, flash
from model import quiz_pregunta, biblioteca

quiz_pregunta_controller = Blueprint("quiz_pregunta_controller", __name__)

@quiz_pregunta_controller.route("/<int:quiz_id>", methods=["GET", "POST"])
def gestionar_preguntas(quiz_id):
    if request.method == "POST":
        pregunta = request.form["pregunta"]
        img_id = request.form.get("img_id")
        opcion_a = request.form["opcion_a"]
        opcion_b = request.form["opcion_b"]
        opcion_c = request.form.get("opcion_c")
        opcion_d = request.form.get("opcion_d")
        respuesta = request.form["respuesta_correcta"]

        if pregunta and opcion_a and opcion_b and respuesta:
            quiz_pregunta.crear_pregunta(quiz_id, pregunta, img_id, opcion_a, opcion_b, opcion_c, opcion_d, respuesta)
            flash("✅ Pregunta creada correctamente", "success")
        else:
            flash("❌ Pregunta y opciones A, B y respuesta correcta son obligatorias", "error")
        return redirect(url_for("quiz_pregunta_controller.gestionar_preguntas", quiz_id=quiz_id))

    preguntas = quiz_pregunta.listar_preguntas(quiz_id)
    archivos = biblioteca.listar_imagenes()
    return render_template("Biblioteca/quiz_pregunta.html", quiz_id=quiz_id, preguntas=preguntas, archivos=archivos)

@quiz_pregunta_controller.route("/eliminar/<int:quiz_id>/<int:id_pregunta>", methods=["POST"])
def eliminar_pregunta(quiz_id, id_pregunta):
    quiz_pregunta.eliminar_pregunta(id_pregunta)
    flash("🗑 Pregunta eliminada correctamente", "success")
    return redirect(url_for("quiz_pregunta_controller.gestionar_preguntas", quiz_id=quiz_id))
