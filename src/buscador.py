"""Busca sitios de empresas en la web a partir de palabras clave de nicho + ubicación.

Usa el endpoint HTML de DuckDuckGo (sin API key, sin login) y descarta
dominios que no son sitios propios de una empresa (directorios, redes
sociales, marketplaces), que se analizan por separado.
"""
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

DOMINIOS_EXCLUIDOS = {
    "facebook.com", "instagram.com", "tiktok.com", "wikipedia.org",
    "linkedin.com", "youtube.com", "indeed.com", "mercadolibre.com",
    "google.com", "yelp.com", "tripadvisor.com", "booking.com",
    "trustpilot.com", "glassdoor.com",
}
FRAGMENTOS_EXCLUIDOS = ("paginasamarillas", "guialocal", "paginblanca")


def _es_directorio(dominio):
    return dominio in DOMINIOS_EXCLUIDOS or any(f in dominio for f in FRAGMENTOS_EXCLUIDOS)


def _url_real(href):
    """DuckDuckGo envuelve los resultados en /l/?uddg=<url codificada>."""
    if href.startswith("//duckduckgo.com/l/"):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        return urllib.parse.unquote(qs.get("uddg", [""])[0])
    return href


def _dominio(url):
    return urllib.parse.urlparse(url).netloc.replace("www.", "")


def buscar(query, max_resultados=15, pausa=1.5):
    """Devuelve una lista de dicts {titulo, url} de sitios de empresas."""
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    resultados = []
    for enlace in soup.select("a.result__a"):
        url = _url_real(enlace.get("href", ""))
        if not url.startswith("http"):
            continue
        dominio = _dominio(url)
        if _es_directorio(dominio):
            continue
        resultados.append({"titulo": enlace.get_text(strip=True), "url": url})
        if len(resultados) >= max_resultados:
            break

    time.sleep(pausa)  # trato cortés con el servicio, evita bloqueos por ráfaga
    return resultados


def buscar_por_nicho(nicho_terminos, ubicacion, max_resultados, pausa=1.5):
    """Busca cada término del nicho (+ ubicación, si se indica) y junta
    resultados únicos por dominio. Con ubicacion vacía, la búsqueda es
    en español sin restringir país (todo el mundo hispanohablante)."""
    vistos = set()
    encontrados = []
    for termino in nicho_terminos:
        query = f"{termino} {ubicacion}".strip()
        for r in buscar(query, max_resultados=max_resultados, pausa=pausa):
            dominio = _dominio(r["url"])
            if dominio in vistos:
                continue
            vistos.add(dominio)
            r["termino_busqueda"] = termino
            encontrados.append(r)
    return encontrados
