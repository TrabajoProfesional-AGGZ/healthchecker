import { useState } from 'react';

export default function FacturacionTab() {
  // Estado inicial con los datos mockeados (en el futuro vendrán de tu API de FastAPI)
  const [clubes, setClubes] = useState([
    {
      id: 1,
      nombre: 'Club Atlético Talleres (RE)',
      socios: 2450,
      transacciones: 18200,
      cuotaFija: 80000,
      comisionVariable: 364000
    },
    {
      id: 2,
      nombre: 'San Lorenzo de Almagro',
      socios: 81200,
      transacciones: 145000,
      cuotaFija: 250000,
      comisionVariable: 2900000
    },
    {
      id: 3,
      nombre: 'Boca Jrs.',
      socios: 18400,
      transacciones: 42100,
      cuotaFija: 150000,
      comisionVariable: 842000
    }
  ]);

  // Funciones de formateo local (pesos argentinos y separadores de miles)
  const formatMoney = (num) => '$ ' + num.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const formatNumber = (num) => num.toLocaleString('es-AR');

  // Cálculos dinámicos para la fila de sumatoria final
  const totalFijo = clubes.reduce((acc, club) => acc + club.cuotaFija, 0);
  const totalVariable = clubes.reduce((acc, club) => acc + club.comisionVariable, 0);
  const totalFacturar = totalFijo + totalVariable;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
        <h2 className="section-title" style={{ margin: 0, borderBottom: 'none', paddingBottom: 0 }}>Métricas y Facturación Global</h2>
        {/* Un botón extra de UI para futuras implementaciones, como exportar a CSV/PDF */}
        <button 
          className="nav-btn active" 
          style={{ width: 'auto', margin: 0, padding: '0.6rem 1.2rem', fontSize: '0.85rem' }}
          onClick={() => alert('Próximamente: Descarga de reporte CSV')}
        >
          Exportar Reporte
        </button>
      </div>

      <div className="table-container">
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
            {clubes.map((club) => {
              const totalClub = club.cuotaFija + club.comisionVariable;
              
              return (
                <tr key={club.id}>
                  <td><strong>{club.nombre}</strong></td>
                  <td>{formatNumber(club.socios)}</td>
                  <td>{formatNumber(club.transacciones)}</td>
                  <td>{formatMoney(club.cuotaFija)}</td>
                  <td>{formatMoney(club.comisionVariable)}</td>
                  <td className="text-green" style={{ fontWeight: 600 }}>
                    {formatMoney(totalClub)}
                  </td>
                </tr>
              );
            })}

            {/* Fila de Totales Finales */}
            <tr style={{ backgroundColor: 'rgba(255,255,255,0.03)', borderTop: '2px solid var(--border-color)' }}>
              <td colSpan="3" style={{ textAlign: 'right', color: 'var(--text-secondary)', fontWeight: 500, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Total Proyectado:
              </td>
              <td style={{ fontWeight: 600 }}>{formatMoney(totalFijo)}</td>
              <td style={{ fontWeight: 600 }}>{formatMoney(totalVariable)}</td>
              <td className="text-green" style={{ fontSize: '1.15rem', fontWeight: 700 }}>
                {formatMoney(totalFacturar)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}