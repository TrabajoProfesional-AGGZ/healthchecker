import { useState } from 'react';
import { Calculator } from 'lucide-react';

export default function CalculadoraTab() {
  const [ingresos, setIngresos] = useState({ fijo: 150000, varTx: 20, volumen: 45000, clubes: 1 });
  const [costos, setCostos] = useState({ servers: 45000, db: 85000, maint: 120000, misc: 15000 });

  const totalCostos = costos.servers + costos.db + costos.maint + costos.misc;
  const ingresosPorClub = ingresos.fijo + (ingresos.varTx * ingresos.volumen);
  const totalIngresos = ingresosPorClub * ingresos.clubes;
  const gananciaNeta = totalIngresos - totalCostos;
  const roi = totalCostos > 0 ? (gananciaNeta / totalCostos) * 100 : 0;

  const formatMoney = (num) => '$ ' + num.toLocaleString('es-AR');

  const handleIngreso = (campo, val) => setIngresos(prev => ({ ...prev, [campo]: Number(val) }));
  const handleCosto = (campo, val) => setCostos(prev => ({ ...prev, [campo]: Number(val) }));

  return (
    <div>
      <section className="control-banner">
        <div className="control-banner-texture" aria-hidden="true" />
        <div className="control-banner-content">
          <span className="control-banner-eyebrow"><Calculator size={14} /> HERRAMIENTA INTERNA</span>
          <h2 className="control-banner-title">Calculadora de Costos y ROI</h2>
        </div>
      </section>

      <div className="calc-wrapper">
        
        {/* Panel de Ingresos */}
        <div className="control-card">
          <h3 style={{color: 'var(--brand-color)', marginBottom: '1.5rem', marginTop: 0}}>Métricas de Ingresos</h3>
          
          <label className="input-label">Suscripción Fija Mensual ($)</label>
          <input type="number" className="su-input" value={ingresos.fijo} onChange={e => handleIngreso('fijo', e.target.value)} />
          
          <label className="input-label">Comisión por Tx ($)</label>
          <input type="number" className="su-input" value={ingresos.varTx} onChange={e => handleIngreso('varTx', e.target.value)} />
          
          <label className="input-label">Volumen de Tx Estimado</label>
          <input type="number" className="su-input" value={ingresos.volumen} onChange={e => handleIngreso('volumen', e.target.value)} />
          
          <label className="input-label">Cantidad de Clubes</label>
          <input type="number" className="su-input" value={ingresos.clubes} onChange={e => handleIngreso('clubes', e.target.value)} />
        </div>

        {/* Panel de Costos */}
        <div className="control-card">
          <h3 style={{color: 'var(--color-error)', marginBottom: '1.5rem', marginTop: 0}}>Costos de Infraestructura</h3>
          
          <label className="input-label">Servidores y API Gateway ($)</label>
          <input type="number" className="su-input" value={costos.servers} onChange={e => handleCosto('servers', e.target.value)} />
          
          <label className="input-label">Hosting Bases de Datos y Redis ($)</label>
          <input type="number" className="su-input" value={costos.db} onChange={e => handleCosto('db', e.target.value)} />
          
          <label className="input-label">Mantenimiento y Soporte ($)</label>
          <input type="number" className="su-input" value={costos.maint} onChange={e => handleCosto('maint', e.target.value)} />
          
          <label className="input-label">Misceláneos (APIs, dominios) ($)</label>
          <input type="number" className="su-input" value={costos.misc} onChange={e => handleCosto('misc', e.target.value)} />
        </div>

        {/* Resultados */}
        <div className="control-card" style={{gridColumn: '1 / -1', border: '1px solid var(--brand-color)'}}>
          <h3 style={{marginTop: 0}}>Proyección Financiera</h3>
          <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', padding: '1rem 0'}}>
            <span>Costos Operativos:</span>
            <span className="text-red">{formatMoney(totalCostos)}</span>
          </div>
          <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', padding: '1rem 0'}}>
            <span>Ingresos Brutos:</span>
            <span style={{color: 'var(--brand-color)', fontWeight: 600}}>{formatMoney(totalIngresos)}</span>
          </div>
          <div style={{display: 'flex', justifyContent: 'space-between', padding: '1rem 0', fontSize: '1.2rem', fontWeight: 'bold'}}>
            <span>Ganancia Neta:</span>
            <span className={gananciaNeta >= 0 ? 'text-green' : 'text-red'}>{formatMoney(gananciaNeta)}</span>
          </div>
          <div style={{display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0'}}>
            <span style={{color: 'var(--text-secondary)'}}>Retorno de Inversión (ROI):</span>
            <span className={roi >= 0 ? 'text-green' : 'text-red'}>{roi.toFixed(2)}%</span>
          </div>
        </div>

      </div>
    </div>
  );
}