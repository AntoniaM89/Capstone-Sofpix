from model.db import get_connection

def agregar_archivo(nombre, tipo, contenido, profesor_correo, carpeta):
    conn = get_connection()
    cur = conn.cursor()
    if carpeta == "":
        carpeta = "Home"
    cur.execute("""
        INSERT INTO BIBLIOTECA (Nombre, Tipo, Contenido, Profesor_Correo, Carpeta)
        VALUES (:1, :2, :3, :4, :5)
    """, (nombre, tipo, contenido, profesor_correo, carpeta))
    conn.commit()
    cur.close()
    conn.close()

def listar_archivos(profesor_correo, carpeta):
    conn = get_connection()
    cur = conn.cursor()
    if carpeta:
        cur.execute("""
            SELECT ID, Nombre, Tipo, Fecha_Subida, Carpeta
            FROM BIBLIOTECA
            WHERE Profesor_Correo=:1 AND Carpeta=:2
        """, (profesor_correo, carpeta))
    else:
        cur.execute("""
            SELECT ID, Nombre, Tipo, Fecha_Subida, Carpeta
            FROM BIBLIOTECA
            WHERE Profesor_Correo=:1
        """, (profesor_correo,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def renombrar_archivo(archivo_id, nuevo_nombre):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE BIBLIOTECA SET Nombre=:1 WHERE ID=:2", (nuevo_nombre, archivo_id))
    conn.commit()
    cur.close()
    conn.close()

def eliminar_archivo(archivo_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM BIBLIOTECA WHERE ID=:1", (archivo_id,))
    conn.commit()
    cur.close()
    conn.close()