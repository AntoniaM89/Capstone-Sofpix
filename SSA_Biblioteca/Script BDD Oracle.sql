-- ======================================
-- Tablas para Oracle
-- ======================================

-- Tabla profesor
CREATE TABLE profesor (
    correo       VARCHAR2(100) NOT NULL,
    nom_user     VARCHAR2(50) NOT NULL,
    seg_nom_user VARCHAR2(50),
    ap_pat_user  VARCHAR2(50) NOT NULL,
    ap_mat_user  VARCHAR2(50),
    pass_enc     VARCHAR2(100) NOT NULL,
    area         VARCHAR2(50) NOT NULL,
    rol          VARCHAR2(20) DEFAULT 'profesor' CHECK (rol IN ('admin','profesor')),
    PRIMARY KEY (correo)
);

-- Tabla curso
CREATE TABLE curso (
    id_curso   VARCHAR2(50) NOT NULL,
    nivel      VARCHAR2(50) NOT NULL,
    generacion NUMBER NOT NULL,
    PRIMARY KEY (id_curso)
);

-- Tabla alumno
CREATE TABLE alumno (
    rut_alum     NUMBER(20) NOT NULL,
    nom_alum     VARCHAR2(50) NOT NULL,
    seg_nom_alum VARCHAR2(50),
    ap_pat_alum  VARCHAR2(50) NOT NULL,
    ap_mat_alum  VARCHAR2(50),
    curso_id     VARCHAR2(50),
    PRIMARY KEY (rut_alum),
    FOREIGN KEY (curso_id) REFERENCES curso(id_curso)
);

-- Tabla asignatura
CREATE TABLE asignatura (
    codigo          VARCHAR2(50) NOT NULL,
    nombre_asi      VARCHAR2(50) NOT NULL,
    profesor_correo VARCHAR2(100),
    PRIMARY KEY (codigo),
    FOREIGN KEY (profesor_correo) REFERENCES profesor(correo)
);

-- Tabla intermedia curso_asignatura
CREATE TABLE curso_asignatura (
    curso_id VARCHAR2(50) NOT NULL,
    asignatura_codigo VARCHAR2(50) NOT NULL,
    PRIMARY KEY (curso_id, asignatura_codigo),
    FOREIGN KEY (curso_id) REFERENCES curso(id_curso) ON DELETE CASCADE,
    FOREIGN KEY (asignatura_codigo) REFERENCES asignatura(codigo) ON DELETE CASCADE
);

-- Tabla intermedia alumno_asignatura
CREATE TABLE alumno_asignatura (
    id INT NOT NULL,
    alumno_rut NUMBER(20) NOT NULL,
    asignatura_codigo VARCHAR2(50) NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (alumno_rut, asignatura_codigo),
    FOREIGN KEY (alumno_rut) REFERENCES alumno(rut_alum) ON DELETE CASCADE,
    FOREIGN KEY (asignatura_codigo) REFERENCES asignatura(codigo) ON DELETE CASCADE
);

-- Secuencia y trigger para id auto-incremental de alumno_asignatura
CREATE SEQUENCE seq_alumno_asignatura START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER trg_alumno_asignatura
BEFORE INSERT ON alumno_asignatura
FOR EACH ROW
BEGIN
  IF :NEW.id IS NULL THEN
    SELECT seq_alumno_asignatura.NEXTVAL INTO :NEW.id FROM dual;
  END IF;
END;
/

-- Tabla actividad
CREATE TABLE actividad (
    id_act         VARCHAR2(50) NOT NULL,
    nom_act        VARCHAR2(50) NOT NULL,
    tipo_act       VARCHAR2(50) NOT NULL,
    json_act       CLOB,
    nombre_carpeta VARCHAR2(50) NOT NULL,
    fecha_cre      TIMESTAMP NOT NULL,
    curso_id       VARCHAR2(50),
    PRIMARY KEY (id_act),
    FOREIGN KEY (curso_id) REFERENCES curso(id_curso)
);

-- Tabla nota
CREATE TABLE nota (
    id_nota           VARCHAR2(100) NOT NULL,
    nombre            VARCHAR2(50) NOT NULL,        
    nota              NUMBER(5,2) NOT NULL,
    observacion       VARCHAR2(500),
    asignatura_codigo VARCHAR2(50) NOT NULL,
    alumno_rut NUMBER(20) NOT NULL,
    PRIMARY KEY (id_nota),
    FOREIGN KEY (asignatura_codigo) REFERENCES asignatura(codigo),
    FOREIGN KEY (alumno_rut) REFERENCES alumno(rut_alum)
);

-- Tabla biblioteca
CREATE TABLE biblioteca (
    id INT NOT NULL,
    nombre          VARCHAR2(255) NOT NULL,
    tipo            VARCHAR2(50),                
    contenido       BLOB NOT NULL,          
    fecha_subida    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    carpeta         VARCHAR2(100),               
    autor_original  VARCHAR2(100),
    profesor_correo VARCHAR2(100),               
    PRIMARY KEY (id),
    FOREIGN KEY (profesor_correo) REFERENCES profesor(correo)
);

-- Secuencia y trigger para id auto-incremental de biblioteca
CREATE SEQUENCE seq_biblioteca START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER trg_biblioteca
BEFORE INSERT ON biblioteca
FOR EACH ROW
BEGIN
  IF :NEW.id IS NULL THEN
    SELECT seq_biblioteca.NEXTVAL INTO :NEW.id FROM dual;
  END IF;
END;
/

-- Tabla quiz
CREATE TABLE quiz (
    id INT NOT NULL,
    titulo          VARCHAR2(100) NOT NULL,
    descripcion     VARCHAR2(400),
    profesor_correo VARCHAR2(100) NOT NULL,
    fecha_creacion  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    carpeta         VARCHAR2(100) DEFAULT 'General',
    PRIMARY KEY (id),
    FOREIGN KEY (profesor_correo) REFERENCES profesor(correo)
);

-- Secuencia y trigger para id auto-incremental de quiz
CREATE SEQUENCE seq_quiz START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER trg_quiz
BEFORE INSERT ON quiz
FOR EACH ROW
BEGIN
  IF :NEW.id IS NULL THEN
    SELECT seq_quiz.NEXTVAL INTO :NEW.id FROM dual;
  END IF;
END;
/

-- Tabla quiz_pregunta
CREATE TABLE quiz_pregunta (
    id INT NOT NULL,
    quiz_id INT NOT NULL,
    pregunta            VARCHAR2(500) NOT NULL,
    img_url             VARCHAR2(500),
    opcion_a            VARCHAR2(250) NOT NULL,
    opcion_b            VARCHAR2(250) NOT NULL,
    opcion_c            VARCHAR2(250) NOT NULL,
    opcion_d            VARCHAR2(250) NOT NULL,
    respuesta_correcta  VARCHAR2(1) CHECK (respuesta_correcta IN ('A','B','C','D')) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
);

-- Secuencia y trigger para id auto-incremental de quiz_pregunta
CREATE SEQUENCE seq_quiz_pregunta START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER trg_quiz_pregunta
BEFORE INSERT ON quiz_pregunta
FOR EACH ROW
BEGIN
  IF :NEW.id IS NULL THEN
    SELECT seq_quiz_pregunta.NEXTVAL INTO :NEW.id FROM dual;
  END IF;
END;
/