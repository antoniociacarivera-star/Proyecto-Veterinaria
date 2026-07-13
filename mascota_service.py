import json
from typing import Optional

from models.mascota import Mascota


def registrar_evento(
    conexion,
    tipo_evento: str,
    contenido: dict
) -> None:
    """
    Guarda un evento JSON dentro de la tabla VET1.
    """

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


def registrar_mascota(
    conexion,
    mascota: Mascota,
    usuario: str = "ADMINISTRADOR"
) -> int:
    """
    Registra una mascota y devuelve su ID.
    """

    cursor = conexion.cursor()
    id_generado = cursor.var(int)

    try:
        cursor.execute(
            """
            INSERT INTO MASCOTAS (
                ID_DUENO,
                NOMBRE_MASCOTA,
                ESPECIE,
                RAZA,
                ACTIVO,
                USUARIO_ALTA,
                FECHA_ALTA
            )
            VALUES (
                :id_dueno,
                :nombre,
                :especie,
                :raza,
                1,
                :usuario,
                SYSDATE
            )
            RETURNING ID_MASCOTA INTO :id_generado
            """,
            {
                "id_dueno": mascota.id_dueno,
                "nombre": mascota.nombre.strip(),
                "especie": mascota.especie.strip().upper(),
                "raza": (
                    mascota.raza.strip()
                    if mascota.raza
                    else None
                ),
                "usuario": usuario,
                "id_generado": id_generado
            }
        )

        id_mascota = int(id_generado.getvalue()[0])

        registrar_evento(
            conexion,
            "MASCOTA_REGISTRADA",
            {
                "id_mascota": id_mascota,
                "id_dueno": mascota.id_dueno,
                "mascota": mascota.nombre.strip(),
                "especie": mascota.especie.strip().upper(),
                "raza": mascota.raza,
                "usuario": usuario,
                "mensaje": (
                    f"La mascota {mascota.nombre.strip()} "
                    "fue registrada correctamente."
                )
            }
        )

        conexion.commit()
        return id_mascota

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()


def listar_mascotas(
    conexion,
    incluir_inactivas: bool = False
) -> list[dict]:
    """
    Devuelve todas las mascotas con el nombre del dueño.
    """

    cursor = conexion.cursor()

    try:
        consulta = """
            SELECT
                M.ID_MASCOTA,
                M.ID_DUENO,
                M.NOMBRE_MASCOTA,
                M.ESPECIE,
                M.RAZA,
                M.ACTIVO,
                M.FECHA_ALTA,
                D.NOMBRE AS NOMBRE_DUENO,
                D.TELEFONO,
                D.CORREO
            FROM MASCOTAS M
            INNER JOIN DUENOS D
                ON D.ID_DUENO = M.ID_DUENO
        """

        if not incluir_inactivas:
            consulta += """
                WHERE NVL(M.ACTIVO, 1) = 1
            """

        consulta += """
            ORDER BY M.ID_MASCOTA DESC
        """

        cursor.execute(consulta)
        filas = cursor.fetchall()

        mascotas = []

        for fila in filas:
            mascotas.append(
                {
                    "ID": fila[0],
                    "ID dueño": fila[1],
                    "Mascota": fila[2],
                    "Especie": fila[3],
                    "Raza": fila[4] or "No especificada",
                    "Estado": (
                        "ACTIVA"
                        if fila[5] == 1
                        else "INACTIVA"
                    ),
                    "Fecha de registro": fila[6],
                    "Dueño": fila[7],
                    "Teléfono": fila[8] or "",
                    "Correo": fila[9] or ""
                }
            )

        return mascotas

    finally:
        cursor.close()


