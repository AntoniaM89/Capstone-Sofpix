from flask import render_template, request, send_file, flash, session, redirect, url_for, jsonify
from io import BytesIO
import pandas as pd
from model.metricas_mod import Metric
from model import SSA, cursos_mod, asignaturas_mod, profesores_mod, metricas_mod, alumnos_mod
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm


# ==============================
# PÁGINA PRINCIPAL DE MÉTRICAS
# ==============================
def reportes():
    metric = Metric()

    # Acción limpiar filtros
    if request.args.get("action") == "limpiar":
        return redirect(url_for("reportes"))

    # Filtros desde GET
    filtros = {
        "curso": request.args.get("curso") or None,
        "asignatura": request.args.get("asignatura") or None,
        "profesor": request.args.get("profesor") or None,
    }

    rol = session.get("rol")
    correo_user = session.get("correo_prof")

    # -----------------------------
    # FILTROS AUTOMÁTICOS PARA PROFESOR
    # -----------------------------
    if rol == "profesor":
        filtros["profesor"] = correo_user

        # Cursos del profesor
        cursos = SSA.get_cursos_por_profesor(correo_user)
        # Asignaturas del profesor, opcionalmente filtradas por curso
        asignaturas = SSA.get_asignaturas_por_profesor(
            correo_prof=correo_user
        )

        
        # Profesores → solo él
        profesores = [{"correo": correo_user}]

    else:
        # ADMIN → puede ver todo
        cursos = cursos_mod.list_cursos()
        asignaturas = asignaturas_mod.list_asignaturas()
        profesores = profesores_mod.list_profesores()

    # -----------------------------
    # Paginación
    # -----------------------------
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    resultados = metric.obtener_tabla_resultados(filtros, limite=per_page, offset=offset)
    total_registros = metric.contar_tabla_resultados(filtros)
    total_paginas = (total_registros + per_page - 1) // per_page if total_registros > 0 else 1

    # -----------------------------
    # Métricas y KPIs
    # -----------------------------
    summary = metric.get_summary_counts()
    promedio_curso = metric.obtener_promedio_curso(filtros["curso"]) if filtros.get("curso") else None
    promedio_profesor = metric.obtener_promedio_profesor(filtros.get("profesor"), filtros.get("curso"), filtros.get("asignatura"))
    alumnos_por_asignatura = metric.obtener_alumnos_por_asignatura(filtros.get("asignatura"), filtros.get("curso"), filtros.get("profesor"))
    alumnos_destacados = metric.obtener_alumnos_destacados(filtros)
    alumnos_normales = metric.obtener_alumnos_normal(filtros)
    alumnos_en_riesgo = metric.obtener_alumnos_en_riesgo(filtros)
    asignaturas_promedio = metric.obtener_asignaturas_promedio(filtros.get("curso"), filtros.get("profesor"))

    return render_template(
        "SSA/metricas.html",
        cursos=cursos,
        asignaturas=asignaturas,
        profesores=profesores,
        resultados=resultados,
        filtros=filtros,
        summary=summary,
        promedio_curso=promedio_curso,
        promedio_profesor=promedio_profesor,
        alumnos_por_asignatura=alumnos_por_asignatura,
        alumnos_destacados=alumnos_destacados,
        alumnos_normales=alumnos_normales,
        alumnos_en_riesgo=alumnos_en_riesgo,
        asignaturas_promedio=asignaturas_promedio,
        page=page,
        per_page=per_page,
        total_paginas=total_paginas,
        total_registros=total_registros
    )


def metricas_data():
    metric = Metric()

    # Filtros (match con tu formulario)
    filtros = {
        "curso": request.args.get("curso") or None,
        "asignatura": request.args.get("asignatura") or None,
        "profesor": request.args.get("profesor") or None,
    }

    # Si el rol es profesor forzamos su correo (coherente con tu lógica)
    rol = session.get("rol")
    if rol == "profesor":
        filtros["profesor"] = session.get("correo_prof")

    # Paginación
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page

    # Ordenamiento (nombre de columna + dirección)
    sort = request.args.get("sort", "nom_alum")
    order = request.args.get("order", "ASC")

    # Fetch datos paginados y ordenados
    resultados = metric.obtener_tabla_resultados(
        filtros,
        limite=per_page,
        offset=offset,
        sort=sort,
        order=order
    )

    total_registros = metric.contar_tabla_resultados(filtros)
    total_paginas = (total_registros + per_page - 1) // per_page if total_registros > 0 else 1

    return jsonify({
        "success": True,
        "datos": resultados,
        "page": page,
        "per_page": per_page,
        "total_paginas": total_paginas,
        "total_registros": total_registros,
        "sort": sort,
        "order": order
    })


