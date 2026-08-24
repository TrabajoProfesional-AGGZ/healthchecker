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
app = FastAPI(title="SocioUnido Control Plane")

# --- CONFIGURACIÓN DEL HISTORIAL ---
LOGS_HISTORY = []
MAX_LOGS = 30

# Hemos agregado los nodos Frontend y las Bases de Datos al monitoreo
endpoints = [
    {"name": "Gateway", "url": "https://sociounido-gateway.onrender.com/__health", "type": "Microservicio"},
    {"name": "MS Club", "url": "https://microservicio-club.onrender.com/health", "type": "Microservicio"},
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

colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
name_to_color = {endpoint["name"]: colors[i % len(colors)] for i, endpoint in enumerate(endpoints)}

def ping_loop():
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for endpoint in endpoints:
            name = endpoint["name"]
            url = endpoint["url"]
            tipo = endpoint["type"]
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
                status_text = "FAILED"
                status_color = "orange"
                print(f"{color}[{name}] | URL: {url} - Error: Timeout/Down")
            
            log_entry = {
                "time": timestamp,
                "name": name,
                "type": tipo,
                "url": url,
                "status": status_text,
                "color": status_color
            }
            
            LOGS_HISTORY.insert(0, log_entry)
        
        while len(LOGS_HISTORY) > MAX_LOGS:
            LOGS_HISTORY.pop()
        
        time.sleep(60)

@app.on_event("startup")
def start_background_pinger():
    print(Fore.CYAN + "Iniciando servicio web y lanzando pinger en segundo plano...")
    pinger_thread = threading.Thread(target=ping_loop, daemon=True)
    pinger_thread.start()

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    ciclos = {}
    for log in LOGS_HISTORY:
        tiempo = log['time']
        if tiempo not in ciclos:
            ciclos[tiempo] = []
        ciclos[tiempo].append(log)

    nodos_html = ""
    for tiempo, resultados in ciclos.items():
        
        grouped_results = {"Microservicio": "", "Base de Datos": "", "Frontend": ""}
        
        for res in resultados:
            status_class = "status-ok" if res['color'] == "green" else "status-error" if res['color'] == "red" else "status-warning"
            pulse_html = '<div class="pulse-dot"></div>' if status_class == "status-ok" else '<div class="error-dot"></div>'
            
            card = f"""
            <div class="service-card {status_class}">
                <div class="card-header">
                    <span class="service-name">{res['name']}</span>
                    <a href="{res['url']}" target="_blank" class="external-link" title="Inspeccionar">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
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
            if res['type'] in grouped_results:
                grouped_results[res['type']] += card

        nodos_html += f"""
        <div class="cycle-section">
            <div class="cycle-header">
                Último escaneo: {tiempo}
            </div>
            
            <h3 class="group-title">Bases de Datos & Caché</h3>
            <div class="service-grid">{grouped_results['Base de Datos']}</div>
            
            <h3 class="group-title">Microservicios Backend</h3>
            <div class="service-grid">{grouped_results['Microservicio']}</div>
            
            <h3 class="group-title">Interfaces Frontend</h3>
            <div class="service-grid">{grouped_results['Frontend']}</div>
        </div>
        """
        break # Solo mostramos el último ciclo en esta nueva UI

    if not nodos_html:
        nodos_html = """
        <div class="empty-state">
            <div class="spinner"></div>
            <p>Inicializando telemetría del ecosistema SocioUnido...</p>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SocioUnido Control Plane</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-main: #0a0a0a; --bg-card: #141414; --bg-card-hover: #1c1c1c;
                --border-color: #262626; --text-primary: #f5f5f5; --text-secondary: #a3a3a3;
                --color-ok: #10b981; --bg-ok: rgba(16, 185, 129, 0.1);
                --color-error: #ef4444; --bg-error: rgba(239, 68, 68, 0.1);
                --color-warn: #f59e0b; --bg-warn: rgba(245, 158, 11, 0.1);
                --brand-color: #3b82f6;
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: 'Inter', sans-serif; background-color: var(--bg-main); color: var(--text-primary); display: flex; height: 100vh; overflow: hidden; }}
            
            /* Sidebar */
            .sidebar {{ width: 280px; background-color: #0f0f0f; border-right: 1px solid var(--border-color); padding: 2rem 1rem; display: flex; flex-direction: column; }}
            .sidebar h1 {{ font-size: 1.2rem; font-weight: 600; margin-bottom: 2rem; color: #fff; text-align: center; }}
            .nav-btn {{ background: transparent; border: none; color: var(--text-secondary); padding: 1rem; text-align: left; width: 100%; border-radius: 8px; cursor: pointer; font-size: 0.95rem; font-weight: 500; transition: all 0.2s; margin-bottom: 0.5rem; }}
            .nav-btn:hover {{ background: rgba(255,255,255,0.05); color: #fff; }}
            .nav-btn.active {{ background: rgba(59, 130, 246, 0.15); color: var(--brand-color); border-left: 3px solid var(--brand-color); }}
            
            /* Content Area */
            .main-content {{ flex: 1; padding: 3rem 4rem; overflow-y: auto; }}
            .tab-pane {{ display: none; animation: fadeIn 0.3s ease; }}
            .tab-pane.active {{ display: block; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            h2.section-title {{ font-size: 1.8rem; margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; }}
            
            /* Nodos Styles */
            .group-title {{ font-size: 1.1rem; color: var(--text-secondary); margin: 2rem 0 1rem 0; font-weight: 500; }}
            .cycle-header {{ font-size: 0.85rem; color: var(--color-ok); margin-bottom: 1rem; }}
            .service-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }}
            .service-card {{ background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; transition: transform 0.2s ease, border-color 0.2s ease; }}
            .service-card:hover {{ transform: translateY(-2px); border-color: #404040; background-color: var(--bg-card-hover); }}
            .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }}
            .service-name {{ font-weight: 500; font-size: 0.95rem; }}
            .external-link {{ color: var(--text-secondary); transition: color 0.2s; display: flex; }}
            .external-link:hover {{ color: var(--text-primary); }}
            .status-indicator {{ display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; padding: 6px 12px; border-radius: 6px; }}
            .status-ok .status-indicator {{ color: var(--color-ok); background: var(--bg-ok); }}
            .status-error .status-indicator {{ color: var(--color-error); background: var(--bg-error); }}
            .status-warning .status-indicator {{ color: var(--color-warn); background: var(--bg-warn); }}
            .pulse-dot {{ width: 8px; height: 8px; background-color: var(--color-ok); border-radius: 50%; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); animation: pulse-green 2s infinite; }}
            @keyframes pulse-green {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }} }}
            .error-dot {{ width: 8px; height: 8px; background-color: var(--color-error); border-radius: 50%; animation: blink-red 1s infinite; }}
            @keyframes blink-red {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}

            /* Table Styles */
            .table-container {{ background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border-color); overflow: hidden; }}
            table {{ width: 100%; border-collapse: collapse; text-align: left; }}
            th, td {{ padding: 1.25rem 1rem; border-bottom: 1px solid var(--border-color); }}
            th {{ background: #0f0f0f; color: var(--text-secondary); font-weight: 500; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }}
            tr:hover td {{ background: rgba(255,255,255,0.02); }}
            
            /* Calculator Styles */
            .calc-wrapper {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
            .calc-card {{ background: var(--bg-card); padding: 2rem; border-radius: 8px; border: 1px solid var(--border-color); }}
            .calc-card h3 {{ font-size: 1.1rem; margin-bottom: 1.5rem; color: var(--brand-color); }}
            .input-group {{ margin-bottom: 1.25rem; }}
            .input-group label {{ display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; }}
            .input-group input {{ width: 100%; background: #0a0a0a; border: 1px solid var(--border-color); color: #fff; padding: 0.75rem 1rem; border-radius: 6px; font-family: 'Inter', sans-serif; font-size: 1rem; }}
            .input-group input:focus {{ outline: none; border-color: var(--brand-color); }}
            .result-row {{ display: flex; justify-content: space-between; padding: 1rem 0; border-bottom: 1px solid var(--border-color); font-size: 1.1rem; }}
            .result-row:last-child {{ border-bottom: none; font-weight: 600; font-size: 1.3rem; margin-top: 1rem; }}
            .text-green {{ color: var(--color-ok); }}
        </style>
    </head>
    <body>
        
        <aside class="sidebar">
            <h1>SocioUnido<br><span style="color:var(--brand-color); font-size:0.8rem; letter-spacing: 2px;">CONTROL PLANE</span></h1>
            <button class="nav-btn active" onclick="switchTab(event, 'tab-nodos')">Estado del Ecosistema</button>
            <button class="nav-btn" onclick="switchTab(event, 'tab-facturacion')">Métricas y Facturación</button>
            <button class="nav-btn" onclick="switchTab(event, 'tab-calculadora')">Calculadora de Réditos</button>
        </aside>

        <main class="main-content">
            
            <!-- TAB: NODOS -->
            <div id="tab-nodos" class="tab-pane active">
                <h2 class="section-title">Salud de Infraestructura</h2>
                {nodos_html}
            </div>

            <!-- TAB: FACTURACIÓN -->
            <div id="tab-facturacion" class="tab-pane">
                <h2 class="section-title">Métricas Globales de Clubes</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Club Cliente</th>
                                <th>Socios Activos</th>
                                <th>Transacciones (Mes)</th>
                                <th>Suscripción Fija</th>
                                <th>Comisión Variable</th>
                                <th>Total a Facturar</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Club Atlético Talleres (RE)</strong></td>
                                <td>2,450</td>
                                <td>18,200</td>
                                <td>$ 80,000.00</td>
                                <td>$ 364,000.00</td>
                                <td class="text-green">$ 444,000.00</td>
                            </tr>
                            <tr>
                                <td><strong>Club Atlético San Lorenzo</strong></td>
                                <td>81,200</td>
                                <td>145,000</td>
                                <td>$ 250,000.00</td>
                                <td>$ 2,900,000.00</td>
                                <td class="text-green">$ 3,150,000.00</td>
                            </tr>
                            <tr>
                                <td><strong>Asoc. Atlética Argentinos Jrs.</strong></td>
                                <td>18,400</td>
                                <td>42,100</td>
                                <td>$ 150,000.00</td>
                                <td>$ 842,000.00</td>
                                <td class="text-green">$ 992,000.00</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- TAB: CALCULADORA -->
            <div id="tab-calculadora" class="tab-pane">
                <h2 class="section-title">Calculadora de Costos y ROI</h2>
                <div class="calc-wrapper">
                    <!-- Ingresos -->
                    <div class="calc-card">
                        <h3>Métricas de Ingresos (Simulación)</h3>
                        <div class="input-group">
                            <label>Suscripción Fija Mensual por Club ($)</label>
                            <input type="number" id="ing_fijo" class="calc-input" value="150000">
                        </div>
                        <div class="input-group">
                            <label>Comisión cobrada por Transacción ($)</label>
                            <input type="number" id="ing_var" class="calc-input" value="20">
                        </div>
                        <div class="input-group">
                            <label>Volumen de Transacciones Estimado</label>
                            <input type="number" id="vol_tx" class="calc-input" value="45000">
                        </div>
                        <div class="input-group">
                            <label>Cantidad de Clubes Clientes</label>
                            <input type="number" id="cant_clubes" class="calc-input" value="1">
                        </div>
                    </div>

                    <!-- Costos -->
                    <div class="calc-card">
                        <h3>Métricas de Costos Operativos</h3>
                        <div class="input-group">
                            <label>Servidores y API Gateway ($)</label>
                            <input type="number" id="cost_servers" class="calc-input" value="45000">
                        </div>
                        <div class="input-group">
                            <label>Hosting Bases de Datos y Redis ($)</label>
                            <input type="number" id="cost_db" class="calc-input" value="85000">
                        </div>
                        <div class="input-group">
                            <label>Costos de Mantenimiento y Soporte ($)</label>
                            <input type="number" id="cost_maint" class="calc-input" value="120000">
                        </div>
                        <div class="input-group">
                            <label>Misceláneos (APIs externas, dominios) ($)</label>
                            <input type="number" id="cost_misc" class="calc-input" value="15000">
                        </div>
                    </div>
                    
                    <!-- Resultados -->
                    <div class="calc-card" style="grid-column: span 2; border-color: var(--brand-color);">
                        <h3>Proyección Financiera Mensual</h3>
                        <div class="result-row">
                            <span>Total Costos de Infraestructura:</span>
                            <span id="out_costos" style="color: var(--color-error);">$ 0.00</span>
                        </div>
                        <div class="result-row">
                            <span>Total Ingresos Brutos:</span>
                            <span id="out_ingresos" style="color: var(--brand-color);">$ 0.00</span>
                        </div>
                        <div class="result-row">
                            <span>Ganancia Neta (Profit):</span>
                            <span id="out_neto">$ 0.00</span>
                        </div>
                        <div class="result-row">
                            <span>Retorno de Inversión (ROI):</span>
                            <span id="out_roi" class="text-green">0.00%</span>
                        </div>
                    </div>
                </div>
            </div>

        </main>

        <script>
            // Lógica para pestañas
            function switchTab(event, tabId) {{
                document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                event.currentTarget.classList.add('active');
            }}

            // Lógica de la Calculadora Financiera
            function calcularROI() {{
                const getVal = id => parseFloat(document.getElementById(id).value) || 0;
                
                // Costos
                const totalCostos = getVal('cost_servers') + getVal('cost_db') + getVal('cost_maint') + getVal('cost_misc');
                
                // Ingresos
                const clubes = getVal('cant_clubes');
                const ingresosPorClub = getVal('ing_fijo') + (getVal('ing_var') * getVal('vol_tx'));
                const totalIngresos = ingresosPorClub * clubes;

                // Profit y ROI
                const gananciaNeta = totalIngresos - totalCostos;
                let roi = 0;
                if (totalCostos > 0) {{
                    roi = (gananciaNeta / totalCostos) * 100;
                }}

                // Render
                const formatMoney = num => '$ ' + num.toLocaleString('es-AR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                
                document.getElementById('out_costos').innerText = formatMoney(totalCostos);
                document.getElementById('out_ingresos').innerText = formatMoney(totalIngresos);
                
                const elNeto = document.getElementById('out_neto');
                elNeto.innerText = formatMoney(gananciaNeta);
                elNeto.style.color = gananciaNeta >= 0 ? 'var(--color-ok)' : 'var(--color-error)';
                
                const elRoi = document.getElementById('out_roi');
                elRoi.innerText = roi.toFixed(2) + '%';
                elRoi.style.color = roi >= 0 ? 'var(--color-ok)' : 'var(--color-error)';
            }}

            // Escuchar cambios en los inputs
            document.querySelectorAll('.calc-input').forEach(inp => {{
                inp.addEventListener('input', calcularROI);
            }});
            
            // Auto recarga si estamos en la pestaña de Nodos
            setInterval(function() {{
                if(document.getElementById('tab-nodos').classList.contains('active')) {{
                    window.location.reload();
                }}
            }}, 20000);

            // Init calculation
            calcularROI();
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)