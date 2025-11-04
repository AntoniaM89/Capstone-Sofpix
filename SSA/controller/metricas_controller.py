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
        print(correo_user)
        print(cursos)
        # Asignaturas del profesor, opcionalmente filtradas por curso
        asignaturas = SSA.get_asignaturas_por_profesor(
            correo_prof=correo_user
        )

        print(asignaturas)
        
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

    print(cursos)
    
    print(asignaturas)

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
    filtros = {
        "curso": request.args.get("curso") or None,
        "asignatura": request.args.get("asignatura") or None,
        "profesor": request.args.get("profesor") or None,
    }

    metric = Metric() # Asegúrate de que esta clase está correctamente instanciada

    # 🔹 Obtener todos los registros sin límite
    tabla = metric.obtener_tabla_resultados(filtros, sin_limite=True)

    if not tabla:
        flash("No hay datos para exportar con los filtros seleccionados.", "warning")
        return redirect(url_for("reportes"))

    # 🔹 Obtener los nombres amigables para usar en el nombre del archivo
    nombres_filtros = {
        "curso_nom": metric.obtener_nombre_amigable_curso(filtros["curso"]) if filtros["curso"] else None,
        "asignatura_nom": metric.obtener_nombre_amigable_asignatura(filtros["asignatura"]) if filtros["asignatura"] else None,
        "profesor_nom": tabla[0]["profesor"] if filtros["profesor"] and tabla else None,
    }

    # 🔹 Convertir a DataFrame
    df = pd.DataFrame(tabla)

    print(df)
    # 🔹 Renombrar columnas
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


    # 🔹 Crear columna Curso combinando Nivel + Generación
    df["Curso"] = df["Nivel"] + " " + df["Generación"].astype(str)

    # 🔹 Seleccionar solo las columnas finales y reordenarlas para Excel
    df = df[["Alumno", "RUT", "Asignatura", "Curso", "Profesor", "Promedio", "Observación"]]

    # 🔹 Preparar archivo en memoria
    output = BytesIO()
    
    # *** CORRECCIÓN APLICADA AQUÍ ***
    # Se eliminó el argumento 'encoding'. Se añade 'engine' como buena práctica.
    df.to_excel(output, index=False, engine='openpyxl') 
    
    output.seek(0)

    # 🔹 Construir nombre de archivo usando NOMBRES AMIGABLES
    partes = ["Reporte_Metricas"]
    
    if nombres_filtros["curso_nom"]:
        partes.append(nombres_filtros["curso_nom"].replace(" ", "_").replace(".", "")) 
    if nombres_filtros["asignatura_nom"]:
        partes.append(nombres_filtros["asignatura_nom"].replace(" ", "_").replace(".", ""))
    if nombres_filtros["profesor_nom"]:
        profesor_limpio = nombres_filtros["profesor_nom"].replace(" ", "_").replace(".", "_").replace("@", "_")
        partes.append(profesor_limpio)

    nombre_archivo = "_".join(partes) + ".xlsx"

    # 🔹 Enviar archivo al navegador
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
    filtros = {
        "curso": request.args.get("curso") or None,
        "asignatura": request.args.get("asignatura") or None,
        "profesor": request.args.get("profesor") or None,
    }

    metric = Metric()
    resultados = metric.obtener_tabla_resultados(filtros, sin_limite=True)

    nombre = "Reporte"
    if filtros["curso"]:
        nombre += f"_{filtros['curso']}"
    if filtros["asignatura"]:
        nombre += f"_{filtros['asignatura']}"
    if filtros["profesor"]:
        nombre += f"_{filtros['profesor']}"
    nombre += ".pdf"

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

    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Wrapped', wordWrap='CJK', fontSize=9))
    styles.add(ParagraphStyle(name='TableHeader', alignment=1, fontSize=10, fontName='Helvetica-Bold', textColor=colors.white))
    styles.add(ParagraphStyle(name='Filters', fontSize=9, textColor=colors.black, leading=12))

    # Encabezado con título
    elements.append(Paragraph("Sistema SSA - Reporte de Notas", styles['Title']))
    elements.append(Spacer(1, 6))

    # Filtros aplicados
    filtros_texto = ""
    filtros_texto += f"Curso: {filtros['curso'] or 'Todos'}<br/>"
    filtros_texto += f"Asignatura: {filtros['asignatura'] or 'Todas'}<br/>"
    filtros_texto += f"Profesor: {filtros['profesor'] or 'Todos'}<br/>"
    elements.append(Paragraph(filtros_texto, styles['Filters']))
    elements.append(Spacer(1, 12))

    # Datos de la tabla
    data = [["Alumno", "RUT", "Asignatura", "Curso", "Profesor", "Promedio", "Observación"]]

    print(data)
    
    for fila in resultados:
        nombre_alumno = fila['nom_alum']
       
        data.append([
            Paragraph(nombre_alumno, styles['Wrapped']),
            Paragraph(str(fila['rut_alum']), styles['Wrapped']),
            Paragraph(fila['nombre_asi'], styles['Wrapped']),
            Paragraph(f"{fila['nivel']} {fila['generacion']}", styles['Wrapped']),
            Paragraph(fila['profesor'], styles['Wrapped']),
            Paragraph(str(fila['promedio']), styles['Wrapped']),
            Paragraph(fila.get('observacion',''), styles['Wrapped'])
        ])

    # Columnas más angostas
    col_widths = [5*cm, 2.5*cm, 5*cm, 2.5*cm, 4*cm, 2*cm, 5*cm]

    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign='LEFT')

    # Estilos de tabla
    tbl_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F81BD")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,1), (-1,-1), 2),
        ('BOTTOMPADDING', (0,1), (-1,-1), 2),
    ])

    # Colorear filas alternas y destacar promedios
    for i, fila in enumerate(resultados):
        row_idx = i + 1
        if i % 2 == 0:
            tbl_style.add('BACKGROUND', (0,row_idx), (-1,row_idx), colors.HexColor("#DCE6F1"))
        else:
            tbl_style.add('BACKGROUND', (0,row_idx), (-1,row_idx), colors.white)
        try:
            promedio = float(fila['promedio'])
            if promedio >= 6.0:
                tbl_style.add('TEXTCOLOR', (5,row_idx), (5,row_idx), colors.green)
            elif promedio < 4.0:
                tbl_style.add('TEXTCOLOR', (5,row_idx), (5,row_idx), colors.red)
        except:
            pass

    table.setStyle(tbl_style)
    elements.append(table)

    # Footer con fecha y página
    def add_page_number(canvas, doc):
        canvas.saveState()
        footer_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Página {doc.page}"
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(landscape(A4)[0]-1*cm, 1*cm, footer_text)
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
