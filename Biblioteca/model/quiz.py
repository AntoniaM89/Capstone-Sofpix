from model.db import get_connection

# === Crear un nuevo quiz ===
def crear_quiz(titulo, descripcion, profesor_correo, carpeta="General"):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO quiz (titulo, descripcion, profesor_correo, carpeta)
            VALUES (%s, %s, %s, %s)
            """,
            (titulo, descripcion, profesor_correo, carpeta)
        )
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()


# === Listar todos los quizzes ===
def listar_quizzes():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT q.id, q.titulo, q.descripcion, q.profesor_correo, q.fecha_creacion, q.carpeta,
                   p.nom_user, p.seg_nom_user, p.ap_pat_user, p.ap_mat_user
            FROM quiz q
            JOIN profesor p ON q.profesor_correo = p.correo
            ORDER BY q.fecha_creacion DESC
            """
        )
        return cur.fetchall()  # devuelve lista de diccionarios
    finally:
        if cur: cur.close()
        if conn: conn.close()


# === Obtener quiz por ID ===
def obtener_quiz(id_quiz):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, titulo, descripcion, profesor_correo, fecha_creacion, carpeta FROM quiz WHERE id = %s",
            (id_quiz,)
        )
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()


# === Eliminar quiz ===
def eliminar_quiz(id_quiz):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM quiz WHERE id = %s", (id_quiz,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()
