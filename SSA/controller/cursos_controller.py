import os
from flask import request, render_template, redirect, url_for, flash, session
from mysql.connector import IntegrityError
from model.SSA import NIVEL_MAP
from model import SSA, cursos_mod
from controller.SSA_Controller import set_flash , require_login



# ================== CURSOS ==================
def add_curso():
    if request.method == 'POST':
        nivel = request.form['nivel']
        generacion = request.form['generacion']
        prefijo = NIVEL_MAP.get(nivel)
        if not prefijo:
            set_flash("Nivel inválido", "error")
            return render_template("SSA/agregar_curso.html", NIVEL_MAP=NIVEL_MAP)

        id_curso = f"{prefijo}{generacion}"
        if cursos_mod.curso_exists(id_curso):
            set_flash(f"Ya existe un curso con nivel '{nivel}' y generación '{generacion}'", "error")
            return redirect(url_for('list_cursos'))

        cursos_mod.add_curso(id_curso, nivel, generacion)
        set_flash("Curso creado correctamente", "success")
        return redirect(url_for('list_cursos'))

    return render_template("SSA/agregar_curso.html", NIVEL_MAP=NIVEL_MAP)

def detail_curso(id_curso):
    curso = cursos_mod.get_curso(id_curso)
    if not curso:
        flash("Curso no encontrado", "error")
        return redirect(url_for('list_cursos'))

    asignatura = asignaturas_mod.get_asignatura(curso['codigo_asignatura'])
    profesor = profesores_mod.get_profesor(asignatura['profesor_correo'])

    return render_template(
        "SSA/detalle_curso.html",
        curso=curso,
        asignatura_nombre=asignatura['nombre_asi'],
        profesor_nombre=f"{profesor['nom_user']} {profesor['ap_pat_user']}",
        codigo_asignatura=curso['codigo_asignatura'],   
        id_curso=curso['id_curso']                     
    )



def update_curso(id_curso):
    curso = cursos_mod.get_curso(id_curso)
    if not curso:
        set_flash("Curso no encontrado.", "error")
        return redirect(url_for('list_cursos'))

    if request.method == 'POST':
        nivel = request.form['nivel']
        generacion = request.form['generacion']
        prefijo = NIVEL_MAP.get(nivel)
        if not prefijo:
            set_flash("Nivel inválido", "error")
            return render_template("SSA/editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)

        nuevo_id_curso = f"{prefijo}{generacion}"
        if nuevo_id_curso != id_curso and cursos_mod.curso_exists(nuevo_id_curso):
            set_flash(f"Ya existe un curso con nivel '{nivel}' y generación '{generacion}'", "error")
            return render_template("SSA/editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)

        try:
            cursos_mod.update_curso(id_curso, nivel=nivel, generacion=generacion)
            set_flash("Curso actualizado correctamente.", "success")
            return redirect(url_for('list_cursos'))
        except IntegrityError:
            set_flash("No se puede actualizar el curso porque tiene alumnos asociados.", "error")
            return render_template("SSA/editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)
        except Exception as e:
            set_flash(f"Ocurrió un error al actualizar el curso: {e}", "error")
            return render_template("SSA/editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)

    return render_template("SSA/editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)


def delete_curso(id_curso):
    curso = cursos_mod.get_curso(id_curso)
    if not curso:
        set_flash("Curso no encontrado.", "error")
        return redirect(url_for("list_cursos"))

    alumnos = SSA.get_alumnos_por_curso(id_curso)
    tiene_dependencias = bool(alumnos)

    if request.method == "POST":
        if tiene_dependencias:
            set_flash("No se puede eliminar: el curso tiene alumnos asignados", "error")
            return redirect(url_for("list_cursos"))
        else:
            cursos_mod.delete_curso(id_curso)
            set_flash("Curso eliminado correctamente", "success")
            return redirect(url_for("list_cursos"))

    return render_template(
        "eliminar_confirmacion.html",
        tipo="curso",
        nombre=f"{curso['nivel']} {curso['generacion']}",
        dependencias=tiene_dependencias,
        volver=url_for("list_cursos")
    )

def list_cursos():
    rol = require_login()
    if isinstance(rol, str) and rol.startswith('redirect'):
        return rol

    correo_prof = session.get('correo_prof')
    cursos = []

    if rol == 'profesor':
        cursos_prof = SSA.get_cursos_por_profesor(correo_prof)

        print(cursos_prof)
        
        if not cursos_prof:
            set_flash("Sin cursos asignados. Favor solicitar gestión con el administrador.", "info")
            return render_template("SSA/all_cursos.html", cursos=[], rol=rol)

        for curso_raw in cursos_prof:
            print(curso_raw)
            curso_id = curso_raw['id_curso']
            curso_raw['alumnos'] = SSA.get_alumnos_por_curso(curso_id)
            curso_raw['asignaturas'] = SSA.list_asignaturas_por_curso_y_profesor(curso_id, correo_prof)
            
            
            cursos.append(curso_raw)

    else: 
        cursos_all = cursos_mod.list_cursos()
        for curso_raw in cursos_all:
            curso_id = curso_raw['id_curso']
            curso_raw['alumnos'] = SSA.get_alumnos_por_curso(curso_id)
            asignaturas = SSA.get_asignaturas_por_curso(curso_id)
            
            for asignatura in asignaturas:
                codigo_asi = asignatura['codigo']
                
                profesores = SSA.list_profesores_por_asignatura(codigo_asi)
                
                if profesores:
                    asignatura['profesor_nombre'] = profesores[0]['nombre_prof'] 
                    asignatura['profesor_correo'] = profesores[0]['correo_prof'] 
                else:
                    asignatura['profesor_nombre'] = "No Asignado"
                    asignatura['profesor_correo'] = None

            curso_raw['asignaturas'] = asignaturas
            cursos.append(curso_raw)
            
    return render_template("SSA/all_cursos.html", cursos=cursos, rol=rol)



