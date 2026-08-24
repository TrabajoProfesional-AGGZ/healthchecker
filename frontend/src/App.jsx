import { useState } from 'react';
import NodosTab from './tabs/NodosTab';
import FacturacionTab from './tabs/FacturacionTab';
import CalculadoraTab from './tabs/CalculadoraTab';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('nodos');

  return (
    <div className="app-container">
      <aside className="sidebar">
        <h1>SocioUnido<br/><span style={{color: 'var(--brand-color)', fontSize: '0.8rem', letterSpacing: '2px'}}>CONTROL PLANE</span></h1>
        <button className={`nav-btn ${activeTab === 'nodos' ? 'active' : ''}`} onClick={() => setActiveTab('nodos')}>Estado del Ecosistema</button>
        <button className={`nav-btn ${activeTab === 'facturacion' ? 'active' : ''}`} onClick={() => setActiveTab('facturacion')}>Métricas y Facturación</button>
        <button className={`nav-btn ${activeTab === 'calculadora' ? 'active' : ''}`} onClick={() => setActiveTab('calculadora')}>Calculadora de Réditos</button>
      </aside>

      <main className="main-content">
        {activeTab === 'nodos' && <NodosTab />}
        {activeTab === 'facturacion' && <FacturacionTab />}
        {activeTab === 'calculadora' && <CalculadoraTab />}
      </main>
    </div>
  );
}