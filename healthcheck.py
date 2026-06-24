import os
import threading
import time
from datetime import datetime
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from colorama import Fore, init

init(autoreset=True)

app = FastAPI(title="Keep-Alive Pinger")

# --- CONFIGURACIÓN DEL HISTORIAL ---
LOGS_HISTORY = []
MAX_LOGS = 20  # Guardamos los últimos 50 pings para no saturar la memoria RAM

endpoints = [
    {"name": "Gateway", "url": "https://sociounido-gateway.onrender.com/__health"},
    {"name": "MS Club", "url": "https://microservicio-club.onrender.com/api/v1/socios/health"},
    {"name": "MS Auth", "url": "https://microservicio-autenticacion-sdy6.onrender.com/api/v1/auth/health"},
    {"name": "Web Admin", "url": "https://sociounido-web.vercel.app/"},
]

colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
name_to_color = {endpoint["name"]: colors[i % len(colors)] for i, endpoint in enumerate(endpoints)}

def ping_loop():
    while True:
        # Hora local de Buenos Aires para el registro
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for endpoint in endpoints:
            name = endpoint["name"]
            url = endpoint["url"]
            color = name_to_color[name]
            
            try:
                response = requests.get(url, timeout=10)
                if response.ok:
                    status_text = "OK"
                    status_color = "green"
                    print(f"{color}[{name}] | URL: {url} - Status: {Fore.GREEN}{response.status_code}")
                else:
                    status_text = f"ERROR ({response.status_code})"
                    status_color = "red"
                    print(f"{color}[{name}] | URL: {url} - Status: {Fore.RED}{response.status_code}")
            except requests.RequestException as e:
                status_text = "FAILED (Timeout/Down)"
                status_color = "orange"
                print(f"{color}[{name}] | URL: {url} - Error: {e}")
            
            # Guardamos el log estructurado para la web
            log_entry = {
                "time": timestamp,
                "name": name,
                "url": url,
                "status": status_text,
                "color": status_color
            }
            
            # Insertamos al principio para que el más nuevo salga arriba
            LOGS_HISTORY.insert(0, log_entry)
            
        # Controlamos el tamaño de la lista para evitar fugas de memoria
        while len(LOGS_HISTORY) > MAX_LOGS:
            LOGS_HISTORY.pop()
            
        time.sleep(20)

@app.on_event("startup")
def start_background_pinger():
    print(Fore.CYAN + "Iniciando servicio web y lanzando pinger en segundo plano...")
    pinger_thread = threading.Thread(target=ping_loop, daemon=True)
    pinger_thread.start()

# --- ENDPOINT COMPARTIDO PARA LA VISTA WEB ---
@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    # 1. Agrupamos los logs por el timestamp exacto (el intervalo)
    ciclos = {}
    for log in LOGS_HISTORY:
        tiempo = log['time']
        if tiempo not in ciclos:
            ciclos[tiempo] = []
        ciclos[tiempo].append(log)

    # 2. Armamos las tarjetas (cards) por cada ciclo
    cards_html = ""
    for tiempo, resultados in ciclos.items():
        grid_items = ""
        for res in resultados:
            grid_items += f"""
            <div class="service-item">
                <div class="service-name">{res['name']}</div>
                <div class="service-url"><a href="{res['url']}" target="_blank">Ver Endpoint</a></div>
                <div class="service-status" style="color: {res['color']};">{res['status']}</div>
            </div>
            """
        
        cards_html += f"""
        <div class="cycle-card">
            <div class="cycle-header">⏱️ Check: {tiempo}</div>
            <div class="service-grid">
                {grid_items}
            </div>
        </div>
        """

    if not cards_html:
        cards_html = "<div class='cycle-card' style='text-align:center;'>Esperando el primer ciclo de pings...</div>"

    # 3. HTML con CSS Grid y Auto-Refresh
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SocioUnido | Pinger Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 40px; }}
            h1 {{ color: #ffffff; border-bottom: 2px solid #333; padding-bottom: 10px; }}
            .info {{ color: #888; font-size: 0.9em; margin-bottom: 30px; }}
            
            /* Contenedor de cada intervalo */
            .cycle-card {{
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 15px 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                border-left: 4px solid #00adb5;
            }}
            .cycle-header {{
                font-size: 1.1em;
                font-weight: bold;
                color: #00adb5;
                margin-bottom: 15px;
                border-bottom: 1px solid #333;
                padding-bottom: 8px;
            }}
            
            /* Grilla interna de microservicios */
            .service-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}
            .service-item {{
                background-color: #252525;
                padding: 12px;
                border-radius: 6px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                border: 1px solid #333;
            }}
            .service-name {{ font-weight: bold; font-size: 1.1em; margin-bottom: 5px; color: #fff; }}
            .service-url a {{ color: #4fc3f7; text-decoration: none; font-size: 0.85em; }}
            .service-url a:hover {{ text-decoration: underline; }}
            .service-status {{ font-weight: bold; margin-top: 8px; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <h1>SocioUnido - Monitor Dinámico</h1>
        <p class="info">Auto-actualización cada 20 segundos. Mitigación de Cold Start activa.</p>
        
        <div id="dashboard">
            {cards_html}
        </div>

        <script>
            // Recarga la página automáticamente cada 20 segundos para ver los nuevos pings
            setTimeout(function() {{
                window.location.reload(1);
            }}, 20000);
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)