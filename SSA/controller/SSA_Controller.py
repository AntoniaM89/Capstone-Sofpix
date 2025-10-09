import os
from flask import request, render_template, redirect, url_for, flash, session
from model import SSA
from model.SSA import NIVEL_MAP

# ================== Utilidades ==================
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

def set_flash(message, category="info"):
    session.pop('_flashes', None)
    flash(message, category)

def require_login():
    rol = session.get("rol")
    if not rol:
        set_flash("Debe iniciar sesión primero", "error")
        return redirect(url_for('login'))
    return rol

# ================== PROFESORES ==================
def add_profesor():
    if request.method == 'POST':
        correo = request.form['correo'].strip().lower()
        nombre = request.form['nombre'].strip()
        password = request.form['password'].strip()
        SSA.insert_profesor(correo, nombre, password)
        set_flash("Profesor agregado correctamente", "success")
        return redirect(url_for('list_profesores'))
    return render_template("agregar_profesor.html")

def detail_profesor(correo):
    profesor = SSA.get_profesor(correo)
    if not profesor:
        set_flash("Profesor no encontrado", "error")
        return redirect(url_for('list_profesores'))
    return render_template("detalle_profesor.html", profesor=profesor)

def update_profesor(correo):
    profesor = SSA.get_profesor(correo)
    if not profesor:
        set_flash("Profesor no encontrado", "error")
        return redirect(url_for('list_profesores'))

    if request.method == 'POST':
        SSA.update_profesor(
            correo=correo,
            nom_user=request.form.get('nom_user', '').strip(),
            seg_nom_user=request.form.get('seg_nom_user', '').strip(),
            ap_pat_user=request.form.get('ap_pat_user', '').strip(),
            ap_mat_user=request.form.get('ap_mat_user', '').strip(),
            pass_enc=request.form.get('pass_enc', '').strip(),
            area=request.form.get('area', '').strip()
        )
        set_flash("Profesor actualizado correctamente", "success")
        profesor = SSA.get_profesor(correo)
    return render_template("editar_profesor.html", profesor=profesor)

def delete_profesor(correo):
    profesor = SSA.get_profesor(correo)
    if not profesor:
        set_flash("Profesor no encontrado", "error")
        return redirect(url_for('list_profesores'))

    asignaturas = SSA.list_asignaturas_por_profesor(correo)
    tiene_dependencias = bool(asignaturas)

    if request.method == "POST":
        if tiene_dependencias:
            set_flash("No se puede eliminar: el profesor tiene asignaturas asignadas", "error")
            return redirect(url_for('list_profesores'))
        else:
            SSA.delete_profesor(correo)
            set_flash("Profesor eliminado correctamente", "success")
            return redirect(url_for('list_profesores'))

    return render_template(
        "eliminar_confirmacion.html",
        tipo="profesor",
        nombre=f"{profesor['nom_user']} {profesor['ap_pat_user']} {profesor['ap_mat_user']}",
        dependencias=tiene_dependencias,
        volver=url_for('list_profesores')
    )

def list_profesores():
    rol = session.get('rol')
    correo = session.get('correo_prof')

    if rol == 'admin':
        profesores = SSA.list_profesores()
    elif rol == 'profesor' and correo:
        prof = SSA.get_profesor(correo)
        profesores = [prof] if prof else []
    else:
        profesores = []

    return render_template("all_profesores.html", profesores=profesores)

