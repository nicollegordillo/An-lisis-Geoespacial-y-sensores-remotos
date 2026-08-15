# Lab 4 — Cianobacteria en Atitlán y Amatitlán

## Equipo de desarrollo

- Daniel Oswaldo Juárez Herrera
- Humberto Alexander de la Cruz
- Nicolle Alexandra Gordillo

## Descripción del proyecto

Los lagos de Atitlán y Amatitlán vienen mostrando
floraciones de cianobacteria, un riesgo para la salud pública y el turismo. Este
proyecto usa imágenes satelitales Sentinel-2 (vía openEO) para monitorear ese
fenómeno de forma remota: se calcula el índice NDCI/Chl-a (script CyanoLakes) junto
con NDVI y NDWI en 11 fechas por lago, y se analiza cómo varía la floración en el
tiempo y en el espacio.

## Contenido

- `01_descarga.py` — descarga las 22 escenas (11 fechas x 2 lagos) vía openEO a `datos/raw/`.
- `02_analisis.ipynb` — cálculo de índices y todo el análisis.
- `datos/` — imágenes crudas, índices derivados y geojson de cada lago.
- `resultados/` — CSVs, figuras y mapas interactivos generados por el notebook.

## Estado

Completos: Ejercicios 1-6 (conexión API, descarga, cálculo de índices, análisis
temporal, análisis espacial, correlación NDCI-NDVI/NDWI).

