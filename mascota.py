from dataclasses import dataclass
from typing import Optional


@dataclass
class Mascota:
    id_dueno: int
    nombre: str
    especie: str
    raza: Optional[str] = None
    activo: int = 1
    id_mascota: Optional[int] = None