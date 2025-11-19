import os
from flask import request, render_template, redirect, url_for, flash, session
from mysql.connector import IntegrityError
from model.SSA import NIVEL_MAP
from model import SSA, asignaturas_mod, cursos_mod, profesores_mod
from controller.SSA_Controller import set_flash


ASIGN_MAP = {
    "Matematicas": "MAT",
    "Lenguaje y Comunicaciones": "LYC",
    "Consejo de Curso": "CCU",
    "Tecnologia": "TEC",
    "Ciencias": "CIE",
    "Historia": "HIS",
    "Musica": "MUS",
    "Artes": "ART",
    "Ingles": "ENG",
    "Religion": "REL",
    "Educacion Fisica": "EFI",
    "Orientacion": "ORI",
    "Filosofia": "FIL",
    "Biologia": "BIO",
    "Fisica": "FIS",
    "Quimica": "QUI",
}

# ================== ASIGNATURAS ==================
def add_asignatura():
    profesores = profesores_mod.list_profesores()
    seleccion = request.form.get('nombre_asi') or None
    action_type = request.form.get('action_type', 'guardar')

    if request.method == 'POST':
        if action_type == 'seleccion':
            return render_template("SSA/agregar_asignatura.html",
                                   asign_map=ASIGN_MAP,
                                   profesores=profesores,
                                   seleccion=seleccion)

        elif action_type == 'guardar':
            profesor_correo = request.form.get('profesor_correo')

            if seleccion == "Otros":
                nombre = request.form.get('nombre_manual', '').capitalize().strip()
                base_codigo = request.form.get('codigo_manual', '').upper().strip()

                if not nombre or not base_codigo:
                    flash("Por favor completar todos los campos", "info")
                    return render_template("SSA/agregar_asignatura.html",
                                           asign_map=ASIGN_MAP,
                                           profesores=profesores,
                                           seleccion=seleccion)

                if SSA.codigo_base_exists(base_codigo):
                    flash(f"El código {base_codigo} ya existe", "warning")
                    return render_template("SSA/agregar_asignatura.html",
                                           asign_map=ASIGN_MAP,
                                           profesores=profesores,
                                           seleccion=seleccion)

                if SSA.nombre_asignatura_exists(nombre):
                    flash(f"La asignatura '{nombre}' ya existe", "warning")
                    return render_template("SSA/agregar_asignatura.html",
                                           asign_map=ASIGN_MAP,
                                           profesores=profesores,
                                           seleccion=seleccion)
            else:
                nombre = seleccion
                base_codigo = ASIGN_MAP.get(nombre)

            nuevo_codigo = SSA.generar_codigo_asignatura(base_codigo)
            asignaturas_mod.add_asignatura(nuevo_codigo, nombre, profesor_correo)

            if seleccion == "Otros" and nombre not in ASIGN_MAP:
                ASIGN_MAP[nombre] = base_codigo

            flash("Asignatura creada exitosamente", "success")
            return redirect(url_for('mis_asignaturas'))

    return render_template("SSA/agregar_asignatura.html",
                           asign_map=ASIGN_MAP,
                           profesores=profesores,
                           seleccion=seleccion)


def detail_asignatura(codigo):
    asignatura = asignaturas_mod.get_asignatura(codigo)
    if not asignatura:
        set_flash("Asignatura no encontrada", "error")
        return redirect(url_for('mis_asignaturas'))
    return render_template("SSA/detalle_asignatura.html", asignatura=asignatura)

def update_asignatura(codigo):
    asignatura = asignaturas_mod.get_asignatura(codigo)
    if not asignatura:
        set_flash("Asignatura no encontrada", "error")
        return redirect(url_for('mis_asignaturas'))

    profesores = profesores_mod.list_profesores()
    if request.method == 'POST':
        nombre_asi = request.form['nombre_asi']
        profesor_correo = request.form['profesor_correo']
        try:
            asignaturas_mod.update_asignatura(codigo_actual=codigo,
                                  nombre_asi=nombre_asi,
                                  profesor_correo=profesor_correo,
                                  asign_map=ASIGN_MAP)
            set_flash("Asignatura actualizada correctamente", "success")
            return redirect(url_for('mis_asignaturas'))
        except ValueError as ve:
            set_flash(str(ve), "error")
            return redirect(url_for('update_asignatura', codigo=codigo))

    return render_template("SSA/editar_asignatura.html", asignatura=asignatura, profesores=profesores, asign_map=ASIGN_MAP)

def delete_asignatura(codigo):
    asignatura = asignaturas_mod.get_asignatura(codigo)
    if not asignatura:
        set_flash("Asignatura no encontrada.", "error")
        return redirect(url_for("mis_asignaturas"))

    notas_count = SSA.count_notas_asignatura(codigo) if hasattr(SSA, 'count_notas_asignatura') else 0
    cursos_count = SSA.count_cursos_asignatura(codigo) if hasattr(SSA, 'count_cursos_asignatura') else 0

    dependencias = notas_count + cursos_count
    tiene_dependencias = dependencias > 0

    if request.method == "POST":
        if tiene_dependencias:
            set_flash("No se puede eliminar: la asignatura tiene cursos o notas asociadas", "error")
            return redirect(url_for("mis_asignaturas"))
        eliminado, _ = asignaturas_mod.delete_asignatura(codigo)  
        if eliminado:
            set_flash("Asignatura eliminada correctamente", "success")
        else:
            set_flash("No se pudo eliminar la asignatura", "error")
        return redirect(url_for("mis_asignaturas"))

    return render_template(
        "eliminar_confirmacion.html",
        tipo="asignatura",
        nombre=f"{asignatura['nombre_asi']} ({asignatura['codigo']})",
        dependencias=tiene_dependencias,
        volver=url_for("mis_asignaturas")
    )



def list_asignaturas():
    rol = require_login()
    if isinstance(rol, str) and rol.startswith('redirect'):
        return rol

    correo_prof = session.get("correo_prof")

    if rol == "admin":
        asignaturas = SSA.get_all_asignaturas_y_cursos()
    else:
        asignaturas = SSA.get_asignaturas_por_profesor(correo_prof)
        for asi in asignaturas:
            cursos_raw = SSA.list_cursos_por_asignatura_prof(asi['codigo'], correo_prof)
            asi["cursos"] = [
                {"codigo": c["id_curso"], "nombre": f"{c['nivel']} {c['generacion']}"}
                for c in cursos_raw
            ]

    return render_template("SSA/all_asignaturas.html", asignaturas=asignaturas)
