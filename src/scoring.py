"""Calcula qué tan buen candidato es una empresa para ofrecerle un bot/automatización.

Lógica: si ya atiende manualmente por WhatsApp y no tiene ningún chatbot
detectado, es un buen candidato (dolor real, sin competencia instalada).
Si ya tiene un chatbot, se descarta como lead de "vender bot nuevo" (podría
servir para otra oferta, como "mejora tu bot actual", pero eso es otro caso).
"""

ALTA = "ALTA"
MEDIA = "MEDIA"
BAJA = "BAJA"
DESCARTAR = "DESCARTAR"


def calcular_relevancia(señales):
    """señales: el dict que devuelve analizador_sitio.analizar_sitio()."""
    if not señales["accesible"]:
        return {"puntaje": 0, "categoria": BAJA, "motivo": "sitio no accesible"}

    if señales["chatbots_detectados"]:
        return {
            "puntaje": 0,
            "categoria": DESCARTAR,
            "motivo": f"ya usa: {', '.join(señales['chatbots_detectados'])}",
        }

    puntaje = 0
    motivos = []

    if señales["whatsapp_manual"]:
        puntaje += 3
        motivos.append("atiende WhatsApp manualmente")

    if señales["facebook"] or señales["instagram"]:
        puntaje += 1
        motivos.append("activo en redes sociales")

    if puntaje >= 4:
        categoria = ALTA
    elif puntaje >= 2:
        categoria = MEDIA
    else:
        categoria = BAJA

    return {"puntaje": puntaje, "categoria": categoria, "motivo": "; ".join(motivos) or "sin señales claras"}
