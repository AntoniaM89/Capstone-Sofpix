from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from config import get_connection
from datetime import datetime
import traceback

app = Flask(__name__)
app.secret_key = "supersecret12348765" #Aca puede ir cualquier cosa, es para mandar mensajes de debug

# Asignaturas predefinidas, se guarda fuera para poder agregar mas despues
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
    "Orientacion": "ORI" 
}

def set_flash(message, category="info"):
    session.pop('_flashes', None)  # Limpiar mensajes
    flash(message, category)

@app.route('/')
def home():
    return render_template('index.html')


## PROFESOR ##
# Create
@app.route('/profesores/nuevo', methods=['GET', 'POST'])
def agregar_profesor():
    if request.method == 'POST':
        data = {
            "correo": request.form["correo"].strip().lower(), 
            "nom_user": request.form["nom_user"].strip(),
            "seg_nom_user": request.form.get("seg_nom_user", "").strip() or None,
            "ap_pat_user": request.form["ap_pat_user"].strip(),
            "ap_mat_user": request.form.get("ap_mat_user", "").strip() or None,
            "pass_enc": request.form["pass_enc"],
            "area": request.form["area"]
        }
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Verificar si el correo ya existe
            cur.execute("SELECT COUNT(*) FROM profesor WHERE correo = :1", (data["correo"],))
            if cur.fetchone()[0] > 0:
                set_flash("Ya existe un profesor con este correo", "error")
                return redirect(url_for('listar_profesores'))

            # Insertar si no existe
            cur.execute("""
                INSERT INTO profesor 
                (correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, tuple(data.values()))
            conn.commit()
            set_flash("Profesor agregado correctamente", "success")
            return redirect(url_for('listar_profesores'))
        except Exception as e:
            set_flash(f"Error al agregar profesor: {str(e)}", "error")
        finally:
            if cur: cur.close()
            if conn: conn.close()
    return render_template('agregar_profesor.html')


# Read
@app.route('/profesores/<correo>')
def detalle_profesor(correo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, area FROM profesor WHERE correo = :1", (correo,))
        profesor = cur.fetchone()
        if not profesor:
            set_flash("Profesor no encontrado", "error")
            return redirect(url_for('listar_profesores'))
        return render_template('detalle_profesor.html', profesor=profesor)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Update
@app.route('/profesores/editar/<correo>', methods=['GET', 'POST'])
def editar_profesor(correo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area FROM profesor WHERE correo = :1", (correo,))
        profesor = cur.fetchone()
        if not profesor:
            set_flash("Profesor no encontrado", "error")
            return redirect(url_for('listar_profesores'))

        if request.method == 'POST':
            data = {
                "nom_user": request.form["nom_user"],
                "seg_nom_user": request.form.get("seg_nom_user"),
                "ap_pat_user": request.form["ap_pat_user"],
                "ap_mat_user": request.form.get("ap_mat_user"),
                "pass_enc": request.form["pass_enc"],
                "area": request.form["area"]
            }
            try:
                cur.execute("""
                    UPDATE profesor
                    SET nom_user = :1, seg_nom_user = :2, ap_pat_user = :3, ap_mat_user = :4, pass_enc = :5, area = :6
                    WHERE correo = :7
                """, (data["nom_user"], data["seg_nom_user"], data["ap_pat_user"], data["ap_mat_user"], data["pass_enc"], data["area"], correo))
                conn.commit()
                set_flash("Profesor actualizado correctamente", "success")
            except Exception as e:
                set_flash(f"Error: {str(e)}", "error")
            return redirect(url_for('listar_profesores'))

        return render_template('editar_profesor.html', profesor=profesor)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Delete
@app.route('/profesores/eliminar/<correo>', methods=['GET', 'POST'])
def eliminar_profesor(correo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT correo, nom_user, ap_pat_user FROM profesor WHERE correo = :1", (correo,))
        profesor = cur.fetchone()
        if not profesor:
            set_flash("Profesor no encontrado", "error")
            return redirect(url_for('listar_profesores'))

        if request.method == 'POST':
            cur.execute("DELETE FROM profesor WHERE correo = :1", (correo,))
            conn.commit()
            set_flash("Profesor eliminado correctamente", "success")
            return redirect(url_for('listar_profesores'))

        return render_template('eliminar_profesor.html', profesor=profesor)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# List
@app.route('/profesores')
def listar_profesores():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, area FROM profesor")
        profesores = cur.fetchall()
        return render_template('all_profesores.html', profesores=profesores)
    finally:
        if cur: cur.close()
        if conn: conn.close()


## ASIGNATURAS ##
# Create
@app.route('/asignaturas/nueva', methods=['GET', 'POST'])
def agregar_asignatura():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        asignaturas = list(ASIGN_MAP.keys())

        # Listar Profesores
        cur.execute("""
            SELECT correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user 
            FROM profesor 
            ORDER BY nom_user
        """)
        profesores = cur.fetchall()

        seleccion = request.form.get('nombre_asi')

        if request.method == 'POST' and request.form.get('action') == 'guardar':
            profesor_correo = request.form.get("profesor_correo")

            # Si se selecciona "Otros"
            if seleccion == "Otros":
                nombre_asi = request.form.get("nombre_manual", "").strip()
                codigo_asi = request.form.get("codigo_manual", "").strip().upper()

                if not nombre_asi or not codigo_asi:
                    set_flash("Debe ingresar nombre y código para asignatura 'Otros'", "error")
                    return render_template('agregar_asignatura.html', asignaturas=asignaturas,
                                           profesores=profesores, seleccion=seleccion)

                # Agregar al ASIGN_MAP
                ASIGN_MAP[nombre_asi] = codigo_asi
                asignaturas = list(ASIGN_MAP.keys())

            else:
                nombre_asi = seleccion
                codigo_asi = ASIGN_MAP.get(nombre_asi, nombre_asi[:3].upper())

            cur.execute("SELECT codigo_seq.NEXTVAL FROM dual")
            seq_val = cur.fetchone()[0]

            # Concatenar código y asignatura
            codigo_asi_full = f"{codigo_asi}{seq_val}"

            # Nombre completo del profesor
            prof_seleccionado = next((p for p in profesores if p[0] == profesor_correo), None)
            if not prof_seleccionado:
                set_flash("Profesor seleccionado no válido", "error")
                return render_template('agregar_asignatura.html', asignaturas=asignaturas,
                                       profesores=profesores, seleccion=seleccion)
            nombre_prof = f"{prof_seleccionado[1]} {prof_seleccionado[2] or ''} {prof_seleccionado[3]} {prof_seleccionado[4] or ''}".strip()

            # Verificar si ya existe en DB (con el código completo)
            cur.execute("SELECT COUNT(*) FROM asignatura WHERE codigo = :1", (codigo_asi_full,))
            if cur.fetchone()[0] > 0:
                set_flash("Ya existe una asignatura con este código", "error")
                return redirect(url_for('listar_asignaturas'))

            # Insertar
            try:
                cur.execute("""
                    INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
                    VALUES (:1, :2, :3, :4)
                """, (codigo_asi_full, nombre_asi, nombre_prof, profesor_correo))
                conn.commit()
                set_flash("Asignatura agregada correctamente", "success")
                return redirect(url_for('listar_asignaturas'))
            except Exception as e:
                set_flash(f"Error al agregar asignatura: {str(e)}", "error")

        return render_template('agregar_asignatura.html', asignaturas=asignaturas,
                               profesores=profesores, seleccion=seleccion)
    finally:
        if cur: cur.close()
        if conn: conn.close()


# Read
@app.route('/asignaturas/<codigo>')
def detalle_asignatura(codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.codigo,
                   a.nombre_asi,
                   p.nom_user || ' ' || NVL(p.seg_nom_user,'') || ' ' || p.ap_pat_user || ' ' || NVL(p.ap_mat_user,'') AS nombre_prof,
                   a.profesor_correo
            FROM asignatura a
            JOIN profesor p ON a.profesor_correo = p.correo
            WHERE a.codigo = :1
        """, (codigo,))
        asignatura = cur.fetchone()
        if not asignatura:
            set_flash("Asignatura no encontrada", "error")
            return redirect(url_for('listar_asignaturas'))
        return render_template('detalle_asignatura.html', asignatura=asignatura)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Update
