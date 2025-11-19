from model.db import get_connection
from model import alumnos_mod

#==========================
# ASIGNATURA
#==========================

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


# PERSONALIZADAS #
def asignar_a_asignatura(rut_alum, codigo_asignatura):
    """Asigna un alumno a una asignatura (tabla alumno_asignatura)."""
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT IGNORE INTO alumno_asignatura (alumno_rut, asignatura_codigo)
            VALUES (%s, %s)
        """, (rut_alum, codigo_asignatura))
        conn.commit()

        success = cur.rowcount > 0
        alumno = alumnos_mod.get_alumno(rut_alum)
        
        return success, alumno

    except Exception as e:
        if conn:
            conn.rollback()
        return False, alumnos_mod.get_alumno(rut_alum)
    finally:
        if cur: cur.close()
        if conn: conn.close()


def quitar_de_asignatura(rut_alum, codigo_asignatura):
    """Quita la relación alumno-asignatura."""
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM alumno_asignatura
            WHERE alumno_rut = %s AND asignatura_codigo = %s
        """, (rut_alum, codigo_asignatura))
        conn.commit()

        success = cur.rowcount > 0
        alumno = alumnos_mod.get_alumno(rut_alum)
        return success, alumno

    except Exception as e:
        if conn:
            conn.rollback()
        return False, alumnos_mod.get_alumno(rut_alum)
    finally:
        if cur: cur.close()
        if conn: conn.close()
