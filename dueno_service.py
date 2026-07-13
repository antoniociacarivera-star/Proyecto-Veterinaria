import json
from typing import Optional

from models.dueno import Dueno


def registrar_evento(
    conexion,
    tipo_evento: str,
    contenido: dict
) -> None:
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO VET1 (
                TIPO_EVENTO,
                CONTENIDO_JSON
            )
            VALUES (
                :tipo_evento,
                :contenido_json
            )
            """,
            {
                "tipo_evento": tipo_evento,
                "contenido_json": json.dumps(
                    contenido,
                    ensure_ascii=False
                )
            }
        )

    finally:
        cursor.close()


def registrar_dueno(
    conexion,
    dueno: Dueno,
    usuario: str = "ADMINISTRADOR"
) -> int:
    cursor = conexion.cursor()
    id_generado = cursor.var(int)

    try:
        cursor.execute(
            """
            INSERT INTO DUENOS (
                NOMBRE,
                TELEFONO,
                CORREO,
                ACTIVO,
                USUARIO_ALTA,
                FECHA_ALTA
            )
            VALUES (
                :nombre,
                :telefono,
                :correo,
                1,
                :usuario,
                SYSDATE
            )
            RETURNING ID_DUENO INTO :id_generado
            """,
            {
                "nombre": dueno.nombre.strip(),
                "telefono": (
                    dueno.telefono.strip()
                    if dueno.telefono
                    else None
                ),
                "correo": (
                    dueno.correo.strip().lower()
                    if dueno.correo
                    else None
                ),
                "usuario": usuario,
                "id_generado": id_generado
            }
        )

        id_dueno = int(id_generado.getvalue()[0])

        registrar_evento(
            conexion,
            "DUENO_REGISTRADO",
            {
                "id_dueno": id_dueno,
                "nombre": dueno.nombre.strip(),
                "telefono": dueno.telefono,
                "correo": dueno.correo,
                "mensaje": (
                    f"El dueño {dueno.nombre.strip()} "
                    "fue registrado correctamente."
                )
            }
        )

        conexion.commit()
        return id_dueno

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()


def listar_duenos(
    conexion,
    incluir_inactivos: bool = False
) -> list[dict]:
    cursor = conexion.cursor()

    try:
        consulta = """
            SELECT
                ID_DUENO,
                NOMBRE,
                TELEFONO,
                CORREO,
                ACTIVO,
                FECHA_ALTA
            FROM DUENOS
        """

        if not incluir_inactivos:
            consulta += """
                WHERE NVL(ACTIVO, 1) = 1
            """

        consulta += """
            ORDER BY NOMBRE
        """

        cursor.execute(consulta)
        filas = cursor.fetchall()

        return [
            {
                "ID": fila[0],
                "Nombre": fila[1],
                "Teléfono": fila[2] or "",
                "Correo": fila[3] or "",
                "Estado": (
                    "ACTIVO"
                    if fila[4] == 1
                    else "INACTIVO"
                ),
                "Fecha de registro": fila[5]
            }
            for fila in filas
        ]

    finally:
        cursor.close()


def buscar_duenos(
    conexion,
    texto: str
) -> list[dict]:
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                ID_DUENO,
                NOMBRE,
                TELEFONO,
                CORREO,
                ACTIVO,
                FECHA_ALTA
            FROM DUENOS
            WHERE NVL(ACTIVO, 1) = 1
              AND (
                    UPPER(NOMBRE)
                        LIKE UPPER(:busqueda)
                 OR UPPER(NVL(TELEFONO, ''))
                        LIKE UPPER(:busqueda)
                 OR UPPER(NVL(CORREO, ''))
                        LIKE UPPER(:busqueda)
              )
            ORDER BY NOMBRE
            """,
            {
                "busqueda": f"%{texto.strip()}%"
            }
        )

        filas = cursor.fetchall()

        return [
            {
                "ID": fila[0],
                "Nombre": fila[1],
                "Teléfono": fila[2] or "",
                "Correo": fila[3] or "",
                "Estado": (
                    "ACTIVO"
                    if fila[4] == 1
                    else "INACTIVO"
                ),
                "Fecha de registro": fila[5]
            }
            for fila in filas
        ]

    finally:
        cursor.close()


