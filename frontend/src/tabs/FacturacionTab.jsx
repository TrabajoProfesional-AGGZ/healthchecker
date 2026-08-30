import { useState } from 'react';
import { DollarSign } from 'lucide-react';

/**
 * Componente que muestra una tabla de métricas y proyección de facturación global
 * de los clubes clientes actuales.
 *
 * @returns {JSX.Element}
 */
export default function FacturacionTab() {
  const [clubes, setClubes] = useState([
    { id: 1, nombre: 'Club Atlético Talleres (RE)', socios: 2450, transacciones: 18200, cuotaFija: 80000, comisionVariable: 364000 },
    { id: 2, nombre: 'San Lorenzo de Almagro', socios: 81200, transacciones: 145000, cuotaFija: 250000, comisionVariable: 2900000 },
    { id: 3, nombre: 'Asoc. Atlética Argentinos Jrs.', socios: 18400, transacciones: 42100, cuotaFija: 150000, comisionVariable: 842000 }
  ]);

  const formatMoney = (num) => '$ ' + num.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const formatNumber = (num) => num.toLocaleString('es-AR');

  const totalFijo = clubes.reduce((acc, club) => acc + club.cuotaFija, 0);
  const totalVariable = clubes.reduce((acc, club) => acc + club.comisionVariable, 0);
  const totalFacturar = totalFijo + totalVariable;

  return (
    <div>
      <section className="control-banner">
        <div className="control-banner-texture" aria-hidden="true" />
        <div className="control-banner-content">
          <span className="control-banner-eyebrow"><DollarSign size={14} /> RENTABILIDAD B2B</span>
          <h2 className="control-banner-title">Métricas y Facturación Global</h2>
        </div>
      </section>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Club Cliente</th>
              <th>Socios Activos</th>
              <th>Transacciones</th>
              <th>Suscripción Fija</th>
              <th>Comisión Variable</th>
              <th>Total a Facturar</th>
            </tr>
          </thead>
          <tbody>
            {clubes.map((club) => (
              <tr key={club.id}>
                <td style={{fontWeight: 600, color: 'var(--text-primary)'}}>{club.nombre}</td>
                <td>{formatNumber(club.socios)}</td>
                <td>{formatNumber(club.transacciones)}</td>
                <td>{formatMoney(club.cuotaFija)}</td>
                <td>{formatMoney(club.comisionVariable)}</td>
                <td className="text-green">{formatMoney(club.cuotaFija + club.comisionVariable)}</td>
              </tr>
            ))}
            <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)'}}>
              <td colSpan="3" style={{ textAlign: 'right', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.85rem', letterSpacing: '0.05em' }}>
                TOTAL PROYECTADO:
              </td>
              <td style={{ fontWeight: 600 }}>{formatMoney(totalFijo)}</td>
              <td style={{ fontWeight: 600 }}>{formatMoney(totalVariable)}</td>
              <td className="text-green" style={{ fontSize: '1.1rem' }}>
                {formatMoney(totalFacturar)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
