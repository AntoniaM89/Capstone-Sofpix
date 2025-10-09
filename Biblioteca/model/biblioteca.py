from model.db import get_connection

# === AGREGAR ARCHIVO ===
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


# === OBTENER ARCHIVO (para descarga) ===
def obtener_archivo(id_archivo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT nombre, tipo, contenido FROM BIBLIOTECA WHERE id = %s", (id_archivo,))
    archivo = cur.fetchone()

    if archivo:
        # Si usas DictCursor, archivo será un diccionario
        if isinstance(archivo, dict):
            nombre = archivo['nombre']
            tipo = archivo['tipo']
            contenido = archivo['contenido']
        else:
            # Si aún es tupla (cursor normal)
            nombre, tipo, contenido = archivo

        cur.close()
        conn.close()
        return nombre, tipo, contenido

    cur.close()
    conn.close()
    return None


# === EDITAR NOMBRE ===
def editar_nombre(id_archivo, nuevo_nombre):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE BIBLIOTECA SET nombre = %s WHERE id = %s", (nuevo_nombre, id_archivo))
    conn.commit()
    cur.close()
    conn.close()


# === ELIMINAR ARCHIVO ===
def eliminar_archivo(id_archivo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM BIBLIOTECA WHERE id = %s", (id_archivo,))
    conn.commit()
    cur.close()
    conn.close()