def obtener_dueno_por_id(
    conexion,
    id_dueno: int
) -> Optional[dict]:
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                ID_DUENO,
                NOMBRE,
                TELEFONO,
                CORREO,
                ACTIVO
            FROM DUENOS
            WHERE ID_DUENO = :id_dueno
            """,
            {
                "id_dueno": id_dueno
            }
        )

        fila = cursor.fetchone()

        if not fila:
            return None

        return {
            "id_dueno": fila[0],
            "nombre": fila[1],
            "telefono": fila[2] or "",
            "correo": fila[3] or "",
            "activo": fila[4]
        }

    finally:
        cursor.close()


def actualizar_dueno(
    conexion,
    id_dueno: int,
    nombre: str,
    telefono: Optional[str],
    correo: Optional[str],
    usuario: str = "ADMINISTRADOR"
) -> bool:
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE DUENOS
            SET
                NOMBRE = :nombre,
                TELEFONO = :telefono,
                CORREO = :correo,
                USUARIO_MODIFICA = :usuario,
                FECHA_MODIFICA = SYSDATE
            WHERE ID_DUENO = :id_dueno
              AND NVL(ACTIVO, 1) = 1
            """,
            {
                "nombre": nombre.strip(),
                "telefono": (
                    telefono.strip()
                    if telefono
                    else None
                ),
                "correo": (
                    correo.strip().lower()
                    if correo
                    else None
                ),
                "usuario": usuario,
                "id_dueno": id_dueno
            }
        )

        actualizado = cursor.rowcount > 0

        if actualizado:
            registrar_evento(
                conexion,
                "DUENO_ACTUALIZADO",
                {
                    "id_dueno": id_dueno,
                    "nombre": nombre.strip(),
                    "telefono": telefono,
                    "correo": correo,
                    "mensaje": (
                        f"Los datos de {nombre.strip()} "
                        "fueron actualizados."
                    )
                }
            )

        conexion.commit()
        return actualizado

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()


def desactivar_dueno(
    conexion,
    id_dueno: int,
    usuario: str = "ADMINISTRADOR"
) -> bool:
    dueno = obtener_dueno_por_id(
        conexion,
        id_dueno
    )

    if not dueno:
        return False

    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE DUENOS
            SET
                ACTIVO = 0,
                USUARIO_MODIFICA = :usuario,
                FECHA_MODIFICA = SYSDATE
            WHERE ID_DUENO = :id_dueno
              AND NVL(ACTIVO, 1) = 1
            """,
            {
                "usuario": usuario,
                "id_dueno": id_dueno
            }
        )

        desactivado = cursor.rowcount > 0

        if desactivado:
            registrar_evento(
                conexion,
                "DUENO_DESACTIVADO",
                {
                    "id_dueno": id_dueno,
                    "nombre": dueno["nombre"],
                    "mensaje": (
                        f"El dueño {dueno['nombre']} "
                        "fue desactivado."
                    )
                }
            )

        conexion.commit()
        return desactivado

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()


def reactivar_dueno(
    conexion,
    id_dueno: int,
    usuario: str = "ADMINISTRADOR"
) -> bool:
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE DUENOS
            SET
                ACTIVO = 1,
                USUARIO_MODIFICA = :usuario,
                FECHA_MODIFICA = SYSDATE
            WHERE ID_DUENO = :id_dueno
              AND ACTIVO = 0
            """,
            {
                "usuario": usuario,
                "id_dueno": id_dueno
            }
        )

        reactivado = cursor.rowcount > 0

        if reactivado:
            registrar_evento(
                conexion,
                "DUENO_REACTIVADO",
                {
                    "id_dueno": id_dueno,
                    "mensaje": (
                        "El dueño fue reactivado "
                        "correctamente."
                    )
                }
            )

        conexion.commit()
        return reactivado

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()