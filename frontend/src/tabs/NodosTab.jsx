import { useState, useEffect } from 'react';
import { Activity, ExternalLink } from 'lucide-react';

const URL_HEALTHCHECKER = import.meta.env.VITE_HEALTH_BASE_URL;

const TIPOS = ['Base de Datos', 'Microservicio', 'Frontend'];

/** Color del texto de estado, por clase de tarjeta. */
const CLASE_DE_TEXTO = {
  success: 'text-green',
  muted: 'text-muted',
  warning: 'text-red',
  danger: 'text-red',
};

/**
 * Traduce el color que manda la API a la clase de la tarjeta.
 *
 * `gray` no es una caída: es el club que todavía no atiende tráfico y por eso no se sondea.
 * Pintarlo de rojo haría que un alta a medio terminar se confunda con una base caída, que es
 * justo la distinción que el tablero tiene que dejar clara.
 *
 * @param {string} color - 'green', 'red', 'orange' o 'gray'.
 * @returns {string} Sufijo de la clase `service-card--*`.
 */
function claseDeEstado(color) {
  if (color === 'green') return 'success';
  if (color === 'gray') return 'muted';
  if (color === 'orange') return 'warning';
  return 'danger';
}

/**
 * Agrupa los nodos de un tipo por club, dejando primero los compartidos.
 *
 * Los nodos del pool de cómputo (el gateway y los microservicios) no llevan club porque son
 * los mismos para todos los clientes; los que se multiplican por club llevan su slug.
 *
 * @param {Array<Object>} nodos - Filas del último escaneo, ya filtradas por tipo.
 * @returns {Array<[string|null, Array<Object>]>} Pares (club, nodos) en orden de presentación.
 */
function agruparPorClub(nodos) {
  const porClub = new Map();
  nodos.forEach((nodo) => {
    const clave = nodo.club || null;
    if (!porClub.has(clave)) porClub.set(clave, []);
    porClub.get(clave).push(nodo);
  });

  return [...porClub.entries()].sort(([a], [b]) => {
    if (a === b) return 0;
    if (a === null) return -1;
    if (b === null) return 1;
    return a.localeCompare(b);
  });
}

/**
 * Componente que monitorea el estado de salud de la infraestructura (pinger),
 * mostrando el estado actual de las bases de datos, microservicios y frontends.
 *
 * La matriz la arma el backend contra el catálogo de clubes, así que dar de alta un cliente
 * agrega sus nodos acá sin tocar ni este componente ni la lista del backend.
 *
 * @returns {JSX.Element}
 */
export default function NodosTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${URL_HEALTHCHECKER}/api/status`);
        const json = await res.json();
        if (json.status === 'ok') setData(json.data);
      } catch (error) {
        console.error("Error fetching status:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 20000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !data) return <p style={{color: 'var(--text-secondary)'}}>Inicializando telemetría...</p>;

  const grouped = data.logs.reduce((acc, log) => {
    if (!acc[log.type]) acc[log.type] = [];
    acc[log.type].push(log);
    return acc;
  }, {});

  return (
    <div>
      <section className="control-banner">
        <div className="control-banner-texture" aria-hidden="true" />
        <div className="control-banner-content">
          <span className="control-banner-eyebrow"><Activity size={14} /> PINGER DE SERVICIOS</span>
          <h2 className="control-banner-title">Salud de Infraestructura</h2>
          <p style={{color: 'rgba(255,255,255,0.7)', margin: '10px 0 0', fontSize: '0.9rem'}}>Último escaneo: {data.time}</p>
          <button onClick={() => window.location.reload()} style={{marginTop: '10px', padding: '6px 12px', backgroundColor: 'var(--brand-color)', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>
            Refrescar
          </button>
        </div>
      </section>

      {TIPOS.map(tipo => (
        <div key={tipo}>
          <h3 style={{color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '1rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem'}}>{tipo}</h3>
          {agruparPorClub(grouped[tipo] || []).map(([club, nodos]) => (
            <div key={club || 'compartidos'}>
              <h4 style={{color: 'var(--text-secondary)', margin: '0 0 0.75rem', fontSize: '0.8rem', letterSpacing: '0.05em', textTransform: 'uppercase'}}>
                {club ? `Club: ${club}` : 'Compartidos (pool de cómputo)'}
              </h4>
              <div className="service-grid">
                {nodos.map((servicio, idx) => {
                  const statusClass = claseDeEstado(servicio.color);
                  return (
                    <div key={idx} className={`service-card service-card--${statusClass}`}>
                      <div style={{display: 'flex', flexDirection: 'column', gap: '4px'}}>
                        <span style={{fontWeight: 600, fontSize: '0.95rem'}}>{servicio.name}</span>
                        <span className={CLASE_DE_TEXTO[statusClass]} style={{fontSize: '0.85rem'}}>
                          {servicio.status}
                        </span>
                      </div>
                      {servicio.url && (
                        <a href={servicio.url} target="_blank" rel="noreferrer" style={{color: 'var(--text-secondary)', padding: '8px', background: 'var(--bg-main)', borderRadius: '50%'}}>
                          <ExternalLink size={16} />
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
