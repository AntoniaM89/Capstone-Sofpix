import os
from flask import request, render_template, redirect, url_for, flash, session
from mysql.connector import IntegrityError
from model.SSA import NIVEL_MAP
from model import SSA, profesores_mod, cursos_mod, asignaturas_mod, alumnos_mod, notas_mod


# ================== Utilidades ==================

def set_flash(message, category="info"):
    session.pop('_flashes', None)
    flash(message, category)

def require_login():
    rol = session.get("rol")
    if not rol:
        set_flash("Debe iniciar sesión primero", "error")
        return redirect(url_for('login'))
    return rol


# ================== LOGIN ==================
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip().lower()
        pass_enc = request.form["pass_enc"]
        prof = profesores_mod.get_profesor(correo)

        if prof and prof.get('correo') == correo and prof.get('pass_enc') == pass_enc:
            session['correo_prof'] = correo
            session['rol'] = prof.get('rol', 'profesor')
            return redirect(url_for('home'))
        else:
            set_flash("Correo o contraseña incorrectos", "error")

    return render_template("login/sign_in.html")

# ================== VISTAS PROFESORES ==================
def mis_asignaturas():
    rol = require_login()
    if isinstance(rol, str) and rol.startswith('redirect'):
        return rol

    correo_prof = session.get("correo_prof")

    if rol == "profesor":
        asignaturas = SSA.get_asignaturas_por_profesor(correo_prof)

        # Si no tiene asignaturas asignadas
        if not asignaturas or len(asignaturas) == 0:
            set_flash("Sin asignaturas asignadas. Favor solicitar gestión con el administrador.", "info")
            return render_template("SSA/all_asignaturas.html", asignaturas=[])

        # Si tiene asignaturas, añadir sus cursos
        for asi in asignaturas:
            cursos_raw = SSA.list_cursos_por_asignatura_prof(asi['codigo'], correo_prof)
            cursos = [{"codigo": c["id_curso"], "nombre": f"{c['nivel']} {c['generacion']}"} for c in cursos_raw]
            asi["cursos"] = cursos

    else: 
        asignaturas = SSA.get_all_asignaturas_y_cursos()

    return render_template("SSA/all_asignaturas.html", asignaturas=asignaturas)

def detalle_curso_prof_asignatura(codigo_asignatura, codigo_curso):
    rol = require_login()
    if isinstance(rol, str) and rol.startswith("redirect"):
        return rol

    usuario = session.get("correo_prof") or session.get("correo")
    if not usuario:
        set_flash("Sesión no válida o expirada.", "error")
        return redirect(url_for("login"))

    curso_raw = cursos_mod.get_curso(codigo_curso)
    asignatura_raw = asignaturas_mod.get_asignatura(codigo_asignatura)

    if not curso_raw or not asignatura_raw:
        set_flash("Curso o asignatura no encontrado.", "error")
        return redirect(url_for("mis_asignaturas"))

    if rol == "profesor":
        profesor_asignaturas = SSA.get_asignaturas_por_profesor(usuario)
        codigos_autorizados = [a["codigo"] for a in profesor_asignaturas]
        if codigo_asignatura not in codigos_autorizados:
            set_flash("Acceso no autorizado a esta asignatura.", "error")
            return redirect(url_for("mis_asignaturas"))

    alumnos_curso = SSA.get_alumnos_por_curso(codigo_curso)

    alumnos_asignatura = SSA.get_alumnos_por_asignatura(codigo_asignatura)
    alumnos_asignatura_ruts = {a["rut_alum"] for a in alumnos_asignatura}

    alumnos = []
    for alumno in alumnos_curso:
        if alumno["rut_alum"] in alumnos_asignatura_ruts:
            notas = SSA.get_notas_alumno_asignatura(alumno["rut_alum"], codigo_asignatura, codigo_curso)
            alumno["notas"] = notas or []
            alumnos.append(alumno)
        else:
            alumno["notas"] = []
            alumnos.append(alumno)

    curso = {
        "nivel": curso_raw["nivel"],
        "generacion": curso_raw["generacion"],
        "alumnos": alumnos
    }

    profesor_nombre = asignatura_raw.get("profesor", "Profesor desconocido")
    return render_template(
        "SSA/detalle_curso.html",
        curso=curso,
        asignatura_nombre=asignatura_raw["nombre_asi"],
        profesor_nombre=profesor_nombre,
        codigo_asignatura=codigo_asignatura,
        id_curso=codigo_curso,
        alumnos=alumnos
    )