def metricas_kpis():
    filtros = {
        "curso": request.args.get("curso"),
        "asignatura": request.args.get("asignatura"),
        "profesor": request.args.get("profesor")
    }

    metric = Metric()

    return jsonify({
        "promedio_curso": metric.obtener_promedio_curso(filtros["curso"]),
        "total_alumnos": metric.obtener_alumnos_por_asignatura(
            filtros["asignatura"], filtros["curso"], filtros["profesor"]
        ),
        "destacados": len(metric.obtener_alumnos_destacados(filtros)),
        "normales": len(metric.obtener_alumnos_normal(filtros)),
        "en_riesgo": len(metric.obtener_alumnos_en_riesgo(filtros)),
        "asignaturas": metric.obtener_asignaturas_promedio(
            filtros["curso"], filtros["profesor"]
        ),
        "profesores": metric.obtener_promedio_profesor(
            profesor_correo=filtros["profesor"],
            id_curso=filtros["curso"],
            codigo_asignatura=filtros["asignatura"]
        )
    })

# ==============================
# FILTROS DINÁMICOS (AJAX)
# ==============================
def filtros_dinamicos():
    curso_id = request.args.get('curso') or None
    asignatura_codigo = request.args.get('asignatura') or None
    profesor_correo = request.args.get('profesor') or None
    rol = request.args.get('rol')

    # Para profesor, siempre se bloquea su propio correo
    if rol == 'profesor':
        profesor_correo = session.get('correo_prof')

    metricas = Metric()

    # Bloqueo de profesor (solo admin con asignatura seleccionada)
    profesor_bloqueado = None
    if rol == 'admin' and asignatura_codigo:
        profesor_fijo_correo = metricas.obtener_profesor_por_asignatura(asignatura_codigo)
        if profesor_fijo_correo:
            profesor_bloqueado = profesor_fijo_correo
            profesor_correo = profesor_fijo_correo

    # -----------------------------
    # Cursos
    # -----------------------------

    cursos = metricas.obtener_cursos_con_datos(
        codigo_asignatura=asignatura_codigo,
        profesor_correo=profesor_correo
    )

    # -----------------------------
    # Asignaturas
    # -----------------------------
    asignaturas = metricas.obtener_asignaturas_con_datos(
        id_curso=curso_id,
        profesor_correo=profesor_correo
    )

    # -----------------------------
    # Profesores
    # -----------------------------
    profesores_js = []
    if rol == 'admin':
        if profesor_bloqueado:
            profesores = metricas.obtener_profesores_con_datos(profesor_correo=profesor_bloqueado)
        else:
            profesores = metricas.obtener_profesores_con_datos(
                id_curso=curso_id,
                codigo_asignatura=asignatura_codigo
            )
        profesores_js = [{"correo": p["correo"], "nombre": p["nombre"]} for p in profesores]

    # -----------------------------
    # Formateo para JS
    # -----------------------------
    cursos_js = [{"id_curso": c["id_curso"], "nivel": c["nivel"], "generacion": c["generacion"], "nombre": c["nombre"]} for c in cursos]
    asignaturas_js = [{"codigo": a["codigo"], "nombre": f"{a['nombre_asi']} ({a['codigo']})"} for a in asignaturas]


    return jsonify({
        "success": True,
        "cursos": cursos_js,
        "asignaturas": asignaturas_js,
        "profesores": profesores_js,
        "profesor_bloqueado": profesor_bloqueado
    })


