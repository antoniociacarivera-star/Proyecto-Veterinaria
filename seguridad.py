import base64
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_CREDENCIALES = BASE_DIR / "config" / "credenciales.enc"


def generar_clave(password_maestra: str, salt: bytes) -> bytes:
    """Genera una clave Fernet usando la contraseña maestra."""

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )

    clave = kdf.derive(password_maestra.encode("utf-8"))

    return base64.urlsafe_b64encode(clave)


def cifrar_credenciales(
    credenciales: dict,
    password_maestra: str
) -> None:
    """Cifra las credenciales y las guarda en credenciales.enc."""

    if not password_maestra:
        raise ValueError("La contraseña maestra no puede estar vacía.")

    ARCHIVO_CREDENCIALES.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    salt = os.urandom(16)
    clave = generar_clave(password_maestra, salt)
    cifrador = Fernet(clave)

    texto_json = json.dumps(
        credenciales,
        ensure_ascii=False
    ).encode("utf-8")

    datos_cifrados = cifrador.encrypt(texto_json)

    with open(ARCHIVO_CREDENCIALES, "wb") as archivo:
        archivo.write(salt + datos_cifrados)


def descifrar_credenciales(password_maestra: str) -> dict:
    """Descifra las credenciales usando la contraseña maestra."""

    if not ARCHIVO_CREDENCIALES.exists():
        raise FileNotFoundError(
            "No existe config/credenciales.enc. "
            "Ejecuta primero utils/crear_credenciales.py."
        )

    with open(ARCHIVO_CREDENCIALES, "rb") as archivo:
        contenido = archivo.read()

    if len(contenido) <= 16:
        raise ValueError(
            "El archivo credenciales.enc está vacío o dañado."
        )

    salt = contenido[:16]
    datos_cifrados = contenido[16:]

    clave = generar_clave(password_maestra, salt)
    cifrador = Fernet(clave)

    try:
        texto_json = cifrador.decrypt(datos_cifrados)
        return json.loads(texto_json.decode("utf-8"))

    except InvalidToken as error:
        raise ValueError(
            "La contraseña maestra es incorrecta."
        ) from error

    except json.JSONDecodeError as error:
        raise ValueError(
            "Las credenciales cifradas están dañadas."
        ) from error