@app.route('/asignaturas/editar/<codigo>', methods=['GET', 'POST'])
def editar_asignatura(codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user FROM profesor ORDER BY nom_user")
        profesores = cur.fetchall()

        cur.execute("SELECT codigo, nombre_asi, profesor_correo FROM asignatura WHERE codigo = :1", (codigo,))
        asignatura = cur.fetchone()
        if not asignatura:
            set_flash("Asignatura no encontrada", "error")
            return redirect(url_for('listar_asignaturas'))

        if request.method == 'POST':
            nombre_asi = request.form.get("nombre_asi")
            profesor_correo = request.form.get("profesor_correo")

            if not nombre_asi or not profesor_correo:
                set_flash("Debe completar todos los campos", "error")
                return render_template('editar_asignatura.html', asignatura=asignatura, profesores=profesores)

            try:
                cur.execute("UPDATE asignatura SET nombre_asi = :1, profesor_correo = :2 WHERE codigo = :3",
                            (nombre_asi, profesor_correo, codigo))
                conn.commit()
                set_flash("Asignatura actualizada correctamente", "success")
                return redirect(url_for('listar_asignaturas'))
            except Exception as e:
                set_flash(f"Error: {str(e)}", "error")

        return render_template('editar_asignatura.html', asignatura=asignatura, profesores=profesores)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Delete
@app.route('/asignaturas/eliminar/<codigo>', methods=['GET', 'POST'])
def eliminar_asignatura(codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT codigo, nombre_asi FROM asignatura WHERE codigo = :1", (codigo,))
        asignatura = cur.fetchone()
        if not asignatura:
            set_flash("Asignatura no encontrada", "error")
            return redirect(url_for('listar_asignaturas'))

        if request.method == 'POST':
            cur.execute("DELETE FROM asignatura WHERE codigo = :1", (codigo,))
            conn.commit()
            set_flash("Asignatura eliminada correctamente", "success")
            return redirect(url_for('listar_asignaturas'))

        return render_template('eliminar_asignatura.html', asignatura=asignatura)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# List
@app.route('/asignaturas')
def listar_asignaturas():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.codigo,
                   a.nombre_asi,
                   p.nom_user || ' ' || NVL(p.seg_nom_user,'') || ' ' || p.ap_pat_user || ' ' || NVL(p.ap_mat_user,'') AS nombre_prof,
                   a.profesor_correo
            FROM asignatura a
            JOIN profesor p ON a.profesor_correo = p.correo
            ORDER BY a.codigo
        """)
        asignaturas = cur.fetchall()
        return render_template('all_asignaturas.html', asignaturas=asignaturas)
    finally:
        if cur: cur.close()
        if conn: conn.close()


## CURSO  ##
# Create
@app.route('/cursos/nuevo', methods=['GET', 'POST'])
def agregar_curso():
    if request.method == 'POST':
        nivel = request.form['nivel']
        generacion = request.form['generacion']

        # Diccionario para estandarizar los niveles de los cursos, lo mantenemos dentro de la funcion
        # Porque es un numero no variable
        NIVEL_MAP = {
            "Pre Kinder": "0PK",
            "Kinder": "00K",
            "1 Basico": "001",
            "2 Basico": "002",
            "3 Basico": "003",
            "4 Basico": "004",
            "5 Basico": "005",
            "6 Basico": "006",
            "7 Basico": "007",
            "8 Basico": "008",
            "I Medio": "009",
            "II Medio": "010",
            "III Medio": "011",
            "IV Medio": "012"
        }

        nivel_codigo = NIVEL_MAP.get(nivel)
        if not nivel_codigo:
            set_flash("Nivel no válido", "error")
            return redirect(url_for('listar_cursos'))

        id_curso = f"{nivel_codigo}{generacion}"

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM curso WHERE id_curso = :1", (id_curso,))
            if cur.fetchone()[0] > 0:
                set_flash("El curso ya existe", "error")
                return redirect(url_for('listar_cursos'))

            cur.execute("INSERT INTO curso (id_curso, nivel, generacion) VALUES (:1, :2, :3)",
                        (id_curso, nivel, generacion))
            conn.commit()
            set_flash("Curso agregado con éxito", "success")
            return redirect(url_for('listar_cursos'))
        except Exception as e:
            set_flash(f"Error al agregar curso: {str(e)}", "error")
            return redirect(url_for('listar_cursos'))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template("agregar_curso.html")

# Read
@app.route('/cursos/<id_curso>')
def detalle_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_curso, nivel, generacion FROM curso WHERE id_curso = :1", (id_curso,))
        curso = cur.fetchone()
        if not curso:
            set_flash("Curso no encontrado", "error")
            return redirect(url_for('listar_cursos'))
        return render_template("detalle_curso.html", curso=curso)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Update
@app.route('/cursos/editar/<id_curso>', methods=['GET', 'POST'])
def editar_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_curso, nivel, generacion FROM curso WHERE id_curso = :1", (id_curso,))
        curso = cur.fetchone()
        if not curso:
            set_flash("Curso no encontrado", "error")
            return redirect(url_for('listar_cursos'))

        if request.method == 'POST':
            nivel = request.form['nivel']
            generacion = request.form['generacion']

            cur.execute("UPDATE curso SET nivel = :1, generacion = :2 WHERE id_curso = :3",
                        (nivel, generacion, id_curso))
            conn.commit()
            set_flash("Curso actualizado correctamente", "success")
            return redirect(url_for('listar_cursos'))

        return render_template("editar_curso.html", curso=curso)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Delete
@app.route('/cursos/eliminar/<id_curso>', methods=['GET', 'POST'])
def eliminar_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_curso, nivel, generacion FROM curso WHERE id_curso = :1", (id_curso,))
        curso = cur.fetchone()
        if not curso:
            set_flash("Curso no encontrado", "error")
            return redirect(url_for('listar_cursos'))

        if request.method == 'POST':
            cur.execute("DELETE FROM curso WHERE id_curso = :1", (id_curso,))
            conn.commit()
            set_flash("Curso eliminado correctamente", "success")
            return redirect(url_for('listar_cursos'))

        return render_template("eliminar_curso.html", curso=curso)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# List
@app.route('/cursos')
def listar_cursos():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_curso, nivel, generacion FROM curso ORDER BY generacion, nivel")
        cursos = cur.fetchall()
        return render_template("all_cursos.html", cursos=cursos)
    finally:
        if cur: cur.close()
        if conn: conn.close()

## ALUMNO ##
# Create
@app.route('/alumnos/nuevo', methods=['GET', 'POST'])
def agregar_alumno():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Traer cursos para el dropdown
        cur.execute("SELECT id_curso, nivel, generacion FROM curso ORDER BY generacion, nivel")
        cursos = cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

    if request.method == 'POST':
        rut_alum = request.form['rut_alum']
        nom_alum = request.form['nom_alum']
        seg_nom_alum = request.form.get('seg_nom_alum')
        ap_pat_alum = request.form['ap_pat_alum']
        ap_mat_alum = request.form.get('ap_mat_alum')
        curso_id = request.form['curso_id']

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Verificar si ya existe el alumno
            cur.execute("SELECT COUNT(*) FROM alumno WHERE rut_alum = :1", (rut_alum,))
            if cur.fetchone()[0] > 0:
                set_flash("El alumno ya existe", "error")
                return redirect(url_for('listar_alumnos'))

            cur.execute("""
                INSERT INTO alumno (rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id)
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id))
            conn.commit()
            set_flash("Alumno agregado correctamente", "success")
            return redirect(url_for('listar_alumnos'))
        except Exception as e:
            set_flash(f"Error al agregar alumno: {str(e)}", "error")
            return redirect(url_for('listar_alumnos'))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template("agregar_alumno.html", cursos=cursos)

