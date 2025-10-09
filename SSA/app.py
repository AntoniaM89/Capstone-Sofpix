import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from controller import SSA_Controller

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
# RUTAS PROFESORES
# ==============================
app.add_url_rule('/profesores/nuevo', 'add_profesor', SSA_Controller.add_profesor, methods=['GET', 'POST'])
app.add_url_rule('/profesores/<correo>', 'detail_profesor', SSA_Controller.detail_profesor)
app.add_url_rule('/profesores/editar/<correo>', 'update_profesor', SSA_Controller.update_profesor, methods=['GET', 'POST'])
app.add_url_rule('/profesores/eliminar/<correo>', 'delete_profesor', SSA_Controller.delete_profesor, methods=['GET', 'POST'])
app.add_url_rule('/profesores', 'list_profesores', SSA_Controller.list_profesores)


# ==============================
# RUTAS ASIGNATURAS
# ==============================
app.add_url_rule('/asignaturas/nuevo', 'add_asignatura', SSA_Controller.add_asignatura, methods=['GET', 'POST'])
app.add_url_rule('/asignaturas/<codigo>', 'detail_asignatura', SSA_Controller.detail_asignatura)
app.add_url_rule('/asignaturas/editar/<codigo>', 'update_asignatura', SSA_Controller.update_asignatura, methods=['GET', 'POST'])
app.add_url_rule('/asignaturas/eliminar/<codigo>', 'delete_asignatura', SSA_Controller.delete_asignatura, methods=['GET', 'POST'])
app.add_url_rule('/asignaturas', 'mis_asignaturas', SSA_Controller.mis_asignaturas)


# ==============================
# RUTAS CURSOS
# ==============================
app.add_url_rule('/cursos/nuevo', 'add_curso', SSA_Controller.add_curso, methods=['GET', 'POST'])
app.add_url_rule('/cursos/<id_curso>', 'detail_curso', SSA_Controller.detail_curso)
app.add_url_rule('/cursos/editar/<id_curso>', 'update_curso', SSA_Controller.update_curso, methods=['GET', 'POST'])
app.add_url_rule('/cursos/eliminar/<id_curso>', 'delete_curso', SSA_Controller.delete_curso, methods=['GET', 'POST'])
app.add_url_rule('/cursos', 'list_cursos', SSA_Controller.list_cursos)

# Rutas de alumnos por curso
app.add_url_rule('/cursos/<id_curso>/alumnos', 'alumnos_por_curso', SSA_Controller.alumnos_por_curso)
# Ruta para ver detalle de un curso
app.add_url_rule(
    '/cursos/<id_curso>/detalle', 
    'detalle_curso', 
    SSA_Controller.detalle_curso_general
)


# ==============================
# RUTAS ALUMNOS
# ==============================
app.add_url_rule('/alumnos/nuevo', 'add_alumno', SSA_Controller.add_alumno, methods=['GET', 'POST'])
app.add_url_rule('/alumnos/<rut_alum>', 'detail_alumno', SSA_Controller.detail_alumno)
app.add_url_rule('/alumnos/editar/<rut_alum>', 'update_alumno', SSA_Controller.update_alumno, methods=['GET', 'POST'])
app.add_url_rule('/alumnos/eliminar/<rut_alum>', 'delete_alumno', SSA_Controller.delete_alumno, methods=['GET', 'POST'])
app.add_url_rule('/alumnos', 'list_alumnos', SSA_Controller.list_alumnos)
# Notas de un alumno
app.add_url_rule('/alumnos/<rut_alum>/notas', 'detail_alumno_notas', SSA_Controller.detail_alumno_notas)
# Notas de un alumno en una asignatura específica
app.add_url_rule(
    '/alumnos/<rut_alum>/asignatura/<codigo_asignatura>/curso/<id_curso>/notas',
    'detail_alumno_notas_asignatura',
    SSA_Controller.detail_alumno_notas_asignatura
)



# ==============================
# RUTAS NOTAS
# ==============================
app.add_url_rule('/notas/nueva', 'add_nota', SSA_Controller.add_nota, methods=['GET', 'POST'])
app.add_url_rule('/notas/<id_nota>', 'detail_nota', SSA_Controller.detail_nota)
app.add_url_rule('/notas/editar/<id_nota>', 'update_nota', SSA_Controller.update_nota, methods=['GET', 'POST'])
app.add_url_rule('/notas/eliminar/<id_nota>', 'delete_nota', SSA_Controller.delete_nota, methods=['GET', 'POST'])
app.add_url_rule('/notas', 'list_notas', SSA_Controller.list_notas)


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


# ==============================
# RUTAS ESPECIALES
# ==============================
@app.route('/asignatura/<codigo_asignatura>/curso/<codigo_curso>')
def detalle_curso_prof_asignatura(codigo_asignatura, codigo_curso):
    return SSA_Controller.detalle_curso_prof_asignatura(codigo_asignatura, codigo_curso)

@app.route('/lista', methods=['GET', 'POST'])
def prueba():
    return render_template("prueba.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
