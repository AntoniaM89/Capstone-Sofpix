import pymysql

# Configuración MySQL
DB_USER = "root"
DB_PASS = "Yin1234."
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "SSA_DB"

def get_connection():
    """
    Devuelve una nueva conexión a la base de datos MySQL.
    """
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # Para obtener resultados como diccionario
    )