# Read
@app.route('/alumnos/<rut_alum>')
def detalle_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.rut_alum, a.nom_alum, a.seg_nom_alum, a.ap_pat_alum, a.ap_mat_alum,
                   c.id_curso, c.nivel, c.generacion
            FROM alumno a
            LEFT JOIN curso c ON a.curso_id = c.id_curso
            WHERE a.rut_alum = :1
        """, (rut_alum,))
        alumno = cur.fetchone()
        if not alumno:
            set_flash("Alumno no encontrado", "error")
            return redirect(url_for('listar_alumnos'))
        return render_template("detalle_alumno.html", alumno=alumno)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Update
@app.route('/alumnos/editar/<rut_alum>', methods=['GET', 'POST'])
def editar_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Traer alumno
        cur.execute("SELECT rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id FROM alumno WHERE rut_alum = :1", (rut_alum,))
        alumno = cur.fetchone()
        if not alumno:
            set_flash("Alumno no encontrado", "error")
            return redirect(url_for('listar_alumnos'))

        # Traer cursos para dropdown
        cur.execute("SELECT id_curso, nivel, generacion FROM curso ORDER BY generacion, nivel")
        cursos = cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

    if request.method == 'POST':
        nom_alum = request.form['nom_alum']
        seg_nom_alum = request.form.get('seg_nom_alum')
        ap_pat_alum = request.form['ap_pat_alum']
        ap_mat_alum = request.form.get('ap_mat_alum')
        curso_id = request.form['curso_id']

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE alumno
                SET nom_alum = :1, seg_nom_alum = :2, ap_pat_alum = :3, ap_mat_alum = :4, curso_id = :5
                WHERE rut_alum = :6
            """, (nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id, rut_alum))
            conn.commit()
            set_flash("Alumno actualizado correctamente", "success")
            return redirect(url_for('listar_alumnos'))
        except Exception as e:
            set_flash(f"Error al actualizar alumno: {str(e)}", "error")
            return redirect(url_for('listar_alumnos'))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template("editar_alumno.html", alumno=alumno, cursos=cursos)

