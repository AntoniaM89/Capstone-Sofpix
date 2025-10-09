-- Crear base de datos
CREATE DATABASE IF NOT EXISTS SSA_DB;
USE SSA_DB;

-- Borrar tablas si existen (orden correcto por claves foráneas)
DROP TABLE IF EXISTS nota;
DROP TABLE IF EXISTS actividad;
DROP TABLE IF EXISTS alumno;
DROP TABLE IF EXISTS asignatura;
DROP TABLE IF EXISTS curso;
DROP TABLE IF EXISTS biblioteca;
DROP TABLE IF EXISTS quiz_pregunta;
DROP TABLE IF EXISTS quiz;
DROP TABLE IF EXISTS profesor;


-- ======================================
-- Tablas
-- ======================================

-- Tabla profesor
CREATE TABLE profesor (
    correo       VARCHAR(100) NOT NULL,
    nom_user     VARCHAR(50) NOT NULL,
    seg_nom_user VARCHAR(50),
    ap_pat_user  VARCHAR(50) NOT NULL,
    ap_mat_user  VARCHAR(50),
    pass_enc     VARCHAR(100) NOT NULL,
    area         VARCHAR(50) NOT NULL,
    rol          ENUM('admin','profesor') NOT NULL DEFAULT 'profesor',
    PRIMARY KEY (correo)
);

-- Tabla curso
CREATE TABLE curso (
    id_curso   VARCHAR(50) NOT NULL,
    nivel      VARCHAR(50) NOT NULL,
    generacion INT NOT NULL,
    PRIMARY KEY (id_curso)
);

-- Tabla alumno
CREATE TABLE alumno (
    rut_alum     INT NOT NULL,
    nom_alum     VARCHAR(50) NOT NULL,
    seg_nom_alum VARCHAR(50),
    ap_pat_alum  VARCHAR(50) NOT NULL,
    ap_mat_alum  VARCHAR(50),
    curso_id     VARCHAR(50),
    PRIMARY KEY (rut_alum),
    FOREIGN KEY (curso_id) REFERENCES curso (id_curso)
);

-- Tabla asignatura
CREATE TABLE asignatura (
    codigo          VARCHAR(50) NOT NULL,
    nombre_asi      VARCHAR(50) NOT NULL,
    profesor_correo VARCHAR(100),
    PRIMARY KEY (codigo),
    FOREIGN KEY (profesor_correo) REFERENCES profesor (correo)
);

-- Tabla actividad
CREATE TABLE actividad (
    id_act         VARCHAR(50) NOT NULL,
    nom_act        VARCHAR(50) NOT NULL,
    tipo_act       VARCHAR(50) NOT NULL,
    json_act       TEXT,
    nombre_carpeta VARCHAR(50) NOT NULL,
    fecha_cre      DATETIME NOT NULL,
    curso_id       VARCHAR(50),
    PRIMARY KEY (id_act),
    FOREIGN KEY (curso_id) REFERENCES curso (id_curso)
);

-- Tabla nota
CREATE TABLE nota (
    id_nota           VARCHAR(100) NOT NULL,
    nombre            VARCHAR(20) NOT NULL,
    nota              DECIMAL(5,2) NOT NULL,
    codigo_curso      VARCHAR(20) NOT NULL,
    asignatura_codigo VARCHAR(50),
    alumno_rut_alum   INT,
    PRIMARY KEY (id_nota),
    FOREIGN KEY (asignatura_codigo) REFERENCES asignatura (codigo),
    FOREIGN KEY (alumno_rut_alum) REFERENCES alumno (rut_alum)
);


-- NUEVAS

-- Tabla biblioteca
CREATE TABLE biblioteca (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(255) NOT NULL,
    tipo            VARCHAR(50),                -- ej: pdf, docx, img
    contenido       LONGBLOB NOT NULL,          -- archivo binario
    fecha_subida    DATETIME DEFAULT CURRENT_TIMESTAMP,
    carpeta         VARCHAR(100),               -- ubicación
    profesor_correo VARCHAR(100),               -- profesor que sube
    FOREIGN KEY (profesor_correo) REFERENCES profesor (correo)
);

-- Tabla quiz
CREATE TABLE quiz (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    titulo          VARCHAR(100) NOT NULL,
    descripcion     VARCHAR(400),
    profesor_correo VARCHAR(100) NOT NULL,
    fecha_creacion  DATETIME DEFAULT CURRENT_TIMESTAMP,
    carpeta         VARCHAR(100) DEFAULT 'General',
    FOREIGN KEY (profesor_correo) REFERENCES profesor (correo)
);

