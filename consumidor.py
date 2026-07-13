def procesar_notificacion(evento: dict) -> str:
    """
    Simula el consumidor de mensajes de ActiveMQ.
    """

    if not isinstance(evento, dict):
        raise TypeError(
            "El evento debe ser un diccionario."
        )

    mascota = evento.get(
        "mascota",
        "Mascota"
    )

    mensaje = evento.get(
        "mensaje",
        "Notificación recibida."
    )

    evento["estado"] = "PROCESADO"

    return f"{mascota}: {mensaje}"