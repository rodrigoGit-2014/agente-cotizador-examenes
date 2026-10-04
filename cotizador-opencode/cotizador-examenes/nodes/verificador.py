"""Nodo `verificador` — passthrough en el paso `03`.

En el paso `07` reemplazará por "no confirmado" todo dato del reporte sin respaldo en una
observación y retirará recomendaciones. Por ahora solo aprueba.
"""

from __future__ import annotations


def nodo_verificador(state: dict) -> dict:
    return {"verificacion": {"aprobado": True, "correcciones": []}}
