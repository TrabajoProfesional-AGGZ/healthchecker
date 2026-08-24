import { useState, useEffect } from 'react';

export default function NodosTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Apuntar a tu backend de FastAPI
        const res = await fetch('http://localhost:8000/api/status');
        const json = await res.json();
        if (json.status === 'ok') {
          setData(json.data);
        }
      } catch (error) {
        console.error("Error fetching status:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 20000); // Polling cada 20s
    return () => clearInterval(interval);
  }, []);

  if (loading || !data) return <p style={{color: 'var(--text-secondary)'}}>Inicializando telemetría...</p>;

  // Agrupar los logs por tipo
  const grouped = data.logs.reduce((acc, log) => {
    if (!acc[log.type]) acc[log.type] = [];
    acc[log.type].push(log);
    return acc;
  }, {});

  return (
    <div>
      <h2 className="section-title">Salud de Infraestructura</h2>
      <p style={{color: 'var(--color-ok)', marginBottom: '1rem'}}>Último escaneo: {data.time}</p>

      {['Base de Datos', 'Microservicio', 'Frontend'].map(tipo => (
        <div key={tipo}>
          <h3 style={{color: 'var(--text-secondary)', marginBottom: '1rem'}}>{tipo}</h3>
          <div className="service-grid">
            {grouped[tipo]?.map((servicio, idx) => (
              <div key={idx} className="service-card" style={{borderLeft: `4px solid var(--color-${servicio.color === 'green' ? 'ok' : 'error'})`}}>
                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                  <span style={{fontWeight: 600}}>{servicio.name}</span>
                  <a href={servicio.url} target="_blank" rel="noreferrer" style={{color: 'var(--brand-color)'}}>Link</a>
                </div>
                <div style={{marginTop: '10px', color: `var(--color-${servicio.color === 'green' ? 'ok' : 'error'})`}}>
                  {servicio.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}