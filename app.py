import json
from datetime import datetime

import streamlit as st

from database.conexion import obtener_conexion
from mq.consumidor import procesar_notificacion
from mq.productor import enviar_notificacion
from modulos.mascotas import mostrar_pagina_mascotas
from modulos.duenos import mostrar_pagina_duenos
# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="VetControl",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# ESTILOS CSS
# =========================================================

st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(
        135deg,
        rgba(15, 23, 42, 0.98),
        rgba(30, 41, 59, 0.98)
    );
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.encabezado-principal {
    padding: 24px 28px;
    border-radius: 22px;
    background: linear-gradient(
        135deg,
        rgba(14, 165, 233, 0.22),
        rgba(99, 102, 241, 0.22)
    );
    border: 1px solid rgba(255, 255, 255, 0.12);
    margin-bottom: 25px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.20);
}

.titulo-principal {
    font-size: 42px;
    font-weight: 850;
    margin: 0;
    color: #f8fafc;
}

.subtitulo-principal {
    margin-top: 5px;
    margin-bottom: 0;
    font-size: 17px;
    color: #cbd5e1;
}

.fecha-actual {
    margin-top: 12px;
    font-size: 14px;
    color: #94a3b8;
}

.tarjeta {
    padding: 20px;
    border-radius: 18px;
    background: rgba(30, 41, 59, 0.70);
    border: 1px solid rgba(255, 255, 255, 0.10);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    min-height: 145px;
}

.tarjeta-icono {
    font-size: 30px;
}

.tarjeta-titulo {
    color: #94a3b8;
    font-size: 15px;
    margin-top: 8px;
}

.tarjeta-valor {
    color: #f8fafc;
    font-size: 30px;
    font-weight: 800;
    margin-top: 6px;
}

.tarjeta-descripcion {
    color: #cbd5e1;
    font-size: 13px;
    margin-top: 4px;
}

.seccion {
    padding: 22px;
    border-radius: 18px;
    background: rgba(30, 41, 59, 0.60);
    border: 1px solid rgba(255, 255, 255, 0.10);
    margin-top: 18px;
}

.estado-activo {
    color: #4ade80;
    font-weight: 700;
}

.estado-simulado {
    color: #facc15;
    font-weight: 700;
}

