import os
import threading
import time
from datetime import datetime
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

"""API para la recolección y exposición de la telemetría del sistema."""

app = FastAPI(title="SocioUnido Control Plane API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOGS_HISTORY = []
MAX_LOGS = 30

MS_AUTH_URL = os.environ.get(
    "MS_AUTH_URL", "https://microservicio-autenticacion-lo4w.onrender.com"
)
INTERNAL_SECRET_TOKEN = os.environ.get("INTERNAL_SECRET_TOKEN", "")
RUTA_INVENTARIO = "/api/v1/internos/clubes"


NODOS_COMPARTIDOS = [
    {"name": "Gateway", "url": "https://api.sociounido.com/__health", "type": "Microservicio"},
    {"name": "MS Club", "url": "https://microservicio-club-pm6o.onrender.com/api/v1/socios/health", "type": "Microservicio"},
    {"name": "MS Auth", "url": f"{MS_AUTH_URL}/api/v1/auth/health", "type": "Microservicio"},
    {"name": "MS Analiticas", "url": "https://microservicio-analiticas-ngys.onrender.com/api/v1/metricas/health", "type": "Microservicio"},
    {"name": "MS Pagos", "url": "https://microservicio-pagos-0cc3.onrender.com/api/v1/pagos/health", "type": "Microservicio"},
    {"name": "MS Bot", "url": "https://microservicio-bot-conversacional.onrender.com/health", "type": "Microservicio"},
    {"name": "MS Acceso", "url": "https://microservicio-acceso-ko73.onrender.com/api/v1/accesos/health", "type": "Microservicio"},
]

NOMBRES_DE_DOMINIO = {
    "pwa_socio": "App SocioUnido (PWA)",
    "panel_admin": "Web Admin",
    "control_acceso": "App Empleados (Control)",
}


def obtener_clubes():
    """El inventario del catálogo, con la base de cada club ya sondeada."""
    try:
        respuesta = requests.get(
            f"{MS_AUTH_URL}{RUTA_INVENTARIO}",
            params={"sondear": "true"},
            headers={"X-Internal-Secret": INTERNAL_SECRET_TOKEN},
            timeout=30,
        )
        respuesta.raise_for_status()
        return respuesta.json().get("clubes", []), None
    except requests.RequestException as fallo:
        return [], f"FAILED ({fallo.__class__.__name__})"


def _nodo_de_base(club):
    """La fila del tablero que corresponde a la base de un club, ya resuelta."""
    base = club.get("base") or {}
    estado = base.get("estado")
    latencia = base.get("latencia_ms")

    if estado == "ok":
        texto = f"OK ({latencia:.0f} ms)" if latencia is not None else "OK"
        color = "green"
    elif estado == "error":
        texto, color = f"ERROR ({base.get('detalle') or 'sin detalle'})", "red"
    else:
        # Un club en `provisionando` o `suspendido` no se sondea, y no es una caída: tiene que
        # verse distinto de una base que no responde.
        texto, color = f"SIN SONDEAR ({club.get('estado', 'desconocido')})", "gray"

    return {
        "name": f"Base de {club.get('nombre') or club.get('slug')}",
        "type": "Base de Datos",
        "url": None,
        "club": club.get("slug"),
        "status": texto,
        "color": color,
    }


def _nodos_a_pinguear(clubes):
    """Los nodos que este servicio consulta él mismo: el pool compartido y los frontends."""
    nodos = [{**nodo, "club": None} for nodo in NODOS_COMPARTIDOS]
    for club in clubes:
        for tipo, dominio in (club.get("dominios") or {}).items():
            nodos.append({
                "name": f"{NOMBRES_DE_DOMINIO.get(tipo, tipo)} — {club.get('nombre') or club.get('slug')}",
                "url": f"https://{dominio}/",
                "type": "Frontend",
                "club": club.get("slug"),
            })
    return nodos


def _pinguear(nodo, timestamp):
    """Consulta un nodo y devuelve su fila del tablero."""
    try:
        response = requests.get(nodo["url"], timeout=10)
        if response.ok:
            status, color = "OK", "green"
        else:
            status, color = f"ERROR ({response.status_code})", "red"
    except requests.RequestException:
        status, color = "FAILED", "orange"

    return {
        "time": timestamp,
        "name": nodo["name"],
        "type": nodo["type"],
        "url": nodo["url"],
        "club": nodo.get("club"),
        "status": status,
        "color": color,
    }


def escanear():
    """Un ciclo completo de monitoreo: el catálogo, el pool compartido y los nodos por club."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clubes, error_catalogo = obtener_clubes()

    ciclo_actual = [{
        "time": timestamp,
        "name": "Catálogo de clubes (control plane)",
        "type": "Microservicio",
        "url": f"{MS_AUTH_URL}{RUTA_INVENTARIO}",
        "club": None,
        "status": error_catalogo or f"OK ({len(clubes)} club/es)",
        "color": "red" if error_catalogo else "green",
    }]

    for nodo in _nodos_a_pinguear(clubes):
        ciclo_actual.append(_pinguear(nodo, timestamp))

    for club in clubes:
        ciclo_actual.append({"time": timestamp, **_nodo_de_base(club)})

    return {"time": timestamp, "logs": ciclo_actual}


def ping_loop():
    """Ejecuta un ciclo infinito de consultas periódicas para validar la salud de los endpoints."""
    while True:
        LOGS_HISTORY.insert(0, escanear())

        if len(LOGS_HISTORY) > MAX_LOGS:
            LOGS_HISTORY.pop()

        time.sleep(60)

@app.on_event("startup")
def start_background_pinger():
    """Inicia el demonio de monitoreo continuo en segundo plano al arrancar la aplicación."""
    threading.Thread(target=ping_loop, daemon=True).start()

@app.get("/api/status")
def get_status():
    """Devuelve los resultados de salud obtenidos durante el último escaneo."""
    if not LOGS_HISTORY:
        return {"status": "loading", "data": None}
    return {"status": "ok", "data": LOGS_HISTORY[0]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
