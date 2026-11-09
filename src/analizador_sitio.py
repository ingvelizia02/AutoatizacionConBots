"""Analiza el sitio web público de una empresa para detectar:
- si ya usa algún chatbot/automatización (ManyChat, Tidio, etc.)
- si atiende por WhatsApp de forma manual (enlace wa.me / api.whatsapp.com)
- sus redes sociales enlazadas desde su propio sitio

Solo descarga páginas públicas con una petición HTTP normal (sin login,
sin simular navegador real, sin JavaScript). No entra a Facebook/Instagram
con sesión: de esas páginas solo lee las etiquetas Open Graph que cualquier
vista previa de enlace vería sin iniciar sesión.
"""
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup

from .buscador import USER_AGENT

HERRAMIENTAS_CHATBOT = {
    "manychat": "ManyChat",
    "chatfuel": "Chatfuel",
    "tidio": "Tidio",
    "intercom": "Intercom",
    "drift.com": "Drift",
    "crisp.chat": "Crisp",
    "zendesk": "Zendesk Chat",
    "freshchat": "Freshchat",
    "landbot": "Landbot",
    "botpress": "Botpress",
    "tawk.to": "Tawk.to",
}

PATRON_WHATSAPP = re.compile(r"(?:wa\.me/|api\.whatsapp\.com/send)", re.IGNORECASE)


def _obtener_html(url, timeout=15):
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException:
        return None


def detectar_chatbots(html):
    html_bajo = html.lower()
    return sorted({nombre for clave, nombre in HERRAMIENTAS_CHATBOT.items() if clave in html_bajo})


def detectar_whatsapp_manual(html):
    return bool(PATRON_WHATSAPP.search(html))


def extraer_redes_sociales(html, url_base):
    soup = BeautifulSoup(html, "html.parser")
    redes = {}
    for enlace in soup.find_all("a", href=True):
        href = urllib.parse.urljoin(url_base, enlace["href"])
        dominio = urllib.parse.urlparse(href).netloc.replace("www.", "")
        if dominio == "facebook.com" and "facebook" not in redes:
            redes["facebook"] = href
        elif dominio == "instagram.com" and "instagram" not in redes:
            redes["instagram"] = href
    return redes


def analizar_sitio(url):
    """Devuelve un dict con las señales detectadas en el sitio de la empresa."""
    html = _obtener_html(url)
    if html is None:
        return {
            "url": url,
            "accesible": False,
            "chatbots_detectados": [],
            "whatsapp_manual": False,
            "facebook": None,
            "instagram": None,
        }
    redes = extraer_redes_sociales(html, url)
    return {
        "url": url,
        "accesible": True,
        "chatbots_detectados": detectar_chatbots(html),
        "whatsapp_manual": detectar_whatsapp_manual(html),
        "facebook": redes.get("facebook"),
        "instagram": redes.get("instagram"),
    }


def leer_vista_previa_red_social(url):
    """Lee solo las etiquetas Open Graph públicas (og:title, og:description)
    de una página de Facebook/Instagram, sin iniciar sesión. Puede devolver
    poco o nada: ambas plataformas limitan fuerte lo que muestran sin login.
    """
    html = _obtener_html(url)
    if html is None:
        return {"titulo": None, "descripcion": None, "accesible": False}
    soup = BeautifulSoup(html, "html.parser")

    def _meta(prop):
        tag = soup.find("meta", property=prop)
        return tag["content"].strip() if tag and tag.get("content") else None

    return {
        "titulo": _meta("og:title"),
        "descripcion": _meta("og:description"),
        "accesible": True,
    }
