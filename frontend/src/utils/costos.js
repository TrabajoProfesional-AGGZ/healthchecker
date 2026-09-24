/**
 * Modelo de costos y precios de SocioUnido.
 *
 * Reemplaza a la planilla `Costos-funcionamiento.xlsx`, que queda como catálogo histórico.
 * Los precios de `PRECIOS` se verificaron contra las páginas oficiales de cada proveedor en
 * septiembre de 2026; cada entrada lleva la fuente para poder re-chequearla.
 *
 * Correcciones respecto de la planilla original:
 *  - Neon dejó de tener plan fijo (eran USD 19 / USD 69): hoy es pago por uso sin mínimo, así
 *    que el costo de base se calcula por club a partir de horas-CU y GB, que es lo que
 *    corresponde con una base por club.
 *  - El dominio de cada club se prorratea (precio anual sobre 12) y se multiplica por la
 *    cantidad de clubes. En la planilla se sumaba entero y una sola vez, sin importar cuántos
 *    clubes hubiera.
 *  - Vercel cobra USD 20 de plataforma que ya incluyen un asiento con permiso de deploy; sólo
 *    los asientos adicionales valen USD 20. Los asientos de sólo lectura son gratis.
 *  - Google Workspace Business Starter vale USD 7 por usuario, no USD 4 ni USD 5.
 *  - Firebase se calcula por tramos de usuarios activos mensuales en vez de asumirse en cero.
 *  - Se incorporan partidas que la planilla no tenía: ancho de banda y minutos de build de
 *    Render, Redis (Render Key Value), impuestos sobre compras en dólares y sobre la venta.
 */

/** Catálogo de precios de los proveedores, en dólares. */
export const PRECIOS = {
  // https://render.com/pricing (verificado 2026-09)
  render: {
    workspace: { hobby: 0, pro: 25, scale: 499 },
    computo: { starter: 7, standard: 25, pro: 85 },
    keyValue: { gratis: 0, '256mb': 10, '1gb': 32, '5gb': 135 },
    anchoDeBandaIncluidoGb: 5,
    anchoDeBandaUsdPorGb: 0.15,
    dominiosIncluidos: 2,
    dominioUsdPorMes: 0.25,
    minutosBuildIncluidos: 500,
    usdPorMilMinutosBuild: 5,
  },
  // https://neon.com/docs/introduction/plans (verificado 2026-09): pago por uso, sin plan fijo.
  neon: {
    launch: { usdPorCuHora: 0.106 },
    scale: { usdPorCuHora: 0.222 },
    usdPorGbMes: 0.35,
  },
  // https://cloud.google.com/identity-platform/pricing (verificado 2026-09)
  firebase: {
    tramosUam: [
      { hasta: 50000, usdPorUam: 0 },
      { hasta: 100000, usdPorUam: 0.0055 },
      { hasta: 1000000, usdPorUam: 0.0046 },
      { hasta: 10000000, usdPorUam: 0.0032 },
      { hasta: Infinity, usdPorUam: 0.0025 },
    ],
    usdPorSmsArgentina: 0.09,
  },
  // https://vercel.com/docs/plans/pro-plan (verificado 2026-09)
  vercel: { plataforma: 20, asientoAdicional: 20 },
  // https://cloudinary.com/pricing (verificado 2026-09)
  cloudinary: { free: 0, plus: 89, advanced: 224 },
  // https://workspace.google.com/pricing (verificado 2026-09), Business Starter sin promoción.
  workspace: { usdPorUsuario: 7 },
  // Cloudflare Registrar vende a costo; un .com ronda los USD 10,5 anuales.
  dominioUsdPorAnio: 10.5,
};