# Delete
@app.route('/alumnos/eliminar/<rut_alum>', methods=['GET', 'POST'])
def eliminar_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT rut_alum, nom_alum, ap_pat_alum FROM alumno WHERE rut_alum = :1", (rut_alum,))
        alumno = cur.fetchone()
        if not alumno:
            set_flash("Alumno no encontrado", "error")
            return redirect(url_for('listar_alumnos'))

        if request.method == 'POST':
            cur.execute("DELETE FROM alumno WHERE rut_alum = :1", (rut_alum,))
            conn.commit()
            set_flash("Alumno eliminado correctamente", "success")
            return redirect(url_for('listar_alumnos'))

        return render_template("eliminar_alumno.html", alumno=alumno)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# List
@app.route('/alumnos')
def listar_alumnos():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.rut_alum, a.nom_alum, a.seg_nom_alum, a.ap_pat_alum, a.ap_mat_alum,
                   c.nivel, c.generacion
            FROM alumno a
            LEFT JOIN curso c ON a.curso_id = c.id_curso
            ORDER BY c.generacion, c.nivel, a.nom_alum
        """)
        alumnos = cur.fetchall()
        return render_template("all_alumnos.html", alumnos=alumnos)
    finally:
        if cur: cur.close()
        if conn: conn.close()


## NOTAS ##
# Create
@app.route('/notas/nueva', methods=['GET', 'POST'])
def agregar_nota():
    conn = get_connection()
    cur = conn.cursor()

    # Lista de cursos
    cur.execute("SELECT id_curso, nivel, generacion FROM curso ORDER BY nivel, generacion")
    cursos = cur.fetchall()

    curso_seleccionado = None
    alumnos = []

    if request.method == 'POST':
        curso_seleccionado = request.form.get('curso_id')

        # Si se eligió un curso, cargamos los alumnos de ese curso
        if curso_seleccionado:
            cur.execute("""
                SELECT rut_alum,
                       nom_alum || ' ' || NVL(seg_nom_alum,'') || ' ' || ap_pat_alum || ' ' || NVL(ap_mat_alum,'') AS nombre_completo
                FROM alumno
                WHERE curso_id = :1
                ORDER BY nom_alum
            """, (curso_seleccionado,))
            alumnos = cur.fetchall()

        # Guardar nota si se completaron todos los campos
        if 'alumno_rut_alum' in request.form and 'asignatura_codigo' in request.form and 'nombre' in request.form:
            alumno_rut = request.form['alumno_rut_alum']
            asignatura_cod = request.form['asignatura_codigo']
            nombre_eval = request.form['nombre']
            nota_val = float(request.form['nota'])

            # Construcción del id_nota
            nombre_eval_sin_espacios = nombre_eval.replace(" ", "")
            id_nota = f"{asignatura_cod}{curso_seleccionado}{alumno_rut}{nombre_eval_sin_espacios}"

            # Verificar si la nota ya existe
            cur.execute("SELECT COUNT(*) FROM nota WHERE id_nota = :1", (id_nota,))
            if cur.fetchone()[0] > 0:
                flash("La nota ya existe para este alumno y evaluación", "error")
                cur.close()
                conn.close()
                return redirect(url_for('listar_notas'))

            # Insertar
            try:
                cur.execute("""
                    INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
                    VALUES (:1, :2, :3, :4, :5, :6)
                """, (id_nota, nombre_eval, nota_val, curso_seleccionado, asignatura_cod, alumno_rut))
                conn.commit()
                flash("Nota agregada correctamente", "success")
                cur.close()
                conn.close()
                return redirect(url_for('listar_notas'))
            except Exception as e:
                flash(f"Error al agregar nota: {str(e)}", "error")

    # Lista de asignaturas
    cur.execute("SELECT codigo, nombre_asi || '- Docente: ' || nombre_prof AS detalle FROM asignatura")
    asignaturas = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('agregar_nota.html', cursos=cursos, curso_seleccionado=curso_seleccionado,
                           alumnos=alumnos, asignaturas=asignaturas)

# Read
@app.route('/notas/<id_nota>')
def detalle_nota(id_nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT n.id_nota,
               n.nombre,
               n.nota,
               a.codigo,
               a.nombre_asi,
               a.nombre_prof,
               al.rut_alum,
               NVL(al.nom_alum,'') AS nom_alum,
               NVL(al.seg_nom_alum,'') AS seg_nom_alum,
               NVL(al.ap_pat_alum,'') AS ap_pat_alum,
               NVL(al.ap_mat_alum,'') AS ap_mat_alum,
               NVL(al.curso_id,'') AS curso_id
        FROM nota n
        LEFT JOIN asignatura a ON n.asignatura_codigo = a.codigo
        LEFT JOIN alumno al ON n.alumno_rut_alum = al.rut_alum
        WHERE n.id_nota = :1
        """, (id_nota,))

        nota = cur.fetchone()
        if not nota:
            set_flash("Nota no encontrada", "error")
            return redirect(url_for('listar_notas'))
        
        # Construir nombre completo del alumno controlando los 'None'
        nombre_alumno = " ".join(filter(None, [nota[7], nota[8], nota[9], nota[10]]))
        
        return render_template("detalle_nota.html", nota=nota, nombre_alumno=nombre_alumno)
    finally:
        if cur: cur.close()
        if conn: conn.close()


