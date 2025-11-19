from model.db import get_connection

#==========
# PROFESOR
#==========

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

def add_profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, password, area):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO profesor (correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user,pass_enc, area)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, password, area))
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
            WHERE rol = 'profesor'
            ORDER BY correo
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()