def buscar_mascotas(
    conexion,
    texto: str
) -> list[dict]:
    """
    Busca mascotas por nombre, especie, raza o dueño.
    """

    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                M.ID_MASCOTA,
                M.ID_DUENO,
                M.NOMBRE_MASCOTA,
                M.ESPECIE,
                M.RAZA,
                M.ACTIVO,
                M.FECHA_ALTA,
                D.NOMBRE AS NOMBRE_DUENO,
                D.TELEFONO,
                D.CORREO
            FROM MASCOTAS M
            INNER JOIN DUENOS D
                ON D.ID_DUENO = M.ID_DUENO
            WHERE NVL(M.ACTIVO, 1) = 1
              AND (
                    UPPER(M.NOMBRE_MASCOTA)
                        LIKE UPPER(:busqueda)
                 OR UPPER(M.ESPECIE)
                        LIKE UPPER(:busqueda)
                 OR UPPER(NVL(M.RAZA, ''))
                        LIKE UPPER(:busqueda)
                 OR UPPER(D.NOMBRE)
                        LIKE UPPER(:busqueda)
              )
            ORDER BY M.NOMBRE_MASCOTA
            """,
            {
                "busqueda": f"%{texto.strip()}%"
            }
        )

        filas = cursor.fetchall()
        resultados = []

        for fila in filas:
            resultados.append(
                {
                    "ID": fila[0],
                    "ID dueño": fila[1],
                    "Mascota": fila[2],
                    "Especie": fila[3],
                    "Raza": fila[4] or "No especificada",
                    "Estado": (
                        "ACTIVA"
                        if fila[5] == 1
                        else "INACTIVA"
                    ),
                    "Fecha de registro": fila[6],
                    "Dueño": fila[7],
                    "Teléfono": fila[8] or "",
                    "Correo": fila[9] or ""
                }
            )

        return resultados

    finally:
        cursor.close()


def obtener_mascota_por_id(
    conexion,
    id_mascota: int
) -> Optional[dict]:
    """
    Obtiene una sola mascota por su ID.
    """

    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                ID_MASCOTA,
                ID_DUENO,
                NOMBRE_MASCOTA,
                ESPECIE,
                RAZA,
                ACTIVO
            FROM MASCOTAS
            WHERE ID_MASCOTA = :id_mascota
            """,
            {
                "id_mascota": id_mascota
            }
        )

        fila = cursor.fetchone()

        if not fila:
            return None

        return {
            "id_mascota": fila[0],
            "id_dueno": fila[1],
            "nombre": fila[2],
            "especie": fila[3],
            "raza": fila[4] or "",
            "activo": fila[5]
        }

    finally:
        cursor.close()


def actualizar_mascota(
    conexion,
    id_mascota: int,
    id_dueno: int,
    nombre: str,
    especie: str,
    raza: Optional[str],
    usuario: str = "ADMINISTRADOR"
) -> bool:
    """
    Actualiza los datos de una mascota.
    """

    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE MASCOTAS
            SET
                ID_DUENO = :id_dueno,
                NOMBRE_MASCOTA = :nombre,
                ESPECIE = :especie,
                RAZA = :raza,
                USUARIO_MODIFICA = :usuario,
                FECHA_MODIFICA = SYSDATE
            WHERE ID_MASCOTA = :id_mascota
              AND NVL(ACTIVO, 1) = 1
            """,
            {
                "id_dueno": id_dueno,
                "nombre": nombre.strip(),
                "especie": especie.strip().upper(),
                "raza": raza.strip() if raza else None,
                "usuario": usuario,
                "id_mascota": id_mascota
            }
        )

        actualizado = cursor.rowcount > 0

        if actualizado:
            registrar_evento(
                conexion,
                "MASCOTA_ACTUALIZADA",
                {
                    "id_mascota": id_mascota,
                    "id_dueno": id_dueno,
                    "mascota": nombre.strip(),
                    "especie": especie.strip().upper(),
                    "raza": raza,
                    "usuario": usuario,
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


def eliminar_mascota(
    conexion,
    id_mascota: int,
    usuario: str = "ADMINISTRADOR"
) -> bool:
    """
    Realiza una eliminación lógica estableciendo ACTIVO = 0.
    """

    mascota = obtener_mascota_por_id(
        conexion,
        id_mascota
    )

    if not mascota:
        return False

    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE MASCOTAS
            SET
                ACTIVO = 0,
                USUARIO_MODIFICA = :usuario,
                FECHA_MODIFICA = SYSDATE
            WHERE ID_MASCOTA = :id_mascota
              AND NVL(ACTIVO, 1) = 1
            """,
            {
                "usuario": usuario,
                "id_mascota": id_mascota
            }
        )

        eliminado = cursor.rowcount > 0

        if eliminado:
            registrar_evento(
                conexion,
                "MASCOTA_DESACTIVADA",
                {
                    "id_mascota": id_mascota,
                    "mascota": mascota["nombre"],
                    "usuario": usuario,
                    "mensaje": (
                        f"La mascota {mascota['nombre']} "
                        "fue desactivada."
                    )
                }
            )

        conexion.commit()
        return eliminado

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()


def reactivar_mascota(
    conexion,
    id_mascota: int,
    usuario: str = "ADMINISTRADOR"
) -> bool:
    """
    Reactiva una mascota que había sido desactivada.
    """

    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            UPDATE MASCOTAS
            SET
                ACTIVO = 1,
                USUARIO_MODIFICA = :usuario,
                FECHA_MODIFICA = SYSDATE
            WHERE ID_MASCOTA = :id_mascota
              AND ACTIVO = 0
            """,
            {
                "usuario": usuario,
                "id_mascota": id_mascota
            }
        )

        reactivado = cursor.rowcount > 0

        if reactivado:
            registrar_evento(
                conexion,
                "MASCOTA_REACTIVADA",
                {
                    "id_mascota": id_mascota,
                    "usuario": usuario,
                    "mensaje": (
                        "La mascota fue reactivada "
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