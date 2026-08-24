"""
Tests para healthcheck.py (Refactorizado a API JSON)
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from healthcheck import app, LOGS_HISTORY, MAX_LOGS, ping_loop, endpoints


@pytest.fixture(autouse=True)
def limpiar_logs():
    """Limpia el historial antes de cada test."""
    LOGS_HISTORY.clear()
    yield
    LOGS_HISTORY.clear()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


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


# ─── ping_loop ───

@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_ping_exitoso(mock_get, mock_sleep):
    """Cuando los servicios responden OK, el ciclo guarda status OK."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == 1
    ultimo_ciclo = LOGS_HISTORY[0]["logs"]
    assert len(ultimo_ciclo) == len(endpoints)
    assert all(log["status"] == "OK" for log in ultimo_ciclo)
    assert all(log["color"] == "green" for log in ultimo_ciclo)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_ping_error_status(mock_get, mock_sleep):
    """Cuando un servicio responde con error, el ciclo guarda el status code."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 502
    mock_get.return_value = mock_response

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == 1
    ultimo_ciclo = LOGS_HISTORY[0]["logs"]
    assert len(ultimo_ciclo) == len(endpoints)
    assert all("ERROR (502)" in log["status"] for log in ultimo_ciclo)
    assert all(log["color"] == "red" for log in ultimo_ciclo)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_ping_excepcion(mock_get, mock_sleep):
    """Cuando la request falla (timeout/conexión), el ciclo guarda FAILED."""
    mock_get.side_effect = requests.RequestException("Connection refused")

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == 1
    ultimo_ciclo = LOGS_HISTORY[0]["logs"]
    assert len(ultimo_ciclo) == len(endpoints)
    assert all("FAILED" in log["status"] for log in ultimo_ciclo)
    assert all(log["color"] == "orange" for log in ultimo_ciclo)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_logs_no_superan_max(mock_get, mock_sleep):
    """El historial (lista de ciclos) no crece más allá de MAX_LOGS."""
    # Llenamos el historial al máximo con ciclos simulados
    for i in range(MAX_LOGS):
        LOGS_HISTORY.append({"time": f"time-{i}", "logs": []})

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) <= MAX_LOGS


# ─── Configuración ───

def test_endpoints_configurados():
    """Verifica que hay endpoints configurados para monitorear con los campos correctos."""
    assert len(endpoints) >= 1
    for ep in endpoints:
        assert "name" in ep
        assert "url" in ep
        assert "type" in ep
        assert ep["url"].startswith("https://")