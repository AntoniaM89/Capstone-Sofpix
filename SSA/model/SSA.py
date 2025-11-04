from model.db import get_connection

NIVEL_MAP = {
    "Pre Kinder": "0PK",
    "Kinder": "00K",
    "1 Basico": "001",
    "2 Basico": "002",
    "3 Basico": "003",
    "4 Basico": "004",
    "5 Basico": "005",
    "6 Basico": "006",
    "7 Basico": "007",
    "8 Basico": "008",
    "I Medio": "009",
    "II Medio": "010",
    "III Medio": "011",
    "IV Medio": "012"
}

#=============================================
# FUNCIONES CORREGIDAS / CONSULTAS COMPLETAS
#=============================================

# ===================== PROFESORES =====================
def list_asignaturas_por_profesor(correo_prof):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.codigo, a.nombre_asi,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS nombre_prof
            FROM asignatura a
            JOIN profesor p ON a.profesor_correo = p.correo
            WHERE LOWER(a.profesor_correo) = LOWER(%s)
        """, (correo_prof,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_profesores_por_curso(curso_id):
    """
    Lista todos los profesores que dictan alguna asignatura en el curso dado
    """
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT p.correo AS correo_prof,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ',
                          p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS nombre_prof
            FROM curso_asignatura ca
            JOIN asignatura a ON ca.asignatura_codigo = a.codigo
            JOIN profesor p ON a.profesor_correo = p.correo
            WHERE ca.curso_id = %s
            ORDER BY nombre_prof
        """, (curso_id,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def list_profesores_por_asignatura(codigo_asi):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT p.correo AS correo_prof,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ',
                          p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS nombre_prof
            FROM asignatura a
            JOIN profesor p ON a.profesor_correo = p.correo
            WHERE a.codigo = %s
            ORDER BY nombre_prof
        """, (codigo_asi,))
        rows = cur.fetchall()
        return [{"correo_prof": r["correo_prof"], "nombre_prof": r["nombre_prof"]} for r in rows]
    finally:
        if cur: cur.close()
        if conn: conn.close()


def list_profesores_por_curso_asignatura(curso_id, codigo_asi):
    """
    Devuelve los profesores de una asignatura específica en un curso dado.
    """
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT p.correo AS correo_prof,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ',
                          p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS nombre_prof
            FROM curso_asignatura ca
            JOIN asignatura a ON ca.asignatura_codigo = a.codigo
            JOIN profesor p ON a.profesor_correo = p.correo
            WHERE ca.curso_id = %s
              AND a.codigo = %s
            ORDER BY nombre_prof
        """, (curso_id, codigo_asi))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_asignaturas_por_curso_y_profesor(curso_id, correo_prof):
    """
    Devuelve todas las asignaturas de un curso dictadas por un profesor específico.
    """
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.codigo, a.nombre_asi
            FROM curso_asignatura ca
            JOIN asignatura a ON ca.asignatura_codigo = a.codigo
            WHERE ca.curso_id = %s
              AND a.profesor_correo = %s
            ORDER BY a.nombre_asi
        """, (curso_id, correo_prof))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

# ===================== CURSOS =====================
def get_cursos_por_profesor(correo_prof):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT c.id_curso, c.nivel, c.generacion
            FROM curso c
            JOIN curso_asignatura ca ON ca.curso_id = c.id_curso
            JOIN asignatura a ON a.codigo = ca.asignatura_codigo
            WHERE a.profesor_correo = %s
            ORDER BY c.nivel, c.generacion
        """, (correo_prof,))
        rows = cur.fetchall()
        return [{"id_curso": r["id_curso"], "nivel": r["nivel"],"generacion": r["generacion"], "nombre": f"{r['nivel']} {r['generacion']}"} for r in rows]
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_curso_por_id(id_curso):
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


def get_cursos_por_asignatura(codigo_asi):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT c.id_curso, c.nivel, c.generacion
            FROM curso_asignatura ca
            JOIN curso c ON ca.curso_id = c.id_curso
            WHERE ca.asignatura_codigo = %s
            ORDER BY c.nivel, c.generacion
        """, (codigo_asi,))
        rows = cur.fetchall()
        return [{"codigo": r["id_curso"], "nombre": f"{r['nivel']} {r['generacion']}"} for r in rows]
    finally:
        if cur: cur.close()
        if conn: conn.close()

def list_cursos_por_asignatura_prof(codigo_asignatura, correo_prof):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT c.id_curso, c.nivel, c.generacion
            FROM curso c
            JOIN curso_asignatura ca ON ca.curso_id = c.id_curso
            JOIN asignatura a ON a.codigo = ca.asignatura_codigo AND a.profesor_correo = %s
            WHERE a.codigo = %s
            ORDER BY c.nivel, c.generacion
        """, (correo_prof, codigo_asignatura))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

