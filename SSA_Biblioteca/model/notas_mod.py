from model.db import get_connection

def nota_exists(id_nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM nota WHERE id_nota = %s", (id_nota,))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def add_nota(id_nota, asignatura_codigo, alumno_rut, nombre_eval, nota, observacion=None):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO nota (id_nota, nombre, nota, observacion, asignatura_codigo, alumno_rut)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_nota, nombre_eval, nota, observacion, asignatura_codigo, alumno_rut))
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
            SELECT n.id_nota,
                   n.asignatura_codigo,
                   n.alumno_rut,
                   n.nombre,
                   n.nota,
                   n.observacion,
                   a.nombre_asi,
                   CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ', al.ap_pat_alum, ' ', IFNULL(al.ap_mat_alum,'')) AS alumno_nombre,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor,
                   c.id_curso,
                   c.nivel, c.generacion
            FROM nota n
            LEFT JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN alumno al ON n.alumno_rut = al.rut_alum
            LEFT JOIN curso c ON al.curso_id = c.id_curso
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            WHERE n.id_nota = %s
            ORDER BY n.id_nota
        """, (id_nota,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def update_nota(id_nota_old, id_nota_new, nueva_nota, nuevo_nombre, nueva_observacion=None):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE nota
            SET id_nota = %s,
                nombre = %s,
                nota = %s,
                observacion = %s
            WHERE id_nota = %s
        """, (id_nota_new, nuevo_nombre, nueva_nota, nueva_observacion, id_nota_old))
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
            SELECT n.id_nota,
                   n.asignatura_codigo,
                   n.alumno_rut,
                   n.nombre,
                   n.nota,
                   n.observacion,
                   a.nombre_asi,
                   CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ', al.ap_pat_alum, ' ', IFNULL(al.ap_mat_alum,'')) AS alumno_nombre,
                   c.nivel, c.generacion
            FROM nota n
            LEFT JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN alumno al ON n.alumno_rut = al.rut_alum
            LEFT JOIN curso c ON al.curso_id = c.id_curso
            ORDER BY n.id_nota
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()
