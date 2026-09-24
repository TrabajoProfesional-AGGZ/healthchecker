import { useState } from 'react';
import { Calculator, Settings2, BarChart3, Receipt } from 'lucide-react';
import {
  PRECIOS,
  OPCIONES,
  TIERS_INICIALES,
  GLOBALES_INICIALES,
  proyectar,
} from '../utils/costos';

const formatoUsd = (numero) =>
  'USD ' + numero.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const formatoArs = (numero) =>
  'ARS ' + numero.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/**
 * Un campo numérico con su etiqueta y, si hace falta, una aclaración del precio de lista.
 *
 * @returns {JSX.Element}
 */
function Campo({ etiqueta, valor, onChange, paso = '1', ancho = 1, ayuda }) {
  return (
    <div style={{ gridColumn: ancho === 2 ? '1 / -1' : 'auto' }}>
      <label className="input-label">{etiqueta}</label>
      <input
        type="number"
        className="su-input"
        step={paso}
        value={valor}
        onChange={(evento) => onChange(evento.target.value)}
      />
      {ayuda && (
        <span className="text-muted" style={{ fontSize: '0.75rem', display: 'block', marginTop: '0.35rem' }}>
          {ayuda}
        </span>
      )}
    </div>
  );
}

/**
 * Un desplegable para elegir el plan de un proveedor.
 *
 * @returns {JSX.Element}
 */
function Selector({ etiqueta, valor, opciones, onChange, ancho = 1 }) {
  return (
    <div style={{ gridColumn: ancho === 2 ? '1 / -1' : 'auto' }}>
      <label className="input-label">{etiqueta}</label>
      <select
        className="su-input"
        style={{ cursor: 'pointer' }}
        value={valor}
        onChange={(evento) => onChange(evento.target.value)}
      >
        {opciones.map((opcion) => (
          <option key={opcion.valor} value={opcion.valor}>
            {opcion.etiqueta}
          </option>
        ))}
      </select>
    </div>
  );
}

/**
 * Una fila del panel de resultados, con el valor en dólares y su equivalente en pesos.
 *
 * @returns {JSX.Element}
 */
function Resultado({ etiqueta, usd, dolar, destacado = false, color }) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        borderBottom: '1px solid var(--color-border)',
        padding: destacado ? '1.5rem 0' : '1rem 0',
        fontSize: destacado ? '1.2rem' : '1rem',
        fontWeight: destacado ? 'bold' : 'normal',
      }}
    >
      <span style={{ color: destacado ? 'var(--text-primary)' : 'var(--text-secondary)' }}>{etiqueta}</span>
      <div style={{ textAlign: 'right' }}>
        <span className={color} style={{ display: 'block', fontWeight: 600 }}>
          {formatoUsd(usd)}
        </span>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 'normal' }}>
          {formatoArs(usd * dolar)}
        </span>
      </div>
    </div>
  );
}

/**
 * Componente para calcular el costo operativo, la cuota que hay que cobrarle a cada club y el
 * retorno de cada escenario (tier) de volumen.
 *
 * Los precios salen de `utils/costos.js`, verificados contra las páginas de los proveedores;
 * acá sólo se editan los supuestos de uso.
 *
 * @returns {JSX.Element}
 */
