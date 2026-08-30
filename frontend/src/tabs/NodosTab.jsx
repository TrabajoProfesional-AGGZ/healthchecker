import { useState, useEffect } from 'react';
import { Activity, ExternalLink } from 'lucide-react';

const URL_HEALTHCHECKER = import.meta.env.VITE_HEALTH_BASE_URL;

/**
 * Componente que monitorea el estado de salud de la infraestructura (pinger),
 * mostrando el estado actual de las bases de datos, microservicios y frontends.
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

      {['Base de Datos', 'Microservicio', 'Frontend'].map(tipo => (
        <div key={tipo}>
          <h3 style={{color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '1rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem'}}>{tipo}</h3>
          <div className="service-grid">
            {grouped[tipo]?.map((servicio, idx) => {
              const statusClass = servicio.color === 'green' ? 'success' : 'danger';
              return (
                <div key={idx} className={`service-card service-card--${statusClass}`}>
                  <div style={{display: 'flex', flexDirection: 'column', gap: '4px'}}>
                    <span style={{fontWeight: 600, fontSize: '0.95rem'}}>{servicio.name}</span>
                    <span className={statusClass === 'success' ? 'text-green' : 'text-red'} style={{fontSize: '0.85rem'}}>
                      {servicio.status}
                    </span>
                  </div>
                  <a href={servicio.url} target="_blank" rel="noreferrer" style={{color: 'var(--text-secondary)', padding: '8px', background: 'var(--bg-main)', borderRadius: '50%'}}>
                    <ExternalLink size={16} />
                  </a>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