div[data-testid="stForm"] {
    background: rgba(30, 41, 59, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 22px;
}

div[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

div[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.70);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 15px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        rgba(15, 23, 42, 1),
        rgba(30, 41, 59, 1)
    );
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.login-caja {
    max-width: 550px;
    margin: 45px auto;
    padding: 35px;
    border-radius: 24px;
    background: rgba(30, 41, 59, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 18px 55px rgba(0, 0, 0, 0.32);
}

.login-logo {
    text-align: center;
    font-size: 65px;
    margin-bottom: 5px;
}

.login-titulo {
    text-align: center;
    font-size: 38px;
    font-weight: 850;
    color: #f8fafc;
    margin-bottom: 0;
}

.login-subtitulo {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 25px;
}

.pie-pagina {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    margin-top: 35px;
}

h1,
h2,
h3 {
    color: #f8fafc;
}
</style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESIÓN
# =========================================================

def inicializar_sesion():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if "password_maestra" not in st.session_state:
        st.session_state.password_maestra = ""

    if "ultima_notificacion" not in st.session_state:
        st.session_state.ultima_notificacion = None


# =========================================================
# COMPONENTES VISUALES
# =========================================================

def mostrar_encabezado():
    fecha = datetime.now().strftime("%d/%m/%Y - %H:%M")

    st.markdown(
        f"""
<div class="encabezado-principal">
    <p class="titulo-principal">🐾 VetControl</p>
    <p class="subtitulo-principal">
        Sistema web de administración veterinaria
    </p>
    <p class="fecha-actual">
        Bienvenido, Antonio 👋 &nbsp; | &nbsp; {fecha}
    </p>
</div>
        """,
        unsafe_allow_html=True
    )


def crear_tarjeta(
    icono: str,
    titulo: str,
    valor: str,
    descripcion: str
):
    st.markdown(
        f"""
<div class="tarjeta">
    <div class="tarjeta-icono">{icono}</div>
    <div class="tarjeta-titulo">{titulo}</div>
    <div class="tarjeta-valor">{valor}</div>
    <div class="tarjeta-descripcion">{descripcion}</div>
</div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# BASE DE DATOS
# =========================================================

def obtener_estadisticas(conexion):
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                COUNT(*),
                NVL(
                    SUM(
                        TO_NUMBER(
                            JSON_VALUE(
                                CONTENIDO_JSON,
                                '$.costo'
                            )
                        )
                    ),
                    0
                )
            FROM VET1
            WHERE TIPO_EVENTO = 'NUEVA_CONSULTA'
            """
        )

        resultado = cursor.fetchone()

        cursor.execute(
            """
            SELECT JSON_VALUE(
                CONTENIDO_JSON,
                '$.mascota'
            )
            FROM VET1
            WHERE TIPO_EVENTO = 'NUEVA_CONSULTA'
            ORDER BY ID_EVENTO DESC
            FETCH FIRST 1 ROW ONLY
            """
        )

        ultima_fila = cursor.fetchone()

        ultima_mascota = (
            ultima_fila[0]
            if ultima_fila
            else "Sin registros"
        )

        return {
            "consultas": int(resultado[0] or 0),
            "ingresos": float(resultado[1] or 0),
            "ultima_mascota": ultima_mascota
        }

    finally:
        cursor.close()


def consultar_registros(conexion):
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                ID_EVENTO,
                JSON_VALUE(
                    CONTENIDO_JSON,
                    '$.mascota'
                ),
                JSON_VALUE(
                    CONTENIDO_JSON,
                    '$.diagnostico'
                ),
                JSON_VALUE(
                    CONTENIDO_JSON,
                    '$.costo'
                ),
                FECHA_CREACION
            FROM VET1
            WHERE TIPO_EVENTO = 'NUEVA_CONSULTA'
            ORDER BY ID_EVENTO DESC
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()


# =========================================================
# INICIO
# =========================================================

def mostrar_inicio(conexion):
    try:
        datos = obtener_estadisticas(conexion)

    except Exception as error:
        st.warning(
            f"No se pudieron obtener las estadísticas: {error}"
        )

        datos = {
            "consultas": 0,
            "ingresos": 0,
            "ultima_mascota": "No disponible"
        }

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        crear_tarjeta(
            "📋",
            "Consultas registradas",
            str(datos["consultas"]),
            "Total guardado en Oracle"
        )

    with col2:
        crear_tarjeta(
            "💰",
            "Ingresos registrados",
            f"${datos['ingresos']:,.2f}",
            "Suma de todas las consultas"
        )

    with col3:
        crear_tarjeta(
            "🐶",
            "Última mascota",
            datos["ultima_mascota"],
            "Registro más reciente"
        )

    with col4:
        crear_tarjeta(
            "🗄️",
            "Base de datos",
            "Oracle XE",
            "Conexión activa"
        )

    st.markdown(
        """
<div class="seccion">
    <h3>Estado del sistema</h3>
    <p>
        🟢 Oracle Database:
        <span class="estado-activo">Conectado</span>
    </p>
    <p>
        🟢 Credenciales:
        <span class="estado-activo">Cifradas</span>
    </p>
    <p>
        🟡 ActiveMQ:
        <span class="estado-simulado">Simulación funcional</span>
    </p>
    <p>
        🟢 Aplicación web:
        <span class="estado-activo">En funcionamiento</span>
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="seccion">
    <h3>Tecnologías utilizadas</h3>
    <p>
        Python, Streamlit, Oracle Database, JSON,
        cifrado Fernet y arquitectura de mensajería.
    </p>
</div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# REGISTRAR CONSULTA
# =========================================================

def obtener_mascotas_activas(conexion):
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT
                M.ID_MASCOTA,
                M.NOMBRE_MASCOTA,
                M.ESPECIE,
                D.NOMBRE
            FROM MASCOTAS M
            INNER JOIN DUENOS D
                ON D.ID_DUENO = M.ID_DUENO
            WHERE NVL(M.ACTIVO, 1) = 1
            ORDER BY M.NOMBRE_MASCOTA
            """
        )

        filas = cursor.fetchall()

        return [
            {
                "id_mascota": fila[0],
                "mascota": fila[1],
                "especie": fila[2],
                "dueno": fila[3]
            }
            for fila in filas
        ]

    finally:
        cursor.close()


def registrar_consulta(conexion):
    st.subheader("📋 Registrar nueva consulta")

    try:
        mascotas = obtener_mascotas_activas(conexion)

    except Exception as error:
        st.error(
            f"No se pudieron cargar las mascotas: {error}"
        )
        return

    if not mascotas:
        st.warning(
            "Primero debes registrar una mascota activa."
        )
        return

    opciones = {
        (
            f"{mascota['mascota']} · "
            f"{mascota['especie']} · "
            f"Dueño: {mascota['dueno']}"
        ): mascota
        for mascota in mascotas
    }

    with st.form(
        "formulario_consulta",
        clear_on_submit=True
    ):
        seleccion = st.selectbox(
            "Mascota",
            list(opciones.keys())
        )

        diagnostico = st.text_area(
            "Diagnóstico o servicio",
            placeholder=(
                "Ejemplo: Vacunación, revisión general, "
                "desparasitación..."
            ),
            height=110
        )

        costo = st.number_input(
            "Costo de la consulta",
            min_value=0.0,
            step=50.0,
            format="%.2f"
        )

        guardar = st.form_submit_button(
            "💾 Guardar consulta",
            use_container_width=True
        )

    if guardar:
        diagnostico_limpio = diagnostico.strip()

        if not diagnostico_limpio:
            st.warning(
                "Debes escribir el diagnóstico o servicio."
            )
            return

        mascota = opciones[seleccion]

        contenido = {
            "id_mascota": mascota["id_mascota"],
            "mascota": mascota["mascota"],
            "dueno": mascota["dueno"],
            "diagnostico": diagnostico_limpio,
            "costo": float(costo)
        }

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
                    "tipo_evento": "NUEVA_CONSULTA",
                    "contenido_json": json.dumps(
                        contenido,
                        ensure_ascii=False
                    )
                }
            )

            conexion.commit()

            evento = enviar_notificacion(
                mascota=mascota["mascota"],
                mensaje=(
                    "La consulta fue registrada y "
                    "la mascota fue atendida."
                )
            )

            mensaje = procesar_notificacion(evento)

            st.session_state.ultima_notificacion = evento

            st.success(
                f"✅ La consulta de "
                f"{mascota['mascota']} "
                "fue registrada correctamente."
            )

            st.toast(
                mensaje,
                icon="📨"
            )

        except Exception as error:
            conexion.rollback()

            st.error(
                f"No se pudo guardar la consulta: {error}"
            )

        finally:
            cursor.close()
            
    if st.session_state.ultima_notificacion:
        st.markdown(
            """
<div class="seccion">
    <h3>📨 Último evento generado</h3>
</div>
            """,
            unsafe_allow_html=True
        )

        st.json(
            st.session_state.ultima_notificacion
        )


