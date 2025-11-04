from model.db import get_connection

def crear_pregunta(quiz_id, pregunta, img_id, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO QUIZ_PREGUNTA (QUIZ_ID, PREGUNTA, IMG_URL, OPCION_A, OPCION_B, OPCION_C, OPCION_D, RESPUESTA_CORRECTA)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                quiz_id,
                pregunta,
                str(img_id) if img_id else None,
                opcion_a,
                opcion_b,
                opcion_c,
                opcion_d,
                respuesta_correcta
            )
        )
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def listar_preguntas(quiz_id):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT
                qp.ID,
                qp.PREGUNTA,
                b.ID AS IMAGEN,
                qp.OPCION_A,
                qp.OPCION_B,
                qp.OPCION_C,
                qp.OPCION_D,
                qp.RESPUESTA_CORRECTA
            FROM QUIZ_PREGUNTA qp
            LEFT JOIN BIBLIOTECA b ON qp.IMG_URL = b.ID
            WHERE qp.QUIZ_ID = %s
            """,
            (quiz_id,)
        )
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()


def eliminar_pregunta(id_pregunta):
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM QUIZ_PREGUNTA WHERE ID = %s", (id_pregunta,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()
