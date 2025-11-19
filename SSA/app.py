import os
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from controller import SSA_Controller, alumnos_controller, asignaturas_controller, cursos_controller, notas_controller,profesores_controller, metricas_controller
from controller.biblioteca_controller import biblioteca_controller
from controller.quiz_controller import quiz_controller
from controller.quiz_pregunta_controller import quiz_pregunta_controller
from controller.download_manager import descargar_archivo_local

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "view", "templates"),
    static_folder=os.path.join(BASE_DIR, "view", "static")
)
app.secret_key = "supersecret12348765"

def set_flash(message, category="info"):
    session.pop('_flashes', None)
    flash(message, category)




# ==============================
# RUTAS LOGIN Y HOME
# ==============================
@app.route('/')
def init():
    return render_template("init.html")

@app.route('/home') 
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return SSA_Controller.login()


#################################
# SSA
#################################
# ==============================
# RUTAS PROFESORES
# ==============================
app.add_url_rule('/profesores/nuevo', 'add_profesor', profesores_controller.add_profesor, methods=['GET', 'POST'])
app.add_url_rule('/profesores/<correo>', 'detail_profesor', profesores_controller.detail_profesor)
app.add_url_rule('/profesores/editar/<correo>', 'update_profesor', profesores_controller.update_profesor, methods=['GET', 'POST'])
app.add_url_rule('/profesores/eliminar/<correo>', 'delete_profesor', profesores_controller.delete_profesor, methods=['GET', 'POST'])
app.add_url_rule('/profesores', 'list_profesores', profesores_controller.list_profesores)


# ==============================
# RUTAS ASIGNATURAS
# ==============================
app.add_url_rule('/asignaturas/nuevo', 'add_asignatura', asignaturas_controller.add_asignatura, methods=['GET', 'POST'])
app.add_url_rule('/asignaturas/<codigo>', 'detail_asignatura', asignaturas_controller.detail_asignatura)
app.add_url_rule('/asignaturas/editar/<codigo>', 'update_asignatura', asignaturas_controller.update_asignatura, methods=['GET', 'POST'])
app.add_url_rule('/asignaturas/eliminar/<codigo>', 'delete_asignatura', asignaturas_controller.delete_asignatura, methods=['GET', 'POST'])
app.add_url_rule('/asignaturas', 'mis_asignaturas', SSA_Controller.mis_asignaturas)

app.add_url_rule(
    '/asignaturas/<codigo_asignatura>/curso/<id_curso>/alumnos',
    'gestionar_alumnos',
    SSA_Controller.gestionar_alumnos,
    methods=['GET', 'POST']
)



# ==============================
# RUTAS CURSOS
# ==============================
app.add_url_rule('/cursos/nuevo', 'add_curso', cursos_controller.add_curso, methods=['GET', 'POST'])
app.add_url_rule('/cursos/<id_curso>/asignaturas', 'gestionar_asignaturas', SSA_Controller.gestionar_asignaturas, methods=['GET', 'POST'])
app.add_url_rule('/cursos/editar/<id_curso>', 'update_curso', cursos_controller.update_curso, methods=['GET', 'POST'])
app.add_url_rule('/cursos/eliminar/<id_curso>', 'delete_curso', cursos_controller.delete_curso, methods=['GET', 'POST'])
app.add_url_rule('/cursos', 'list_cursos', cursos_controller.list_cursos)

# ==============================
# RUTAS ALUMNOS
# ==============================
app.add_url_rule('/alumnos/nuevo', 'add_alumno', alumnos_controller.add_alumno, methods=['GET', 'POST'])
app.add_url_rule('/alumnos/<rut_alum>', 'detail_alumno', alumnos_controller.detail_alumno)
app.add_url_rule('/alumnos/editar/<rut_alum>', 'update_alumno', alumnos_controller.update_alumno, methods=['GET', 'POST'])
app.add_url_rule('/alumnos/eliminar/<rut_alum>', 'delete_alumno', alumnos_controller.delete_alumno, methods=['GET', 'POST'])
app.add_url_rule('/alumnos', 'list_alumnos', alumnos_controller.list_alumnos)
# Notas de un alumno
app.add_url_rule('/alumnos/<rut_alum>/notas', 'detail_alumno_notas', SSA_Controller.detail_alumno_notas)

# ==============================
# RUTAS NOTAS
# ==============================
app.add_url_rule('/notas/nueva', 'add_nota', notas_controller.add_nota, methods=['GET', 'POST'])
app.add_url_rule('/notas/<id_nota>', 'detail_nota', notas_controller.detail_nota)
app.add_url_rule('/notas/editar/<id_nota>', 'update_nota', notas_controller.update_nota, methods=['GET', 'POST'])
app.add_url_rule('/notas/eliminar/<id_nota>', 'delete_nota', notas_controller.delete_nota, methods=['GET', 'POST'])
app.add_url_rule('/notas', 'list_notas', notas_controller.list_notas)



# ==============================
# RUTAS REPORTES / MÉTRICAS
# ==============================
app.add_url_rule('/Reportes', 'reportes', metricas_controller.reportes, methods=['GET', 'POST'])
app.add_url_rule('/Reportes/export/excel', 'export_metricas_excel', metricas_controller.export_metricas_excel)
app.add_url_rule('/Reportes/export/pdf', 'export_metricas_pdf', metricas_controller.export_metricas_pdf)
app.add_url_rule('/Reportes/informe_alumno', 'informe_alumno', metricas_controller.informe_alumno, methods=['GET','POST'])
app.add_url_rule('/Reportes/informe_alumno/obtener_alumnos/<curso_id>', 'obtener_alumnos', metricas_controller.obtener_alumnos)
app.add_url_rule('/Reportes/informe_alumno/pdf', 'informe_alumno_pdf', metricas_controller.export_informe_alumno_pdf)


# ==============================
# RUTAS ESPECIALES PARA DROPDOWNS
# ==============================
app.add_url_rule('/Reportes/filtros_dinamicos', 'filtros_dinamicos', metricas_controller.filtros_dinamicos)
app.add_url_rule('/metricas/data', 'metricas_data', metricas_controller.metricas_data, methods=['GET'])
app.add_url_rule('/metricas/kpis', 'metricas_kpis', metricas_controller.metricas_kpis, methods=['GET'])


# ==============================
# RUTAS ESPECIALES
# ==============================
@app.route('/asignatura/<codigo_asignatura>/curso/<codigo_curso>')
def detalle_curso_prof_asignatura(codigo_asignatura, codigo_curso):
    return SSA_Controller.detalle_curso_prof_asignatura(codigo_asignatura, codigo_curso)


@app.route('/SSA', methods=['GET', 'POST'])
def SSA():
    return render_template("SSA/ssa.html")


#################################
# Biblioteca
#################################

# Registrar blueprints
app.register_blueprint(biblioteca_controller, url_prefix="/biblioteca")
app.register_blueprint(quiz_controller, url_prefix="/quiz")
app.register_blueprint(quiz_pregunta_controller, url_prefix="/quiz_pregunta")

@app.route('/Biblioteca', methods=['GET', 'POST'])
def biblioteca():
    return render_template("Biblioteca/index.html")


# ==========================
# API para PyWebView
# ==========================
class API:
    def descargar(self, id_archivo):
        ruta = descargar_archivo_local(id_archivo)
        return {"ok": ruta is not None, "ruta": ruta}




# Ruta Default
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

