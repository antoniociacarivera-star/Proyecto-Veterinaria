import sys
from getpass import getpass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from utils.seguridad import cifrar_credenciales


def main():
    print()
    print("Configuración segura de Oracle")
    print("------------------------------")

    usuario = input("Usuario de Oracle: ").strip()

    password_oracle = getpass(
        "Contraseña de Oracle: "
    )

    host = input(
        "Host [localhost]: "
    ).strip() or "localhost"

    puerto_texto = input(
        "Puerto [1521]: "
    ).strip() or "1521"

    servicio = input(
        "Service Name [XE]: "
    ).strip() or "XE"

    password_maestra = getpass(
        "Crea una contraseña maestra: "
    )

    confirmacion = getpass(
        "Confirma la contraseña maestra: "
    )

    if not usuario:
        print("El usuario de Oracle no puede estar vacío.")
        return

    if not password_oracle:
        print("La contraseña de Oracle no puede estar vacía.")
        return

    if not password_maestra:
        print("La contraseña maestra no puede estar vacía.")
        return

    if password_maestra != confirmacion:
        print("Las contraseñas maestras no coinciden.")
        return

    try:
        puerto = int(puerto_texto)

    except ValueError:
        print("El puerto debe ser un número.")
        return

    credenciales = {
        "usuario": usuario,
        "password": password_oracle,
        "host": host,
        "puerto": puerto,
        "servicio": servicio
    }

    try:
        cifrar_credenciales(
            credenciales,
            password_maestra
        )

        print()
        print("Credenciales cifradas correctamente.")
        print("Archivo creado: config/credenciales.enc")

    except Exception as error:
        print(f"No se pudieron cifrar las credenciales: {error}")


if __name__ == "__main__":
    main()