# =========================================================
# HISTORIAL
# =========================================================

def mostrar_consultas(conexion):
    st.subheader("📚 Historial de consultas")

    busqueda = st.text_input(
        "Buscar consulta",
        placeholder="Escribe una mascota o diagnóstico"
    )

    try:
        filas = consultar_registros(conexion)

    except Exception as error:
        st.error(
            f"No se pudieron consultar los registros: {error}"
        )
        return

    datos = []
    texto_busqueda = busqueda.strip().lower()

    for fila in filas:
        registro = {
            "ID": fila[0],
            "Mascota": fila[1] or "",
            "Diagnóstico": fila[2] or "",
            "Costo": float(fila[3] or 0),
            "Fecha": fila[4]
        }

        contenido = (
            f"{registro['Mascota']} "
            f"{registro['Diagnóstico']}"
        ).lower()

        if texto_busqueda and texto_busqueda not in contenido:
            continue

        datos.append(registro)

    if not datos:
        st.info(
            "No se encontraron consultas."
        )
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(
            f"Se encontraron **{len(datos)} registros**."
        )

    with col2:
        total_filtrado = sum(
            registro["Costo"]
            for registro in datos
        )

        st.metric(
            "Total mostrado",
            f"${total_filtrado:,.2f}"
        )

    st.dataframe(
        datos,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(
                "Folio",
                width="small"
            ),
            "Mascota": st.column_config.TextColumn(
                "Mascota",
                width="medium"
            ),
            "Diagnóstico": st.column_config.TextColumn(
                "Diagnóstico o servicio",
                width="large"
            ),
            "Costo": st.column_config.NumberColumn(
                "Costo",
                format="$%.2f"
            ),
            "Fecha": st.column_config.DatetimeColumn(
                "Fecha",
                format="DD/MM/YYYY HH:mm"
            )
        }
    )


# =========================================================
# NOTIFICACIONES
# =========================================================

