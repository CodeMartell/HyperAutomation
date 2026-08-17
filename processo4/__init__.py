"""
Módulo Processo 4 — SAC (Serviço de Atendimento ao Cliente)
"""

from .sac import (
    executar_sac,
    verificar_status_p3,
    tratar_resultado_sac,
    comunicar_cliente,
    registrar_atendimento,
    fallback_sac,
)

__all__ = [
    "executar_sac",
    "verificar_status_p3",
    "tratar_resultado_sac",
    "comunicar_cliente",
    "registrar_atendimento",
    "fallback_sac",
]
