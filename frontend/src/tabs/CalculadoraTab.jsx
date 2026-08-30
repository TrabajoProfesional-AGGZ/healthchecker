import { useState } from 'react';
import { Calculator, Settings2, BarChart3 } from 'lucide-react';

export default function CalculadoraTab() {
  // Configuración global que aplica a todos los Tiers
  const [globalConfig, setGlobalConfig] = useState({
    activeTierId: 1,
    dolar: 1500,
    cuotaClubUsd: 1000,
    teamSize: 4,
    mesesPrueba: 1,
    googleWorkspace: 20,
    dominioCentral: 0.47
  });

  // Tiers extraídos exactamente de tu archivo Excel
  const [tiers, setTiers] = useState([
    { id: 1, nombre: 'Tier 1 (< 10k socios)', clubes: 3, renderCuenta: 25, renderServicios: 56, db: 19, cloudinary: 0, vercel: 80, dominios: 10.5, firebase: 0, extras: 0 },
    { id: 2, nombre: 'Tier 2 (10k - 20k socios)', clubes: 6, renderCuenta: 25, renderServicios: 74, db: 19, cloudinary: 0, vercel: 80, dominios: 10.5, firebase: 0, extras: 0 },
    { id: 3, nombre: 'Tier 3 (20k - 50k socios)', clubes: 15, renderCuenta: 25, renderServicios: 92, db: 19, cloudinary: 0, vercel: 80, dominios: 10.5, firebase: 0, extras: 0 },
    { id: 4, nombre: 'Tier 4 (> 100k socios)', clubes: 30, renderCuenta: 25, renderServicios: 284, db: 69, cloudinary: 89, vercel: 80, dominios: 10.5, firebase: 0, extras: 0 }
  ]);

  const handleGlobal = (campo, val) => setGlobalConfig(prev => ({ ...prev, [campo]: Number(val) }));
  
  const handleTierUpdate = (campo, val) => {
    setTiers(prev => prev.map(t => 
      t.id === globalConfig.activeTierId ? { ...t, [campo]: campo === 'nombre' ? val : Number(val) } : t
    ));
  };

  const activeTier = tiers.find(t => t.id === globalConfig.activeTierId);

  const formatUsd = (num) => 'USD ' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const formatArs = (num) => 'ARS ' + num.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  // === CÁLCULOS (Usando el Tier Activo) ===
  const costoTotalUsd = activeTier.renderCuenta + activeTier.renderServicios + activeTier.db + 
                        activeTier.cloudinary + activeTier.vercel + activeTier.dominios + 
                        activeTier.firebase + activeTier.extras + 
                        globalConfig.googleWorkspace + globalConfig.dominioCentral;

  const ingresosMensualesUsd = globalConfig.cuotaClubUsd * activeTier.clubes;
  const gananciaNetaUsd = ingresosMensualesUsd - costoTotalUsd;

  // Conversiones a ARS
  const costoTotalArs = costoTotalUsd * globalConfig.dolar;
  const ingresosMensualesArs = ingresosMensualesUsd * globalConfig.dolar;
  const gananciaNetaArs = gananciaNetaUsd * globalConfig.dolar;

  // Ganancia particionada
  const gananciaPorPersonaUsd = gananciaNetaUsd / (globalConfig.teamSize || 1);
  const gananciaPorPersonaArs = gananciaNetaArs / (globalConfig.teamSize || 1);

  // Break-Even (Meses hasta recuperar la inversión de prueba)
  let mesesBreakEven = "Nunca";
  if (gananciaNetaUsd > 0) {
    const inversionPrueba = costoTotalUsd * globalConfig.mesesPrueba;
    const mesesRecupero = inversionPrueba / gananciaNetaUsd;
    mesesBreakEven = Math.ceil(globalConfig.mesesPrueba + mesesRecupero);
  }

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
        
        {/* Panel 1: Configuración Global y Selección de Escenario */}
        <div className="control-card">
          <h3 style={{color: 'var(--brand-color)', marginBottom: '1.5rem', marginTop: 0, display: 'flex', alignItems: 'center', gap: '8px'}}>
            <Settings2 size={18} /> Configuración Global
          </h3>
          
          <div style={{gridColumn: '1 / -1', marginBottom: '1rem'}}>
            <label className="input-label" style={{fontWeight: 'bold', color: 'var(--text-primary)'}}>
              Escenario Activo (Tier)
            </label>
            <select 
              className="su-input" 
              style={{cursor: 'pointer', border: '1px solid var(--brand-color)', backgroundColor: 'rgba(59, 130, 246, 0.05)'}}
              value={globalConfig.activeTierId} 
              onChange={e => handleGlobal('activeTierId', e.target.value)}
            >
              {tiers.map(t => (
                <option key={t.id} value={t.id}>{t.nombre} ({t.clubes} clubes)</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div>
              <label className="input-label">Cotización Dólar (ARS)</label>
              <input type="number" className="su-input" value={globalConfig.dolar} onChange={e => handleGlobal('dolar', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Cuota por Club (USD)</label>
              <input type="number" className="su-input" value={globalConfig.cuotaClubUsd} onChange={e => handleGlobal('cuotaClubUsd', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Integrantes Equipo</label>
              <input type="number" className="su-input" value={globalConfig.teamSize} onChange={e => handleGlobal('teamSize', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Meses Prueba Gratis</label>
              <input type="number" className="su-input" value={globalConfig.mesesPrueba} onChange={e => handleGlobal('mesesPrueba', e.target.value)} />
            </div>
            <div>
              <label className="input-label">G. Workspace (Fijo)</label>
              <input type="number" className="su-input" value={globalConfig.googleWorkspace} onChange={e => handleGlobal('googleWorkspace', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Dominio SU (Fijo)</label>
              <input type="number" className="su-input" step="0.01" value={globalConfig.dominioCentral} onChange={e => handleGlobal('dominioCentral', e.target.value)} />
            </div>
          </div>
        </div>

        {/* Panel 2: Costos del Tier Seleccionado */}
        <div className="control-card">
          <h3 style={{color: 'var(--color-error)', marginBottom: '1.5rem', marginTop: 0}}>
            Variables del {activeTier.nombre.split(' ')[0] + ' ' + activeTier.nombre.split(' ')[1]}
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div style={{gridColumn: '1 / -1'}}>
              <label className="input-label">Nombre del Escenario</label>
              <input type="text" className="su-input" value={activeTier.nombre} onChange={e => handleTierUpdate('nombre', e.target.value)} />
            </div>
            <div style={{gridColumn: '1 / -1'}}>
              <label className="input-label">Cantidad de Clubes Proyectados</label>
              <input type="number" className="su-input" value={activeTier.clubes} onChange={e => handleTierUpdate('clubes', e.target.value)} />
            </div>

            <div>
              <label className="input-label">Render (Cuenta)</label>
              <input type="number" className="su-input" value={activeTier.renderCuenta} onChange={e => handleTierUpdate('renderCuenta', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Render (Servicios)</label>
              <input type="number" className="su-input" value={activeTier.renderServicios} onChange={e => handleTierUpdate('renderServicios', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Vercel</label>
              <input type="number" className="su-input" value={activeTier.vercel} onChange={e => handleTierUpdate('vercel', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Base de Datos</label>
              <input type="number" className="su-input" value={activeTier.db} onChange={e => handleTierUpdate('db', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Cloudinary</label>
              <input type="number" className="su-input" value={activeTier.cloudinary} onChange={e => handleTierUpdate('cloudinary', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Dominios (Clubes)</label>
              <input type="number" className="su-input" value={activeTier.dominios} onChange={e => handleTierUpdate('dominios', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Firebase</label>
              <input type="number" className="su-input" value={activeTier.firebase} onChange={e => handleTierUpdate('firebase', e.target.value)} />
            </div>
            <div>
              <label className="input-label">Extras</label>
              <input type="number" className="su-input" value={activeTier.extras} onChange={e => handleTierUpdate('extras', e.target.value)} />
            </div>
          </div>
        </div>

        {/* Panel 3: Resultados */}
        <div className="control-card" style={{gridColumn: '1 / -1', border: '1px solid var(--brand-color)'}}>
          <h3 style={{marginTop: 0, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px'}}>
            <BarChart3 size={18} color="var(--brand-color)" /> Proyección Financiera ({activeTier.nombre})
          </h3>
          
          <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', padding: '1rem 0'}}>
            <span style={{color: 'var(--text-secondary)'}}>Ingresos Brutos Mensuales:</span>
            <div style={{textAlign: 'right'}}>
              <span style={{color: 'var(--brand-color)', fontWeight: 600, display: 'block'}}>{formatUsd(ingresosMensualesUsd)}</span>
              <span style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>{formatArs(ingresosMensualesArs)}</span>
            </div>
          </div>

          <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', padding: '1rem 0'}}>
            <span style={{color: 'var(--text-secondary)'}}>Costos Operativos Mensuales:</span>
            <div style={{textAlign: 'right'}}>
              <span className="text-red" style={{display: 'block'}}>{formatUsd(costoTotalUsd)}</span>
              <span style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>{formatArs(costoTotalArs)}</span>
            </div>
          </div>

          <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', padding: '1.5rem 0', fontSize: '1.2rem', fontWeight: 'bold'}}>
            <span>Ganancia Neta Mensual:</span>
            <div style={{textAlign: 'right'}}>
              <span className={gananciaNetaUsd >= 0 ? 'text-green' : 'text-red'} style={{display: 'block'}}>{formatUsd(gananciaNetaUsd)}</span>
              <span style={{fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: 'normal'}}>{formatArs(gananciaNetaArs)}</span>
            </div>
          </div>

          <div style={{display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', padding: '1.5rem 0', fontSize: '1.1rem', fontWeight: 'bold'}}>
            <span>Ganancia por Persona (/{globalConfig.teamSize}):</span>
            <div style={{textAlign: 'right'}}>
              <span className={gananciaPorPersonaUsd >= 0 ? 'text-green' : 'text-red'} style={{display: 'block'}}>{formatUsd(gananciaPorPersonaUsd)}</span>
              <span style={{fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 'normal'}}>{formatArs(gananciaPorPersonaArs)}</span>
            </div>
          </div>

          <div style={{display: 'flex', justifyContent: 'space-between', padding: '1rem 0'}}>
            <span style={{color: 'var(--text-secondary)'}}>Meses hasta ganar plata (Break-Even):</span>
            <span style={{fontWeight: 'bold', fontSize: '1.1rem'}}>{mesesBreakEven}</span>
          </div>
        </div>

      </div>
    </div>
  );
}