import oracledb

# Configurar credenciales
DB_USER = "tester"
DB_PASS = "testing1234"
DB_HOST = "localhost"
DB_PORT = "1521"
DB_SERVICE = "ORCLPDB"
DB_DSN = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"

def get_connection():
    # Devuelve una nueva conexión a la base de datos Oracle.
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASS,
        dsn=DB_DSN
    )