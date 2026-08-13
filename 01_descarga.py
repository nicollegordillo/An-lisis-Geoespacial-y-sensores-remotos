"""
LABORATORIO 4 - CC3084 | Ejercicios 1 y 2
==========================================
Descarga de imagenes Sentinel-2 de los lagos Atitlan y Amatitlan usando openEO.

Requisitos:
    pip install openeo rasterio numpy pandas scipy matplotlib folium
    Cuenta gratuita en https://dataspace.copernicus.eu
    (la primera ejecucion abre el navegador para autenticarse)

Uso:
    python 01_descarga.py                      # ambos lagos, 22 imagenes
    python 01_descarga.py atitlan              # solo un lago
    python 01_descarga.py atitlan 2026-04-13   # solo una fecha
"""

import sys
from datetime import date, timedelta
from pathlib import Path

import openeo

# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------
DIR_RAW = Path(__file__).resolve().parent / "datos" / "raw"

# Coordenadas del enunciado (EPSG:4326)
BBOX = {
    "atitlan": {"west": -91.326256, "east": -91.07151,
                "south": 14.5948, "north": 14.750979, "crs": "EPSG:4326"},
    "amatitlan": {"west": -90.638065, "east": -90.512924,
                  "south": 14.412347, "north": 14.493799, "crs": "EPSG:4326"},
}

# Las 11 fechas oficiales por lago
FECHAS = {
    "atitlan": ["2025-01-18", "2025-04-13", "2025-05-13", "2025-07-17",
                "2025-11-21", "2025-12-29", "2026-02-12", "2026-03-24",
                "2026-04-13", "2026-04-28", "2026-07-22"],
    "amatitlan": ["2025-01-28", "2025-04-15", "2025-04-28", "2025-11-24",
                  "2026-01-08", "2026-02-02", "2026-02-07", "2026-03-29",
                  "2026-04-13", "2026-04-28", "2026-06-19"],
}

# Solo las bandas minimas necesarias (evita bajar escenas completas):
#   mascara de agua -> B02 B03 B04 B08 B11 B12
#   Floating Algal Index -> B04 B07 B8A
#   NDCI / clorofila -> B04 B05
#   NDVI -> B04 B08   |   NDWI -> B03 B08
#   SCL -> clasificacion de escena, para descartar nubes
BANDAS = ["B02", "B03", "B04", "B05", "B07", "B08", "B8A", "B11", "B12", "SCL"]

RESOLUCION_GRADOS = 0.0002   # ~20 m
CRS_SALIDA = "EPSG:4326"     # asi los mapas de folium no necesitan reproyeccion


# ---------------------------------------------------------------------------
def conectar():
    """Ejercicio 1: conexion autenticada con la API de Sentinel-2 (openEO)."""
    print("Conectando a openeo.dataspace.copernicus.eu ...")
    conexion = openeo.connect("openeo.dataspace.copernicus.eu")
    conexion.authenticate_oidc()
    meta = conexion.describe_collection("SENTINEL2_L2A")
    print(f"Conectado. Coleccion: {meta['id']}")
    print(f"Bandas a descargar: {', '.join(BANDAS)}\n")
    return conexion


def descargar(conexion, lago, fecha):
    """Ejercicio 2: baja un GeoTIFF multibanda recortado al lago."""
    salida = DIR_RAW / lago / f"{lago}_{fecha}.tif"
    salida.parent.mkdir(parents=True, exist_ok=True)
    if salida.exists():
        print(f"  [ya existe] {salida.name}")
        return

    d0 = date.fromisoformat(fecha)
    d1 = d0 + timedelta(days=1)   # openEO excluye el extremo final

    cubo = conexion.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=BBOX[lago],
        temporal_extent=[d0.isoformat(), d1.isoformat()],
        bands=BANDAS,
    )
    # Todas las bandas en la misma malla (~20 m, EPSG:4326) para poder apilar fechas
    cubo = cubo.resample_spatial(
        resolution=RESOLUCION_GRADOS, projection=CRS_SALIDA, method="near")
    # Si hubiera dos pasadas el mismo dia, se combinan en una sola imagen
    cubo = cubo.reduce_dimension(dimension="t", reducer="max")

    print(f"  descargando {lago} {fecha} ...", flush=True)
    cubo.download(str(salida), format="GTiff")
    print(f"  [ok] {salida.name} ({salida.stat().st_size/1e6:.1f} MB)")


def main():
    args = sys.argv[1:]
    lagos = [args[0]] if args and args[0] in BBOX else list(BBOX)
    filtro = args[1:] if len(args) > 1 else None

    conexion = conectar()
    fallos = []
    for lago in lagos:
        fechas = filtro or FECHAS[lago]
        print(f"--- {lago.upper()} ({len(fechas)} fechas) ---")
        for fecha in fechas:
            try:
                descargar(conexion, lago, fecha)
            except Exception as exc:                      # noqa: BLE001
                print(f"  [ERROR] {lago} {fecha}: {exc}")
                fallos.append((lago, fecha))
        print()

    if fallos:
        print("Reintentar estas fechas:", ", ".join(f"{l} {f}" for l, f in fallos))
    else:
        print("Listo. Ahora abra 02_analisis.ipynb")


if __name__ == "__main__":
    main()
