# Automatización con Bots — prospección de clientes

Proyecto para encontrar empresas de habla hispana (sin país fijo) que
atienden por WhatsApp de forma manual y no tienen ningún chatbot/automatización
instalada, para ofrecerles bots o automatizaciones (ManyChat, etc.).

## Cómo funciona

1. `src/buscador.py` busca empresas por nicho usando el buscador HTML de
   DuckDuckGo (sin API key, sin login), descartando directorios y redes
   sociales.
2. `src/analizador_sitio.py` visita el sitio propio de cada empresa y
   detecta: si ya usa un chatbot conocido, si atiende WhatsApp manualmente
   (enlace `wa.me`/`api.whatsapp.com`), y sus redes sociales enlazadas desde
   su propio sitio. De Facebook/Instagram solo lee las etiquetas públicas
   de vista previa (Open Graph) — nunca inicia sesión ni simula ser un
   usuario logueado.
3. `src/scoring.py` puntúa cada empresa: alta relevancia si atiende manual
   por WhatsApp y no tiene ningún bot; se descarta si ya tiene uno.
4. `src/pipeline.py` junta todo y guarda un CSV en `data/` listo para
   revisar o subir a un Google Sheet.

## Uso

```bash
python3 -m src.pipeline --salida data/leads.csv
```

Opciones:
- `--config`: ruta al archivo de nichos/ubicación (por defecto `config/busqueda.json`).
- `--limite-por-nicho`: tope de empresas por nicho, útil para pruebas rápidas.

## Configuración de nichos

Editar `config/busqueda.json`: lista de nichos con sus términos de búsqueda
en español, y `ubicacion` (vacío = todo el mundo hispanohablante, sin
restringir país).

## Red y alcance

Este scraper necesita visitar sitios web arbitrarios (el dominio de cada
empresa encontrada), así que requiere una red sin restricciones de host.
No hace scraping con sesión iniciada de Facebook/Instagram: eso viola sus
Términos de Servicio y arriesga bloqueo de cuenta/IP.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```