# ==============================
# EXPORTACIÓN A EXCEL
# ==============================
def export_metricas_excel():
    # 🔹 Obtener filtros + sort + order
    filtros = {
        "curso": request.args.get("curso") or None,
        "asignatura": request.args.get("asignatura") or None,
        "profesor": request.args.get("profesor") or None,
    }

    sort = request.args.get("sort", "nom_alum")
    order = request.args.get("order", "ASC")

    metric = Metric()

    # 🔹 Obtener TODOS los datos según filtros (sin paginación)
    tabla = metric.obtener_tabla_resultados(
        filtros=filtros,
        sin_limite=True,
        sort=sort,
        order=order
    )

    if not tabla:
        flash("No hay datos para exportar con los filtros seleccionados.", "warning")
        return redirect(url_for("reportes"))

    # 🔹 Crear nombre del archivo
    partes = ["Reporte_Metricas"]

    if filtros["curso"]:
        partes.append(f"{filtros['curso']}")
    if filtros["asignatura"]:
        partes.append(f"{filtros['asignatura']}")
    if filtros["profesor"]:
        partes.append(f"{filtros['profesor'].replace('@', '_')}")

    nombre_archivo = "_".join(partes) + ".xlsx"

    # 🔹 Crear DataFrame limpio
    df = pd.DataFrame(tabla)

    df = df.rename(columns={
        "nom_alum": "Alumno",
        "rut_alum": "RUT",
        "nombre_asi": "Asignatura",
        "nivel": "Nivel",
        "generacion": "Generación",
        "profesor": "Profesor",
        "promedio": "Promedio",
        "observacion": "Observación"
    })

    # Curso: Nivel + Generación
    df["Curso"] = df["Nivel"] + " " + df["Generación"].astype(str)

    df = df[["Alumno", "RUT", "Asignatura", "Curso", "Profesor", "Promedio", "Observación"]]

    # 🔹 Exportar
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================
# EXPORTACIÓN A PDF
# ==============================
def export_metricas_pdf():
    # 🔹 Obtener filtros + sort + order
    filtros = {
        "curso": request.args.get("curso") or None,
        "asignatura": request.args.get("asignatura") or None,
        "profesor": request.args.get("profesor") or None,
    }

    sort = request.args.get("sort", "nom_alum")
    order = request.args.get("order", "ASC")

    metric = Metric()

    # 🔹 Obtener TODOS los datos filtrados (sin paginación)
    resultados = metric.obtener_tabla_resultados(
        filtros=filtros,
        sin_limite=True,
        sort=sort,
        order=order
    )

    # 🔹 Crear nombre del archivo
    partes = ["Reporte_Metricas"]

    if filtros["curso"]:
        partes.append(f"{filtros['curso']}")
    if filtros["asignatura"]:
        partes.append(f"{filtros['asignatura']}")
    if filtros["profesor"]:
        partes.append(f"{filtros['profesor'].replace('@', '_')}")

    nombre = "_".join(partes) + ".pdf"

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    elements = []

    # ====================
    # ESTILOS
    # ====================
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Wrapped", wordWrap="CJK", fontSize=9))
    styles.add(ParagraphStyle(name="Filters", fontSize=9))
    styles.add(ParagraphStyle(name="TitleBig", fontSize=16, alignment=1))

    # ====================
    # TÍTULO
    # ====================
    elements.append(Paragraph("Sistema SSA — Reporte Métricas", styles["TitleBig"]))
    elements.append(Spacer(1, 10))

    # ====================
    # FILTROS UTILIZADOS
    # ====================
    filtros_texto = (
        f"<b>Curso:</b> {filtros['curso'] or 'Todos'}<br/>"
        f"<b>Asignatura:</b> {filtros['asignatura'] or 'Todas'}<br/>"
        f"<b>Profesor:</b> {filtros['profesor'] or 'Todos'}"
    )

    elements.append(Paragraph(filtros_texto, styles["Filters"]))
    elements.append(Spacer(1, 12))

    # ====================
    # TABLA
    # ====================
    data = [["Alumno", "RUT", "Asignatura", "Curso", "Profesor", "Promedio", "Observación"]]

    for fila in resultados:
        data.append([
            Paragraph(fila["nom_alum"], styles["Wrapped"]),
            Paragraph(str(fila["rut_alum"]), styles["Wrapped"]),
            Paragraph(fila["nombre_asi"], styles["Wrapped"]),
            Paragraph(f"{fila['nivel']} {fila['generacion']}", styles["Wrapped"]),
            Paragraph(fila["profesor"], styles["Wrapped"]),
            Paragraph(str(fila["promedio"]), styles["Wrapped"]),
            Paragraph(fila.get("observacion", ""), styles["Wrapped"]),
        ])

    col_widths = [5*cm, 3*cm, 5*cm, 3*cm, 4*cm, 2.5*cm, 5*cm]

    table = Table(data, colWidths=col_widths, repeatRows=1)

    estilo = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ])

    # Filas alternadas
    for i in range(1, len(data)):
        estilo.add(
            "BACKGROUND",
            (0, i), (-1, i),
            colors.HexColor("#DCE6F1") if i % 2 else colors.white
        )

    table.setStyle(estilo)
    elements.append(table)

    # ====================
    # FOOTER
    # ====================
    def add_page_number(canvas, doc):
        canvas.saveState()
        text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Página {doc.page}"
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(landscape(A4)[0] - 1*cm, 1*cm, text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre,
        mimetype="application/pdf"
    )

def fecha_texto_spanish(dt):
    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","diciembre"]
    return f"{dt.day} de {meses[dt.month-1]} de {dt.year}"

