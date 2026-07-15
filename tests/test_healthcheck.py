"""
Tests para healthcheck.py
"""

import pytest
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


# ─── Dashboard ───

def test_dashboard_sin_logs(client):
    """Cuando no hay logs, muestra el mensaje de estado vacío (empty state)."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Aguardando telemetría" in response.text
    assert "empty-state" in response.text


def test_dashboard_con_logs(client):
    """Cuando hay logs, los muestra en la grilla con sus respectivas clases de estado."""
    LOGS_HISTORY.append({
        "time": "2026-06-15 10:00:00",
        "name": "Gateway",
        "url": "https://example.com/__health",
        "status": "OK",
        "color": "green",
    })
    LOGS_HISTORY.append({
        "time": "2026-06-15 10:00:00",
        "name": "MS Club",
        "url": "https://example.com/health",
        "status": "ERROR (502)",
        "color": "red",
    })

    response = client.get("/")
    assert response.status_code == 200
    
    # Verifica los datos insertados
    assert "Gateway" in response.text
    assert "MS Club" in response.text
    assert "OK" in response.text
    assert "ERROR (502)" in response.text
    
    # Verifica que el motor de plantillas inyectó las clases CSS correctas
    assert "status-ok" in response.text
    assert "status-error" in response.text
    assert "service-card" in response.text


def test_dashboard_html_tiene_titulo(client):
    """Verifica que los títulos y encabezados modernos estén presentes."""
    response = client.get("/")
    assert "SocioUnido" in response.text
    assert "Status Overview" in response.text


# ─── ping_loop ───

@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_ping_exitoso(mock_get, mock_sleep):
    """Cuando los servicios responden OK, loguea status OK."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == len(endpoints)
    assert all(log["status"] == "OK" for log in LOGS_HISTORY)
    assert all(log["color"] == "green" for log in LOGS_HISTORY)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_ping_error_status(mock_get, mock_sleep):
    """Cuando un servicio responde con error, loguea el status code."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 502
    mock_get.return_value = mock_response

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == len(endpoints)
    assert all("ERROR" in log["status"] for log in LOGS_HISTORY)
    assert all(log["color"] == "red" for log in LOGS_HISTORY)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_ping_excepcion(mock_get, mock_sleep):
    """Cuando la request falla (timeout/conexión), loguea FAILED."""
    import requests
    mock_get.side_effect = requests.RequestException("Connection refused")

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) == len(endpoints)
    assert all("FAILED" in log["status"] for log in LOGS_HISTORY)
    assert all(log["color"] == "orange" for log in LOGS_HISTORY)


@patch("healthcheck.time.sleep", side_effect=StopIteration)
@patch("healthcheck.requests.get")
def test_logs_no_superan_max(mock_get, mock_sleep):
    """El historial no crece más allá de MAX_LOGS."""
    # Llenamos el historial al máximo
    for i in range(MAX_LOGS):
        LOGS_HISTORY.append({"time": "", "name": f"old-{i}", "url": "", "status": "OK", "color": "green"})

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    with pytest.raises(StopIteration):
        ping_loop()

    assert len(LOGS_HISTORY) <= MAX_LOGS


# ─── Configuración ───

def test_endpoints_configurados():
    """Verifica que hay endpoints configurados para monitorear."""
    assert len(endpoints) >= 1
    for ep in endpoints:
        assert "name" in ep
        assert "url" in ep
        assert ep["url"].startswith("https://")