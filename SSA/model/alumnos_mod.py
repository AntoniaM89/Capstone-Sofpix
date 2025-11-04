from model.db import get_connection

#==========================
# ALUMNO
#==========================

def alumno_exists(rut):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM alumno WHERE rut_alum = %s", (rut,))
        return cur.fetchone() is not None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def add_alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alumno (rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id))
        conn.commit()
        return get_alumno(rut_alum)
    except Exception as e:
        if conn: conn.rollback()
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.rut_alum, a.nom_alum, a.seg_nom_alum, a.ap_pat_alum, a.ap_mat_alum,
                   a.curso_id, c.nivel, c.generacion
            FROM alumno a
            LEFT JOIN curso c ON a.curso_id = c.id_curso
            WHERE a.rut_alum = %s
        """, (rut_alum,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def update_alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
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
        return get_alumno(rut_alum)
    except Exception as e:
        if conn: conn.rollback()
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()


def delete_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Revisar si tiene notas
        cur.execute("SELECT COUNT(*) as count FROM nota WHERE alumno_rut = %s", (rut_alum,))
        count = cur.fetchone()['count']
        if count > 0:
            return False, get_alumno(rut_alum)

        # Eliminar alumno
        cur.execute("DELETE FROM alumno WHERE rut_alum = %s", (rut_alum,))
        conn.commit()

        if cur.rowcount == 0:
           return False, get_alumno(rut_alum)

        return True, None

    except Exception as e:
        if conn: conn.rollback()
        return False, get_alumno(rut_alum)

    finally:
        if cur: cur.close()
        if conn: conn.close()


def list_alumnos():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.rut_alum, a.nom_alum, a.seg_nom_alum, a.ap_pat_alum, a.ap_mat_alum,
                   a.curso_id, c.nivel, c.generacion
            FROM alumno a
            LEFT JOIN curso c ON a.curso_id = c.id_curso
            ORDER BY a.ap_pat_alum, a.ap_mat_alum, a.nom_alum
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


# ==========================
# FUNCIONES PERSONALIZADAS
# ==========================
def get_alumnos_por_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM alumno
            WHERE curso_id = %s
            ORDER BY ap_pat_alum, ap_mat_alum, nom_alum
        """, (id_curso,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_alumnos_disponibles(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM alumno
            WHERE curso_id IS NULL OR curso_id != %s
            ORDER BY ap_pat_alum, ap_mat_alum, nom_alum
        """, (id_curso,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()
    
def alumno_tiene_notas(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM nota WHERE alumno_rut = %s", (rut_alum,))
        count = cur.fetchone()[0]
        return count > 0
    except Exception as e:
        return True
    finally:
        if cur: cur.close()
        if conn: conn.close()
