import streamlit as st

from models.mascota import Mascota
from services.mascota_service import (
    actualizar_mascota,
    buscar_mascotas,
    eliminar_mascota,
    listar_mascotas,
    obtener_mascota_por_id,
    reactivar_mascota,
    registrar_mascota,
)


def obtener_duenos(conexion) -> list[dict]:
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                ID_DUENO,
                NOMBRE,
                TELEFONO,
                CORREO
            FROM DUENOS
            WHERE NVL(ACTIVO, 1) = 1
            ORDER BY NOMBRE
            """
        )

        filas = cursor.fetchall()

        return [
            {
                "id_dueno": fila[0],
                "nombre": fila[1],
                "telefono": fila[2] or "",
                "correo": fila[3] or "",
            }
            for fila in filas
        ]

    finally:
        cursor.close()


def mostrar_registro(conexion):
    st.subheader("➕ Registrar mascota")

    try:
        duenos = obtener_duenos(conexion)

    except Exception as error:
        st.error(f"No se pudieron consultar los dueños: {error}")
        return

    if not duenos:
        st.warning(
            "No existen dueños activos. Registra primero un dueño."
        )
        return

    opciones_duenos = {
        (
            f"{dueno['nombre']} "
            f"(ID: {dueno['id_dueno']})"
        ): dueno["id_dueno"]
        for dueno in duenos
    }

    with st.form(
        "form_registrar_mascota",
        clear_on_submit=True,
    ):
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input(
                "Nombre de la mascota",
                placeholder="Ejemplo: Firulais",
            )

            especie = st.selectbox(
                "Especie",
                [
                    "PERRO",
                    "GATO",
                    "AVE",
                    "CONEJO",
                    "REPTIL",
                    "OTRO",
                ],
            )

        with col2:
            raza = st.text_input(
                "Raza",
                placeholder="Ejemplo: Labrador",
            )

            dueno_seleccionado = st.selectbox(
                "Dueño",
                list(opciones_duenos.keys()),
            )

        guardar = st.form_submit_button(
            "💾 Registrar mascota",
            use_container_width=True,
        )

    if guardar:
        if not nombre.strip():
            st.warning("Escribe el nombre de la mascota.")
            return

        mascota = Mascota(
            id_dueno=opciones_duenos[dueno_seleccionado],
            nombre=nombre.strip(),
            especie=especie,
            raza=raza.strip() or None,
        )

        try:
            id_mascota = registrar_mascota(
                conexion,
                mascota,
            )

            st.success(
                f"🐾 {mascota.nombre} fue registrada "
                f"con el ID {id_mascota}."
            )

            st.balloons()

        except Exception as error:
            st.error(
                f"No se pudo registrar la mascota: {error}"
            )


def mostrar_listado(conexion):
    st.subheader("📋 Listado de mascotas")

    incluir_inactivas = st.checkbox(
        "Mostrar también mascotas inactivas"
    )

    try:
        mascotas = listar_mascotas(
            conexion,
            incluir_inactivas=incluir_inactivas,
        )

    except Exception as error:
        st.error(
            f"No se pudieron consultar las mascotas: {error}"
        )
        return

    if not mascotas:
        st.info("Todavía no existen mascotas registradas.")
        return

    st.dataframe(
        mascotas,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(
                "ID",
                width="small",
            ),
            "ID dueño": st.column_config.NumberColumn(
                "ID dueño",
                width="small",
            ),
            "Fecha de registro": (
                st.column_config.DatetimeColumn(
                    "Fecha de registro",
                    format="DD/MM/YYYY HH:mm",
                )
            ),
        },
    )


def mostrar_busqueda(conexion):
    st.subheader("🔎 Buscar mascota")

    texto = st.text_input(
        "Buscar",
        placeholder=(
            "Escribe el nombre, especie, raza o dueño"
        ),
    )

    if not texto.strip():
        st.info("Escribe un término para comenzar la búsqueda.")
        return

    try:
        resultados = buscar_mascotas(
            conexion,
            texto,
        )

    except Exception as error:
        st.error(
            f"No se pudo realizar la búsqueda: {error}"
        )
        return

    if not resultados:
        st.warning("No se encontraron coincidencias.")
        return

    st.success(
        f"Se encontraron {len(resultados)} resultados."
    )

    st.dataframe(
        resultados,
        use_container_width=True,
        hide_index=True,
    )


def mostrar_edicion(conexion):
    st.subheader("✏️ Editar mascota")

    try:
        mascotas = listar_mascotas(
            conexion,
            incluir_inactivas=False,
        )
        duenos = obtener_duenos(conexion)

    except Exception as error:
        st.error(f"No se pudieron cargar los datos: {error}")
        return

    if not mascotas:
        st.warning("No hay mascotas activas para editar.")
        return

    if not duenos:
        st.warning("No hay dueños activos disponibles.")
        return

    opciones_mascotas = {
        (
            f"{mascota['Mascota']} "
            f"(ID: {mascota['ID']})"
        ): mascota["ID"]
        for mascota in mascotas
    }

    seleccion = st.selectbox(
        "Selecciona una mascota",
        list(opciones_mascotas.keys()),
    )

    id_mascota = opciones_mascotas[seleccion]

    try:
        datos = obtener_mascota_por_id(
            conexion,
            id_mascota,
        )

    except Exception as error:
        st.error(
            f"No se pudo cargar la mascota: {error}"
        )
        return

    if not datos:
        st.warning("La mascota seleccionada ya no existe.")
        return

    opciones_duenos = {
        (
            f"{dueno['nombre']} "
            f"(ID: {dueno['id_dueno']})"
        ): dueno["id_dueno"]
        for dueno in duenos
    }

    etiquetas_duenos = list(opciones_duenos.keys())
    id_dueno_actual = datos["id_dueno"]

    indice_dueno = 0

    for indice, etiqueta in enumerate(etiquetas_duenos):
        if opciones_duenos[etiqueta] == id_dueno_actual:
            indice_dueno = indice
            break

    especies = [
        "PERRO",
        "GATO",
        "AVE",
        "CONEJO",
        "REPTIL",
        "OTRO",
    ]

    especie_actual = datos["especie"].upper()

    indice_especie = (
        especies.index(especie_actual)
        if especie_actual in especies
        else especies.index("OTRO")
    )

    with st.form("form_editar_mascota"):
        nombre = st.text_input(
            "Nombre",
            value=datos["nombre"],
        )

        col1, col2 = st.columns(2)

        with col1:
            especie = st.selectbox(
                "Especie",
                especies,
                index=indice_especie,
            )

        with col2:
            raza = st.text_input(
                "Raza",
                value=datos["raza"],
            )

        dueno_seleccionado = st.selectbox(
            "Dueño",
            etiquetas_duenos,
            index=indice_dueno,
        )

        actualizar = st.form_submit_button(
            "💾 Guardar cambios",
            use_container_width=True,
        )

    if actualizar:
        if not nombre.strip():
            st.warning("El nombre no puede estar vacío.")
            return

        try:
            actualizado = actualizar_mascota(
                conexion=conexion,
                id_mascota=id_mascota,
                id_dueno=opciones_duenos[
                    dueno_seleccionado
                ],
                nombre=nombre,
                especie=especie,
                raza=raza,
            )

            if actualizado:
                st.success(
                    "Los datos de la mascota "
                    "fueron actualizados."
                )
            else:
                st.warning(
                    "No se encontró una mascota activa "
                    "con ese ID."
                )

        except Exception as error:
            st.error(
                f"No se pudo actualizar la mascota: {error}"
            )


def mostrar_desactivacion(conexion):
    st.subheader("🗑️ Desactivar o reactivar mascota")

    try:
        mascotas = listar_mascotas(
            conexion,
            incluir_inactivas=True,
        )

    except Exception as error:
        st.error(
            f"No se pudieron cargar las mascotas: {error}"
        )
        return

    if not mascotas:
        st.info("No existen mascotas registradas.")
        return

    opciones = {
        (
            f"{mascota['Mascota']} · "
            f"{mascota['Estado']} · "
            f"ID {mascota['ID']}"
        ): mascota
        for mascota in mascotas
    }

    seleccion = st.selectbox(
        "Selecciona una mascota",
        list(opciones.keys()),
    )

    mascota = opciones[seleccion]

    st.write(f"**Mascota:** {mascota['Mascota']}")
    st.write(f"**Dueño:** {mascota['Dueño']}")
    st.write(f"**Estado:** {mascota['Estado']}")

    if mascota["Estado"] == "ACTIVA":
        confirmar = st.checkbox(
            "Confirmo que deseo desactivar esta mascota"
        )

        if st.button(
            "🗑️ Desactivar mascota",
            use_container_width=True,
            disabled=not confirmar,
        ):
            try:
                eliminado = eliminar_mascota(
                    conexion,
                    mascota["ID"],
                )

                if eliminado:
                    st.success(
                        "La mascota fue desactivada."
                    )
                    st.rerun()
                else:
                    st.warning(
                        "La mascota ya estaba inactiva "
                        "o no existe."
                    )

            except Exception as error:
                st.error(
                    f"No se pudo desactivar: {error}"
                )

    else:
        if st.button(
            "♻️ Reactivar mascota",
            use_container_width=True,
        ):
            try:
                reactivado = reactivar_mascota(
                    conexion,
                    mascota["ID"],
                )

                if reactivado:
                    st.success(
                        "La mascota fue reactivada."
                    )
                    st.rerun()
                else:
                    st.warning(
                        "La mascota ya estaba activa "
                        "o no existe."
                    )

            except Exception as error:
                st.error(
                    f"No se pudo reactivar: {error}"
                )


def mostrar_pagina_mascotas(conexion):
    st.subheader("🐶 Administración de mascotas")

    st.caption(
        "Registra, consulta, busca, edita y "
        "desactiva mascotas."
    )

    pestañas = st.tabs(
        [
            "➕ Registrar",
            "📋 Listar",
            "🔎 Buscar",
            "✏️ Editar",
            "🗑️ Estado",
        ]
    )

    with pestañas[0]:
        mostrar_registro(conexion)

    with pestañas[1]:
        mostrar_listado(conexion)

    with pestañas[2]:
        mostrar_busqueda(conexion)

    with pestañas[3]:
        mostrar_edicion(conexion)

    with pestañas[4]:
        mostrar_desactivacion(conexion)