# ================== ASIGNATURAS ==================
def add_asignatura():
    profesores = SSA.list_profesores()
    seleccion = request.form.get('nombre_asi') or None
    action_type = request.form.get('action_type', 'guardar')

    if request.method == 'POST':
        if action_type == 'seleccion':
            return render_template("agregar_asignatura.html",
                                   asign_map=ASIGN_MAP,
                                   profesores=profesores,
                                   seleccion=seleccion)

        elif action_type == 'guardar':
            profesor_correo = request.form.get('profesor_correo')

            if seleccion == "Otros":
                nombre = request.form.get('nombre_manual', '').capitalize().strip()
                base_codigo = request.form.get('codigo_manual', '').upper().strip()

                if not nombre or not base_codigo:
                    flash("Por favor completar los campos", "info")
                    return render_template("agregar_asignatura.html",
                                           asign_map=ASIGN_MAP,
                                           profesores=profesores,
                                           seleccion=seleccion)

                if SSA.codigo_base_exists(base_codigo):
                    flash(f"El código {base_codigo} ya existe", "warning")
                    return render_template("agregar_asignatura.html",
                                           asign_map=ASIGN_MAP,
                                           profesores=profesores,
                                           seleccion=seleccion)

                if SSA.nombre_asignatura_exists(nombre):
                    flash(f"La asignatura '{nombre}' ya existe", "warning")
                    return render_template("agregar_asignatura.html",
                                           asign_map=ASIGN_MAP,
                                           profesores=profesores,
                                           seleccion=seleccion)
            else:
                nombre = seleccion
                base_codigo = ASIGN_MAP.get(nombre)

            nuevo_codigo = SSA.generar_codigo_asignatura(base_codigo)

            SSA.add_asignatura(nuevo_codigo, nombre, profesor_correo)

            if seleccion == "Otros" and nombre not in ASIGN_MAP:
                ASIGN_MAP[nombre] = base_codigo

            return redirect(url_for('mis_asignaturas'))

    return render_template("agregar_asignatura.html",
                           asign_map=ASIGN_MAP,
                           profesores=profesores,
                           seleccion=seleccion)

def detail_asignatura(codigo):
    asignatura = SSA.get_asignatura(codigo)
    if not asignatura:
        set_flash("Asignatura no encontrada", "error")
        return redirect(url_for('mis_asignaturas'))
    return render_template("detalle_asignatura.html", asignatura=asignatura)

def update_asignatura(codigo):
    asignatura = SSA.get_asignatura(codigo)
    if not asignatura:
        set_flash("Asignatura no encontrada", "error")
        return redirect(url_for('mis_asignaturas'))

    profesores = SSA.list_profesores()
    if request.method == 'POST':
        nombre_asi = request.form['nombre_asi']
        profesor_correo = request.form['profesor_correo']
        try:
            SSA.update_asignatura(codigo_actual=codigo,
                                  nombre_asi=nombre_asi,
                                  profesor_correo=profesor_correo,
                                  asign_map=ASIGN_MAP)
            set_flash("Asignatura actualizada correctamente", "success")
            return redirect(url_for('mis_asignaturas'))
        except ValueError as ve:
            set_flash(str(ve), "error")
            return redirect(url_for('update_asignatura', codigo=codigo))

    return render_template("editar_asignatura.html", asignatura=asignatura, profesores=profesores, asign_map=ASIGN_MAP)

def delete_asignatura(codigo):
    asignatura = SSA.get_asignatura(codigo)
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
        eliminado, _ = SSA.delete_asignatura(codigo)  
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
    asignaturas = SSA.list_asignaturas()
    return render_template("all_asignaturas.html", asignaturas=asignaturas)

# ================== CURSOS ==================
def add_curso():
    if request.method == 'POST':
        nivel = request.form['nivel']
        generacion = request.form['generacion']
        prefijo = NIVEL_MAP.get(nivel)
        if not prefijo:
            set_flash("Nivel inválido", "error")
            return render_template("agregar_curso.html", NIVEL_MAP=NIVEL_MAP)

        id_curso = f"{prefijo}{generacion}"
        if SSA.curso_exists(id_curso):
            set_flash(f"Ya existe un curso con nivel '{nivel}' y generación '{generacion}'", "error")
            return redirect(url_for('list_cursos'))

        SSA.add_curso(id_curso, nivel, generacion)
        set_flash("Curso creado correctamente", "success")
        return redirect(url_for('list_cursos'))

    return render_template("agregar_curso.html", NIVEL_MAP=NIVEL_MAP)