def mostrar_notificaciones():
    st.subheader("📨 Servicio de notificaciones")

    st.info(
        "Este módulo representa al consumidor de mensajes. "
        "Actualmente funciona como una simulación de ActiveMQ."
    )

    if not st.session_state.ultima_notificacion:
        st.warning(
            "Todavía no se ha generado ninguna notificación."
        )
        return

    evento = st.session_state.ultima_notificacion

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Estado",
        evento.get("estado", "Sin estado")
    )

    col2.metric(
        "Mascota",
        evento.get("mascota", "No disponible")
    )

    col3.metric(
        "Cola",
        evento.get("cola", "notificaciones")
    )

    st.json(evento)


# =========================================================
# PRÓXIMOS MÓDULOS
# =========================================================

def mostrar_proximamente(
    titulo: str,
    descripcion: str
):
    st.subheader(titulo)

    st.info(descripcion)

    st.markdown(
        """
<div class="seccion">
    <h3>Módulo en construcción</h3>
    <p>
        Esta sección se conectará posteriormente
        con nuevas tablas de Oracle.
    </p>
</div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# LOGIN
# =========================================================

def mostrar_acceso():
    st.markdown(
        """
<div class="login-caja">
    <div class="login-logo">🐾</div>
    <div class="login-titulo">VetControl</div>
    <div class="login-subtitulo">
        Sistema de información web veterinaria
    </div>
</div>
        """,
        unsafe_allow_html=True
    )

    columna_izquierda, columna_centro, columna_derecha = (
        st.columns([1, 1.2, 1])
    )

    with columna_centro:
        password_maestra = st.text_input(
            "Contraseña maestra",
            type="password",
            placeholder="Escribe tu contraseña"
        )

        entrar = st.button(
            "🔐 Iniciar sesión",
            use_container_width=True
        )

        if entrar:
            if not password_maestra:
                st.warning(
                    "Escribe la contraseña maestra."
                )
                return

            try:
                conexion_prueba = obtener_conexion(
                    password_maestra
                )

                conexion_prueba.close()

                st.session_state.autenticado = True
                st.session_state.password_maestra = (
                    password_maestra
                )

                st.rerun()

            except ValueError:
                st.error(
                    "La contraseña maestra es incorrecta."
                )

            except FileNotFoundError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    f"No se pudo conectar con Oracle: {error}"
                )

        st.caption(
            "🔒 Las credenciales de Oracle se encuentran cifradas."
        )


def cerrar_sesion():
    st.session_state.autenticado = False
    st.session_state.password_maestra = ""
    st.session_state.ultima_notificacion = None
    st.rerun()


# =========================================================
# APLICACIÓN PRINCIPAL
# =========================================================

def main():
    inicializar_sesion()

    if not st.session_state.autenticado:
        mostrar_acceso()
        st.stop()

    try:
        conexion = obtener_conexion(
            st.session_state.password_maestra
        )

    except Exception as error:
        st.session_state.autenticado = False

        st.error(
            f"No fue posible abrir la conexión: {error}"
        )
        st.stop()

    with st.sidebar:
        st.title("🐾 Control Veterinario")

        st.caption(
            "Sistema veterinario"
        )

        st.divider()

        opcion = st.radio(
            "Navegación",
            [
                "🏠 Inicio",
                "🐶 Mascotas",
                "👤 Dueños",
                "📋 Registrar consulta",
                "📚 Historial",
                "💉 Vacunas",
                "📨 Notificaciones"
            ]
        )

        st.divider()

        st.caption(
            "Base de datos Oracle: conectada"
        )

        st.caption(
            "Usuario: Administrador"
        )

        if st.button(
            "🚪 Cerrar sesión",
            use_container_width=True
        ):
            conexion.close()
            cerrar_sesion()

    mostrar_encabezado()

    try:
        if opcion == "🏠 Inicio":
            mostrar_inicio(conexion)

        elif opcion == "🐶 Mascotas":
            mostrar_pagina_mascotas(conexion)
        elif opcion == "👤 Dueños":
          mostrar_pagina_duenos(conexion)

        elif opcion == "📋 Registrar consulta":
            registrar_consulta(conexion)

        elif opcion == "📚 Historial":
            mostrar_consultas(conexion)

        elif opcion == "💉 Vacunas":
            mostrar_proximamente(
                "💉 Control de vacunas",
                (
                    "Aquí se registrarán las vacunas "
                    "aplicadas a cada mascota."
                )
            )

        elif opcion == "📨 Notificaciones":
            mostrar_notificaciones()

    finally:
        conexion.close()

    st.markdown(
        """
<div class="pie-pagina">
    VetControl · Sistema de Información Web · 2026
</div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()