import { useState } from 'react';

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
      <h2 className="section-title">Calculadora de Costos y ROI</h2>
      <div className="calc-wrapper">
        
        {/* Panel de Ingresos */}
        <div className="table-container" style={{padding: '2rem'}}>
          <h3 style={{color: 'var(--brand-color)', marginBottom: '1.5rem'}}>Métricas de Ingresos</h3>
          <label>Suscripción Fija Mensual ($)</label>
          <input type="number" value={ingresos.fijo} onChange={e => handleIngreso('fijo', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
          
          <label>Comisión por Tx ($)</label>
          <input type="number" value={ingresos.varTx} onChange={e => handleIngreso('varTx', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
          
          <label>Volumen de Tx Estimado</label>
          <input type="number" value={ingresos.volumen} onChange={e => handleIngreso('volumen', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
          
          <label>Cantidad de Clubes</label>
          <input type="number" value={ingresos.clubes} onChange={e => handleIngreso('clubes', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
        </div>

        {/* Panel de Costos */}
        <div className="table-container" style={{padding: '2rem'}}>
            <h3 style={{color: 'var(--color-error)', marginBottom: '1.5rem'}}>Costos de Infraestructura</h3>
            <label>Servidores y API Gateway ($)</label>
            <input type="number" value={costos.servers} onChange={e => handleCosto('servers', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
            
            <label>Hosting Bases de Datos y Redis ($)</label>
            <input type="number" value={costos.db} onChange={e => handleCosto('db', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
            <label>Costos de Mantenimiento y Soporte ($)</label>
            <input type="number" value={costos.maint} onChange={e => handleCosto('maint', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
            <label>Misceláneos (APIs externas, dominios) ($)</label>
            <input type="number" value={costos.misc} onChange={e => handleCosto('misc', e.target.value)} style={{width: '100%', marginBottom: '1rem', padding: '0.5rem', background: '#000', color: '#fff', border: '1px solid #333'}} />
        </div>

        {/* Resultados */}
        <div className="table-container" style={{gridColumn: 'span 2', padding: '2rem', border: '1px solid var(--brand-color)'}}>
          <h3>Proyección Financiera</h3>
          <p>Costos: <span className="text-red">{formatMoney(totalCostos)}</span></p>
          <p>Ingresos Brutos: <span style={{color: 'var(--brand-color)'}}>{formatMoney(totalIngresos)}</span></p>
          <h2 style={{marginTop: '1rem'}}>
            Ganancia Neta: <span className={gananciaNeta >= 0 ? 'text-green' : 'text-red'}>{formatMoney(gananciaNeta)}</span>
          </h2>
          <p>ROI: <span className={roi >= 0 ? 'text-green' : 'text-red'}>{roi.toFixed(2)}%</span></p>
        </div>

      </div>
    </div>
  );
}