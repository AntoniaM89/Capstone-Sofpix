import os
from flask import request, render_template, redirect, url_for, flash, session
from mysql.connector import IntegrityError
from model.SSA import NIVEL_MAP
from model import SSA, alumnos_mod, cursos_mod
from controller.SSA_Controller import set_flash




# ================== ALUMNOS ==================

def add_alumno():
    cursos = cursos_mod.list_cursos()
    if request.method == 'POST':
        rut = request.form['rut_alum'].strip()
        nombre = request.form['nom_alum'].strip()
        seg_nom = request.form.get('seg_nom_alum', '').strip()
        ap_pat = request.form['ap_pat_alum'].strip()
        ap_mat = request.form.get('ap_mat_alum', '').strip()
        curso_id = request.form['curso_id'].strip()

        
        if alumnos_mod.alumno_exists(rut):
            set_flash("RUT ya registrado, por favor usa otro", "error")
            return render_template("SSA/agregar_alumno.html",
                                   rut_alum=rut,
                                   nom_alum=nombre,
                                   seg_nom_alum=seg_nom,
                                   ap_pat_alum=ap_pat,
                                   ap_mat_alum=ap_mat,
                                   curso_id=curso_id,
                                   cursos=cursos
                                )

        alumnos_mod.add_alumno(rut, nombre, seg_nom, ap_pat, ap_mat, curso_id)
        set_flash("Alumno agregado correctamente", "success")
        return redirect(url_for('list_alumnos'))

    return render_template("SSA/agregar_alumno.html", cursos=cursos)

def detail_alumno(rut_alum):
    alumno = alumnos_mod.get_alumno(rut_alum)
    if not alumno:
        set_flash("Alumno no encontrado", "error")
        return redirect(url_for('list_alumnos'))
    notas = SSA.get_notas_alumno(rut_alum)
    return render_template("SSA/detalle_alumno.html", alumno=alumno, notas=notas)


def update_alumno(rut_alum):
    alumno = alumnos_mod.get_alumno(rut_alum)
    cursos = cursos_mod.list_cursos()
    tiene_notas = alumnos_mod.alumno_tiene_notas(rut_alum)
    if request.method == "POST":
        datos_actualizados = {
            'nom_alum': request.form.get('nom_alum', '').strip(),
            'seg_nom_alum': request.form.get('seg_nom_alum', '').strip(),
            'ap_pat_alum': request.form.get('ap_pat_alum', '').strip(),
            'ap_mat_alum': request.form.get('ap_mat_alum', '').strip(),
            'curso_id': request.form.get('curso_id')
        }

        if tiene_notas and datos_actualizados['curso_id'] != str(alumno['curso_id']):
            set_flash("No se puede cambiar el curso de un alumno que ya tiene notas registradas.", "error")
            return redirect(url_for('update_alumno', rut_alum=rut_alum))

        alumnos_mod.update_alumno(
            rut_alum,
            datos_actualizados['nom_alum'],
            datos_actualizados['seg_nom_alum'],
            datos_actualizados['ap_pat_alum'],
            datos_actualizados['ap_mat_alum'],
            datos_actualizados['curso_id']
        )

        set_flash("Alumno actualizado correctamente", "success")
        return redirect(url_for('list_alumnos'))

    return render_template(
        "SSA/editar_alumno.html",
        alumno=alumno,
        cursos=cursos,
        tiene_notas=tiene_notas
    )

def delete_alumno(rut_alum):
    alumno = alumnos_mod.get_alumno(rut_alum)
    if not alumno:
        set_flash("Alumno no encontrado.", "error")
        return redirect(url_for('list_alumnos'))

    # Dependencias
    notas = SSA.get_notas_alumno(rut_alum)
    asignaturas = SSA.get_alumnos_por_asignatura_alumno(rut_alum)
    
    # Nombre completo
    nombre_completo = f"{alumno['nom_alum']} "
    if alumno.get('seg_nom_alum'):
        nombre_completo += f"{alumno['seg_nom_alum']} "
    nombre_completo += alumno['ap_pat_alum']
    if alumno.get('ap_mat_alum'):
        nombre_completo += f" {alumno['ap_mat_alum']}"

    if request.method == "POST":
        if notas:
            lista_notas = ", ".join([f"{n['nombre']} ({n['nombre_asi']})" for n in notas])
            set_flash(f"No se puede eliminar: el alumno tiene notas registradas: {lista_notas}", "error")
            return redirect(url_for('list_alumnos'))
        elif asignaturas:
            lista_asig = ", ".join([f"{a['nombre_asi']} ({a['asignatura_codigo']})" for a in asignaturas])
            set_flash(f"No se puede eliminar: el alumno está asignado a las siguientes asignaturas: {lista_asig}", "error")
            return redirect(url_for('list_alumnos'))
        else:
            alumnos_mod.delete_alumno(rut_alum)
            set_flash("Alumno eliminado correctamente", "success")
            return redirect(url_for('list_alumnos'))

    return render_template(
        "eliminar_confirmacion.html",
        tipo="alumno",
        nombre=nombre_completo,
        dependencias=bool(notas or asignaturas),
        notas=notas,
        asignaturas=asignaturas,
        volver=url_for('list_alumnos')
    )


def list_alumnos(id_curso=None):
    rol = session.get("rol")
    correo_prof = session.get("correo_prof")

    if not rol:
        set_flash("Debe iniciar sesión primero", "error")
        return redirect(url_for('login'))

    alumnos = []

    if rol == 'profesor' and not id_curso:
        cursos_prof = SSA.get_cursos_por_profesor(correo_prof)

        if not cursos_prof:
            set_flash("No hay alumnos asignados. Favor solicitar gestión con el administrador.", "info")
            return render_template("SSA/all_alumnos.html", alumnos=[], titulo="Listado de Alumnos", rol=rol)

        for curso in cursos_prof:
            alumnos_curso = SSA.get_alumnos_por_curso(curso['id_curso'])
            for alum in alumnos_curso:
                alum['curso_nivel'] = curso['nivel']
                alum['curso_generacion'] = curso['generacion']
                alum['curso'] = f"{curso['nivel']} {curso['generacion']}"
                alumnos.append(alum)

        titulo = "Alumnos de tus cursos"

    else:
        if id_curso:
            alumnos = SSA.get_alumnos_por_curso(id_curso)
            curso = cursos_mod.get_curso(id_curso)
            titulo = f"Alumnos del curso {curso['nivel']} {curso['generacion']}" if curso else "Alumnos del curso"
            for alum in alumnos:
                alum['curso_nivel'] = curso['nivel'] if curso else None
                alum['curso_generacion'] = curso['generacion'] if curso else None
                alum['curso'] = f"{curso['nivel']} {curso['generacion']}" if curso else None
        else:
            alumnos = alumnos_mod.list_alumnos()  # Todos los alumnos para admin
            titulo = "Listado General de Alumnos"
            for alum in alumnos:
                if alum.get('curso_id'):
                    c = cursos_mod.get_curso(alum['curso_id'])
                    alum['curso_nivel'] = c['nivel']
                    alum['curso_generacion'] = c['generacion']
                    alum['curso'] = f"{c['nivel']} {c['generacion']}"
                else:
                    alum['curso_nivel'] = None
                    alum['curso_generacion'] = None
                    alum['curso'] = None

    return render_template("SSA/all_alumnos.html", alumnos=alumnos, titulo=titulo, rol=rol)
