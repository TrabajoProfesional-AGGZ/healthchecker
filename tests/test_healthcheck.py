"""
Tests para healthcheck.py (API JSON, con la matriz por club)

Lo que se fija acá es lo que hace que el tablero siga sirviendo con N clientes: que los nodos
que se multiplican por club salgan del catálogo y no de una lista escrita a mano, que cada
fila diga de qué club es, y que un catálogo inalcanzable no deje sin monitoreo a los nodos
compartidos — que son justo los que permiten diagnosticar por qué no se pudo leer.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from healthcheck import (
    app, LOGS_HISTORY, MAX_LOGS, NODOS_COMPARTIDOS, escanear, ping_loop,
)


CLUB_ACTIVO = {
    "id": "11111111-1111-1111-1111-111111111111",
    "slug": "club-uno",
    "nombre": "Club Uno",
    "estado": "activo",
    "dominios": {"pwa_socio": "socios.uno.com", "panel_admin": "admin.uno.com"},
    "base": {"estado": "ok", "latencia_ms": 42.0, "detalle": None},
}

CLUB_PROVISIONANDO = {
    "id": "22222222-2222-2222-2222-222222222222",
    "slug": "club-dos",
    "nombre": "Club Dos",
    "estado": "provisionando",
    "dominios": {},
    "base": {"estado": "no_sondeada", "latencia_ms": None, "detalle": None},
}


@pytest.fixture(autouse=True)
def limpiar_logs():
    """Limpia el historial antes de cada test."""
    LOGS_HISTORY.clear()
    yield
    LOGS_HISTORY.clear()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def _respuesta_ok(cuerpo):
    """Una respuesta de `requests` que devuelve ese JSON."""
    respuesta = MagicMock()
    respuesta.ok = True
    respuesta.status_code = 200
    respuesta.json.return_value = cuerpo
    return respuesta


@pytest.fixture
def catalogo_con_dos_clubes():
    """`requests.get` devolviendo el inventario para el catálogo y OK para todo lo demás."""
    inventario = _respuesta_ok({"total": 2, "clubes": [CLUB_ACTIVO, CLUB_PROVISIONANDO]})

    def responder(url, **kwargs):
        if "/internos/clubes" in url:
            return inventario
        return _respuesta_ok({})

    with patch("healthcheck.requests.get", side_effect=responder) as mock_get:
        yield mock_get


# ─── API Status ───

def test_api_status_sin_logs(client):
    """Cuando no hay logs, devuelve status 'loading' y data None."""
    response = client.get("/api/status")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "loading"
    assert data["data"] is None


def test_api_status_con_logs(client):
    """Cuando hay logs, devuelve el último ciclo de escaneo en formato JSON."""
    LOGS_HISTORY.append({
        "time": "2026-08-24 10:00:00",
        "logs": [
            {
                "time": "2026-08-24 10:00:00",
                "name": "Gateway",
                "type": "Microservicio",
                "url": "https://example.com/__health",
                "club": None,
                "status": "OK",
                "color": "green",
            }
        ]
    })

    response = client.get("/api/status")
    assert response.status_code == 200

    json_resp = response.json()
    assert json_resp["status"] == "ok"
    assert json_resp["data"]["time"] == "2026-08-24 10:00:00"
    assert len(json_resp["data"]["logs"]) == 1
    assert json_resp["data"]["logs"][0]["name"] == "Gateway"
    assert json_resp["data"]["logs"][0]["type"] == "Microservicio"


# ─── Matriz por club ───

def test_los_frontends_salen_del_catalogo(catalogo_con_dos_clubes):
    """Un dominio nuevo aparece en el tablero sin tocar este repo, que es el punto.

    Antes eran tres URL de frontend escritas a mano; con N clubes eso se desactualizaba en el
    primer alta.
    """
    logs = escanear()["logs"]

    frontends = {log["name"]: log for log in logs if log["type"] == "Frontend"}
    assert set(frontends) == {
        "App SocioUnido (PWA) — Club Uno",
        "Web Admin — Club Uno",
    }
    assert frontends["Web Admin — Club Uno"]["url"] == "https://admin.uno.com/"
    assert all(log["club"] == "club-uno" for log in frontends.values())


def test_cada_club_activo_aporta_una_sonda_de_base(catalogo_con_dos_clubes):
    """En el modelo silo la base de un club es una sola para los cuatro esquemas.

    Lo que antes eran cuatro nodos de base por servicio hoy es uno por club, y la latencia
    viaja con él: con Neon suspendiendo el compute, un cold start tarda segundos y sin medirlo
    no hay forma de distinguirlo de una base que se está ahogando.
    """
    bases = {log["name"]: log for log in escanear()["logs"] if log["type"] == "Base de Datos"}

    assert bases["Base de Club Uno"]["status"] == "OK (42 ms)"
    assert bases["Base de Club Uno"]["color"] == "green"
    assert bases["Base de Club Uno"]["url"] is None, "la base de un club no es pública"


def test_un_club_que_no_esta_activo_no_se_muestra_como_caido(catalogo_con_dos_clubes):
    """`provisionando` es un estado del alta, no una falla: tiene que verse distinto."""
    bases = {log["name"]: log for log in escanear()["logs"] if log["type"] == "Base de Datos"}

    assert bases["Base de Club Dos"]["color"] == "gray"
    assert "provisionando" in bases["Base de Club Dos"]["status"]


def test_una_base_caida_se_ve_con_su_detalle():
    """El detalle es lo único que distingue 'Neon suspendido' de 'DSN rotado y no actualizado'."""
    club = {**CLUB_ACTIVO, "base": {"estado": "error", "latencia_ms": None,
                                    "detalle": "connection refused"}}
    with patch("healthcheck.requests.get",
               return_value=_respuesta_ok({"clubes": [club]})):
        bases = [log for log in escanear()["logs"] if log["type"] == "Base de Datos"]

    assert bases[0]["color"] == "red"
    assert "connection refused" in bases[0]["status"]


def test_el_catalogo_se_pide_con_el_secreto_interno_y_sondeando(catalogo_con_dos_clubes):
    """Sin el secreto, ms-autenticacion falla cerrado y el tablero se queda sin clubes."""
    escanear()

    llamada = next(c for c in catalogo_con_dos_clubes.call_args_list
                   if "/internos/clubes" in c.args[0])
    assert llamada.kwargs["params"] == {"sondear": "true"}
    assert "X-Internal-Secret" in llamada.kwargs["headers"]


def test_sin_catalogo_siguen_monitoreandose_los_nodos_compartidos():
    """Hacer caer el ciclo entero dejaría sin monitoreo justo a los nodos que permiten
    diagnosticar por qué el catálogo no se pudo leer."""
    def responder(url, **kwargs):
        if "/internos/clubes" in url:
            raise requests.RequestException("timeout")
        return _respuesta_ok({})

    with patch("healthcheck.requests.get", side_effect=responder):
        logs = escanear()["logs"]

    catalogo = next(log for log in logs if log["name"].startswith("Catálogo"))
    assert catalogo["color"] == "red"
    assert len(logs) == 1 + len(NODOS_COMPARTIDOS), "el pool compartido se pinguea igual"


def test_los_nodos_compartidos_no_llevan_club(catalogo_con_dos_clubes):
    """El pool de cómputo es el mismo para todos los clientes: no se multiplica por club."""
    logs = escanear()["logs"]

    compartidos = [log for log in logs if log["name"] in {n["name"] for n in NODOS_COMPARTIDOS}]
    assert len(compartidos) == len(NODOS_COMPARTIDOS)
    assert all(log["club"] is None for log in compartidos)


# ─── ping_loop ───

@patch("healthcheck.time.sleep", side_effect=StopIteration)
def test_ping_exitoso(mock_sleep, catalogo_con_dos_clubes):
    """Cuando los servicios responden OK, el ciclo guarda status OK."""
    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == 1
    pingueados = [log for log in LOGS_HISTORY[0]["logs"] if log["url"]]
    assert all(log["status"].startswith("OK") for log in pingueados)
    assert all(log["color"] == "green" for log in pingueados)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
def test_ping_error_status(mock_sleep):
    """Cuando un servicio responde con error, el ciclo guarda el status code."""
    respuesta = MagicMock()
    respuesta.ok = False
    respuesta.status_code = 502
    respuesta.raise_for_status.side_effect = requests.RequestException("502")

    with patch("healthcheck.requests.get", return_value=respuesta), pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == 1
    compartidos = [log for log in LOGS_HISTORY[0]["logs"]
                   if log["name"] in {n["name"] for n in NODOS_COMPARTIDOS}]
    assert len(compartidos) == len(NODOS_COMPARTIDOS)
    assert all("ERROR (502)" in log["status"] for log in compartidos)
    assert all(log["color"] == "red" for log in compartidos)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get", side_effect=requests.RequestException("Connection refused"))
def test_ping_excepcion(mock_get, mock_sleep):
    """Cuando la request falla (timeout/conexión), el ciclo guarda FAILED."""
    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == 1
    compartidos = [log for log in LOGS_HISTORY[0]["logs"]
                   if log["name"] in {n["name"] for n in NODOS_COMPARTIDOS}]
    assert all("FAILED" in log["status"] for log in compartidos)
    assert all(log["color"] == "orange" for log in compartidos)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
def test_logs_no_superan_max(mock_sleep, catalogo_con_dos_clubes):
    """El historial (lista de ciclos) no crece más allá de MAX_LOGS."""
    for i in range(MAX_LOGS):
        LOGS_HISTORY.append({"time": f"time-{i}", "logs": []})

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) <= MAX_LOGS


# ─── Configuración ───

def test_nodos_compartidos_configurados():
    """Verifica que los nodos del pool de cómputo tienen los campos correctos."""
    assert len(NODOS_COMPARTIDOS) >= 1
    for nodo in NODOS_COMPARTIDOS:
        assert "name" in nodo
        assert "url" in nodo
        assert "type" in nodo
        assert nodo["url"].startswith("https://")
