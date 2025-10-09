from model.db import get_connection

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


##############################
# PROFESOR
##############################

def profesor_exists(correo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT 1 FROM profesor WHERE correo = %s", (correo,))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO profesor (correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user)
            VALUES (%s, %s, %s, %s, %s)
        """, (correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_profesor(correo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol
            FROM profesor
            WHERE correo = %s
        """, (correo,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def update_profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE profesor
            SET nom_user = %s,
                seg_nom_user = %s,
                ap_pat_user = %s,
                ap_mat_user = %s,
                pass_enc = %s,
                area = %s
            WHERE correo = %s
        """, (nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, correo))
        conn.commit()
        return cur.rowcount > 0 
    finally:
        if cur: cur.close()
        if conn: conn.close()



def delete_profesor(correo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM profesor WHERE correo = %s", (correo,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_profesores():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT correo,
                   nom_user,
                   seg_nom_user,
                   ap_pat_user,
                   ap_mat_user,
                   area
            FROM profesor
            ORDER BY correo
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

##############################
# ASIGNATURA
##############################

def asignatura_exists(codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM asignatura WHERE codigo = %s", (codigo,))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_asignatura(codigo, nombre_asi, profesor_correo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO asignatura (codigo, nombre_asi, profesor_correo)
            VALUES (%s, %s, %s)
        """, (codigo, nombre_asi, profesor_correo))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_asignatura(codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.codigo, a.nombre_asi, p.correo,
            CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor
            FROM asignatura a
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            WHERE codigo = %s
            ORDER BY a.codigo
        """, (codigo,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def update_asignatura(codigo_actual, nombre_asi=None, profesor_correo=None, asign_map=None):
    conn = cur = None
    try:
        nuevo_prefijo = asign_map.get(nombre_asi)
        if nuevo_prefijo:
            conn = get_connection()
            cur = conn.cursor()

            nuevo_codigo = codigo_actual
            if nombre_asi and asign_map:
                resto_id = codigo_actual[3:]
                nuevo_codigo = f"{nuevo_prefijo}{resto_id}"

            if nuevo_codigo != codigo_actual:
                cur.execute(
                    "SELECT COUNT(*) FROM nota WHERE asignatura_codigo = %s", 
                    (codigo_actual,)
                )
                count = cur.fetchone()[0]
                if count > 0:
                    raise ValueError(
                        "No se puede actualizar la asignatura: hay notas asociadas"
                    )

            updates = []
            params = []

            if nombre_asi is not None:
                updates.append("nombre_asi = %s")
                params.append(nombre_asi)
            if profesor_correo is not None:
                updates.append("profesor_correo = %s")
                params.append(profesor_correo)
            if nuevo_codigo != codigo_actual:
                updates.append("codigo = %s")
                params.append(nuevo_codigo)

            if updates:
                query = "UPDATE asignatura SET " + ", ".join(updates) + " WHERE codigo = %s"
                params.append(codigo_actual)
                cur.execute(query, tuple(params))

            conn.commit()
            return nuevo_codigo

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def delete_asignatura(codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM nota WHERE asignatura_codigo = %s", (codigo,))
        notas_count = cur.fetchone()[0]

        if notas_count > 0:
            return False, notas_count

        cur.execute("DELETE FROM asignatura WHERE codigo = %s", (codigo,))
        conn.commit()
        return True, 0

    finally:
        if cur: cur.close()
        if conn: conn.close()



def list_asignaturas():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.codigo,
                   a.nombre_asi,
                   p.correo,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor
            FROM asignatura a
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            ORDER BY a.codigo
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

##############################
# CURSO
##############################

def curso_exists(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM curso WHERE id_curso = %s", (id_curso,))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_curso(id_curso, nivel, generacion):
    if curso_exists(id_curso):
        return False
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO curso (id_curso, nivel, generacion)
            VALUES (%s, %s, %s)
        """, (id_curso, nivel, generacion))
        conn.commit()
        return True
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id_curso, nivel, generacion
            FROM curso
            WHERE id_curso = %s
        """, (id_curso,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def update_curso(id_curso_actual, nivel=None, generacion=None):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT nivel, generacion FROM curso WHERE id_curso = %s", (id_curso_actual,))
        curso = cur.fetchone()
        if not curso:
            return None 

        nivel_actual, generacion_actual = curso

        nivel_nuevo = nivel if nivel is not None else nivel_actual
        generacion_nueva = generacion if generacion is not None else generacion_actual
        prefijo = NIVEL_MAP.get(nivel_nuevo)
        if not prefijo:
            return None 

        nuevo_id_curso = f"{prefijo}{generacion_nueva}"

        if nuevo_id_curso != id_curso_actual and curso_exists(nuevo_id_curso):
            return None  

        if nuevo_id_curso != id_curso_actual:
            cur.execute("UPDATE alumno SET curso_id = %s WHERE curso_id = %s",
                        (nuevo_id_curso, id_curso_actual))
            cur.execute("UPDATE actividad SET curso_id = %s WHERE curso_id = %s",
                        (nuevo_id_curso, id_curso_actual))

        updates = []
        params = []

        if nivel is not None:
            updates.append("nivel = %s")
            params.append(nivel)
        if generacion is not None:
            updates.append("generacion = %s")
            params.append(generacion)
        if nuevo_id_curso != id_curso_actual:
            updates.append("id_curso = %s")
            params.append(nuevo_id_curso)

        if updates:
            query = "UPDATE curso SET " + ", ".join(updates) + " WHERE id_curso = %s"
            params.append(id_curso_actual)
            cur.execute(query, tuple(params))
            conn.commit()

        return nuevo_id_curso

    finally:
        if cur: cur.close()
        if conn: conn.close()

def delete_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM curso WHERE id_curso = %s", (id_curso,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_cursos():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id_curso, nivel, generacion
            FROM curso c
            ORDER BY id_curso
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

##############################
# ALUMNO
##############################

def alumno_exists(rut):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM alumno WHERE rut = %s", (rut,))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO alumno (rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id))
        conn.commit()
        return True
    except Exception as e:
        print("Error al agregar alumno:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_alumno(rut_alum):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT a.rut_alum, a.nom_alum, a.seg_nom_alum, a.ap_pat_alum, a.ap_mat_alum,
                   a.curso_id, c.nivel, c.generacion
            FROM alumno a
            LEFT JOIN curso c ON a.curso_id = c.id_curso
            WHERE a.rut_alum = %s
        """, (rut_alum,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def update_alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE alumno
            SET nom_alum = %s,
                seg_nom_alum = %s,
                ap_pat_alum = %s,
                ap_mat_alum = %s,
                curso_id = %s
            WHERE rut_alum = %s
        """, (nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id, rut_alum))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print("Error al actualizar alumno:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def delete_alumno(rut_alum):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM nota WHERE alumno_rut_alum = %s", (rut_alum,))
        count = cur.fetchone()[0]
        if count > 0:
            print(f"No se puede eliminar el alumno {rut_alum}: tiene {count} nota(s) asociada(s).")
            return False

        cur.execute("DELETE FROM alumno WHERE rut_alum = %s", (rut_alum,))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print("Error al eliminar alumno:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def list_alumnos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT a.rut_alum, a.nom_alum, a.seg_nom_alum, a.ap_pat_alum, a.ap_mat_alum,
                   a.curso_id, c.nivel, c.generacion
            FROM alumno a
            LEFT JOIN curso c ON a.curso_id = c.id_curso
            ORDER BY a.ap_pat_alum, a.ap_mat_alum, a.nom_alum
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

##############################
# NOTA
##############################

def add_nota(id_nota, asignatura_codigo, curso_id, alumno_rut, nombre_eval, nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO nota (id_nota,nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_nota, nombre_eval, nota, curso_id, asignatura_codigo, alumno_rut))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_nota(id_nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT n.id_nota, n.asignatura_codigo, n.codigo_curso, n.alumno_rut_alum, n.nombre, n.nota, a.nombre_asi,
                   CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ', al.ap_pat_alum, ' ', IFNULL(al.ap_mat_alum,'')) AS alumno_nombre,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor
            FROM nota n
            LEFT JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN alumno al ON n.alumno_rut_alum = al.rut_alum
            LEFT JOIN curso c ON n.codigo_curso = c.id_curso
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            WHERE n.id_nota = %s
            ORDER BY n.id_nota
        """, (id_nota,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def update_nota(id_nota_old, id_nota_new, nueva_nota, nuevo_nombre):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE nota
            SET id_nota = %s,
                nombre = %s,
                nota = %s
            WHERE id_nota = %s
        """, (id_nota_new, nuevo_nombre, nueva_nota, id_nota_old))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def delete_nota(id_nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM nota WHERE id_nota = %s", (id_nota,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_notas():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT n.id_nota, n.asignatura_codigo, n.codigo_curso, n.alumno_rut_alum, n.nombre, n.nota,
                   a.nombre_asi,
                   CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ', al.ap_pat_alum, ' ', IFNULL(al.ap_mat_alum,'')) AS alumno_nombre,
                   c.nivel, c.generacion
            FROM nota n
            LEFT JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN alumno al ON n.alumno_rut_alum = al.rut_alum
            LEFT JOIN curso c ON n.codigo_curso = c.id_curso
            ORDER BY n.id_nota
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

##############################
# FUNCIONES PERSONALIZADAS / CONSULTAS
##############################

def list_asignaturas_por_profesor(correo_prof):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.codigo, a.nombre_asi, 
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS nombre_prof
            FROM asignatura a
            JOIN profesor p ON a.profesor_correo = p.correo
            WHERE LOWER(a.profesor_correo) = LOWER(%s)
        """, (correo_prof,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_cursos_por_asignatura_prof(codigo_asignatura, correo_profesor):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT c.id_curso, c.nivel, c.generacion
            FROM curso c
            JOIN nota n ON c.id_curso = n.codigo_curso
            JOIN asignatura a ON a.codigo = n.asignatura_codigo
            WHERE a.codigo = %s
              AND a.profesor_correo = %s
        """, (codigo_asignatura, correo_profesor))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_asignaturas_por_profesor(correo_prof):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.codigo, a.nombre_asi, 
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS nombre_prof
            FROM asignatura a
            JOIN profesor p ON a.profesor_correo = p.correo
            WHERE a.profesor_correo = %s
        """, (correo_prof,))
        rows = cur.fetchall()
        return [{"codigo": r[0], "nombre": r[1], "profesor": r[2]} for r in rows]
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_cursos_por_asignatura(codigo_asignatura):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT c.id_curso, c.nivel, c.generacion
            FROM curso c
            LEFT JOIN nota n ON n.curso_id = c.id_curso AND n.asignatura_codigo = %s
            LEFT JOIN alumno a ON a.curso_id = c.id_curso
            WHERE n.asignatura_codigo = %s OR a.curso_id IS NOT NULL
        """, (codigo_asignatura, codigo_asignatura))
        rows = cur.fetchall()
        return [{"id_curso": r[0], "nivel": r[1], "generacion": r[2]} for r in rows]
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_alumnos_por_curso(id_curso):
    """Obtiene todos los alumnos asociados a un curso específico"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum
            FROM alumno
            WHERE curso_id = %s
            ORDER BY ap_pat_alum, ap_mat_alum, nom_alum
        """, (id_curso,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_notas_por_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Consulta con JOINs para traer alumno y asignatura
        cur.execute("""
            SELECT 
                n.id_nota,
                n.nombre AS actividad,
                n.nota,
                n.codigo_curso,
                n.asignatura_codigo,
                asig.nombre_asi AS nombre_asignatura,
                a.rut_alum,
                a.nom_alum,
                a.seg_nom_alum,
                a.ap_pat_alum,
                a.ap_mat_alum
            FROM nota n
            LEFT JOIN asignatura asig ON n.asignatura_codigo = asig.codigo
            LEFT JOIN alumno a ON n.alumno_rut_alum = a.rut_alum
            WHERE n.codigo_curso = %s
            ORDER BY a.ap_pat_alum, a.nom_alum, n.nombre
        """, (id_curso,))

        notas = cur.fetchall()
        return notas

    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_all_asignaturas_y_cursos():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT 
                a.codigo AS asignatura_codigo,
                a.nombre_asi AS asignatura_nombre,
                CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor,
                n.codigo_curso AS curso_id,
                c.nivel,
                c.generacion
            FROM asignatura a
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            LEFT JOIN nota n ON n.asignatura_codigo = a.codigo
            LEFT JOIN curso c ON c.id_curso = n.codigo_curso
            ORDER BY a.codigo, n.codigo_curso
        """)

        rows = cur.fetchall()
        asignaturas = {}
        for r in rows:
            codigo = r['asignatura_codigo']
            if codigo not in asignaturas:
                asignaturas[codigo] = {
                    "codigo": codigo,
                    "nombre": r['asignatura_nombre'],
                    "profesor": r['profesor'],
                    "cursos": []
                }
            if r['curso_id']:
                curso_entry = {"codigo": r['curso_id'], "nombre": f"{r['nivel']} {r['generacion']}"}
                if curso_entry not in asignaturas[codigo]["cursos"]:
                    asignaturas[codigo]["cursos"].append(curso_entry)

        return list(asignaturas.values())

    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_notas_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True) 
        cur.execute("""
            SELECT n.id_nota, n.nombre, n.nota, a.nombre_asi
            FROM nota n
            JOIN asignatura a ON n.asignatura_codigo = a.codigo
            WHERE n.alumno_rut_alum = %s
            ORDER BY a.nombre_asi
        """, (rut_alum,))
        notas = cur.fetchall()
        return [
            {
                'id_nota': n['id_nota'],
                'nombre': n['nombre'],
                'nota': float(n['nota']), 
                'nombre_asi': n['nombre_asi']
            } for n in notas
        ]
    finally:
        if cur: cur.close()
        if conn: conn.close()

def generar_codigo_asignatura(base_codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT codigo FROM asignatura WHERE codigo LIKE %s", (base_codigo + "%",))
        existentes = cur.fetchall()
        
        max_num = 0
        for (codigo,) in existentes:
            try:
                num = int(codigo.replace(base_codigo, ""))
                max_num = max(max_num, num)
            except ValueError:
                continue
        
        nuevo_codigo = f"{base_codigo}{max_num + 1:03d}"
        return nuevo_codigo
    finally:
        if cur: cur.close()
        if conn: conn.close()

def codigo_base_exists(base_codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM asignatura WHERE codigo LIKE %s", (base_codigo + "%",))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def nombre_asignatura_exists(nombre):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM asignatura WHERE nombre_asi = %s", (nombre,))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_notas_alumno_asignatura(rut_alum, codigo_asignatura, id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                n.id_nota,
                n.nombre,
                n.nota,
                a.nombre_asi AS nombre_asignatura,
                c.id_curso,
                c.nivel,
                c.generacion,
                CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ', al.ap_pat_alum, ' ', IFNULL(al.ap_mat_alum,'')) AS nombre_alumno
            FROM nota n
            LEFT JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN alumno al ON n.alumno_rut_alum = al.rut_alum
            LEFT JOIN curso c ON n.codigo_curso = c.id_curso
            WHERE n.alumno_rut_alum = %s
              AND n.asignatura_codigo = %s
              AND n.codigo_curso = %s
            ORDER BY n.nombre
        """, (rut_alum, codigo_asignatura, id_curso))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_asignaturas_por_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.codigo, a.nombre_asi, CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS nombre_prof
            FROM asignatura a
            JOIN profesor p ON a.profesor_correo = p.correo
            JOIN nota n ON n.asignatura_codigo = a.codigo
            WHERE n.codigo_curso = %s
            GROUP BY a.codigo, a.nombre_asi, nombre_prof
        """, (id_curso,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def count_cursos_asignatura(codigo_asignatura):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(DISTINCT n.codigo_curso)
            FROM nota n
            WHERE n.asignatura_codigo = %s
        """, (codigo_asignatura,))
        count = cur.fetchone()[0]
        return int(count or 0)
    finally:
        if cur: cur.close()
        if conn: conn.close()