def detail_curso(id_curso):
    curso = SSA.get_curso(id_curso)
    if not curso:
        flash("Curso no encontrado", "error")
        return redirect(url_for('list_cursos'))

    asignatura = SSA.get_asignatura(curso['codigo_asignatura'])
    profesor = SSA.get_profesor(asignatura['profesor_correo'])

    return render_template(
        "detalle_curso.html",
        curso=curso,
        asignatura_nombre=asignatura['nombre_asi'],
        profesor_nombre=f"{profesor['nom_user']} {profesor['ap_pat_user']}",
        codigo_asignatura=curso['codigo_asignatura'],   
        id_curso=curso['id_curso']                     
    )


from mysql.connector import IntegrityError

def update_curso(id_curso):
    curso = SSA.get_curso(id_curso)
    if not curso:
        set_flash("Curso no encontrado.", "error")
        return redirect(url_for('list_cursos'))

    if request.method == 'POST':
        nivel = request.form['nivel']
        generacion = request.form['generacion']
        prefijo = NIVEL_MAP.get(nivel)
        if not prefijo:
            set_flash("Nivel inválido", "error")
            return render_template("editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)

        nuevo_id_curso = f"{prefijo}{generacion}"
        if nuevo_id_curso != id_curso and SSA.curso_exists(nuevo_id_curso):
            set_flash(f"Ya existe un curso con nivel '{nivel}' y generación '{generacion}'", "error")
            return render_template("editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)

        try:
            SSA.update_curso(id_curso, nivel=nivel, generacion=generacion)
            set_flash("Curso actualizado correctamente.", "success")
            return redirect(url_for('list_cursos'))
        except IntegrityError:
            set_flash("No se puede actualizar el curso porque tiene alumnos asociados.", "error")
            return render_template("editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)
        except Exception as e:
            set_flash(f"Ocurrió un error al actualizar el curso: {e}", "error")
            return render_template("editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)

    return render_template("editar_curso.html", curso=curso, NIVEL_MAP=NIVEL_MAP)


def delete_curso(id_curso):
    curso = SSA.get_curso(id_curso)
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
            SSA.delete_curso(id_curso)
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
    rol = session.get('rol')
    correo_prof = session.get('correo_prof')

    cursos = SSA.list_cursos()

    for curso in cursos:
        curso_id = curso['id_curso']
        curso['alumnos'] = SSA.get_alumnos_por_curso(curso_id)

        if rol == 'profesor':
            curso['asignaturas'] = SSA.list_asignaturas_por_curso_profesor(curso_id, correo_prof)
        else:
            curso['asignaturas'] = SSA.list_asignaturas_por_curso(curso_id)

    return render_template("all_cursos.html", cursos=cursos, rol=rol)

# ================== ALUMNOS ==================
def add_alumno():
    if request.method == 'POST':
        rut = request.form['rut']
        nombre = request.form['nombre']
        SSA.insert_alumno(rut, nombre)
        set_flash("Alumno agregado correctamente", "success")
        return redirect(url_for('list_alumnos'))
    return render_template("agregar_alumno.html")

def detail_alumno(rut_alum):
    alumno = SSA.get_alumno(rut_alum)
    if not alumno:
        set_flash("Alumno no encontrado", "error")
        return redirect(url_for('list_alumnos'))
    notas = SSA.get_notas_alumno(rut_alum)
    return render_template("detalle_alumno.html", alumno=alumno, notas=notas)


def update_alumno(rut_alum):
    alumno = SSA.get_alumno(rut_alum)
    if request.method == 'POST':
        SSA.update_alumno(rut_alum, request.form['nombre'])
        set_flash("Alumno actualizado correctamente", "success")
        return redirect(url_for('list_alumnos'))
    return render_template("editar_alumno.html", alumno=alumno)

def delete_alumno(rut_alum):
    alumno = SSA.get_alumno(rut_alum)
    if not alumno:
        set_flash("Alumno no encontrado.", "error")
        return redirect(url_for('list_alumnos'))

    notas = SSA.get_notas_alumno(rut_alum)
    tiene_dependencias = bool(notas)

    if request.method == "POST":
        if tiene_dependencias:
            set_flash("No se puede eliminar: el alumno tiene notas registradas", "error")
            return redirect(url_for('list_alumnos'))
        else:
            SSA.delete_alumno(rut_alum)
            set_flash("Alumno eliminado correctamente", "success")
            return redirect(url_for('list_alumnos'))

    return render_template(
        "eliminar_confirmacion.html",
        tipo="alumno",
        nombre=alumno['nombre'],
        dependencias=tiene_dependencias,
        volver=url_for('list_alumnos')
    )



def list_alumnos():
    alumnos = SSA.list_alumnos()
    return render_template("all_alumnos.html", alumnos=alumnos)

# ================== NOTAS ==================
def add_nota():
    cursos = SSA.list_cursos()
    curso_seleccionado = request.form.get('curso_id') 
    alumnos = SSA.get_alumnos_por_curso(curso_seleccionado) if curso_seleccionado else []
    asignaturas = SSA.list_asignaturas()

    if request.method == 'POST' and request.form.get('action') == 'guardar':
        alumno_rut = request.form['alumno_rut_alum']
        nombre_eval = request.form['nombre']
        nota = request.form['nota']
        asignatura_codigo = request.form['asignatura_codigo']

        id_nota = f"{asignatura_codigo}{curso_seleccionado}{alumno_rut}{nombre_eval}"
        SSA.add_nota(id_nota, asignatura_codigo, curso_seleccionado, alumno_rut, nombre_eval, nota)
        set_flash("Nota agregada correctamente", "success")
        return redirect(url_for('list_notas'))

    return render_template("agregar_nota.html", cursos=cursos, curso_seleccionado=curso_seleccionado, alumnos=alumnos, asignaturas=asignaturas)

def detail_nota(id_nota):
    nota = SSA.get_nota(id_nota)
    return render_template("detalle_nota.html", nota=nota)


def update_nota(id_nota):
    nota = SSA.get_nota(id_nota)
    if not nota:
        set_flash("Nota no encontrada", "error")
        return redirect(url_for('list_notas'))

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre'].upper()
        nueva_nota = request.form['nota']
        nuevo_id = f"{nota['asignatura_codigo']}{nota['codigo_curso']}{nota['alumno_rut_alum']}{nuevo_nombre}"
        SSA.update_nota(id_nota, nuevo_id, nueva_nota, nuevo_nombre)
        set_flash("Nota actualizada correctamente", "success")
        return redirect(url_for('list_notas'))

    return render_template("editar_nota.html", nota=nota)

def delete_nota(id_nota):
    nota = SSA.get_nota(id_nota)
    if not nota:
        set_flash("Nota no encontrada.", "error")
        return redirect(url_for('list_notas'))

    tiene_dependencias = False

    if request.method == "POST":
        SSA.delete_nota(id_nota)
        set_flash("Nota eliminada correctamente", "success")
        return redirect(url_for('list_notas'))

    return render_template(
        "eliminar_confirmacion.html",
        tipo="nota",
        nombre=f"{nota['nombre_eval']} - {nota['alumno_rut_alum']}",
        dependencias=tiene_dependencias,
        volver=url_for('list_notas')
    )


def list_notas():
    notas = SSA.list_notas()
    return render_template("all_notas.html", notas=notas)

# ================== LOGIN ==================
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip().lower()
        pass_enc = request.form["pass_enc"]
        prof = SSA.get_profesor(correo)

        if prof and prof.get('correo') == correo and prof.get('pass_enc') == pass_enc:
            session['correo_prof'] = correo
            session['rol'] = prof.get('rol', 'profesor')
            return redirect(url_for('home'))
        else:
            set_flash("Correo o contraseña incorrectos", "error")

    return render_template("sign_in.html")

# ================== VISTAS PROFESORES ==================
def mis_asignaturas():
    rol = require_login()
    if isinstance(rol, str) and rol.startswith('redirect'):
        return rol

    correo_prof = session.get("correo_prof")
    if rol == "profesor":
        asignaturas = SSA.get_asignaturas_por_profesor(correo_prof)
        for asi in asignaturas:
            cursos_raw = SSA.list_cursos_por_asignatura_prof(asi['codigo'], correo_prof)
            cursos = [{"codigo": c["id_curso"], "nombre": f"{c['nivel']} {c['generacion']}"} for c in cursos_raw]
            asi["cursos"] = cursos
    else: 
        asignaturas = SSA.get_all_asignaturas_y_cursos()

    return render_template("all_asignaturas.html", asignaturas=asignaturas)

def detalle_curso_prof_asignatura(codigo_asignatura, codigo_curso):
    rol = require_login()
    if isinstance(rol, str) and rol.startswith('redirect'):
        return rol

    curso_raw = SSA.get_curso(codigo_curso)
    asignatura_raw = SSA.get_asignatura(codigo_asignatura)

    if not curso_raw or not asignatura_raw:
        set_flash("Curso o asignatura no encontrado", "error")
        return redirect(url_for('mis_asignaturas'))

    alumnos_raw = SSA.get_alumnos_por_curso(codigo_curso)

    alumnos = []
    for alumno in alumnos_raw:
        notas_filtradas = SSA.get_notas_alumno_asignatura(alumno["rut_alum"], codigo_asignatura, codigo_curso)
        alumno["notas"] = notas_filtradas
        alumnos.append(alumno)

    curso = {
        "nivel": curso_raw["nivel"],
        "generacion": curso_raw["generacion"],
        "alumnos": alumnos
    }

    profesor_nombre = asignatura_raw.get("profesor", "Profesor desconocido")

    return render_template(
        "detalle_curso.html",
        curso=curso,
        asignatura_nombre=asignatura_raw["nombre_asi"],
        profesor_nombre=profesor_nombre,
        codigo_asignatura=codigo_asignatura,
        id_curso=codigo_curso
    )


def alumnos_por_curso(id_curso):
    rol = session.get("rol")
    correo_prof = session.get("correo_prof")

    if not rol:
        set_flash("Debe iniciar sesión primero", "error")
        return redirect(url_for('login'))

    curso_raw = SSA.get_curso(id_curso)
    if not curso_raw:
        set_flash("Curso no encontrado", "error")
        return redirect(url_for('mis_asignaturas'))

    curso = {
        "nivel": curso_raw["nivel"],
        "generacion": curso_raw["generacion"],
        "alumnos": SSA.get_alumnos_por_curso(id_curso)
    }

    return render_template("detalle_alumnos.html", curso=curso)


def detail_alumno_notas(rut_alum):
    alumno = SSA.get_alumno(rut_alum)
    if not alumno:
        set_flash("Alumno no encontrado", "error")
        return redirect(url_for('mis_asignaturas'))

    notas = SSA.get_notas_alumno(rut_alum)
    print(notas)
    return render_template("detalle_nota.html", alumno=alumno, notas=notas)

def detail_alumno_notas_asignatura(rut_alum, codigo_asignatura, id_curso):
    alumno = SSA.get_alumno(rut_alum)
    if not alumno:
        set_flash("Alumno no encontrado", "error")
        return redirect(url_for('mis_asignaturas'))

    curso = SSA.get_curso(id_curso)
    if not curso:
        set_flash("Curso no encontrado", "error")
        return redirect(url_for('mis_asignaturas'))

    asignatura = SSA.get_asignatura(codigo_asignatura)
    if not asignatura:
        set_flash("Asignatura no encontrada", "error")
        return redirect(url_for('mis_asignaturas'))

    notas = SSA.get_notas_alumno_asignatura(rut_alum, codigo_asignatura, id_curso)

    return render_template("detalle_nota_asignatura.html", alumno=alumno, curso=curso, asignatura=asignatura, notas=notas,codigo_asignatura=codigo_asignatura,  # ← nuevo
    id_curso=id_curso)


def detalle_curso_general(id_curso):
    rol = require_login()
    if isinstance(rol, str) and rol.startswith('redirect'):
        return rol

    curso_raw = SSA.get_curso(id_curso)
    if not curso_raw:
        set_flash("Curso no encontrado", "error")
        return redirect(url_for('list_cursos'))

    alumnos = SSA.get_alumnos_por_curso(id_curso)
    
    asignaturas = SSA.list_asignaturas_por_curso(id_curso)

    return render_template(
        "detalle_curso.html",
        curso=curso_raw,
        alumnos=alumnos,
        asignaturas=asignaturas
    )
