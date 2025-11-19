from model.SSA import NIVEL_MAP
from model.db import get_connection

#========
# CURSO #
#========

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
            FROM curso
            ORDER BY generacion,
                CASE nivel
                    WHEN 'Pre Kinder' THEN 1
                    WHEN 'Kinder' THEN 2
                    WHEN '1 Basico' THEN 3
                    WHEN '2 Basico' THEN 4
                    WHEN '3 Basico' THEN 5
                    WHEN '4 Basico' THEN 6
                    WHEN '5 Basico' THEN 7
                    WHEN '6 Basico' THEN 8
                    WHEN '7 Basico' THEN 9
                    WHEN '8 Basico' THEN 10
                    WHEN 'I Medio' THEN 11
                    WHEN 'II Medio' THEN 12
                    WHEN 'III Medio' THEN 13
                    WHEN 'IV Medio' THEN 14
                    ELSE 99
                END
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


#===============
# PARTICULARES #
#===============

def list_asignaturas_por_curso(curso_id):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.codigo, a.nombre_asi, a.profesor_correo
            FROM asignatura a
            JOIN curso_asignatura ca ON a.codigo = ca.asignatura_codigo
            WHERE ca.curso_id = %s
            ORDER BY a.nombre_asi
        """, (curso_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()



def list_asignaturas_disponibles(curso_id):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT codigo, nombre_asi, profesor_correo
            FROM asignatura
            WHERE codigo NOT IN (
                SELECT asignatura_codigo
                FROM curso_asignatura
                WHERE curso_id = %s
            )
            ORDER BY nombre_asi
        """, (curso_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def agregar_asignatura_a_curso(curso_id, asignatura_codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            INSERT INTO curso_asignatura (curso_id, asignatura_codigo)
            VALUES (%s, %s)
        """, (curso_id, asignatura_codigo))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def quitar_asignatura_del_curso(curso_id, asignatura_codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            DELETE FROM curso_asignatura
            WHERE curso_id = %s AND asignatura_codigo = %s
        """, (curso_id, asignatura_codigo))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
