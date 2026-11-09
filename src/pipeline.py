"""Orquesta el flujo completo: buscar empresas por nicho -> analizar su sitio
-> puntuar relevancia -> guardar todo en un CSV listo para revisar o subir
a un Google Sheet.

Uso:
    python3 -m src.pipeline [--config config/busqueda.json] [--salida data/leads.csv]
"""
import argparse
import csv
import json
import sys
from pathlib import Path

from .analizador_sitio import analizar_sitio, leer_vista_previa_red_social
from .buscador import buscar_por_nicho
from .scoring import calcular_relevancia

CAMPOS_CSV = [
    "nicho", "termino_busqueda", "nombre_encontrado", "sitio_web",
    "accesible", "whatsapp_manual", "chatbots_detectados",
    "facebook", "instagram", "red_social_confirmada",
    "categoria", "puntaje", "motivo",
]


def procesar_empresa(nicho, resultado_busqueda):
    url = resultado_busqueda["url"]
    señales = analizar_sitio(url)
    relevancia = calcular_relevancia(señales)

    red_social_confirmada = ""
    red_social_url = señales["facebook"] or señales["instagram"]
    if red_social_url and relevancia["categoria"] != "DESCARTAR":
        vista_previa = leer_vista_previa_red_social(red_social_url)
        red_social_confirmada = vista_previa.get("titulo") or ""

    return {
        "nicho": nicho,
        "termino_busqueda": resultado_busqueda.get("termino_busqueda", ""),
        "nombre_encontrado": resultado_busqueda.get("titulo", ""),
        "sitio_web": url,
        "accesible": señales["accesible"],
        "whatsapp_manual": señales["whatsapp_manual"],
        "chatbots_detectados": ", ".join(señales["chatbots_detectados"]),
        "facebook": señales["facebook"] or "",
        "instagram": señales["instagram"] or "",
        "red_social_confirmada": red_social_confirmada,
        "categoria": relevancia["categoria"],
        "puntaje": relevancia["puntaje"],
        "motivo": relevancia["motivo"],
    }


def ejecutar(ruta_config, ruta_salida, limite_por_nicho=None):
    config = json.loads(Path(ruta_config).read_text(encoding="utf-8"))
    ubicacion = config.get("ubicacion", "")
    max_resultados = config.get("resultados_por_busqueda", 15)

    filas = []
    for nicho, terminos in config["nichos"].items():
        print(f"Buscando nicho: {nicho} ...", file=sys.stderr)
        encontrados = buscar_por_nicho(terminos, ubicacion, max_resultados)
        if limite_por_nicho:
            encontrados = encontrados[:limite_por_nicho]
        for r in encontrados:
            print(f"  analizando {r['url']}", file=sys.stderr)
            filas.append(procesar_empresa(nicho, r))

    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"Listo: {len(filas)} empresas analizadas -> {ruta_salida}", file=sys.stderr)
    return filas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/busqueda.json")
    parser.add_argument("--salida", default="data/leads.csv")
    parser.add_argument(
        "--limite-por-nicho", type=int, default=None,
        help="Tope de empresas a analizar por nicho (útil para pruebas rápidas).",
    )
    args = parser.parse_args()
    ejecutar(args.config, args.salida, args.limite_por_nicho)


if __name__ == "__main__":
    main()
