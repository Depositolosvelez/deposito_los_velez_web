"""
Meta Ads Report — Depósito Los Vélez
Trae métricas de campañas activas, calcula costo/conversión
y alerta si "Puertas de hierro" supera el umbral definido.

Uso:
    python automation/meta_ads_report.py
    python automation/meta_ads_report.py --dias 14
    python automation/meta_ads_report.py --dias 30 --salida reporte.json

Variables de entorno requeridas:
    META_ACCESS_TOKEN   — token de acceso de Meta Marketing API
"""

import os
import sys
import json
import argparse
import datetime
import requests
from pathlib import Path
from dotenv import load_dotenv

# UTF-8 en la consola de Windows para caracteres especiales
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Carga el archivo "env" en la raíz del proyecto (un nivel arriba de automation/)
_ENV_PATH = Path(__file__).resolve().parent.parent / "env"
load_dotenv(_ENV_PATH)

# ── Configuración ────────────────────────────────────────────────────────────

AD_ACCOUNT_ID   = "act_949682794503534"
API_VERSION     = "v21.0"
BASE_URL        = f"https://graph.facebook.com/{API_VERSION}"

# Palabras clave para identificar campañas de interés (insensible a mayúsculas)
# Claves futuras (cuando se creen en Meta Ads):
#   "puertas" → Puertas de hierro
#   "ba" + "os" → Baños (separado para evitar falsos positivos)
CAMPAÑAS_OBJETIVO = {
    "publicaci":    "Publicación",
    "junio":        "Depósito Los Vélez - Junio 2026",
    "puertas":      "Puertas de hierro",
    "baños":  "Baños",
}

# Alerta: si costo/conv de puertas supera este valor (COP) se emite aviso
ALERTA_PUERTAS_COP = 400.0

# Tipos de acción de Meta que cuentan como conversión
TIPOS_CONVERSION = {
    "lead",
    "contact",
    "offsite_conversion.fb_pixel_lead",
    "offsite_conversion.fb_pixel_purchase",
    "onsite_conversion.lead_grouped",
}

# Métricas que pedimos a la API
FIELDS_INSIGHTS = ",".join([
    "campaign_name",
    "spend",
    "impressions",
    "clicks",
    "actions",
    "cost_per_action_type",
    "cpm",
    "ctr",
    "cpc",
    "reach",
    "frequency",
])

# ── Helpers API ───────────────────────────────────────────────────────────────

def _get(endpoint: str, params: dict) -> dict:
    """GET con manejo básico de errores."""
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
    data = resp.json()
    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"Meta API error {err.get('code')}: {err.get('message')}"
        )
    return data


def obtener_campañas(token: str) -> list[dict]:
    """Lista todas las campañas de la cuenta (activas e inactivas)."""
    params = {
        "access_token": token,
        "fields": "id,name,status,objective",
        "limit": 100,
    }
    data = _get(f"{AD_ACCOUNT_ID}/campaigns", params)
    campañas = data.get("data", [])

    # Paginación simple
    while "paging" in data and "next" in data["paging"]:
        resp = requests.get(data["paging"]["next"], timeout=30)
        data = resp.json()
        campañas.extend(data.get("data", []))

    return campañas


def obtener_insights(campaign_id: str, token: str, fecha_desde: str, fecha_hasta: str) -> dict | None:
    """Insights de una campaña para el rango de fechas dado."""
    params = {
        "access_token": token,
        "fields": FIELDS_INSIGHTS,
        "time_range": json.dumps({"since": fecha_desde, "until": fecha_hasta}),
        "level": "campaign",
    }
    data = _get(f"{campaign_id}/insights", params)
    resultados = data.get("data", [])
    return resultados[0] if resultados else None


# ── Procesamiento ─────────────────────────────────────────────────────────────

def _sumar_conversiones(actions: list[dict]) -> float:
    """Suma todas las acciones que consideramos conversión."""
    total = 0.0
    for accion in actions or []:
        if accion.get("action_type") in TIPOS_CONVERSION:
            total += float(accion.get("value", 0))
    return total


def _costo_por_conversion(spend: float, conversiones: float) -> float | None:
    if conversiones <= 0:
        return None
    return round(spend / conversiones, 2)


def clasificar_campaña(nombre: str) -> str:
    """Devuelve la clave de CAMPAÑAS_OBJETIVO o 'otra'."""
    nombre_lower = nombre.lower()
    for clave in CAMPAÑAS_OBJETIVO:
        if clave in nombre_lower:
            return clave
    return "otra"


def procesar_insight(insight: dict) -> dict:
    """Extrae y calcula las métricas clave de un insight."""
    spend        = float(insight.get("spend", 0))
    impresiones  = int(insight.get("impressions", 0))
    clicks       = int(insight.get("clicks", 0))
    alcance      = int(insight.get("reach", 0))
    frecuencia   = float(insight.get("frequency", 0))
    cpm          = float(insight.get("cpm", 0))
    ctr          = float(insight.get("ctr", 0))
    cpc          = float(insight.get("cpc", 0))
    conversiones = _sumar_conversiones(insight.get("actions", []))
    costo_conv   = _costo_por_conversion(spend, conversiones)

    return {
        "campaña":          insight.get("campaign_name", "—"),
        "gasto_cop":        spend,
        "impresiones":      impresiones,
        "alcance":          alcance,
        "frecuencia":       frecuencia,
        "clicks":           clicks,
        "ctr_pct":          round(ctr, 2),
        "cpc_cop":          round(cpc, 2),
        "cpm_cop":          round(cpm, 2),
        "conversiones":     conversiones,
        "costo_conv_cop":   costo_conv,
    }


