import os
from flask import request, render_template, redirect, url_for, flash, session
from mysql.connector import IntegrityError
from model.SSA import NIVEL_MAP
from model import SSA, notas_mod, cursos_mod, asignaturas_mod, alumnos_mod
from controller.SSA_Controller import set_flash, require_login


# ================== NOTAS ==================
def add_nota():
    rol = require_login()
    if isinstance(rol, str) and rol.startswith('redirect'):
        return rol

    correo_prof = session.get("correo_prof")

    id_curso = request.args.get('id_curso')
    codigo_asignatura = request.args.get('codigo_asignatura')
    if not id_curso or not codigo_asignatura:
        flash("Falta información de curso o asignatura.", "error")
        return redirect(url_for('SSA'))

    curso = SSA.get_curso_por_id(id_curso)
    asignatura = asignaturas_mod.get_asignatura(codigo_asignatura)

    if not curso or not asignatura:
        flash("Curso o asignatura no encontrados.", "error")
        return redirect(url_for('SSA'))

    alumnos = SSA.get_alumnos_por_curso_y_asignatura(codigo_asignatura, id_curso)
    if request.method == 'POST':
        alumno_rut = request.form['alumno_rut_alum']
        nombre_eval = request.form['nombre'].strip()
        nota = request.form['nota']
        observacion = request.form.get('observacion')

        nombre_id = nombre_eval.replace(" ", "").upper()
        id_nota = f"{codigo_asignatura}{id_curso}{alumno_rut}{nombre_id}"

        if notas_mod.nota_exists(id_nota):
            flash(f"Ya existe una nota con ese nombre para este alumno en esta asignatura y curso.", "warning")
            return render_template(
                "SSA/agregar_nota.html",
                curso=curso,
                asignatura_nombre=asignatura.get("nombre") or asignatura.get("nombre_asi"),
                alumnos=alumnos,
                codigo_asignatura=codigo_asignatura,
                rol=rol
            )

        notas_mod.add_nota(
            id_nota=id_nota,
            asignatura_codigo=codigo_asignatura,
            alumno_rut=alumno_rut,
            nombre_eval=nombre_eval,
            nota=nota,
            observacion=observacion
        )

        flash("Nota agregada correctamente", "success")
        return redirect(url_for('detalle_curso_prof_asignatura', codigo_curso=id_curso, codigo_asignatura=codigo_asignatura))

    return render_template(
        "SSA/agregar_nota.html",
        curso=curso,
        asignatura_nombre=asignatura.get("nombre") or asignatura.get("nombre_asi"),
        alumnos=alumnos,
        codigo_asignatura=codigo_asignatura,
        rol=rol
    )



def detail_nota(id_nota):
    nota = notas_mod.get_nota(id_nota)
    if not nota:
        set_flash("Nota no encontrada", "error")
        return redirect(url_for('list_notas'))
    return render_template("SSA/detalle_nota.html", nota=nota)


def update_nota(id_nota):
    nota = notas_mod.get_nota(id_nota)
    if not nota:
        set_flash("Nota no encontrada", "error")
        return redirect(url_for('list_notas'))

    next_view = request.args.get('next')

    if request.method == 'POST':
        nombre_input = request.form['nombre'].strip()
        nueva_nota = request.form['nota']
        nueva_observacion = request.form.get('observacion')

        nombre_mostrar = nombre_input.title()
        nombre_id = nombre_input.replace(" ", "").upper()
        nuevo_id = f"{nota['asignatura_codigo']}{nota['alumno_rut']}{nombre_id}"

        notas_mod.update_nota(
            id_nota_old=id_nota,
            id_nota_new=nuevo_id,
            nueva_nota=nueva_nota,
            nuevo_nombre=nombre_mostrar,
            nueva_observacion=nueva_observacion
        )

        set_flash("Nota actualizada correctamente", "success")

        if next_view:
            return redirect(next_view)
        else:
            return redirect(url_for(
                'detalle_curso_prof_asignatura',
                codigo_asignatura=nota['asignatura_codigo'],
                codigo_curso=nota['id_curso']
            ))

    return render_template(
        "SSA/editar_nota.html",
        nota=nota,
        codigo_asignatura=nota['asignatura_codigo'],
        id_curso=nota['id_curso']
    )


def delete_nota(id_nota):
    nota = SSA.get_nota_completa(id_nota)
    if not nota:
        set_flash("Nota no encontrada", "error")
        return redirect(url_for('list_notas'))

    next_view = request.args.get('next')

    if request.method == "POST":
        notas_mod.delete_nota(id_nota)
        set_flash("Nota eliminada correctamente", "success")
        if next_view:
            return redirect(next_view)
        else:
            return redirect(url_for(
                'detalle_curso_prof_asignatura',
                codigo_asignatura=nota['asignatura_codigo'],
                codigo_curso=nota['curso_id']
            ))

    nombre_alumno = f"{nota['nom_alum']}"
    if nota.get('seg_nom_alum'):
        nombre_alumno += f" {nota['seg_nom_alum']}"
    nombre_alumno += f" {nota['ap_pat_alum']}"
    if nota.get('ap_mat_alum'):
        nombre_alumno += f" {nota['ap_mat_alum']}"

    return render_template(
        "eliminar_confirmacion.html",
        tipo="nota",
        nombre=f"{nota['nombre_nota']} - Alumno {nombre_alumno} ({nota['rut_alum']})",
        dependencias=False,
        volver=next_view or url_for(
            'detalle_curso_prof_asignatura',
            codigo_asignatura=nota['asignatura_codigo'],
            codigo_curso=nota['curso_id']
        )
    )


def list_notas():
    rol = require_login()
    if isinstance(rol, str) and rol.startswith("redirect"):
        return rol

    if rol == "admin":
        notas = SSA.list_notas_completas()
    else:
        correo_prof = session.get("correo_prof")
        cursos = SSA.get_cursos_por_profesor(correo_prof)
        notas = []

        for curso in cursos:
            alumnos = SSA.get_alumnos_por_curso(curso["codigo"])
            for alumno in alumnos:
                alumno_notas = SSA.get_notas_alumno_curso_prof(
                    rut_alum=alumno["rut_alum"],
                    curso_id=curso["codigo"],
                    correo_prof=correo_prof
                )
                for n in alumno_notas:
                    n["nom_alum"] = alumno["nom_alum"]
                    n["seg_nom_alum"] = alumno.get("seg_nom_alum")
                    n["ap_pat_alum"] = alumno["ap_pat_alum"]
                    n["ap_mat_alum"] = alumno.get("ap_mat_alum")
                    notas.append(n)
    return render_template("SSA/all_notas.html", notas=notas)