-- Tabla quiz_pregunta
CREATE TABLE quiz_pregunta (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id             INT NOT NULL,
    pregunta            VARCHAR(500) NOT NULL,
    img_url             VARCHAR(500),
    opcion_a            VARCHAR(250) NOT NULL,
    opcion_b            VARCHAR(250) NOT NULL,
    opcion_c            VARCHAR(250) NOT NULL,
    opcion_d            VARCHAR(250) NOT NULL,
    respuesta_correcta  ENUM('A','B','C','D') NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
);


-- ======================================
-- Inserts
-- ======================================

-- Profesores
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('maria.gonzalez@colegio.cl','María','Fernanda','González','Pérez', 'pass001', 'Basica', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('juan.rojas@instituto.cl','Juan','Andrés','Rojas','Morales', 'pass002', 'Media', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('carolina.torres@liceo.cl','Carolina','','Torres','López', 'pass003', 'Basica', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('diego.munoz@escuela.cl','Diego','Alberto','Muñoz','Silva', 'pass004', 'Media', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('sofia.castillo@colegio.cl','Sofía','','Castillo','Martínez', 'pass005', 'Basica', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('ricardo.fernandez@instituto.cl','Ricardo','Eduardo','Fernández','Vega', 'pass006', 'Basica', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('valentina.rivera@liceo.cl','Valentina','','Rivera','Sánchez', 'pass007', 'Media', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('andres.martinez@escuela.cl','Andrés','Felipe','Martínez','Contreras', 'pass008', 'Media', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('paula.vargas@colegio.cl','Paula','Isabel','Vargas','Castro', 'pass009', 'Basica', 'profesor');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('fernando.ortiz@instituto.cl','Fernando','','Ortiz','Ramírez', 'pass010', 'Media', 'profesor');

-- Usuario administrador
INSERT INTO profesor (correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area, rol)
VALUES ('admin@colegio.cl', 'Admin', NULL, 'Principal', 'Sistema', '123456', 'Administración', 'admin');


-- Cursos
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0032025', '3 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0092026', 'I Medio', 2026);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0PK2025', 'Pre Kinder', 2025);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('00K2025', 'Kinder', 2025);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0122027', 'IV Medio', 2027);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0012025', '1 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0022025', '2 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0042025', '4 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0052025', '5 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion) VALUES ('0062025', '6 Basico', 2025);

-- Alumnos
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100001, 'Lucas', 'Emiliano', 'Gómez', 'López', '0012025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100002, 'Camila', '', 'Fernández', 'Rojas', '0012025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100003, 'Martín', 'Joaquín', 'Pérez', 'Vega', '0022025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100004, 'Valentina', '', 'Sánchez', 'Castro', '0022025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100005, 'Ignacio', 'Alonso', 'Torres', 'Pinto', '0032025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100006, 'Isidora', '', 'Martínez', 'Lara', '0032025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100007, 'Benjamín', 'Mateo', 'Ortiz', 'Ramírez', '0042025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100008, 'Florencia', '', 'Castillo', 'Morales', '0042025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100009, 'Tomás', 'Gabriel', 'Vargas', 'Soto', '0052025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100010, 'Antonia', '', 'Fernández', 'López', '0052025');

-- Asignaturas
INSERT INTO asignatura (codigo, nombre_asi, profesor_correo)
VALUES ('MAT1', 'Matematicas', 'juan.rojas@instituto.cl');
INSERT INTO asignatura (codigo, nombre_asi, profesor_correo)
VALUES ('LYC2', 'Lenguaje y Comunicaciones', 'maria.gonzalez@colegio.cl');
INSERT INTO asignatura (codigo, nombre_asi, profesor_correo)
VALUES ('CIE3', 'Ciencias', 'diego.munoz@escuela.cl');
INSERT INTO asignatura (codigo, nombre_asi, profesor_correo)
VALUES ('BIO4', 'Biologia', 'carolina.torres@liceo.cl');
INSERT INTO asignatura (codigo, nombre_asi, profesor_correo)
VALUES ('FIL5', 'Filosofia', 'sofia.castillo@colegio.cl');

-- Notas (extraídas de tu Oracle y adaptadas a MySQL)
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('MAT1001202520100001Control1', 'Control1', 6.5, '0012025', 'MAT1', 20100001);
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('LYC2001202520100001Tarea1', 'Tarea1', 5.8, '0012025', 'LYC2', 20100001);
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('MAT1001202520100002Control1', 'Control1', 6.0, '0012025', 'MAT1', 20100002);
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('LYC2001202520100002Tarea1', 'Tarea1', 5.5, '0012025', 'LYC2', 20100002);

INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('MAT1002202520100003Control1', 'Control1', 6.2, '0022025', 'MAT1', 20100003);
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('LYC2002202520100003Tarea1', 'Tarea1', 5.7, '0022025', 'LYC2', 20100003);
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('MAT1002202520100004Control1', 'Control1', 6.8, '0022025', 'MAT1', 20100004);
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('LYC2002202520100004Tarea1', 'Tarea1', 6.0, '0022025', 'LYC2', 20100004);

INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('CIE3003202520100005Control1', 'Control1', 5.8, '0032025', 'CIE3', 20100005);
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum)
VALUES ('CIE3003202520100006Control1', 'Control1', 6.4, '0032025', 'CIE3', 20100006);
-- Notas adicionales
INSERT INTO nota (id_nota, nombre, nota, codigo_curso, asignatura_codigo, alumno_rut_alum) VALUES
('MAT1001202520100001Control2', 'Control2', 6.8, '0012025', 'MAT1', 20100001),
('LYC2001202520100001Tarea2', 'Tarea2', 6.0, '0012025', 'LYC2', 20100001),
('MAT1001202520100002Control2', 'Control2', 5.9, '0012025', 'MAT1', 20100002),
('LYC2001202520100002Tarea2', 'Tarea2', 5.7, '0012025', 'LYC2', 20100002),

('MAT1002202520100003Control2', 'Control2', 6.5, '0022025', 'MAT1', 20100003),
('LYC2002202520100003Tarea2', 'Tarea2', 6.2, '0022025', 'LYC2', 20100003),
('MAT1002202520100004Control2', 'Control2', 7.0, '0022025', 'MAT1', 20100004),
('LYC2002202520100004Tarea2', 'Tarea2', 6.5, '0022025', 'LYC2', 20100004),

('CIE3003202520100005Control2', 'Control2', 6.0, '0032025', 'CIE3', 20100005),
('BIO4003202520100006Control1', 'Control1', 5.9, '0032025', 'BIO4', 20100006),

('MAT1004202520100007Control1', 'Control1', 6.7, '0042025', 'MAT1', 20100007),
('LYC2004202520100007Tarea1', 'Tarea1', 6.1, '0042025', 'LYC2', 20100007),
('MAT1004202520100008Control1', 'Control1', 6.3, '0042025', 'MAT1', 20100008),
('LYC2004202520100008Tarea1', 'Tarea1', 5.8, '0042025', 'LYC2', 20100008),

('MAT1005202520100009Control1', 'Control1', 6.9, '0052025', 'MAT1', 20100009),
('LYC2005202520100009Tarea1', 'Tarea1', 6.2, '0052025', 'LYC2', 20100009),
('MAT1005202520100010Control1', 'Control1', 6.4, '0052025', 'MAT1', 20100010),
('LYC2005202520100010Tarea1', 'Tarea1', 6.0, '0052025', 'LYC2', 20100010),

('FIL5001202520100001Ensayo1', 'Ensayo1', 5.5, '0012025', 'FIL5', 20100001),
('FIL5001202520100002Ensayo1', 'Ensayo1', 5.8, '0012025', 'FIL5', 20100002),

('BIO4003202520100005Control2', 'Control2', 6.2, '0032025', 'BIO4', 20100005),
('BIO4003202520100006Control2', 'Control2', 6.5, '0032025', 'BIO4', 20100006),

('CIE3003202520100005Tarea1', 'Tarea1', 5.7, '0032025', 'CIE3', 20100005),
('CIE3003202520100006Tarea1', 'Tarea1', 6.1, '0032025', 'CIE3', 20100006),

('FIL5002202520100003Ensayo1', 'Ensayo1', 6.0, '0022025', 'FIL5', 20100003),
('FIL5002202520100004Ensayo1', 'Ensayo1', 5.9, '0022025', 'FIL5', 20100004),

('FIL5004202520100007Ensayo1', 'Ensayo1', 6.3, '0042025', 'FIL5', 20100007),
('FIL5004202520100008Ensayo1', 'Ensayo1', 6.0, '0042025', 'FIL5', 20100008),

('FIL5005202520100009Ensayo1', 'Ensayo1', 6.4, '0052025', 'FIL5', 20100009),
('FIL5005202520100010Ensayo1', 'Ensayo1', 6.1, '0052025', 'FIL5', 20100010);

COMMIT;