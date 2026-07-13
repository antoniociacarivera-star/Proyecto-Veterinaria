from dataclasses import dataclass
from typing import Optional


@dataclass
class Dueno:
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    activo: int = 1
    id_dueno: Optional[int] = None