# Update
@app.route('/notas/editar/<id_nota>', methods=['GET', 'POST'])
def editar_nota(id_nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_nota, nombre, nota FROM nota WHERE id_nota = :1", (id_nota,))
        nota = cur.fetchone()
        if not nota:
            set_flash("Nota no encontrada", "error")
            return redirect(url_for('listar_notas'))
    finally:
        if cur: cur.close()
        if conn: conn.close()

    if request.method == 'POST':
        nueva_nota = float(request.form['nota'])

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE nota SET nota = :1 WHERE id_nota = :2", (nueva_nota, id_nota))
            conn.commit()
            set_flash("Nota actualizada correctamente", "success")
            return redirect(url_for('listar_notas'))
        except Exception as e:
            set_flash(f"Error al actualizar nota: {str(e)}", "error")
            return redirect(url_for('listar_notas'))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template('editar_nota.html', nota=nota)

# Delete
@app.route('/notas/eliminar/<id_nota>', methods=['GET', 'POST'])
def eliminar_nota(id_nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_nota, nombre, nota FROM nota WHERE id_nota = :1", (id_nota,))
        nota = cur.fetchone()
        if not nota:
            set_flash("Nota no encontrada", "error")
            return redirect(url_for('listar_notas'))

        if request.method == 'POST':
            cur.execute("DELETE FROM nota WHERE id_nota = :1", (id_nota,))
            conn.commit()
            set_flash("Nota eliminada correctamente", "success")
            return redirect(url_for('listar_notas'))

        return render_template("eliminar_nota.html", nota=nota)
    finally:
        if cur: cur.close()
        if conn: conn.close()

# List
@app.route('/notas')
def listar_notas():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT n.id_nota, n.nombre, n.nota,
                   a.nombre_asi, al.nom_alum || ' ' || al.ap_pat_alum AS alumno
            FROM nota n
            JOIN asignatura a ON n.asignatura_codigo = a.codigo
            JOIN alumno al ON n.alumno_rut_alum = al.rut_alum
            ORDER BY a.nombre_asi, al.nom_alum
        """)
        notas = cur.fetchall()
        return render_template('all_notas.html', notas=notas)
    finally:
        if cur: cur.close()
        if conn: conn.close()


## ACTIVIDAD ##
# Create
@app.route('/actividades/nueva', methods=['GET', 'POST'])
def agregar_actividad():
    if request.method == 'POST':
        conn = get_connection()
        cur = conn.cursor()
        fecha_cre = datetime.now()
        fecha_str = fecha_cre.strftime("%d%m%Y")
        id_act = f"{fecha_str}_{request.form['nom_act']}_{request.form['tipo_act']}"

        cur.execute("""
            INSERT INTO actividad (id_act, nom_act, tipo_act, json_act, nombre_carpeta, fecha_cre, curso_id)
            VALUES (:id, :nom, :tipo, :json, :carpeta, :fecha, :curso)
        """, {
            "id": id_act,
            "nom": request.form["nom_act"],
            "tipo": request.form["tipo_act"],
            "json": request.form.get("json_act"),
            "carpeta": request.form["nombre_carpeta"],
            "fecha": fecha_cre,
            "curso": request.form.get("curso_id")
        })
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("listar_actividades"))

    # GET → obtener cursos
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_curso, nivel, generacion FROM curso")
    cursos = cur.fetchall()  # lista de tuplas
    cur.close()
    conn.close()

    return render_template("agregar_actividad.html", cursos=cursos)


# Read
@app.route('/actividades/<id_act>')
def detalle_actividad(id_act):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT a.id_act, a.nom_act, a.tipo_act, a.json_act, a.nombre_carpeta, a.fecha_cre,
               c.nivel, c.generacion
        FROM actividad a
        LEFT JOIN curso c ON a.curso_id = c.id_curso
        WHERE a.id_act = :1
    """, (id_act,))
    
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        set_flash("Actividad no encontrada", "error")
        return redirect(url_for("listar_actividades"))

    # Convertimos la fila en diccionario
    actividad = {
        "ID": row[0],
        "Nombre": row[1],
        "Tipo": row[2],
        "JSON": row[3],
        "Carpeta": row[4] if row[4] else "-",
        "Fecha": row[5].strftime("%d-%m-%Y") if isinstance(row[5], datetime) else (str(row[5]) if row[5] else "-"),
        "CursoNivel": row[6] if row[6] else "-",
        "CursoGeneracion": row[7] if row[7] else "-"
    }

    return render_template("detalle_actividad.html", actividad=actividad)

# Update
@app.route('/actividades/editar/<id_act>', methods=['GET', 'POST'])
def editar_actividad(id_act):
    conn = get_connection()
    cur = conn.cursor()

    # Obtener datos de la actividad
    cur.execute("""
        SELECT id_act, nom_act, tipo_act, json_act, nombre_carpeta, curso_id
        FROM actividad
        WHERE id_act = :1
    """, (id_act,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        set_flash("Actividad no encontrada", "error")
        return redirect(url_for("listar_actividades"))

    actividad = {
        "ID": row[0],
        "Nombre": row[1],
        "Tipo": row[2],
        "JSON": row[3],
        "Carpeta": row[4],
        "CursoID": row[5]
    }

    # Obtener lista de cursos
    cur.execute("SELECT id_curso, nivel, generacion FROM curso")
    cursos_rows = cur.fetchall()
    cur.close()
    conn.close()

    cursos = [{"ID": r[0], "Nivel": r[1], "Generacion": r[2]} for r in cursos_rows]

    if request.method == 'POST':
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE actividad
            SET nom_act = :nom, tipo_act = :tipo, json_act = :json,
                nombre_carpeta = :carpeta, curso_id = :curso
            WHERE id_act = :id
        """, {
            "nom": request.form["nom_act"],
            "tipo": request.form["tipo_act"],
            "json": request.form.get("json_act"),
            "carpeta": request.form["nombre_carpeta"],
            "curso": request.form.get("curso_id"),
            "id": id_act
        })
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("listar_actividades"))

    return render_template("editar_actividad.html", actividad=actividad, cursos=cursos)


# Delete
@app.route('/actividades/eliminar/<id_act>', methods=['GET', 'POST'])
def eliminar_actividad(id_act):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_act, nom_act, tipo_act, nombre_carpeta, fecha_cre
        FROM actividad
        WHERE id_act = :1
    """, (id_act,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        set_flash("Actividad no encontrada", "error")
        return redirect(url_for("listar_actividades"))

    actividad = {
        "ID": row[0],
        "Nombre": row[1],
        "Tipo": row[2],
        "Carpeta": row[3] if row[3] else "-",
        "Fecha": row[4].strftime("%d-%m-%Y") if isinstance(row[4], datetime) else (str(row[4]) if row[4] else "-")
    }

    if request.method == 'POST':
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM actividad WHERE id_act = :id", {"id": id_act})
        conn.commit()
        cur.close()
        conn.close()
        set_flash("Actividad eliminada correctamente", "success")
        return redirect(url_for("listar_actividades"))

    return render_template("eliminar_actividad.html", actividad=actividad)


# List
@app.route('/actividades')
def listar_actividades():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id_act, a.nom_act, a.tipo_act, a.nombre_carpeta, a.fecha_cre,
               c.nivel, c.generacion
        FROM actividad a
        LEFT JOIN curso c ON a.curso_id = c.id_curso
    """)
    actividades = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("all_actividades.html", actividades=actividades)

if __name__ == "__main__":
    app.run(debug=True)
