/*** DROP de todas las tablas y autoincrementables***/

DROP TABLE actividad CASCADE CONSTRAINTS;
DROP TABLE alumno CASCADE CONSTRAINTS;
DROP TABLE asignatura CASCADE CONSTRAINTS;
DROP TABLE curso CASCADE CONSTRAINTS;
DROP TABLE nota CASCADE CONSTRAINTS;
DROP TABLE BIBLIOTECA CASCADE CONSTRAINTS;
DROP TABLE profesor CASCADE CONSTRAINTS;
DROP SEQUENCE codigo_seq;
DROP SEQUENCE notas_seq;


// DROP USER tester CASCADE;


/*** Crear user Tester***/
/***
ALTER DATABASE OPEN;
ALTER SESSION SET CONTAINER = ORCLPDB;
CREATE USER tester IDENTIFIED BY testing1234 
DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP;
GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE to tester;
ALTER USER TESTER QUOTA UNLIMITED ON USERS;
***/


CREATE TABLE actividad (
    id_act         VARCHAR2(50) NOT NULL,
    nom_act        VARCHAR2(50) NOT NULL,
    tipo_act       VARCHAR2(50) NOT NULL,
    json_act       CLOB,
    nombre_carpeta VARCHAR2(50) NOT NULL,
    fecha_cre      DATE NOT NULL,
    curso_id       VARCHAR2(50)
);

ALTER TABLE actividad ADD CONSTRAINT actividad_pk PRIMARY KEY ( id_act );

CREATE TABLE alumno (
    rut_alum     INTEGER NOT NULL,
    nom_alum     VARCHAR2(50) NOT NULL,
    seg_nom_alum VARCHAR2(50),
    ap_pat_alum  VARCHAR2(50) NOT NULL,
    ap_mat_alum  VARCHAR2(50),
    curso_id     VARCHAR2(50)
);

ALTER TABLE alumno ADD CONSTRAINT alumno_pk PRIMARY KEY ( rut_alum );

CREATE TABLE asignatura (
    codigo          VARCHAR2(50) NOT NULL,
    nombre_asi      VARCHAR2(50) NOT NULL,
    nombre_prof     VARCHAR2(100) NOT NULL,
    profesor_correo VARCHAR2(100)
);

ALTER TABLE asignatura ADD CONSTRAINT asignatura_pk PRIMARY KEY ( codigo );

CREATE TABLE curso (
    id_curso   VARCHAR2(50) NOT NULL,
    nivel      VARCHAR2(50) NOT NULL,
    generacion INTEGER NOT NULL
);

ALTER TABLE curso ADD CONSTRAINT curso_pk PRIMARY KEY ( id_curso );

CREATE TABLE nota (
    id_nota           VARCHAR2(100) NOT NULL,
    nombre            VARCHAR2(20) NOT NULL,
    nota              FLOAT NOT NULL,
    codigo_curso      VARCHAR2(20) NOT NULL,
    asignatura_codigo VARCHAR2(50),
    alumno_rut_alum   INTEGER
);

ALTER TABLE nota ADD CONSTRAINT nota_pk PRIMARY KEY ( id_nota );

CREATE TABLE profesor (
    correo       VARCHAR2(100) NOT NULL,
    nom_user     VARCHAR2(50) NOT NULL,
    seg_nom_user VARCHAR2(50),
    ap_pat_user  VARCHAR2(50) NOT NULL,
    ap_mat_user  VARCHAR2(50),
    pass_enc     VARCHAR2(100) NOT NULL,
    area         VARCHAR2(50) NOT NULL
);

DROP TABLE BIBLIOTECA CASCADE CONSTRAINTS;

CREATE TABLE BIBLIOTECA (
    ID              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          VARCHAR2(255) NOT NULL,
    tipo            VARCHAR2(50),            -- ej: pdf, docx, img
    contenido       BLOB NOT NULL,           -- archivo binario
    fecha_Subida    DATE DEFAULT SYSDATE,
    carpeta         VARCHAR2(100),           -- UbicaciÃ³n
    profesor_correo VARCHAR2(100)            -- Profesor
);

ALTER TABLE biblioteca
    ADD CONSTRAINT profesor_correo_fk FOREIGN KEY (profesor_correo)
        REFERENCES profesor ( correo );

CREATE TABLE QUIZ (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    titulo VARCHAR2(100) NOT NULL,
    descripcion VARCHAR2(400),
    profesor_correo VARCHAR2(100) NOT NULL,
    fecha_creacion DATE DEFAULT SYSDATE,
    carpeta VARCHAR2(100) DEFAULT 'General'
);

ALTER TABLE QUIZ
    ADD CONSTRAINT profesor_correo__quiz_fk FOREIGN KEY (profesor_correo)
        REFERENCES profesor ( correo );