# ===================== ASIGNATURAS =====================
def get_asignaturas_por_profesor(correo_prof):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT a.codigo, a.nombre_asi
            FROM asignatura a
            WHERE a.profesor_correo = %s
            ORDER BY a.nombre_asi;
        """, (correo_prof,))
        rows = cur.fetchall()
        return [{"codigo": r["codigo"], "nombre_asi": r["nombre_asi"]} for r in rows]
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_asignaturas_por_curso(curso_id):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DISTINCT a.codigo, a.nombre_asi
            FROM curso_asignatura ca
            JOIN asignatura a ON ca.asignatura_codigo = a.codigo
            WHERE ca.curso_id = %s
            ORDER BY a.nombre_asi
        """, (curso_id,))
        rows = cur.fetchall()
        return [{"codigo": r["codigo"], "nombre_asi": r["nombre_asi"]} for r in rows]
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_asignatura_por_codigo(codigo_asi):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT codigo, nombre_asi
            FROM asignatura
            WHERE codigo = %s
        """, (codigo_asi,))
        row = cur.fetchone()
        return [{"codigo": row["codigo"], "nombre_asi": row["nombre_asi"]}] if row else []
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_all_asignaturas_y_cursos():
    """
    Devuelve todas las asignaturas con sus cursos asociados
    """
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                a.codigo AS asignatura_codigo,
                a.nombre_asi AS nombre_asi,
                CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor,
                c.id_curso AS curso_id,
                c.nivel,
                c.generacion
            FROM asignatura a
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            LEFT JOIN curso_asignatura ca ON ca.asignatura_codigo = a.codigo
            LEFT JOIN curso c ON ca.curso_id = c.id_curso
            ORDER BY a.codigo, c.id_curso
        """)
        rows = cur.fetchall()
        asignaturas = {}
        for r in rows:
            codigo = r['asignatura_codigo']
            if codigo not in asignaturas:
                asignaturas[codigo] = {
                    "codigo": codigo,
                    "nombre_asi": r['nombre_asi'],
                    "profesor": r['profesor'],
                    "cursos": []
                }
            if r['curso_id']:
                curso_entry = {"codigo": r['curso_id'], "nombre": f"{r['nivel']} {r['generacion']}"}
                if curso_entry not in asignaturas[codigo]["cursos"]:
                    asignaturas[codigo]["cursos"].append(curso_entry)
        return list(asignaturas.values())
    finally:
        if cur: cur.close()
        if conn: conn.close()