def informe_alumno():
    metric = Metric()
    curso_filtro = request.args.get("curso") or None
    rut_alum = request.args.get("rut") or None

    cursos = cursos_mod.list_cursos()
    alumnos = alumnos_mod.list_alumnos()

    informe = None
    fecha_entrega = None

    if rut_alum:
        informe = metric.preparar_informe_alumno(rut_alum, id_curso=curso_filtro)
        if not informe:
            flash("No se encontró información para el alumno.", "warning")
        else:
            fecha_entrega = fecha_texto_spanish(datetime.now())

    return render_template(
        "SSA/informe_alumno.html",
        cursos=cursos,
        alumnos=alumnos,
        filtros={"curso": curso_filtro, "rut": rut_alum},
        informe=informe,
        fecha_entrega=fecha_entrega
    )

def obtener_alumnos(curso_id):
    alumnos = SSA.get_alumnos_por_curso(curso_id)
    return jsonify(alumnos)

def export_informe_alumno_pdf():
    # Obtener parámetros
    rut = request.args.get("rut") or None
    curso = request.args.get("curso") or None  # opcional

    # Validar que se haya seleccionado un alumno
    if not rut:
        flash("Debe seleccionar un alumno para descargar el informe", "error")
        return redirect(url_for('informe_alumno'))

    # Obtener datos del informe
    metric = Metric()
    informe = metric.preparar_informe_alumno(rut, curso)

    if not informe:
        flash("No hay datos para generar el PDF", "error")
        return redirect(url_for('informe_alumno'))

    # Nombre del archivo
    nombre = f"Informe_{informe['alumno']['rut']}.pdf"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Wrapped', wordWrap='CJK', fontSize=10))
    styles.add(ParagraphStyle(name='Info', fontSize=10, leading=12, spaceAfter=4))
    styles.add(ParagraphStyle(name='Left', alignment=0, fontSize=10))   
    styles.add(ParagraphStyle(name='Center', alignment=1, fontSize=10)) 

    # Título
    elements.append(Paragraph("Sistema SSA - Informe De Notas", styles['Title']))
    elements.append(Spacer(1, 6))

    # Datos del alumno
    info_texto = f"""
    <strong>Don(a):</strong> {informe['alumno']['nombre_completo']}<br/>
    <strong>RUT:</strong> {informe['alumno']['rut']}<br/>
    <strong>Curso:</strong> {informe['alumno']['curso_legible']}<br/>
    <strong>Fecha de entrega:</strong> {datetime.now().strftime('%d/%m/%Y')}<br/>
    """
    elements.append(Paragraph(info_texto, styles['Info']))
    elements.append(Spacer(1, 6))

    # Construir tabla de notas
    data = []

    # Encabezados
    encabezados = [Paragraph("<strong>Asignatura</strong>", styles['Left'])]
    encabezados += [Paragraph(f"<strong>N{i+1}</strong>", styles['Center']) for i in range(informe['max_notas'])]
    encabezados.append(Paragraph("<strong>Promedios</strong>", styles['Center']))
    data.append(encabezados)

    # Filas de notas
    for a in informe['asignaturas']:
        # Nombre de la asignatura en la primera columna
        fila = [Paragraph(str(a['nombre']), styles['Left'])]

        # Notas
        for n in a['notas']:
            fila.append(Paragraph(f"{n:.1f}", styles['Center']))

        # Celdas vacías si faltan notas
        for _ in range(informe['max_notas'] - len(a['notas'])):
            fila.append(Paragraph("", styles['Center']))

        # Promedio de la asignatura
        fila.append(Paragraph(f"{a['promedio']:.1f}" if a['promedio'] is not None else "-", styles['Center']))

        data.append(fila)

    # Fila de promedio final
    fila_prom = [Paragraph("<strong>Promedio final</strong>", styles['Left'])]
    fila_prom += [Paragraph("", styles['Center']) for _ in range(informe['max_notas'])]
    promedio_final = informe.get('promedio_final', None)
    fila_prom.append(Paragraph(f"<strong>{promedio_final:.1f}</strong>" if promedio_final is not None else "-", styles['Center']))
    data.append(fila_prom)

    # Definir anchos de columnas
    col_widths = [6*cm] + [2*cm]*informe['max_notas'] + [2.5*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign='LEFT')

    # Estilo de la tabla
    tbl_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), 
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ])
    table.setStyle(tbl_style)
    elements.append(table)
    # Footer con fecha y número de página
    def add_page_number(canvas, doc):
        canvas.saveState()
        footer_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Página {doc.page}"
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0]-1*cm, 1*cm, footer_text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre,
        mimetype="application/pdf"
    )
