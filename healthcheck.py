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
    {"name": "MS Analiticas", "url": "https://microservicio-analiticas.onrender.com/api/v1/metricas/health"},
    {"name": "Web Admin", "url": "https://sociounido-web.vercel.app/"},
    {"name": "MS Pagos", "url": "https://microservicio-pagos-iump.onrender.com/api/v1/pagos/health"},
    {"name": "App SocioUnido", "url": "https://aplicacion-ruddy.vercel.app/"}
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
            
        time.sleep(60)

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
            # Lógica de asignación de clases para el diseño del sistema
            status_class = "status-ok" if res['color'] == "green" else "status-error" if res['color'] == "red" else "status-warning"
            
            # Renderizado de indicadores visuales (pulso animado) dependientes del estado
            pulse_html = '<div class="pulse-dot"></div>' if status_class == "status-ok" else '<div class="error-dot"></div>'

            # Construcción de la tarjeta individual del microservicio
            grid_items += f"""
            <div class="service-card {status_class}">
                <div class="card-header">
                    <span class="service-name">{res['name']}</span>
                    <a href="{res['url']}" target="_blank" class="external-link" title="Inspeccionar Endpoint">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                            <polyline points="15 3 21 3 21 9"></polyline>
                            <line x1="10" y1="14" x2="21" y2="3"></line>
                        </svg>
                    </a>
                </div>
                <div class="card-body">
                    <div class="status-indicator">
                        {pulse_html}
                        <span class="status-text">{res['status']}</span>
                    </div>
                </div>
            </div>
            """
        
        # Estructura de la sección de cada ciclo de pings
        cards_html += f"""
        <div class="cycle-section">
            <div class="cycle-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                {tiempo}
            </div>
            <div class="service-grid">
                {grid_items}
            </div>
        </div>
        """

    # Pantalla de carga inicial si no hay logs aún
    if not cards_html:
        cards_html = """
        <div class="empty-state">
            <div class="spinner"></div>
            <p>Aguardando telemetría del primer ciclo de pings...</p>
        </div>
        """

    # 3. HTML con CSS moderno usando CSS Variables
    # Nota: Las llaves del CSS usan doble {{ }} para no romper el f-string de Python
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SocioUnido | System Status</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-main: #0a0a0a;
                --bg-card: #141414;
                --bg-card-hover: #1c1c1c;
                --border-color: #262626;
                --text-primary: #f5f5f5;
                --text-secondary: #a3a3a3;
                
                --color-ok: #10b981;
                --bg-ok: rgba(16, 185, 129, 0.1);
                
                --color-error: #ef4444;
                --bg-error: rgba(239, 68, 68, 0.1);
                
                --color-warn: #f59e0b;
                --bg-warn: rgba(245, 158, 11, 0.1);
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                background-color: var(--bg-main); 
                color: var(--text-primary); 
                padding: 2.5rem 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }}

            header {{
                margin-bottom: 2.5rem;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 1.5rem;
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
            }}

            h1 {{ 
                font-size: 1.5rem;
                font-weight: 600;
                letter-spacing: -0.025em;
            }}

            .info-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #171717;
                border: 1px solid var(--border-color);
                padding: 6px 12px;
                border-radius: 999px;
                font-size: 0.75rem;
                color: var(--text-secondary);
                font-weight: 500;
            }}

            .cycle-section {{
                margin-bottom: 3rem;
            }}

            .cycle-header {{
                display: flex;
                align-items: center;
                font-size: 0.875rem;
                font-weight: 500;
                color: var(--text-secondary);
                margin-bottom: 1rem;
            }}

            .service-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 1rem;
            }}

            .service-card {{
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1.25rem;
                transition: transform 0.2s ease, border-color 0.2s ease;
            }}

            .service-card:hover {{
                transform: translateY(-2px);
                border-color: #404040;
                background-color: var(--bg-card-hover);
            }}

            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.25rem;
            }}

            .service-name {{
                font-weight: 500;
                font-size: 0.95rem;
            }}

            .external-link {{
                color: var(--text-secondary);
                transition: color 0.2s;
                display: flex;
            }}
            
            .external-link:hover {{
                color: var(--text-primary);
            }}

            .card-body {{
                display: flex;
                align-items: center;
            }}

            .status-indicator {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 0.85rem;
                font-weight: 600;
                padding: 6px 12px;
                border-radius: 6px;
                letter-spacing: 0.02em;
            }}

            /* Estilos dinámicos inyectados por Python */
            .status-ok .status-indicator {{ color: var(--color-ok); background: var(--bg-ok); }}
            .status-error .status-indicator {{ color: var(--color-error); background: var(--bg-error); }}
            .status-warning .status-indicator {{ color: var(--color-warn); background: var(--bg-warn); }}

            /* Animaciones */
            .pulse-dot {{
                width: 8px;
                height: 8px;
                background-color: var(--color-ok);
                border-radius: 50%;
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
                animation: pulse-green 2s infinite;
            }}

            @keyframes pulse-green {{
                0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
                70% {{ transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
                100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
            }}

            .error-dot {{
                width: 8px;
                height: 8px;
                background-color: var(--color-error);
                border-radius: 50%;
                animation: blink-red 1s infinite;
            }}

            @keyframes blink-red {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.4; }}
            }}

            .empty-state {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 5rem 2rem;
                color: var(--text-secondary);
                background: var(--bg-card);
                border-radius: 8px;
                border: 1px dashed var(--border-color);
                font-size: 0.9rem;
            }}

            .spinner {{
                width: 24px;
                height: 24px;
                border: 2px solid var(--border-color);
                border-top: 2px solid var(--text-secondary);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            }}

            @keyframes spin {{ 
                0% {{ transform: rotate(0deg); }} 
                100% {{ transform: rotate(360deg); }} 
            }}
            
            /* Responsive */
            @media (max-width: 600px) {{
                .service-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <header>
            <div>
                <h1>Status Overview</h1>
            </div>
            <div class="info-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.59-9.21l5.94 5.94"/></svg>
                Auto-refresh: 60s
            </div>
        </header>
        
        <main id="dashboard">
            {cards_html}
        </main>

        <script>
            // Recarga automática de la página
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