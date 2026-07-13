import re

import streamlit as st

from models.dueno import Dueno
from services.dueno_service import (
    actualizar_dueno,
    buscar_duenos,
    desactivar_dueno,
    listar_duenos,
    obtener_dueno_por_id,
    reactivar_dueno,
    registrar_dueno,
)


def correo_valido(correo: str) -> bool:
    if not correo:
        return True

    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(patron, correo) is not None


def mostrar_registro(conexion):
    st.subheader("➕ Registrar dueño")

    with st.form(
        "form_registrar_dueno",
        clear_on_submit=True
    ):
        nombre = st.text_input(
            "Nombre completo",
            placeholder="Ejemplo: Juan Pérez"
        )

        col1, col2 = st.columns(2)

        with col1:
            telefono = st.text_input(
                "Teléfono",
                placeholder="Ejemplo: 5512345678"
            )

        with col2:
            correo = st.text_input(
                "Correo electrónico",
                placeholder="Ejemplo: juan@email.com"
            )

        guardar = st.form_submit_button(
            "💾 Registrar dueño",
            use_container_width=True
        )

    if guardar:
        if not nombre.strip():
            st.warning(
                "Escribe el nombre del dueño."
            )
            return

        if correo.strip() and not correo_valido(
            correo.strip()
        ):
            st.warning(
                "El correo electrónico no tiene "
                "un formato válido."
            )
            return

        dueno = Dueno(
            nombre=nombre.strip(),
            telefono=telefono.strip() or None,
            correo=correo.strip() or None
        )

        try:
            id_dueno = registrar_dueno(
                conexion,
                dueno
            )

            st.success(
                f"✅ {dueno.nombre} fue registrado "
                f"con el ID {id_dueno}."
            )

            st.toast(
                "Dueño registrado y evento JSON generado.",
                icon="📨"
            )

            st.balloons()

        except Exception as error:
            st.error(
                f"No se pudo registrar el dueño: {error}"
            )


def mostrar_listado(conexion):
    st.subheader("📋 Listado de dueños")

    incluir_inactivos = st.checkbox(
        "Mostrar también dueños inactivos"
    )

    try:
        duenos = listar_duenos(
            conexion,
            incluir_inactivos=incluir_inactivos
        )

    except Exception as error:
        st.error(
            f"No se pudieron consultar los dueños: {error}"
        )
        return

    if not duenos:
        st.info(
            "Todavía no existen dueños registrados."
        )
        return

    st.write(
        f"Se encontraron **{len(duenos)} dueños**."
    )

    st.dataframe(
        duenos,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(
                "ID",
                width="small"
            ),
            "Fecha de registro": (
                st.column_config.DatetimeColumn(
                    "Fecha de registro",
                    format="DD/MM/YYYY HH:mm"
                )
            )
        }
    )


def mostrar_busqueda(conexion):
    st.subheader("🔎 Buscar dueño")

    texto = st.text_input(
        "Buscar",
        placeholder=(
            "Escribe el nombre, teléfono o correo"
        )
    )

    if not texto.strip():
        st.info(
            "Escribe un término para comenzar."
        )
        return

    try:
        resultados = buscar_duenos(
            conexion,
            texto
        )

    except Exception as error:
        st.error(
            f"No se pudo realizar la búsqueda: {error}"
        )
        return

    if not resultados:
        st.warning(
            "No se encontraron coincidencias."
        )
        return

    st.success(
        f"Se encontraron {len(resultados)} resultados."
    )

    st.dataframe(
        resultados,
        use_container_width=True,
        hide_index=True
    )