# ===================== ALUMNOS =====================
def get_alumnos_por_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum
            FROM alumno
            WHERE curso_id = %s
            ORDER BY ap_pat_alum, ap_mat_alum, nom_alum
        """, (id_curso,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_alumnos_por_asignatura(codigo_asignatura):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT al.rut_alum, al.nom_alum, al.seg_nom_alum, al.ap_pat_alum, al.ap_mat_alum
            FROM alumno_asignatura aa
            JOIN alumno al ON aa.alumno_rut = al.rut_alum
            WHERE aa.asignatura_codigo = %s
            ORDER BY al.ap_pat_alum, al.nom_alum
        """, (codigo_asignatura,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_alumnos_por_curso_y_asignatura(codigo_asignatura, codigo_curso):
    """
    Devuelve los alumnos de un curso en una asignatura específica
    """
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT al.rut_alum, al.nom_alum, al.seg_nom_alum, al.ap_pat_alum, al.ap_mat_alum
            FROM alumno al
            JOIN alumno_asignatura aa ON al.rut_alum = aa.alumno_rut
            JOIN curso_asignatura ca ON aa.asignatura_codigo = ca.asignatura_codigo
            WHERE al.curso_id = %s AND aa.asignatura_codigo = %s
            ORDER BY al.ap_pat_alum, al.ap_mat_alum, al.nom_alum
        """, (codigo_curso, codigo_asignatura))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_alumnos_por_asignatura_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT aa.asignatura_codigo, a.nombre_asi
            FROM alumno_asignatura aa
            JOIN asignatura a ON aa.asignatura_codigo = a.codigo
            WHERE aa.alumno_rut = %s
        """, (rut_alum,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


# ===================== NOTAS =====================
def get_notas_por_curso(id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                n.id_nota,
                n.nombre AS actividad,
                n.nota,
                n.asignatura_codigo,
                a.nombre_asi AS nombre_asi,
                al.rut_alum,
                al.nom_alum,
                al.seg_nom_alum,
                al.ap_pat_alum,
                al.ap_mat_alum
            FROM nota n
            LEFT JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN alumno al ON n.alumno_rut = al.rut_alum
            WHERE al.curso_id = %s
            ORDER BY al.ap_pat_alum, al.nom_alum, n.nombre
        """, (id_curso,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_notas_alumno(rut_alum):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT n.id_nota, n.nombre, n.nota, n.observacion,
                   a.nombre_asi,
                   CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ',
                          p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor
            FROM nota n
            JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            WHERE n.alumno_rut = %s
            ORDER BY a.nombre_asi, n.nombre
        """, (rut_alum,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_notas_alumno_asignatura(rut_alum, codigo_asignatura, id_curso):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT n.id_nota, n.nombre, n.nota, n.observacion,
                   a.nombre_asi, al.curso_id, 
                   CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ',
                          al.ap_pat_alum, ' ', IFNULL(al.ap_mat_alum,'')) AS nombre_alumno
            FROM nota n
            JOIN alumno al ON n.alumno_rut = al.rut_alum
            JOIN asignatura a ON n.asignatura_codigo = a.codigo
            WHERE n.alumno_rut = %s
              AND n.asignatura_codigo = %s
              AND al.curso_id = %s
            ORDER BY n.nombre
        """, (rut_alum, codigo_asignatura, id_curso))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_nota_completa(id_nota):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT n.id_nota, n.nombre AS nombre_nota, n.nota, n.observacion,
                   n.asignatura_codigo, al.curso_id, al.rut_alum, al.nom_alum,
                   al.seg_nom_alum, al.ap_pat_alum, al.ap_mat_alum
            FROM nota n
            JOIN alumno al ON n.alumno_rut = al.rut_alum
            WHERE n.id_nota = %s
        """, (id_nota,))
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def list_notas_completas():
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT n.id_nota, n.nombre AS nombre_evaluacion, n.nota, n.observacion,
                   a.nombre_asi, CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ',
                   p.ap_pat_user, ' ', IFNULL(p.ap_mat_user,'')) AS profesor,
                   c.nivel, c.generacion,
                   al.rut_alum, al.nom_alum, al.seg_nom_alum, al.ap_pat_alum, al.ap_mat_alum
            FROM nota n
            JOIN asignatura a ON n.asignatura_codigo = a.codigo
            LEFT JOIN profesor p ON a.profesor_correo = p.correo
            LEFT JOIN alumno al ON n.alumno_rut = al.rut_alum
            LEFT JOIN curso c ON al.curso_id = c.id_curso
            ORDER BY c.nivel, c.generacion, a.nombre_asi, al.ap_pat_alum, n.nombre
        """)
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def alumnos_con_notas_en_asignatura(id_curso, codigo_asignatura):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 1
            FROM nota n
            JOIN alumno al ON n.alumno_rut = al.rut_alum
            WHERE n.asignatura_codigo = %s
              AND al.curso_id = %s
            LIMIT 1
        """, (codigo_asignatura, id_curso))
        return bool(cur.fetchone())
    finally:
        if cur: cur.close()
        if conn: conn.close()


# ===================== GENERACIÓN DE CÓDIGOS =====================
def generar_codigo_asignatura(base_codigo):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT codigo FROM asignatura WHERE codigo LIKE %s", (base_codigo + "%",))
        existentes = cur.fetchall()
        
        max_num = 0
        for (codigo,) in existentes:
            try:
                num = int(codigo.replace(base_codigo, ""))
                max_num = max(max_num, num)
            except ValueError:
                continue
        
        nuevo_codigo = f"{base_codigo}{max_num + 1:03d}"
        return nuevo_codigo
    finally:
        if cur: cur.close()
        if conn: conn.close()