export default function CalculadoraTab() {
  const [globales, setGlobales] = useState(GLOBALES_INICIALES);
  const [tiers, setTiers] = useState(TIERS_INICIALES);

  const tierActivo = tiers.find((tier) => tier.id === globales.tierActivo);
  const proyeccion = proyectar(tierActivo, globales);

  const cambiarGlobal = (campo, valor) =>
    setGlobales((previo) => ({ ...previo, [campo]: Number(valor) }));

  const cambiarTier = (campo, valor) =>
    setTiers((previos) =>
      previos.map((tier) =>
        tier.id === globales.tierActivo
          ? { ...tier, [campo]: typeof tier[campo] === 'number' ? Number(valor) : valor }
          : tier,
      ),
    );

  return (
    <div>
      <section className="control-banner">
        <div className="control-banner-texture" aria-hidden="true" />
        <div className="control-banner-content">
          <span className="control-banner-eyebrow">
            <Calculator size={14} /> HERRAMIENTA INTERNA
          </span>
          <h2 className="control-banner-title">Calculadora de Costos y ROI</h2>
        </div>
      </section>

      <div className="calc-wrapper">
        <div className="control-card">
          <h3
            style={{
              color: 'var(--brand-color)',
              marginTop: 0,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Settings2 size={18} /> Configuración global
          </h3>

          <div style={{ marginBottom: '1rem' }}>
            <label className="input-label" style={{ fontWeight: 'bold', color: 'var(--text-primary)' }}>
              Escenario activo
            </label>
            <select
              className="su-input"
              style={{
                cursor: 'pointer',
                border: '1px solid var(--brand-color)',
                backgroundColor: 'rgba(59, 130, 246, 0.05)',
              }}
              value={globales.tierActivo}
              onChange={(evento) => cambiarGlobal('tierActivo', evento.target.value)}
            >
              {tiers.map((tier) => (
                <option key={tier.id} value={tier.id}>
                  {tier.nombre} ({tier.clubes} clubes)
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <Campo
              etiqueta="Cotización del dólar (ARS)"
              valor={globales.dolar}
              onChange={(valor) => cambiarGlobal('dolar', valor)}
            />
            <Campo
              etiqueta="Integrantes del equipo"
              valor={globales.equipo}
              onChange={(valor) => cambiarGlobal('equipo', valor)}
            />
            <Campo
              etiqueta="Contingencia"
              paso="0.05"
              valor={globales.contingencia}
              onChange={(valor) => cambiarGlobal('contingencia', valor)}
              ayuda="Margen por si el costo se pasa"
            />
            <Campo
              etiqueta="Margen de ganancia"
              paso="0.05"
              valor={globales.margen}
              onChange={(valor) => cambiarGlobal('margen', valor)}
              ayuda="1,2 es un 20% sobre el costo"
            />
            <Campo
              etiqueta="Meses de prueba gratis"
              valor={globales.mesesPrueba}
              onChange={(valor) => cambiarGlobal('mesesPrueba', valor)}
            />
            <Campo
              etiqueta="Meses para amortizar el setup"
              valor={globales.mesesAmortizacionSetup}
              onChange={(valor) => cambiarGlobal('mesesAmortizacionSetup', valor)}
              ayuda="El setup se paga una vez y se reparte acá"
            />
            <Campo
              etiqueta="Recargo sobre compras en USD (%)"
              valor={globales.impuestoCompras}
              onChange={(valor) => cambiarGlobal('impuestoCompras', valor)}
              ayuda="Percepciones de tarjeta sobre la infraestructura"
            />
            <Campo
              etiqueta="Impuestos sobre la venta (%)"
              valor={globales.impuestoVentas}
              onChange={(valor) => cambiarGlobal('impuestoVentas', valor)}
              ayuda="Ingresos Brutos. El IVA se le factura aparte al club"
            />
            <Campo
              etiqueta="Workspace de Render (USD)"
              valor={globales.renderWorkspace}
              onChange={(valor) => cambiarGlobal('renderWorkspace', valor)}
              ayuda={`Pro: USD ${PRECIOS.render.workspace.pro} fijos, sin límite de miembros`}
            />
            <Campo
              etiqueta="Asientos de Vercel con deploy"
              valor={globales.asientosVercel}
              onChange={(valor) => cambiarGlobal('asientosVercel', valor)}
              ayuda="El primero ya viene con la tarifa de plataforma"
            />
            <Campo
              etiqueta="Cuentas de Google Workspace"
              valor={globales.cuentasWorkspace}
              onChange={(valor) => cambiarGlobal('cuentasWorkspace', valor)}
              ayuda={`USD ${PRECIOS.workspace.usdPorUsuario} cada una. Los alias de grupo son gratis`}
            />
            <Campo
              etiqueta="Dominio sociounido.com (USD/año)"
              paso="0.5"
              valor={globales.dominioCentralAnual}
              onChange={(valor) => cambiarGlobal('dominioCentralAnual', valor)}
            />
            <Campo
              etiqueta="Dominios propios en Render"
              valor={globales.dominiosEnRender}
              onChange={(valor) => cambiarGlobal('dominiosEnRender', valor)}
              ayuda={`${PRECIOS.render.dominiosIncluidos} incluidos, después USD 0,25 c/u`}
            />
            <Campo
              etiqueta="Minutos de build por mes"
              valor={globales.minutosBuild}
              onChange={(valor) => cambiarGlobal('minutosBuild', valor)}
              ayuda={`${PRECIOS.render.minutosBuildIncluidos} incluidos, después USD ${PRECIOS.render.usdPorMilMinutosBuild} cada 1000`}
            />
          </div>
        </div>

        <div className="control-card">
          <h3 style={{ color: 'var(--color-error)', marginTop: 0, marginBottom: '1.5rem' }}>
            Variables del escenario
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <label className="input-label">Nombre del escenario</label>
              <input
                type="text"
                className="su-input"
                value={tierActivo.nombre}
                onChange={(evento) => cambiarTier('nombre', evento.target.value)}
              />
            </div>

            <Campo
              etiqueta="Clubes en el escenario"
              ancho={2}
              valor={tierActivo.clubes}
              onChange={(valor) => cambiarTier('clubes', valor)}
            />

            <Campo
              etiqueta="Servicios Starter"
              valor={tierActivo.serviciosStarter}
              onChange={(valor) => cambiarTier('serviciosStarter', valor)}
              ayuda={`USD ${PRECIOS.render.computo.starter} c/u`}
            />
            <Campo
              etiqueta="Servicios Standard"
              valor={tierActivo.serviciosStandard}
              onChange={(valor) => cambiarTier('serviciosStandard', valor)}
              ayuda={`USD ${PRECIOS.render.computo.standard} c/u`}
            />
            <Campo
              etiqueta="Servicios Pro"
              valor={tierActivo.serviciosPro}
              onChange={(valor) => cambiarTier('serviciosPro', valor)}
              ayuda={`USD ${PRECIOS.render.computo.pro} c/u`}
            />
            <Campo
              etiqueta="Ancho de banda (GB/mes)"
              valor={tierActivo.anchoDeBandaGb}
              onChange={(valor) => cambiarTier('anchoDeBandaGb', valor)}
              ayuda={`${PRECIOS.render.anchoDeBandaIncluidoGb} GB incluidos`}
            />

            <Selector
              etiqueta="Plan de Neon"
              ancho={2}
              valor={tierActivo.planNeon}
              opciones={OPCIONES.neon}
              onChange={(valor) => cambiarTier('planNeon', valor)}
            />
            <Campo
              etiqueta="CU-horas por club"
              valor={tierActivo.cuHorasPorClub}
              onChange={(valor) => cambiarTier('cuHorasPorClub', valor)}
              ayuda="Una base inactiva escala a cero"
            />
            <Campo
              etiqueta="GB por club"
              valor={tierActivo.gbPorClub}
              onChange={(valor) => cambiarTier('gbPorClub', valor)}
              ayuda="USD 0,35 por GB-mes"
            />

            <Selector
              etiqueta="Plan de Cloudinary"
              valor={tierActivo.planCloudinary}
              opciones={OPCIONES.cloudinary}
              onChange={(valor) => cambiarTier('planCloudinary', valor)}
            />
            <Selector
              etiqueta="Render Key Value (Redis)"
              valor={tierActivo.planKeyValue}
              opciones={OPCIONES.keyValue}
              onChange={(valor) => cambiarTier('planKeyValue', valor)}
            />

            <Campo
              etiqueta="Usuarios activos mensuales"
              valor={tierActivo.uam}
              onChange={(valor) => cambiarTier('uam', valor)}
              ayuda="Firebase: los primeros 50.000 son gratis"
            />
            <Campo
              etiqueta="Trabajo por desarrollador (USD)"
              valor={tierActivo.trabajoPorDesarrollador}
              onChange={(valor) => cambiarTier('trabajoPorDesarrollador', valor)}
            />
            <Campo
              etiqueta="Setup por club (USD, una vez)"
              valor={tierActivo.setupPorClub}
              onChange={(valor) => cambiarTier('setupPorClub', valor)}
              ayuda="Tablas, DNS y migración del padrón"
            />
            <Campo
              etiqueta="Extras (USD/mes)"
              valor={tierActivo.extras}
              onChange={(valor) => cambiarTier('extras', valor)}
            />
          </div>
        </div>

        <div className="control-card" style={{ gridColumn: '1 / -1' }}>
          <h3
            style={{
              marginTop: 0,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Receipt size={18} color="var(--brand-color)" /> Desglose del costo mensual
          </h3>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Partida</th>
                  <th style={{ textAlign: 'right' }}>USD</th>
                  <th style={{ textAlign: 'right' }}>ARS</th>
                  <th style={{ textAlign: 'right' }}>% del total</th>
                </tr>
              </thead>
              <tbody>
                {proyeccion.costo.partidas.map((partida) => (
                  <tr key={partida.clave}>
                    <td style={{ color: partida.usd === 0 ? 'var(--text-secondary)' : 'var(--text-primary)' }}>
                      {partida.etiqueta}
                    </td>
                    <td style={{ textAlign: 'right' }}>{partida.usd.toFixed(2)}</td>
                    <td style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>
                      {(partida.usd * globales.dolar).toLocaleString('es-AR', { maximumFractionDigits: 0 })}
                    </td>
                    <td style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>
                      {((partida.usd / proyeccion.costo.total) * 100).toFixed(1)} %
                    </td>
                  </tr>
                ))}
                <tr>
                  <td style={{ fontWeight: 600 }}>
                    Recargo sobre compras en USD ({globales.impuestoCompras} %)
                  </td>
                  <td style={{ textAlign: 'right' }}>{proyeccion.costo.impuestos.toFixed(2)}</td>
                  <td style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>
                    {(proyeccion.costo.impuestos * globales.dolar).toLocaleString('es-AR', { maximumFractionDigits: 0 })}
                  </td>
                  <td style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>
                    {((proyeccion.costo.impuestos / proyeccion.costo.total) * 100).toFixed(1)} %
                  </td>
                </tr>
                <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
                  <td style={{ fontWeight: 600, letterSpacing: '0.05em', fontSize: '0.85rem' }}>
                    COSTO TOTAL MENSUAL
                  </td>
                  <td className="text-red" style={{ textAlign: 'right', fontSize: '1.05rem' }}>
                    {proyeccion.costo.total.toFixed(2)}
                  </td>
                  <td className="text-red" style={{ textAlign: 'right' }}>
                    {(proyeccion.costo.total * globales.dolar).toLocaleString('es-AR', { maximumFractionDigits: 0 })}
                  </td>
                  <td style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>100,0 %</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="control-card" style={{ gridColumn: '1 / -1', border: '1px solid var(--brand-color)' }}>
          <h3
            style={{
              marginTop: 0,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <BarChart3 size={18} color="var(--brand-color)" /> Proyección financiera ({tierActivo.nombre})
          </h3>

          <Resultado
            etiqueta={`Costo mensual por club (entre ${tierActivo.clubes})`}
            usd={proyeccion.costoPorClub}
            dolar={globales.dolar}
          />
          <Resultado
            etiqueta="Cuota mensual a cobrarle a cada club"
            usd={proyeccion.cuotaPorClub}
            dolar={globales.dolar}
            destacado
            color="text-green"
          />
          <Resultado
            etiqueta="Ingresos brutos mensuales"
            usd={proyeccion.ingresosBrutos}
            dolar={globales.dolar}
          />
          <Resultado
            etiqueta={`Impuestos sobre la venta (${globales.impuestoVentas} %)`}
            usd={proyeccion.impuestosVenta}
            dolar={globales.dolar}
            color="text-red"
          />
          <Resultado
            etiqueta="Costos operativos mensuales"
            usd={proyeccion.costo.total}
            dolar={globales.dolar}
            color="text-red"
          />
          <Resultado
            etiqueta="Ganancia neta mensual"
            usd={proyeccion.ganancia}
            dolar={globales.dolar}
            destacado
            color={proyeccion.ganancia >= 0 ? 'text-green' : 'text-red'}
          />
          <Resultado
            etiqueta={`Retiro por persona (entre ${globales.equipo}, con el trabajo ya facturado)`}
            usd={proyeccion.retiroPorPersona}
            dolar={globales.dolar}
            destacado
            color={proyeccion.retiroPorPersona >= 0 ? 'text-green' : 'text-red'}
          />
          <Resultado
            etiqueta={`Inversión a recuperar (setup de ${tierActivo.clubes} clubes y ${globales.mesesPrueba} mes/es de prueba)`}
            usd={proyeccion.inversionInicial}
            dolar={globales.dolar}
            color="text-red"
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 0' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Meses hasta ganar plata</span>
            <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{proyeccion.mesesHastaGanar}</span>
          </div>

          <p className="text-muted" style={{ fontSize: '0.8rem', marginBottom: 0 }}>
            Precios de proveedores verificados en septiembre de 2026 contra Render, Neon, Vercel,
            Cloudinary, Google Cloud Identity Platform y Google Workspace. Están en{' '}
            <code>src/utils/costos.js</code> junto a la fuente de cada uno.
          </p>
        </div>
      </div>
    </div>
  );
}