def mostrar_edicion(conexion):
    st.subheader("✏️ Editar dueño")

    try:
        duenos = listar_duenos(
            conexion,
            incluir_inactivos=False
        )

    except Exception as error:
        st.error(
            f"No se pudieron cargar los dueños: {error}"
        )
        return

    if not duenos:
        st.warning(
            "No existen dueños activos para editar."
        )
        return

    opciones = {
        (
            f"{dueno['Nombre']} "
            f"(ID: {dueno['ID']})"
        ): dueno["ID"]
        for dueno in duenos
    }

    seleccion = st.selectbox(
        "Selecciona un dueño",
        list(opciones.keys())
    )

    id_dueno = opciones[seleccion]

    try:
        datos = obtener_dueno_por_id(
            conexion,
            id_dueno
        )

    except Exception as error:
        st.error(
            f"No se pudo cargar el dueño: {error}"
        )
        return

    if not datos:
        st.warning(
            "El dueño seleccionado ya no existe."
        )
        return

    with st.form("form_editar_dueno"):
        nombre = st.text_input(
            "Nombre completo",
            value=datos["nombre"]
        )

        col1, col2 = st.columns(2)

        with col1:
            telefono = st.text_input(
                "Teléfono",
                value=datos["telefono"]
            )

        with col2:
            correo = st.text_input(
                "Correo",
                value=datos["correo"]
            )

        guardar = st.form_submit_button(
            "💾 Guardar cambios",
            use_container_width=True
        )

    if guardar:
        if not nombre.strip():
            st.warning(
                "El nombre no puede estar vacío."
            )
            return

        if correo.strip() and not correo_valido(
            correo.strip()
        ):
            st.warning(
                "El correo no tiene un formato válido."
            )
            return

        try:
            actualizado = actualizar_dueno(
                conexion=conexion,
                id_dueno=id_dueno,
                nombre=nombre,
                telefono=telefono,
                correo=correo
            )

            if actualizado:
                st.success(
                    "Los datos del dueño "
                    "fueron actualizados."
                )
            else:
                st.warning(
                    "No se encontró un dueño activo "
                    "con ese ID."
                )

        except Exception as error:
            st.error(
                f"No se pudo actualizar: {error}"
            )


def mostrar_estado(conexion):
    st.subheader("🗑️ Desactivar o reactivar dueño")

    try:
        duenos = listar_duenos(
            conexion,
            incluir_inactivos=True
        )

    except Exception as error:
        st.error(
            f"No se pudieron cargar los dueños: {error}"
        )
        return

    if not duenos:
        st.info(
            "No existen dueños registrados."
        )
        return

    opciones = {
        (
            f"{dueno['Nombre']} · "
            f"{dueno['Estado']} · "
            f"ID {dueno['ID']}"
        ): dueno
        for dueno in duenos
    }

    seleccion = st.selectbox(
        "Selecciona un dueño",
        list(opciones.keys())
    )

    dueno = opciones[seleccion]

    st.write(
        f"**Nombre:** {dueno['Nombre']}"
    )

    st.write(
        f"**Teléfono:** {dueno['Teléfono'] or 'No registrado'}"
    )

    st.write(
        f"**Correo:** {dueno['Correo'] or 'No registrado'}"
    )

    st.write(
        f"**Estado:** {dueno['Estado']}"
    )

    if dueno["Estado"] == "ACTIVO":
        st.warning(
            "Las mascotas del dueño no serán eliminadas, "
            "pero el propietario dejará de aparecer "
            "en nuevos registros."
        )

        confirmar = st.checkbox(
            "Confirmo que deseo desactivar al dueño"
        )

        if st.button(
            "🗑️ Desactivar dueño",
            use_container_width=True,
            disabled=not confirmar
        ):
            try:
                resultado = desactivar_dueno(
                    conexion,
                    dueno["ID"]
                )

                if resultado:
                    st.success(
                        "El dueño fue desactivado."
                    )
                    st.rerun()
                else:
                    st.warning(
                        "El dueño ya estaba inactivo "
                        "o no existe."
                    )

            except Exception as error:
                st.error(
                    f"No se pudo desactivar: {error}"
                )

    else:
        if st.button(
            "♻️ Reactivar dueño",
            use_container_width=True
        ):
            try:
                resultado = reactivar_dueno(
                    conexion,
                    dueno["ID"]
                )

                if resultado:
                    st.success(
                        "El dueño fue reactivado."
                    )
                    st.rerun()
                else:
                    st.warning(
                        "El dueño ya estaba activo "
                        "o no existe."
                    )

            except Exception as error:
                st.error(
                    f"No se pudo reactivar: {error}"
                )


def mostrar_pagina_duenos(conexion):
    st.subheader("👤 Administración de dueños")

    st.caption(
        "Registra, consulta, busca, edita y "
        "desactiva propietarios."
    )

    pestañas = st.tabs(
        [
            "➕ Registrar",
            "📋 Listar",
            "🔎 Buscar",
            "✏️ Editar",
            "🗑️ Estado"
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
        mostrar_estado(conexion)