/** Etiquetas de los planes que se eligen desde la interfaz. */
export const OPCIONES = {
  neon: [
    { valor: 'launch', etiqueta: 'Launch (USD 0,106 por CU-hora)' },
    { valor: 'scale', etiqueta: 'Scale (USD 0,222 por CU-hora)' },
  ],
  cloudinary: [
    { valor: 'free', etiqueta: 'Free, 25 créditos' },
    { valor: 'plus', etiqueta: 'Plus, 225 créditos (USD 89)' },
    { valor: 'advanced', etiqueta: 'Advanced, 600 créditos (USD 224)' },
  ],
  keyValue: [
    { valor: 'gratis', etiqueta: 'Free, 25 MB' },
    { valor: '256mb', etiqueta: '256 MB (USD 10)' },
    { valor: '1gb', etiqueta: '1 GB (USD 32)' },
    { valor: '5gb', etiqueta: '5 GB (USD 135)' },
  ],
};

/**
 * El costo mensual de Firebase Authentication para una cantidad de usuarios activos,
 * aplicando los tramos de precio de Identity Platform de forma acumulativa.
 *
 * @param {number} uam Usuarios activos mensuales.
 * @returns {number} Costo mensual en dólares.
 */
export function costoFirebase(uam) {
  let piso = 0;
  let total = 0;

  for (const tramo of PRECIOS.firebase.tramosUam) {
    const enElTramo = Math.max(0, Math.min(uam, tramo.hasta) - piso);
    total += enElTramo * tramo.usdPorUam;
    piso = tramo.hasta;
    if (uam <= tramo.hasta) break;
  }

  return total;
}

/**
 * El desglose del costo mensual de un tier, partida por partida y en dólares.
 *
 * @param {object} tier Parámetros del escenario.
 * @param {object} globales Parámetros que no dependen del tier.
 * @returns {{partidas: Array<object>, subtotal: number, impuestos: number, total: number}}
 */
export function desglosarCosto(tier, globales) {
  const render = PRECIOS.render;

  const computoRender =
    tier.serviciosStarter * render.computo.starter +
    tier.serviciosStandard * render.computo.standard +
    tier.serviciosPro * render.computo.pro;

  const excedenteAnchoDeBanda =
    Math.max(0, tier.anchoDeBandaGb - render.anchoDeBandaIncluidoGb) * render.anchoDeBandaUsdPorGb;

  const excedenteDominiosRender =
    Math.max(0, globales.dominiosEnRender - render.dominiosIncluidos) * render.dominioUsdPorMes;

  const excedenteBuilds =
    (Math.max(0, globales.minutosBuild - render.minutosBuildIncluidos) / 1000) *
    render.usdPorMilMinutosBuild;

  // Con una base por club, Neon se paga por uso: las horas de cómputo y los GB se multiplican
  // por la cantidad de clubes. Un club inactivo escala a cero y no suma horas.
  const neon =
    tier.clubes *
    (tier.cuHorasPorClub * PRECIOS.neon[tier.planNeon].usdPorCuHora +
      tier.gbPorClub * PRECIOS.neon.usdPorGbMes);

  // Vercel: la tarifa de plataforma ya trae un asiento con permiso de deploy.
  const vercel =
    PRECIOS.vercel.plataforma +
    Math.max(0, globales.asientosVercel - 1) * PRECIOS.vercel.asientoAdicional;

  const partidas = [
    { clave: 'renderWorkspace', etiqueta: 'Render, workspace', usd: globales.renderWorkspace },
    { clave: 'renderComputo', etiqueta: 'Render, cómputo de servicios', usd: computoRender },
    { clave: 'renderAnchoDeBanda', etiqueta: 'Render, ancho de banda excedente', usd: excedenteAnchoDeBanda },
    { clave: 'renderDominios', etiqueta: 'Render, dominios excedentes', usd: excedenteDominiosRender },
    { clave: 'renderBuilds', etiqueta: 'Render, minutos de build excedentes', usd: excedenteBuilds },
    { clave: 'keyValue', etiqueta: 'Render Key Value (Redis)', usd: render.keyValue[tier.planKeyValue] },
    { clave: 'neon', etiqueta: 'Neon, ' + tier.clubes + ' bases por uso', usd: neon },
    { clave: 'cloudinary', etiqueta: 'Cloudinary', usd: PRECIOS.cloudinary[tier.planCloudinary] },
    { clave: 'firebase', etiqueta: 'Firebase Auth, ' + tier.uam.toLocaleString('es-AR') + ' UAM', usd: costoFirebase(tier.uam) },
    { clave: 'vercel', etiqueta: 'Vercel', usd: vercel },
    { clave: 'workspace', etiqueta: 'Google Workspace', usd: globales.cuentasWorkspace * PRECIOS.workspace.usdPorUsuario },
    { clave: 'dominioCentral', etiqueta: 'Dominio sociounido.com (prorrateado)', usd: globales.dominioCentralAnual / 12 },
    { clave: 'dominiosClubes', etiqueta: 'Dominios de club (' + tier.clubes + ', prorrateados)', usd: (tier.clubes * PRECIOS.dominioUsdPorAnio) / 12 },
    { clave: 'manoDeObra', etiqueta: 'Mano de obra (' + globales.equipo + ' por USD ' + tier.trabajoPorDesarrollador + ')', usd: globales.equipo * tier.trabajoPorDesarrollador },
    { clave: 'extras', etiqueta: 'Extras', usd: tier.extras },
  ];

  const subtotal = partidas.reduce((acc, partida) => acc + partida.usd, 0);
  // Toda la infraestructura se paga en dólares con tarjeta argentina: las percepciones e
  // impuestos sobre servicios digitales del exterior encarecen cada factura.
  const impuestos = subtotal * (globales.impuestoCompras / 100);

  return { partidas, subtotal, impuestos, total: subtotal + impuestos };
}