# ── Alertas ───────────────────────────────────────────────────────────────────

def evaluar_alertas(metricas: dict, clave: str) -> list[str]:
    alertas = []

    if clave == "puertas":
        costo = metricas.get("costo_conv_cop")
        if costo is None:
            alertas.append(
                "⚠️  Puertas de hierro: sin conversiones registradas en el período."
            )
        elif costo > ALERTA_PUERTAS_COP:
            alertas.append(
                f"🚨 Puertas de hierro: costo/conv ${costo:,.0f} COP "
                f"supera el umbral de ${ALERTA_PUERTAS_COP:,.0f} COP."
            )
        else:
            alertas.append(
                f"✅ Puertas de hierro: costo/conv ${costo:,.0f} COP "
                f"dentro del umbral (≤ ${ALERTA_PUERTAS_COP:,.0f} COP)."
            )

    return alertas


# ── Salida por consola ────────────────────────────────────────────────────────

SEPARADOR = "─" * 60

def imprimir_campaña(m: dict, alertas: list[str]) -> None:
    print(f"\n{SEPARADOR}")
    print(f"  {m['campaña'].upper()}")
    print(SEPARADOR)
    print(f"  Gasto:          ${m['gasto_cop']:>12,.0f} COP")
    print(f"  Impresiones:    {m['impresiones']:>13,}")
    print(f"  Alcance:        {m['alcance']:>13,}")
    print(f"  Frecuencia:     {m['frecuencia']:>13.2f}")
    print(f"  Clicks:         {m['clicks']:>13,}")
    print(f"  CTR:            {m['ctr_pct']:>12.2f} %")
    print(f"  CPC:            ${m['cpc_cop']:>12,.2f} COP")
    print(f"  CPM:            ${m['cpm_cop']:>12,.2f} COP")
    print(f"  Conversiones:   {m['conversiones']:>13.0f}")
    if m["costo_conv_cop"] is not None:
        print(f"  Costo/conv:     ${m['costo_conv_cop']:>12,.2f} COP")
    else:
        print(f"  Costo/conv:     {'Sin datos':>13}")
    if alertas:
        print()
        for a in alertas:
            print(f"  {a}")


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reporte Meta Ads — Depósito Los Vélez")
    p.add_argument("--dias",   type=int, default=7,    help="Días hacia atrás a analizar (default: 7)")
    p.add_argument("--salida", type=str, default=None, help="Archivo JSON donde guardar el reporte")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        print("ERROR: falta la variable de entorno META_ACCESS_TOKEN.")
        sys.exit(1)

    hoy         = datetime.date.today()
    fecha_hasta = hoy.isoformat()
    fecha_desde = (hoy - datetime.timedelta(days=args.dias)).isoformat()

    print(f"\n{'═' * 60}")
    print(f"  REPORTE META ADS — DEPÓSITO LOS VÉLEZ")
    print(f"  Período: {fecha_desde} → {fecha_hasta} ({args.dias} días)")
    print(f"  Cuenta:  {AD_ACCOUNT_ID}")
    print(f"{'═' * 60}")

    # 1. Traer todas las campañas
    try:
        campañas = obtener_campañas(token)
    except RuntimeError as e:
        print(f"\nERROR al obtener campañas: {e}")
        sys.exit(1)

    print(f"\n  Campañas encontradas en la cuenta: {len(campañas)}")

    # 2. Filtrar las de interés y traer insights
    reporte = []
    todas_alertas = []

    campañas_encontradas = {k: False for k in CAMPAÑAS_OBJETIVO}

    for campaña in campañas:
        clave = clasificar_campaña(campaña["name"])
        if clave == "otra":
            continue

        campañas_encontradas[clave] = True

        try:
            insight = obtener_insights(campaña["id"], token, fecha_desde, fecha_hasta)
        except RuntimeError as e:
            print(f"\n  ⚠️  Error en {campaña['name']}: {e}")
            continue

        if insight is None:
            print(f"\n  ℹ️  Sin datos para: {campaña['name']} (período sin actividad)")
            continue

        metricas = procesar_insight(insight)
        metricas["id"]     = campaña["id"]
        metricas["estado"] = campaña.get("status", "—")
        metricas["clave"]  = clave

        alertas = evaluar_alertas(metricas, clave)
        todas_alertas.extend(alertas)

        imprimir_campaña(metricas, alertas)
        reporte.append(metricas)

    # Avisar campañas no encontradas
    for clave, encontrada in campañas_encontradas.items():
        if not encontrada:
            print(f"\n  ℹ️  No se encontró campaña para: {CAMPAÑAS_OBJETIVO[clave]}")

    # 3. Resumen de alertas
    if todas_alertas:
        print(f"\n{'═' * 60}")
        print("  RESUMEN DE ALERTAS")
        print(f"{'═' * 60}")
        for a in todas_alertas:
            print(f"  {a}")

    # 4. Guardar JSON si se pidió
    if args.salida:
        output = {
            "generado":     datetime.datetime.now().isoformat(),
            "fecha_desde":  fecha_desde,
            "fecha_hasta":  fecha_hasta,
            "campañas":     reporte,
            "alertas":      todas_alertas,
        }
        with open(args.salida, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n  Reporte guardado en: {args.salida}")

    print(f"\n{'═' * 60}\n")


if __name__ == "__main__":
    main()
