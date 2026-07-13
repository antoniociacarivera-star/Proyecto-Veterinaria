from datetime import datetime


def enviar_notificacion(
    mascota: str,
    mensaje: str
) -> dict:
    """
    Simula el productor de mensajes de ActiveMQ.

    En una implementación real, este evento se enviaría
    a una cola de ActiveMQ.
    """

    evento = {
        "tipo": "NOTIFICACION_VETERINARIA",
        "mascota": mascota,
        "mensaje": mensaje,
        "fecha": datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
        "cola": "notificaciones.veterinaria",
        "estado": "ENVIADO"
    }

    return evento