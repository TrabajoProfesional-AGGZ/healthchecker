---
layout: default
title: Endpoints
nav_order: 2
---

# 🔌 Endpoints

En esta sección se listan los endpoints disponibles en el healthchecker.

Esta página sirve como referencia estática para garantizar el acceso a los contratos de la API de forma rápida y clara.

## 🔒 Autenticación

El healthchecker **no expone ninguna ruta autenticada**: lo único que publica es el resultado
del último escaneo, que es el mismo estado que cualquiera puede deducir pinguendo los servicios
uno por uno. El frontend lo consume desde el navegador con CORS abierto.

Hacia adentro sí necesita un secreto: consulta el catálogo de clubes con
`X-Internal-Secret`, igual que cualquier llamada entre servicios del proyecto.

## 🏟️ De dónde sale la matriz de monitoreo

La lista de nodos ya **no** está escrita a mano. Se arma en cada ciclo, y tiene dos partes que
escalan distinto:

| Parte | De dónde sale | Cómo crece |
| --- | --- | --- |
| **Pool de cómputo** (gateway + 7 microservicios) | `NODOS_COMPARTIDOS` en `healthcheck.py` | No crece: son los mismos servicios de Render para todos los clubes |
| **Frontends por club** | `club_dominios` del catálogo, vía `GET /api/v1/internos/clubes` en `microservicio-autenticacion` | Tres dominios por club dado de alta |
| **Base por club** | El sondeo que hace ms-autenticacion con `?sondear=true` | Una sonda por club: en el modelo silo, los cuatro esquemas viven en la misma base |

Dar de alta un club lo agrega al tablero **sin tocar este repo ni redeployarlo**, que es el
mismo principio por el que la conexión de un club salió de `DATABASE_URL`.

El catálogo se pide por HTTP a su dueño y no abriendo la base del control plane: por ese otro
camino este servicio necesitaría la `TENANT_DSN_KEY`, y no hay ninguna razón para dársela a un
servicio que sólo quiere saber qué clubes existen. El sondeo de cada base corre del lado de
ms-autenticacion y vuelve resuelto.

### Lo que dejó de monitorearse, y por qué

Los cuatro nodos de tipo *Base de Datos* que había antes apuntaban a `/health/db`,
`/health/firebase` y `/health/redis`: **rutas que no existen en ninguno de los
microservicios**, así que el tablero venía informando cuatro 404 como si fueran caídas. Dos de
ellos apuntaban además a hosts de Render distintos de los de su propio microservicio
(`microservicio-club.onrender.com` contra `microservicio-club-pm6o`,
`microservicio-autenticacion-sdy6` contra `-lo4w`).

Las bases las reemplaza la sonda por club. **Redis y Firebase quedan sin monitorear** hasta que
tengan un endpoint de salud de verdad en `microservicio-analiticas` y en
`microservicio-autenticacion`: es una deuda conocida, no un olvido.

## ⚙️ Variables de entorno

| Variable | Para qué |
| --- | --- |
| `PORT` | Puerto en el que escucha la API (por defecto 8000) |
| `MS_AUTH_URL` | Base de `microservicio-autenticacion` en Render. Se le pega **directo**, sin pasar por el gateway: el monitoreo tiene que seguir funcionando justamente cuando el gateway es el que está caído |
| `INTERNAL_SECRET_TOKEN` | El mismo secreto interno que comparten los siete servicios. Sin él, ms-autenticacion responde 503 y el tablero queda sin la parte por club |

## Listado de Endpoints

A continuación, haz clic en cada bloque para desplegar los detalles de la petición, parámetros y respuestas.

<details>
  <summary style="font-size: 1.1em; cursor: pointer; padding: 10px; background-color: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff; margin-bottom: 5px;">
    <strong style="color: #007bff;">GET</strong> <code>/api/status</code> - Último escaneo
  </summary>
  <div style="padding: 15px; border: 1px solid #f8f9fa; border-top: none; margin-bottom: 20px;">

    <p><strong>ID de la Operación:</strong> <code>get_status_api_status_get</code></p>

    <p>Devuelve el resultado del último ciclo de monitoreo. El ciclo corre en un hilo de fondo cada 60 segundos y el historial guarda los últimos 30; este endpoint expone sólo el más reciente.</p>

    <h3>Respuestas</h3>

    <p><strong>Código:</strong> <code>200 OK</code> — todavía no corrió ningún ciclo</p>

    <div class="language-json highlighter-rouge"><div class="highlight"><pre class="highlight"><code>{ "status": "loading", "data": null }
</code></pre></div></div>

    <p><strong>Código:</strong> <code>200 OK</code> — con un escaneo hecho</p>

    <div class="language-json highlighter-rouge"><div class="highlight"><pre class="highlight"><code>{
  "status": "ok",
  "data": {
    "time": "2026-09-22 03:00:00",
    "logs": [
      {
        "time": "2026-09-22 03:00:00",
        "name": "Catálogo de clubes (control plane)",
        "type": "Microservicio",
        "url": "https://microservicio-autenticacion-lo4w.onrender.com/api/v1/internos/clubes",
        "club": null,
        "status": "OK (2 club/es)",
        "color": "green"
      },
      {
        "time": "2026-09-22 03:00:00",
        "name": "Web Admin — Club Uno",
        "type": "Frontend",
        "url": "https://admin.uno.com/",
        "club": "club-uno",
        "status": "OK",
        "color": "green"
      },
      {
        "time": "2026-09-22 03:00:00",
        "name": "Base de Club Uno",
        "type": "Base de Datos",
        "url": null,
        "club": "club-uno",
        "status": "OK (42 ms)",
        "color": "green"
      }
    ]
  }
}
</code></pre></div></div>

    <h3>Campos de cada fila</h3>
    <ul>
      <li><code>club</code> — el slug del club al que pertenece el nodo, o <code>null</code> si es del pool compartido. Es lo que agrupa el tablero.</li>
      <li><code>url</code> — <code>null</code> en las filas de base: la base de un club no es pública y no hay nada que un operador pueda abrir en el navegador.</li>
      <li><code>color</code> — <code>green</code> (sano), <code>red</code> (respondió con error), <code>orange</code> (no respondió) y <code>gray</code> (no se sondeó). <strong><code>gray</code> no es una caída</strong>: es el club en <code>provisionando</code> o <code>suspendido</code>, que no atiende tráfico y por eso no se le abre la base. Confundirlo con rojo haría que un alta a medio terminar se vea como una base caída.</li>
      <li><code>status</code> — el texto que se muestra. En las bases incluye la latencia del sondeo: con Neon suspendiendo el compute por inactividad, un cold start tarda segundos y eso es normal; lo que no es normal es que tarde dos ciclos seguidos.</li>
    </ul>

  </div>
</details>
