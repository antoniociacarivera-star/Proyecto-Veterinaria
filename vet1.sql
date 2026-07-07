CREATE TABLE VET1 (
    ID_EVENTO      NUMBER GENERATED ALWAYS AS IDENTITY,
    TIPO_EVENTO    VARCHAR2(50),
    CONTENIDO_JSON VARCHAR2(4000),
    FECHA_CREACION TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT PK_VET1 PRIMARY KEY (ID_EVENTO)
);

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Firulais", "diagnostico": "Vacunación", "costo": 350}');

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Michi", "diagnostico": "Revisión general", "costo": 200}');

COMMIT;

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Dante", "diagnostico": "Corte de pelo", "costo": 150}');
COMMIT;

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Lucas", "diagnostico": "Desparasitación", "costo": 180}');

COMMIT;

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Dino", "diagnostico": "Diarrea", "costo": 280}');

COMMIT;

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Rex", "diagnostico": "Baño", "costo": 580}');

COMMIT;

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "nini", "diagnostico": "rabia", "costo": 200}');

COMMIT;
INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Rini", "diagnostico": "Nabia", "costo": 20000}');

COMMIT;


COMMIT;
INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Pini", "diagnostico": "NERITIRRITIS", "costo": 53200}');

COMMIT;


INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "fINEAS", "diagnostico": "Renisitis", "costo": 1200}');

COMMIT;

INSERT INTO VET1 (TIPO_EVENTO, CONTENIDO_JSON) 
VALUES ('NUEVA_CONSULTA', '{"mascota": "Mailo", "diagnostico": "Rabia", "costo": 5200}');

COMMIT;