def gestionar_asignaturas(id_curso):
    curso = cursos_mod.get_curso(id_curso)
    
    asignaturas_actuales = cursos_mod.list_asignaturas_por_curso(id_curso)
    asignaturas_disponibles = cursos_mod.list_asignaturas_disponibles(id_curso)

    if request.method == "POST":
        accion = request.form.get("accion")
        codigo_asig = request.form.get("codigo_asig")

        if accion == "agregar" and codigo_asig:
            exito = cursos_mod.agregar_asignatura_a_curso(id_curso, codigo_asig)
            if exito:
                flash("Asignatura agregada correctamente", "success")
            else:
                flash("Error al agregar asignatura", "error")

        elif accion == "quitar" and codigo_asig:
            tiene_notas = SSA.alumnos_con_notas_en_asignatura(id_curso, codigo_asig)
            if tiene_notas:
                flash(f"No se puede quitar la asignatura {codigo_asig} porque hay alumnos con notas registradas.", "error")
            else:
                exito = cursos_mod.quitar_asignatura_del_curso(id_curso, codigo_asig)
                if exito:
                    flash("Asignatura quitada correctamente", "success")
                else:
                    flash("Error al quitar asignatura", "error")
        
        asignaturas_actuales = cursos_mod.list_asignaturas_por_curso(id_curso)
        asignaturas_disponibles = cursos_mod.list_asignaturas_disponibles(id_curso)

    return render_template(
        "SSA/gestionar_asignaturas.html",
        curso_id=id_curso,
        curso_nivel=curso['nivel'],
        curso_generacion=curso['generacion'],
        asignaturas_actuales=asignaturas_actuales,
        asignaturas_disponibles=asignaturas_disponibles
    )



def gestionar_alumnos(id_curso, codigo_asignatura):
    curso = cursos_mod.get_curso(id_curso)
    if not curso:
        flash("Curso no encontrado", "error")
        return redirect(url_for('list_cursos'))

    if request.method == 'POST':
        accion = request.form.get('accion')
        rut_alum = request.form.get('rut_alum')
        alumno = alumnos_mod.get_alumno(rut_alum)

        if not alumno:
            flash("Alumno no encontrado", "error")
            return redirect(url_for('gestionar_alumnos', id_curso=id_curso, codigo_asignatura=codigo_asignatura))
        
        if accion == 'agregar':
            asignaturas_mod.asignar_a_asignatura(rut_alum, codigo_asignatura)
            flash(f"Alumno {alumno['nom_alum']} {alumno['ap_pat_alum']} ({alumno['rut_alum']}) agregado a la asignatura.", "success")
        
        elif accion == 'quitar':
            notas = SSA.get_notas_alumno_asignatura(rut_alum, codigo_asignatura, id_curso)
            if notas:
                flash(
                    f"No se puede quitar al alumno {alumno['nom_alum']} {alumno['ap_pat_alum']} ({alumno['rut_alum']}) "
                    f"porque tiene {len(notas)} nota(s) registrada(s) en esta asignatura.", "error"
                )
            else:
                asignaturas_mod.quitar_de_asignatura(rut_alum, codigo_asignatura)
                flash(f"Alumno {alumno['nom_alum']} {alumno['ap_pat_alum']} ({alumno['rut_alum']}) eliminado de la asignatura.", "success")
        
        else:
            flash("Acción desconocida", "error")

        return redirect(url_for('gestionar_alumnos', id_curso=id_curso, codigo_asignatura=codigo_asignatura))

    alumnos_curso = alumnos_mod.get_alumnos_por_curso(id_curso)
    alumnos_en_asignatura = SSA.get_alumnos_por_curso_y_asignatura(codigo_asignatura, id_curso)
    alumnos_disponibles = [a for a in alumnos_curso if a['rut_alum'] not in {x['rut_alum'] for x in alumnos_en_asignatura}]

    return render_template(
        "SSA/gestionar_alumnos.html",
        curso_nivel=curso['nivel'],
        curso_generacion=curso['generacion'],
        alumnos_actuales=alumnos_en_asignatura,
        alumnos_disponibles=alumnos_disponibles,
        codigo_asignatura=codigo_asignatura
    )


def detail_alumno_notas(rut_alum):
    alumno = alumnos_mod.get_alumno(rut_alum)
    if not alumno:
        set_flash("Alumno no encontrado", "error")
        return redirect(url_for('list_alumnos'))
    
    rol = session.get("rol")
    usuario = session.get("correo") or session.get("correo_prof")
    
    if rol == 'profesor':
        notas = SSA.get_notas_alumno_por_profesor(rut_alum, usuario)
    else:
        notas = SSA.get_notas_alumno(rut_alum)

    return render_template("SSA/detalle_alumno.html", alumno=alumno, notas=notas)

def summary_dashboard():
    summary = SSA.get_summary_counts()
    return summary