CREATE TABLE QUIZ_PREGUNTA (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    QUIZ_ID NUMBER NOT NULL,
    PREGUNTA VARCHAR2(500) NOT NULL,
    IMG_URL  VARCHAR2(500),
    OPCION_A VARCHAR2(250) NOT NULL,
    OPCION_B VARCHAR2(250) NOT NULL,
    OPCION_C VARCHAR2(250) NOT NULL,
    OPCION_D VARCHAR2(250) NOT NULL,
    RESPUESTA_CORRECTA VARCHAR2(1) CHECK (RESPUESTA_CORRECTA IN ('A','B','C','D')),
    FOREIGN KEY (QUIZ_ID) REFERENCES QUIZ(ID) ON DELETE CASCADE
);

ALTER TABLE profesor ADD CONSTRAINT profesor_pk PRIMARY KEY ( correo );

ALTER TABLE actividad
    ADD CONSTRAINT actividad_curso_fk FOREIGN KEY ( curso_id )
        REFERENCES curso ( id_curso );

ALTER TABLE alumno
    ADD CONSTRAINT alumno_curso_fk FOREIGN KEY ( curso_id )
        REFERENCES curso ( id_curso );

ALTER TABLE asignatura
    ADD CONSTRAINT asignatura_profesor_fk FOREIGN KEY ( profesor_correo )
        REFERENCES profesor ( correo );

ALTER TABLE nota
    ADD CONSTRAINT nota_alumno_fk FOREIGN KEY ( alumno_rut_alum )
        REFERENCES alumno ( rut_alum );

ALTER TABLE nota
    ADD CONSTRAINT nota_asignatura_fk FOREIGN KEY ( asignatura_codigo )
        REFERENCES asignatura ( codigo );
        
CREATE SEQUENCE codigo_seq
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

CREATE SEQUENCE notas_seq
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

/*** Asignatura + curso + rut alumno + nombre evaluacion

/*** Insert de prueba ***/
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('maria.gonzalez@colegio.cl','Mar�a','Fernanda','Gonz�lez','P�rez', 'pass001', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('juan.rojas@instituto.cl','Juan','Andr�s','Rojas','Morales', 'pass002', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('carolina.torres@liceo.cl','Carolina','','Torres','L�pez', 'pass003', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('diego.munoz@escuela.cl','Diego','Alberto','Mu�oz','Silva', 'pass004', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('sofia.castillo@colegio.cl','Sof�a','','Castillo','Mart�nez', 'pass005', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('ricardo.fernandez@instituto.cl','Ricardo','Eduardo','Fern�ndez','Vega', 'pass006', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('valentina.rivera@liceo.cl','Valentina','','Rivera','S�nchez', 'pass007', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('andres.martinez@escuela.cl','Andr�s','Felipe','Mart�nez','Contreras', 'pass008', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('paula.vargas@colegio.cl','Paula','Isabel','Vargas','Castro', 'pass009', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('fernando.ortiz@instituto.cl','Fernando','','Ortiz','Ram�rez', 'pass010', 'Media');


INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0032025', '3 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0092026', 'I Medio', 2026);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0PK2025', 'Pre Kinder', 2025);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('00K2025', 'Kinder', 2025);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0122027', 'IV Medio', 2027);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0012025', '1 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0022025', '2 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0042025', '4 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0052025', '5 Basico', 2025);
INSERT INTO curso(id_curso, nivel, generacion)
VALUES ('0062025', '6 Basico', 2025);



INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100001, 'Lucas', 'Emiliano', 'G�mez', 'L�pez', '0012025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100002, 'Camila', '', 'Fern�ndez', 'Rojas', '0012025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100003, 'Mart�n', 'Joaqu�n', 'P�rez', 'Vega', '0022025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100004, 'Valentina', '', 'S�nchez', 'Castro', '0022025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100005, 'Ignacio', 'Alonso', 'Torres', 'Pinto', '0032025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100006, 'Isidora', '', 'Mart�nez', 'Lara', '0032025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100007, 'Benjam�n', 'Mateo', 'Ortiz', 'Ram�rez', '0042025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100008, 'Florencia', '', 'Castillo', 'Morales', '0042025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100009, 'Tom�s', 'Gabriel', 'Vargas', 'Soto', '0052025');
INSERT INTO alumno(rut_alum, nom_alum, seg_nom_alum, ap_pat_alum, ap_mat_alum, curso_id) 
VALUES (20100010, 'Antonia', '', 'Fern�ndez', 'L�pez', '0052025');


-- Asignaturas predefinidas
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('MAT1', 'Matematicas', 'Juan Andr�s Rojas Morales', 'juan.rojas@instituto.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('LYC2', 'Lenguaje y Comunicaciones', 'Mar�a Fernanda Gonz�lez P�rez', 'maria.gonzalez@colegio.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('CIE3', 'Ciencias', 'Diego Alberto Mu�oz Silva', 'diego.munoz@escuela.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('BIO4', 'Biologia', 'Carolina Torres L�pez', 'carolina.torres@liceo.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('FIL5', 'Filosofia', 'Sof�a Castillo Mart�nez', 'sofia.castillo@colegio.cl');

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
/*** Si no se pone el commit no se refleja ***/
COMMIT