/**
 * La proyección financiera de un tier: la cuota que hay que cobrarle a cada club para sostener
 * el costo con la contingencia y el margen buscados, y el resultado que deja.
 *
 * La cuota se calcula como en la planilla (costo por club, por contingencia y por margen) con
 * dos correcciones. El setup de cada club es un gasto por única vez, así que se amortiza en un
 * plazo en vez de cobrarse todos los meses para siempre, que es lo que hacía la planilla. Y se
 * inflan los impuestos que no se le trasladan al club, porque si no se los incorpora al precio
 * el margen que queda es menor al buscado.
 *
 * @param {object} tier Parámetros del escenario.
 * @param {object} globales Parámetros que no dependen del tier.
 * @returns {object} Costos, cuota, ingresos, ganancia y meses hasta recuperar la inversión.
 */
export function proyectar(tier, globales) {
  const costo = desglosarCosto(tier, globales);
  const clubes = Math.max(1, tier.clubes);
  const mesesAmortizacion = Math.max(1, globales.mesesAmortizacionSetup);

  const alicuotaVentas = Math.min(0.95, globales.impuestoVentas / 100);
  const cuotaPorClub =
    ((costo.total / clubes + tier.setupPorClub / mesesAmortizacion) *
      globales.contingencia *
      globales.margen) /
    (1 - alicuotaVentas);

  const ingresosBrutos = cuotaPorClub * clubes;
  const impuestosVenta = ingresosBrutos * alicuotaVentas;
  const ingresosNetos = ingresosBrutos - impuestosVenta;
  const ganancia = ingresosNetos - costo.total;

  // La planilla dividía sólo la ganancia por la cantidad de integrantes y olvidaba que el
  // "trabajo por desarrollador" ya está adentro del costo: cada persona se lleva las dos cosas.
  const equipo = Math.max(1, globales.equipo);
  const gananciaPorPersona = ganancia / equipo;
  const retiroPorPersona = gananciaPorPersona + tier.trabajoPorDesarrollador;

  // Lo que hay que recuperar antes de ganar plata: el setup de cada club, que se paga una sola
  // vez, más los meses de prueba gratis, en los que se sostiene todo el costo sin facturar.
  const inversionInicial = clubes * tier.setupPorClub + costo.total * globales.mesesPrueba;

  let mesesHastaGanar = 'Nunca';
  if (ganancia > 0) {
    mesesHastaGanar = globales.mesesPrueba + Math.ceil(inversionInicial / ganancia);
  }

  return {
    costo,
    cuotaPorClub,
    costoPorClub: costo.total / clubes,
    ingresosBrutos,
    impuestosVenta,
    ingresosNetos,
    ganancia,
    gananciaPorPersona,
    retiroPorPersona,
    inversionInicial,
    mesesHastaGanar,
  };
}

