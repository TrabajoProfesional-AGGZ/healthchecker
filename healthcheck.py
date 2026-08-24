import os
import threading
import time
from datetime import datetime
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

endpoints = [
    {"name": "Gateway", "url": "https://gateway-jd61.onrender.com/__health", "type": "Microservicio"},
    {"name": "MS Club", "url": "https://microservicio-club-pm6o.onrender.com/health", "type": "Microservicio"},
    {"name": "MS Auth", "url": "https://microservicio-autenticacion-sdy6.onrender.com/api/v1/auth/health", "type": "Microservicio"},
    {"name": "MS Analiticas", "url": "https://microservicio-analiticas-ngys.onrender.com/api/v1/metricas/health", "type": "Microservicio"},
    {"name": "MS Pagos", "url": "https://microservicio-pagos-0cc3.onrender.com/api/v1/pagos/health", "type": "Microservicio"},
    {"name": "MS Bot", "url": "https://microservicio-bot-conversacional.onrender.com/health", "type": "Microservicio"},
    {"name": "MS Acceso", "url": "https://microservicio-acceso-ko73.onrender.com/api/v1/accesos/health", "type": "Microservicio"},
    
    {"name": "App SocioUnido (PWA)", "url": "https://sociounido-app.vercel.app/", "type": "Frontend"},
    {"name": "App Empleados (Control)", "url": "https://sociounido-empleados.vercel.app/", "type": "Frontend"},
    {"name": "Web Admin", "url": "https://sociounido-web.vercel.app/", "type": "Frontend"},

    {"name": "DB Core (PostgreSQL)", "url": "https://microservicio-club.onrender.com/health/db", "type": "Base de Datos"},
    {"name": "DB Pagos (PostgreSQL)", "url": "https://microservicio-pagos-0cc3.onrender.com/api/v1/pagos/health/db", "type": "Base de Datos"},
    {"name": "DB Auth (Firebase)", "url": "https://microservicio-autenticacion-sdy6.onrender.com/api/v1/auth/health/firebase", "type": "Base de Datos"},
    {"name": "Cache (Redis)", "url": "https://microservicio-analiticas-ngys.onrender.com/api/v1/metricas/health/redis", "type": "Base de Datos"},
]

def ping_loop():
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        ciclo_actual = []
        for endpoint in endpoints:
            name, url, tipo = endpoint["name"], endpoint["url"], endpoint["type"]
            
            try:
                response = requests.get(url, timeout=10)
                if response.ok:
                    status, color = "OK", "green"
                else:
                    status, color = f"ERROR ({response.status_code})", "red"
            except requests.RequestException:
                status, color = "FAILED", "orange"
            
            ciclo_actual.append({
                "time": timestamp,
                "name": name,
                "type": tipo,
                "url": url,
                "status": status,
                "color": color
            })
            
        LOGS_HISTORY.insert(0, {"time": timestamp, "logs": ciclo_actual})
        
        if len(LOGS_HISTORY) > MAX_LOGS:
            LOGS_HISTORY.pop()
        
        time.sleep(60)

@app.on_event("startup")
def start_background_pinger():
    threading.Thread(target=ping_loop, daemon=True).start()

@app.get("/api/status")
def get_status():
    """Devuelve los logs del último escaneo."""
    if not LOGS_HISTORY:
        return {"status": "loading", "data": None}
    return {"status": "ok", "data": LOGS_HISTORY[0]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)