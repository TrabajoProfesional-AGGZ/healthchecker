---
layout: default
title: Endpoints
nav_order: 2
---

# 🔌 Endpoints

En esta sección se listan los endpoints disponibles en el healthchecker.

Esta página sirve como referencia estática para garantizar el acceso a los contratos de la API de forma rápida y clara.

## Listado de Endpoints

A continuación, haz clic en cada bloque para desplegar los detalles de la petición, parámetros y respuestas.

<details>
  <summary style="font-size: 1.1em; cursor: pointer; padding: 10px; background-color: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff; margin-bottom: 5px;">
    <strong style="color: #007bff;">GET</strong> <code>/</code> - Get Dashboard
  </summary>
  <div style="padding: 15px; border: 1px solid #f8f9fa; border-top: none; margin-bottom: 20px;">
    
    <p><strong>ID de la Operación:</strong> <code>get_dashboard__get</code></p>
    
    <p>Este endpoint retorna la interfaz gráfica principal (dashboard) del HealthChecker, donde se puede visualizar el estado de salud y la auditoría de los microservicios.</p>

    <h3>Respuestas</h3>

    <p><strong>Código:</strong> <code>200 OK</code></p>
    <ul>
      <li><strong>Descripción:</strong> Successful Response</li>
      <li><strong>Content-Type:</strong> <code>text/html</code></li>
    </ul>

    <strong>Formato de respuesta:</strong>
    <div class="language-text highlighter-rouge"><div class="highlight"><pre class="highlight"><code>string (Documento HTML)
</code></pre></div></div>

  </div>
</details>
