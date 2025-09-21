import os
import oracledb
from dotenv import load_dotenv

load_dotenv() #Carga las variables de entorno .env

# Inicializar Thick Mode
if os.getenv("USE_THICK") == "1":
    lib_dir = os.getenv("ORACLE_INSTANTCLIENT_DIR")
    if lib_dir:
        oracledb.init_oracle_client(lib_dir=lib_dir)

def get_connection():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "1521")
    service_name = os.getenv("DB_SERVICE", "ORCLPDB")

    # Crear DSN
    dsn = oracledb.makedsn(host, port, service_name=service_name)

    conn = oracledb.connect(user=user, password=password, dsn=dsn)
    return conn

