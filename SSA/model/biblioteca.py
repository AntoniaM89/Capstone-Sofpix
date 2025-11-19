from model.db import get_connection


def agregar_archivo(nombre, tipo, contenido, profesor_correo, carpeta):
    conn = get_connection()
    cur = conn.cursor()
    if not carpeta:
        carpeta = "Home"
    cur.execute("""
        INSERT INTO BIBLIOTECA (nombre, tipo, contenido, profesor_correo, carpeta)
        VALUES (%s, %s, %s, %s, %s)
    """, (nombre, tipo, contenido, profesor_correo, carpeta))
    conn.commit()
    cur.close()
    conn.close()


def obtener_archivo(id_archivo):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)  # << importante!
    cur.execute("""
        SELECT id, nombre, tipo, contenido, profesor_correo, carpeta
        FROM BIBLIOTECA
        WHERE id = %s
    """, (id_archivo,))
    archivo = cur.fetchone()
    cur.close()
    conn.close()
    return archivo  # ahora es dict o None


def editar_nombre(id_archivo, nuevo_nombre):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE BIBLIOTECA SET nombre = %s WHERE id = %s", (nuevo_nombre, id_archivo))
    conn.commit()
    cur.close()
    conn.close()


def eliminar_archivo(id_archivo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM BIBLIOTECA WHERE id = %s", (id_archivo,))
    conn.commit()
    cur.close()
    conn.close()


def listar_archivos():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)  # << dict
        cur.execute("""
            SELECT id, nombre, tipo, fecha_subida, profesor_correo, carpeta, estado
            FROM BIBLIOTECA
            ORDER BY fecha_subida DESC
        """)
        return cur.fetchall()  # lista de dicts
    finally:
        if cur: cur.close()
        if conn: conn.close()

# PERSONALIZADAS #

def obtener_archivos_por_profesor(correo_profesor):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, nombre
            FROM biblioteca
            WHERE profesor_correo = %s
        """, (correo_profesor,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def actualizar_autor_biblioteca(correo_antiguo, correo_nuevo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            UPDATE biblioteca
            SET autor_original = profesor_correo,
                profesor_correo = %s
            WHERE profesor_correo = %s
        """, (correo_nuevo, correo_antiguo))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def listar_imagenes():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT ID, Nombre, Tipo 
            FROM BIBLIOTECA
            WHERE LOWER(Tipo) IN ('png', 'jpg', 'jpeg', 'gif', 'webp', 'svg')
            """
        )
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def obtener_imagen(id_imagen):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT contenido, tipo FROM BIBLIOTECA WHERE ID = %s", (id_imagen,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def actualizar_estado_archivo(id_archivo, nuevo_estado):
    """
    Actualiza el estado de un archivo (Pendiente, Aprobado, Rechazado).
    """
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE biblioteca SET estado = %s WHERE id = %s", 
            (nuevo_estado, id_archivo)
        )
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()