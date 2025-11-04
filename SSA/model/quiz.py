from model.db import get_connection

def crear_quiz(titulo, descripcion, profesor_correo, carpeta="General"):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO QUIZ (titulo, descripcion, profesor_correo, carpeta)
            VALUES (%s, %s, %s, %s)
            """,
            (titulo, descripcion, profesor_correo, carpeta)
        )
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def listar_quizzes():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT q.ID, q.titulo, q.descripcion, q.profesor_correo, q.fecha_creacion, q.carpeta,
                   p.nom_user, p.ap_pat_user
            FROM QUIZ q
            JOIN PROFESOR p ON q.profesor_correo = p.correo
            ORDER BY q.fecha_creacion DESC
            """
        )
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def obtener_quiz(id_quiz):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT ID, titulo, descripcion, profesor_correo, fecha_creacion, carpeta FROM QUIZ WHERE ID = %s",
            (id_quiz,)
        )
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def eliminar_quiz(id_quiz):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM QUIZ WHERE ID = %s", (id_quiz,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()
