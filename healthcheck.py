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
MAX_LOGS = 50  # Guardamos los últimos 50 pings para no saturar la memoria RAM

endpoints = [
    {"name": "Gateway", "url": "https://sociounido-gateway.onrender.com/__health"},
    {"name": "MS Club", "url": "https://microservicio-club.onrender.com/health"},
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
    # Creamos las filas de la tabla dinámicamente
    table_rows = ""
    for log in LOGS_HISTORY:
        table_rows += f"""
        <tr>
            <td>{log['time']}</td>
            <td><strong>{log['name']}</strong></td>
            <td><a href="{log['url']}" target="_blank">{log['url']}</a></td>
            <td style="color: {log['color']}; font-weight: bold;">{log['status']}</td>
        </tr>
        """

    # Si todavía no se ejecutó ningún ping
    if not table_rows:
        table_rows = "<tr><td colspan='4' style='text-align:center;'>Esperando el primer ciclo de pings...</td></tr>"

    # HTML con un diseño oscuro (Dark Mode) simple y limpio
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SocioUnido | Pinger Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 40px; }}
            h1 {{ color: #ffffff; border-bottom: 2px solid #333; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #1e1e1e; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ background-color: #252525; color: #00adb5; }}
            tr:hover {{ background-color: #2a2a2a; }}
            a {{ color: #4fc3f7; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .info {{ color: #888; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>SocioUnido - Infraestructura Keep-Alive</h1>
        <p class="info">Este servicio realiza un chequeo cada 20 segundos para mitigar el Cold Start de la capa gratuita de Render.</p>
        <table>
            <thead>
                <tr>
                    <th>Fecha / Hora</th>
                    <th>Servicio</th>
                    <th>URL Monitoreada</th>
                    <th>Estado de Respuesta</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)