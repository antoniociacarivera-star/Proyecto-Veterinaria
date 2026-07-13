import oracledb

from utils.seguridad import descifrar_credenciales


def obtener_conexion(password_maestra: str):
    """Abre una conexión con Oracle usando credenciales cifradas."""

    credenciales = descifrar_credenciales(
        password_maestra
    )

    conexion = oracledb.connect(
        user=credenciales["usuario"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=int(credenciales["puerto"]),
        service_name=credenciales["servicio"]
    )

    return conexion