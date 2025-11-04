import os
from flask import request, render_template, redirect, url_for, flash, session
from mysql.connector import IntegrityError
from model.SSA import NIVEL_MAP
from model import SSA, profesores_mod, cursos_mod, biblioteca
from controller.SSA_Controller import set_flash



# ================== PROFESORES ==================
def add_profesor():
    if request.method == 'POST':
        correo = request.form['correo'].strip().lower()
        nombre = request.form['nom_user'].strip()
        seg_nom = request.form['seg_nom_user'].strip()
        ap_pat = request.form['ap_pat_user'].strip()
        ap_mat = request.form['ap_mat_user'].strip()
        password = request.form['pass_enc'].strip()
        area = request.form['area'].strip()

        if profesores_mod.profesor_exists(correo):
            set_flash("Correo ya registrado, por favor usa otro", "error")
            return render_template("login/sign_up.html",
                                   correo=correo,
                                   nombre=nombre,
                                   seg_nom=seg_nom,
                                   ap_pat=ap_pat,
                                   ap_mat=ap_mat,
                                   area=area)

        profesores_mod.add_profesor(correo, nombre, seg_nom, ap_pat, ap_mat, password, area)
        set_flash("Profesor agregado correctamente", "success")
        return redirect(url_for('list_profesores'))

    return render_template("login/sign_up.html")

def detail_profesor(correo):
    profesor = profesores_mod.get_profesor(correo)
    if not profesor:
        set_flash("Profesor no encontrado", "error")
        return redirect(url_for('list_profesores'))
    return render_template("SSA/detalle_profesor.html", profesor=profesor)

def update_profesor(correo):
    profesor = profesores_mod.get_profesor(correo)
    if not profesor:
        flash("Profesor no encontrado", "error")
        return redirect(url_for('list_profesores'))

    if request.method == 'POST':
        profesores_mod.update_profesor(
            correo=correo,
            nom_user=request.form.get('nom_user', '').strip(),
            seg_nom_user=request.form.get('seg_nom_user', '').strip(),
            ap_pat_user=request.form.get('ap_pat_user', '').strip(),
            ap_mat_user=request.form.get('ap_mat_user', '').strip(),
            pass_enc=request.form.get('pass_enc', '').strip(),
            area=request.form.get('area', '').strip()
        )
        flash("Profesor actualizado correctamente", "success")
        return redirect(url_for('list_profesores'))

    return render_template("SSA/editar_profesor.html", profesor=profesor)

def delete_profesor(correo):
    profesor = profesores_mod.get_profesor(correo)
    if not profesor:
        set_flash("Profesor no encontrado", "error")
        return redirect(url_for('list_profesores'))

    asignaturas = SSA.list_asignaturas_por_profesor(correo)
    tiene_dependencias = bool(asignaturas)

    archivos_biblio = biblioteca.obtener_archivos_por_profesor(correo)
    if request.method == "POST":
        
        if tiene_dependencias:
            set_flash("No se puede eliminar: el profesor tiene asignaturas asignadas", "error")
            return redirect(url_for('list_profesores'))
        
        if archivos_biblio:
            biblioteca.actualizar_autor_biblioteca(correo, "admin@colegio.cl")

        profesores_mod.delete_profesor(correo)

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
        profesores = profesores_mod.list_profesores()
    elif rol == 'profesor' and correo:
        prof = profesores_mod.get_profesor(correo)
        profesores = [prof] if prof else []
    else:
        profesores = []

    return render_template("SSA/all_profesores.html", profesores=profesores)




        # Generar hash Argon2id seguro
        try:
            hashed_password = ph.hash(password)
        except Exception as e:
            print("Error generando hash Argon2id:", e)
            set_flash("Error interno al crear cuenta", "error")
            return render_template("login/sign_up.html")

        # Guardar en BD el hash
        profesores_mod.add_profesor(
            correo,
            nombre,
            seg_nom,
            ap_pat,
            ap_mat,
            hashed_password, # Aca ahora va el hash, no la contraseña plana
            area
        )

        set_flash("Profesor agregado correctamente", "success")
        return redirect(url_for('list_profesores'))

    #Si es GET mostramos el formulario de register
    return render_template("login/sign_up.html")