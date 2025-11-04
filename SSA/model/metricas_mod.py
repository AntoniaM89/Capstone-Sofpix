from decimal import Decimal, ROUND_CEILING
from model.db import get_connection
from model import alumnos_mod
from datetime import datetime


class Metric:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    # ===========================
    # MÉTRICAS GENERALES
    # ===========================
    def obtener_promedio_curso(self, id_curso):
        query = """
        SELECT ROUND(AVG(n.nota), 2) AS promedio_curso
        FROM nota n
        JOIN alumno a ON a.rut_alum = n.alumno_rut
        WHERE a.curso_id = %s;
        """
        self.cursor.execute(query, (id_curso,))
        resultado = self.cursor.fetchone()
        if resultado and resultado["promedio_curso"] is not None:
            return round(float(resultado["promedio_curso"]), 1)
        return None


    def obtener_tabla_resultados(self, filtros, limite=None, offset=0, sin_limite=False):
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)

            query = """
                SELECT 
                    CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ', al.ap_pat_alum,' ', IFNULL(al.ap_mat_alum,'')) AS nom_alum,
                    al.rut_alum,
                    a.nombre_asi,
                    c.nivel,
                    c.generacion,
                    CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user,' ', IFNULL(p.ap_mat_user,'')) AS profesor,
                    ROUND(AVG(n.nota),1) AS promedio,
                    CASE
                        WHEN AVG(n.nota) >= 6 THEN 'Destacado'
                        WHEN AVG(n.nota) >= 4.5 THEN 'Normal'
                        ELSE 'En riesgo'
                    END AS observacion
                FROM nota n
                INNER JOIN alumno al ON n.alumno_rut = al.rut_alum
                INNER JOIN asignatura a ON n.asignatura_codigo = a.codigo
                INNER JOIN profesor p ON a.profesor_correo = p.correo
                INNER JOIN curso c ON al.curso_id = c.id_curso
                INNER JOIN curso_asignatura ca ON c.id_curso = ca.curso_id AND a.codigo = ca.asignatura_codigo
                WHERE 1=1
            """

            params = []

            # Filtros dinámicos
            if filtros.get("curso"):
                query += " AND c.id_curso = %s"
                params.append(filtros["curso"])

            if filtros.get("asignatura"):
                query += " AND a.codigo = %s"
                params.append(filtros["asignatura"])

            if filtros.get("profesor"):
                query += " AND p.correo = %s"
                params.append(filtros["profesor"])

            query += " GROUP BY al.rut_alum, a.codigo ORDER BY nom_alum ASC, promedio ASC"

            if not sin_limite and limite is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limite, offset])

            cur.execute(query, tuple(params))
            return cur.fetchall()

        except Exception as e:
            print("Error en obtener_tabla_resultados:", e)
            return []
        finally:
            if cur: cur.close()
            if conn: conn.close()


    def contar_tabla_resultados(self, filtros):
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT COUNT(DISTINCT al.rut_alum, a.codigo)
                FROM nota n
                INNER JOIN alumno al ON n.alumno_rut = al.rut_alum
                INNER JOIN asignatura a ON n.asignatura_codigo = a.codigo
                INNER JOIN profesor p ON a.profesor_correo = p.correo
                INNER JOIN curso c ON al.curso_id = c.id_curso
                INNER JOIN curso_asignatura ca ON c.id_curso = ca.curso_id AND a.codigo = ca.asignatura_codigo
                WHERE 1=1
            """

            params = []
            if filtros.get("curso"):
                query += " AND c.id_curso = %s"
                params.append(filtros["curso"])
            if filtros.get("asignatura"):
                query += " AND a.codigo = %s"
                params.append(filtros["asignatura"])
            if filtros.get("profesor"):
                query += " AND p.correo = %s"
                params.append(filtros["profesor"])

            cur.execute(query, tuple(params))
            return cur.fetchone()[0]

        except Exception as e:
            print("Error en contar_tabla_resultados:", e)
            return 0
        finally:
            if cur: cur.close()
            if conn: conn.close()


    def obtener_promedio_profesor(self, profesor_correo=None, id_curso=None, codigo_asignatura=None):
        params = []
        query = """
            SELECT 
                p.correo AS profesor_correo,
                CONCAT(p.nom_user,' ', p.ap_pat_user) AS profe,
                CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user) AS profesor,
                ROUND(AVG(n.nota), 2) AS promedio_profesor
            FROM nota n
            JOIN asignatura asi ON asi.codigo = n.asignatura_codigo
            JOIN alumno a ON a.rut_alum = n.alumno_rut
            LEFT JOIN profesor p ON p.correo = asi.profesor_correo
            WHERE 1=1
        """

        if profesor_correo:
            query += " AND p.correo = %s"
            params.append(profesor_correo)

        if id_curso:
            query += " AND a.curso_id = %s"
            params.append(id_curso)

        if codigo_asignatura:
            query += " AND asi.codigo = %s"
            params.append(codigo_asignatura)

        query += " GROUP BY p.correo, p.nom_user, p.seg_nom_user, p.ap_pat_user ORDER BY promedio_profesor DESC;"

        self.cursor.execute(query, tuple(params))
        resultados = self.cursor.fetchall()

        if not resultados:
            return None if profesor_correo else []

        if profesor_correo:
            return round(float(resultados[0]["promedio_profesor"]), 1) if resultados[0]["promedio_profesor"] else 0

        return [
            {"profesor": r["profesor"] or "Desconocido","profe": r["profe"] or "Desconocido", "promedio": round(float(r["promedio_profesor"]), 1) if r["promedio_profesor"] else 0}
            for r in resultados
        ]

    def obtener_alumnos_por_asignatura(self, codigo_asignatura, id_curso=None, profesor_correo=None):
        if not codigo_asignatura:
            return 0
        query = """
        SELECT COUNT(DISTINCT a.rut_alum) AS total_alumnos
        FROM nota n
        JOIN alumno a ON a.rut_alum = n.alumno_rut
        JOIN asignatura asi ON asi.codigo = n.asignatura_codigo
        LEFT JOIN profesor p ON p.correo = asi.profesor_correo
        WHERE asi.codigo = %s
        """
        params = [codigo_asignatura]
        if id_curso:
            query += " AND a.curso_id = %s"
            params.append(id_curso)
        if profesor_correo:
            query += " AND p.correo = %s"
            params.append(profesor_correo)
        self.cursor.execute(query, tuple(params))
        resultado = self.cursor.fetchone()
        return int(resultado["total_alumnos"]) if resultado and resultado["total_alumnos"] else 0

    ##############################
    # KPIs DE ALUMNOS
    ##############################
    def obtener_alumnos_destacados(self, filtros):
        return self._obtener_alumnos_por_categoria(filtros, ">= 6")

    def obtener_alumnos_normal(self, filtros):
        return self._obtener_alumnos_por_categoria(filtros, "BETWEEN 4.5 AND 5.9")

    def obtener_alumnos_en_riesgo(self, filtros):
        return self._obtener_alumnos_por_categoria(filtros, "< 4.5")

    def _obtener_alumnos_por_categoria(self, filtros, condicion):
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            query = f"""
                SELECT 
                    CONCAT(al.nom_alum, ' ', IFNULL(al.seg_nom_alum,''), ' ', al.ap_pat_alum) AS nombre,
                    ROUND(AVG(n.nota),2) AS promedio,
                    a.nombre_asi AS asignatura,
                    CONCAT(c.nivel, ' ', c.generacion) AS curso
                FROM nota n
                INNER JOIN alumno al ON n.alumno_rut = al.rut_alum
                INNER JOIN asignatura a ON n.asignatura_codigo = a.codigo
                INNER JOIN profesor p ON a.profesor_correo = p.correo
                INNER JOIN curso c ON al.curso_id = c.id_curso
                INNER JOIN curso_asignatura ca ON c.id_curso = ca.curso_id AND a.codigo = ca.asignatura_codigo
                WHERE 1=1
            """

            params = []

            # Filtros
            if filtros.get("curso"):
                query += " AND c.id_curso = %s"
                params.append(filtros["curso"])

            if filtros.get("asignatura"):
                query += " AND a.codigo = %s"
                params.append(filtros["asignatura"])

            if filtros.get("profesor"):
                query += " AND p.correo = %s"
                params.append(filtros["profesor"])

            query += f" GROUP BY al.rut_alum, a.codigo HAVING AVG(n.nota) {condicion} ORDER BY promedio DESC"
            cur.execute(query, tuple(params))
            return cur.fetchall()

        except Exception as e:
            print("Error en _obtener_alumnos_por_categoria:", e)
            return []
        finally:
            if cur: cur.close()
            if conn: conn.close()
    

    def obtener_asignaturas_promedio(self, id_curso=None, profesor_correo=None):
        """
        Devuelve todas las asignaturas según filtros, con su promedio.
        """
        query = """
        SELECT 
            asi.codigo AS codigo,
            asi.nombre_asi AS asignatura,
            ROUND(AVG(n.nota), 2) AS promedio
        FROM nota n
        JOIN asignatura asi ON asi.codigo = n.asignatura_codigo
        JOIN alumno a ON a.rut_alum = n.alumno_rut
        LEFT JOIN profesor p ON p.correo = asi.profesor_correo
        WHERE 1=1
        """
        params = []
        if id_curso:
            query += " AND a.curso_id = %s"
            params.append(id_curso)
        if profesor_correo:
            query += " AND p.correo = %s"
            params.append(profesor_correo)

        query += " GROUP BY asi.codigo, asi.nombre_asi ORDER BY asi.nombre_asi ASC;"

        self.cursor.execute(query, tuple(params))
        resultados = self.cursor.fetchall()

        asignaturas = [
            {"asignatura": r["asignatura"], "codigo": r["codigo"], "promedio": round(float(r["promedio"]), 1)}
            for r in resultados
        ]
        return asignaturas


    # ===========================
    # RESUMEN DE TABLAS
    # ===========================

    def get_summary_counts(self):
        cur = self.conn.cursor(dictionary=True)
        counts = {}
        tablas = ["curso", "alumno", "profesor", "asignatura", "nota"]
        for tabla in tablas:
            cur.execute(f"SELECT COUNT(*) AS total FROM {tabla}")
            counts[tabla + "s"] = cur.fetchone()["total"]
        cur.close()
        return counts
    
    # ===========================
    # INFORME ALUMNO
    # ===========================
    def get_alumno(self, rut_alum):
        """
        Retorna los datos del alumno junto al curso (nivel y generación)
        """
        cur = self.conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                a.rut_alum,
                a.nom_alum,
                a.seg_nom_alum,
                a.ap_pat_alum,
                a.ap_mat_alum,
                c.id_curso,
                c.nivel,
                c.generacion
            FROM alumno a
            LEFT JOIN curso c ON c.id_curso = a.curso_id
            WHERE a.rut_alum = %s
        """, (rut_alum,))
        res = cur.fetchone()
        cur.close()
        return res

    def obtener_notas_por_alumno(self, rut_alum, id_curso=None):
        """
        Devuelve todas las notas del alumno, agrupadas por asignatura.
        """
        cur = self.conn.cursor(dictionary=True)
        params = [rut_alum]
        query = """
            SELECT 
                asi.codigo AS codigo,
                asi.nombre_asi AS nombre_asi,
                n.nombre AS nombre_nota,
                n.nota AS nota
            FROM nota n
            JOIN asignatura asi ON asi.codigo = n.asignatura_codigo
            JOIN alumno a ON a.rut_alum = n.alumno_rut
            JOIN curso c ON c.id_curso = a.curso_id
            WHERE n.alumno_rut = %s
        """
        if id_curso:
            query += " AND c.id_curso = %s"
            params.append(id_curso)

        query += " ORDER BY asi.nombre_asi, n.nombre"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        return rows

    def agrupar_notas_por_asignatura(self, filas):
        """
        Agrupa las notas por asignatura y calcula promedio por asignatura.
        Cada nota se redondea primero al primer decimal según reglas estándar.
        Luego se calcula el promedio de las notas redondeadas, también al primer decimal.
        """
        agrup = {}
        for f in filas:
            cod = f["codigo"]
            nom_asi = f["nombre_asi"]
            if cod not in agrup:
                agrup[cod] = {"codigo": cod, "nombre": nom_asi, "notas": []}


            nota_redondeada = round(f["nota"], 2) 
            agrup[cod]["notas"].append(nota_redondeada)

        asignaturas = []
        max_notas = 0
        for _, v in agrup.items():
            notas = v["notas"]
            if notas:
                promedio = round(sum(notas) / len(notas), 1)
            else:
                promedio = None

            asignaturas.append({
                "codigo": v["codigo"],
                "nombre": v["nombre"],
                "notas": notas,
                "promedio": promedio
            })
            max_notas = max(max_notas, len(notas))

        asignaturas.sort(key=lambda x: x["nombre"])
        return asignaturas, max_notas



    def preparar_informe_alumno(self, rut_alum, id_curso=None):
        alumno = self.get_alumno(rut_alum)
        if not alumno:
            return None

        if not id_curso or id_curso == "None":
            id_curso = (alumno['id_curso'])

        filas = self.obtener_notas_por_alumno(rut_alum, id_curso)
        asignaturas, max_notas = self.agrupar_notas_por_asignatura(filas)

        proms = [a["promedio"] for a in asignaturas if a["promedio"] is not None]
        if proms:
            promedio_final = Decimal(str(sum(proms)/len(proms))).quantize(
                Decimal('0.1'), rounding=ROUND_CEILING
            )
            promedio_final = float(promedio_final)
        else:
            promedio_final = None

        nombre_completo = " ".join(filter(None, [
            alumno["nom_alum"],
            alumno["seg_nom_alum"],
            alumno["ap_pat_alum"],
            alumno["ap_mat_alum"]
        ])).strip()

        curso_legible = f"{alumno['nivel']} {alumno['generacion']}"

        return {
            "alumno": {
                "rut": alumno["rut_alum"],
                "nombre_completo": nombre_completo,
                "curso_legible": curso_legible
            },
            "asignaturas": asignaturas,
            "max_notas": max_notas,
            "promedio_final": promedio_final
        }

    def obtener_cursos_con_datos(self, profesor_correo=None, codigo_asignatura=None):
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            query = """
                SELECT DISTINCT c.id_curso, c.nivel, c.generacion, 
                CONCAT(c.nivel, ' ', c.generacion) AS nombre
                FROM curso c
                INNER JOIN curso_asignatura ca ON c.id_curso = ca.curso_id
                INNER JOIN asignatura a ON ca.asignatura_codigo = a.codigo
                INNER JOIN profesor p ON a.profesor_correo = p.correo
                WHERE 1=1
            """
            params = []
            if profesor_correo:
                query += " AND p.correo = %s"
                params.append(profesor_correo)
            if codigo_asignatura:
                query += " AND a.codigo = %s"
                params.append(codigo_asignatura)

            query += " ORDER BY c.nivel ASC"
            cur.execute(query, tuple(params))
            return cur.fetchall()

        except Exception as e:
            print("Error en obtener_cursos_con_datos:", e)
            return []
        finally:
            if cur: cur.close()
            if conn: conn.close()


    def obtener_asignaturas_con_datos(self, profesor_correo=None, id_curso=None):
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            query = """
                SELECT DISTINCT a.codigo, a.nombre_asi
                FROM asignatura a
                INNER JOIN curso_asignatura ca ON a.codigo = ca.asignatura_codigo
                INNER JOIN curso c ON ca.curso_id = c.id_curso
                INNER JOIN profesor p ON a.profesor_correo = p.correo
                WHERE 1=1
            """
            params = []
            if profesor_correo:
                query += " AND p.correo = %s"
                params.append(profesor_correo)
            if id_curso:
                query += " AND c.id_curso = %s"
                params.append(id_curso)

            query += " ORDER BY a.nombre_asi ASC"
            cur.execute(query, tuple(params))
            return cur.fetchall()

        except Exception as e:
            print("Error en obtener_asignaturas_con_datos:", e)
            return []
        finally:
            if cur: cur.close()
            if conn: conn.close()



    def obtener_profesores_con_datos(self, id_curso=None, codigo_asignatura=None, profesor_correo=None):
        """Devuelve los profesores que tienen notas, filtrados opcionalmente por curso, asignatura y/o correo del profesor."""
        
        query = """
        SELECT DISTINCT 
            p.correo, 
            CONCAT(p.nom_user, ' ', IFNULL(p.seg_nom_user,''), ' ', p.ap_pat_user,' ', IFNULL(p.ap_mat_user,'')) AS nombre
        FROM profesor p
        JOIN asignatura asi ON asi.profesor_correo = p.correo
        JOIN nota n ON n.asignatura_codigo = asi.codigo
        JOIN alumno a ON a.rut_alum = n.alumno_rut
        WHERE 1=1
        """
        params = []
        
        if id_curso:
            query += " AND a.curso_id = %s"
            params.append(id_curso)
            
        if codigo_asignatura:
            query += " AND asi.codigo = %s"
            params.append(codigo_asignatura)
            
        if profesor_correo:
            query += " AND p.correo = %s"
            params.append(profesor_correo)

        query += " ORDER BY nombre ASC;" 
        
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    def obtener_profesor_por_asignatura(self, codigo_asignatura):
        """Retorna el correo del profesor para una asignatura, si existe."""
        query = """
        SELECT profesor_correo
        FROM asignatura
        WHERE codigo = %s
        """
        self.cursor.execute(query, (codigo_asignatura,))
        resultado = self.cursor.fetchone()
        return resultado["profesor_correo"] if resultado and resultado["profesor_correo"] else None