/** Los cuatro escenarios de la planilla, con los valores ya corregidos. */
export const TIERS_INICIALES = [
  {
    id: 1,
    nombre: 'Tier 1 (menos de 10k socios)',
    clubes: 3,
    serviciosStarter: 8,
    serviciosStandard: 0,
    serviciosPro: 0,
    planNeon: 'launch',
    cuHorasPorClub: 90,
    gbPorClub: 2,
    planCloudinary: 'free',
    planKeyValue: '256mb',
    uam: 8000,
    anchoDeBandaGb: 20,
    trabajoPorDesarrollador: 100,
    setupPorClub: 0,
    extras: 0,
  },
  {
    id: 2,
    nombre: 'Tier 2 (10k a 20k socios)',
    clubes: 6,
    serviciosStarter: 7,
    serviciosStandard: 1,
    serviciosPro: 0,
    planNeon: 'launch',
    cuHorasPorClub: 120,
    gbPorClub: 3,
    planCloudinary: 'free',
    planKeyValue: '256mb',
    uam: 18000,
    anchoDeBandaGb: 45,
    trabajoPorDesarrollador: 150,
    setupPorClub: 200,
    extras: 0,
  },
  {
    id: 3,
    nombre: 'Tier 3 (20k a 50k socios)',
    clubes: 15,
    serviciosStarter: 6,
    serviciosStandard: 2,
    serviciosPro: 0,
    planNeon: 'launch',
    cuHorasPorClub: 150,
    gbPorClub: 4,
    planCloudinary: 'plus',
    planKeyValue: '1gb',
    uam: 45000,
    anchoDeBandaGb: 110,
    trabajoPorDesarrollador: 250,
    setupPorClub: 400,
    extras: 0,
  },
  {
    id: 4,
    nombre: 'Tier 4 (unos 100k socios)',
    clubes: 30,
    serviciosStarter: 2,
    serviciosStandard: 4,
    serviciosPro: 2,
    planNeon: 'scale',
    cuHorasPorClub: 200,
    gbPorClub: 6,
    planCloudinary: 'plus',
    planKeyValue: '1gb',
    uam: 100000,
    anchoDeBandaGb: 260,
    trabajoPorDesarrollador: 450,
    setupPorClub: 600,
    extras: 0,
  },
];

/** Parámetros que no dependen del escenario elegido. */
export const GLOBALES_INICIALES = {
  tierActivo: 1,
  dolar: 1500,
  equipo: 4,
  mesesPrueba: 1,
  contingencia: 1.1,
  margen: 1.2,
  mesesAmortizacionSetup: 12,
  // Percepciones y recargos sobre los gastos en dólares pagados con tarjeta argentina.
  impuestoCompras: 30,
  // Sólo los impuestos que no se le trasladan al club: Ingresos Brutos y similares. El IVA se
  // le factura aparte al club, así que por defecto no entra acá.
  impuestoVentas: 5,
  renderWorkspace: PRECIOS.render.workspace.pro,
  asientosVercel: 4,
  cuentasWorkspace: 4,
  dominioCentralAnual: 11,
  dominiosEnRender: 2,
  minutosBuild: 400,
};
