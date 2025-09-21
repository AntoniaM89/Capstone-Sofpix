/*** DROP de todas las tablas y autoincrementables***/

DROP TABLE actividad CASCADE CONSTRAINTS;
DROP TABLE alumno CASCADE CONSTRAINTS;
DROP TABLE asignatura CASCADE CONSTRAINTS;
DROP TABLE curso CASCADE CONSTRAINTS;
DROP TABLE nota CASCADE CONSTRAINTS;
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
VALUES ('maria.gonzalez@colegio.cl','María','Fernanda','González','Pérez', 'pass001', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('juan.rojas@instituto.cl','Juan','Andrés','Rojas','Morales', 'pass002', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('carolina.torres@liceo.cl','Carolina','','Torres','López', 'pass003', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('diego.munoz@escuela.cl','Diego','Alberto','Muñoz','Silva', 'pass004', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('sofia.castillo@colegio.cl','Sofía','','Castillo','Martínez', 'pass005', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('ricardo.fernandez@instituto.cl','Ricardo','Eduardo','Fernández','Vega', 'pass006', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('valentina.rivera@liceo.cl','Valentina','','Rivera','Sánchez', 'pass007', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('andres.martinez@escuela.cl','Andrés','Felipe','Martínez','Contreras', 'pass008', 'Media');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('paula.vargas@colegio.cl','Paula','Isabel','Vargas','Castro', 'pass009', 'Basica');
INSERT INTO profesor(correo, nom_user, seg_nom_user, ap_pat_user, ap_mat_user, pass_enc, area)
VALUES ('fernando.ortiz@instituto.cl','Fernando','','Ortiz','Ramírez', 'pass010', 'Media');


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


-- Asignaturas predefinidas
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('MAT1', 'Matematicas', 'Juan Andrés Rojas Morales', 'juan.rojas@instituto.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('LYC2', 'Lenguaje y Comunicaciones', 'María Fernanda González Pérez', 'maria.gonzalez@colegio.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('CIE3', 'Ciencias', 'Diego Alberto Muñoz Silva', 'diego.munoz@escuela.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('BIO4', 'Biologia', 'Carolina Torres López', 'carolina.torres@liceo.cl');
INSERT INTO asignatura (codigo, nombre_asi, nombre_prof, profesor_correo)
VALUES ('FIL5', 'Filosofia', 'Sofía Castillo Martínez', 'sofia.castillo@colegio.cl');


/*** Si no se pone el commit no se refleja ***/
COMMIT