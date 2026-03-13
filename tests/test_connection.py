"""
test_connection.py – Conexión, API key y manejo de errores de red.

Cubre:
    - Crear cliente con key válida
    - Error cuando no hay key
    - Key desde environment variable
    - Timeout / servidor no responde
    - Error HTTP 4xx y 5xx
    - Reintentos (retry)
    - Context manager (__enter__ / __exit__)
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests

from iniamet import INIAClient
from iniamet.api_client import APIClient


# ========================================================================
# 1. API Key
# ========================================================================

class TestAPIKey:
    """Tests de configuración de API key."""

    def test_client_con_key_directa(self):
        """Se puede crear un cliente pasando la key directamente."""
        client = INIAClient(api_key="mi-key-valida", cache=False)
        assert client.api.api_key == "mi-key-valida"

    def test_client_sin_key_ni_env_falla(self):
        """Sin key ni variable de entorno ni config → ValueError."""
        env_backup = os.environ.pop("INIA_API_KEY", None)
        try:
            # Also mock config file so it doesn't find a key there
            with patch("iniamet.api_client.Path.home", return_value=Path("/nonexistent_dir")):
                with pytest.raises(ValueError, match="No API key"):
                    INIAClient(api_key=None, cache=False)
        finally:
            if env_backup:
                os.environ["INIA_API_KEY"] = env_backup

    def test_client_lee_key_de_env(self):
        """Si no se pasa key pero existe INIA_API_KEY env → la usa."""
        os.environ["INIA_API_KEY"] = "env-key-123"
        try:
            client = INIAClient(cache=False)
            assert client.api.api_key == "env-key-123"
        finally:
            os.environ["INIA_API_KEY"] = "test-api-key-for-ci"

    def test_key_directa_tiene_prioridad_sobre_env(self):
        """Key pasada directamente tiene prioridad sobre env."""
        os.environ["INIA_API_KEY"] = "env-key"
        try:
            client = INIAClient(api_key="directa", cache=False)
            assert client.api.api_key == "directa"
        finally:
            os.environ["INIA_API_KEY"] = "test-api-key-for-ci"


# ========================================================================
# 2. Errores de red / servidor
# ========================================================================

class TestConexionRed:
    """Tests de manejo de errores de red."""

    def test_timeout_retorna_none(self):
        """Si la API no responde (timeout), _request retorna None."""
        api = APIClient(api_key="fake", timeout=1)
        with patch.object(api.session, "get", side_effect=requests.exceptions.Timeout("timeout")):
            result = api._request("estaciones", retry=1)
        assert result is None

    def test_conexion_rechazada_retorna_none(self):
        """ConnectionError → retorna None después de reintentos."""
        api = APIClient(api_key="fake", timeout=1)
        with patch.object(api.session, "get", side_effect=requests.exceptions.ConnectionError("refused")):
            result = api._request("estaciones", retry=1)
        assert result is None

    def test_error_500_reintenta(self):
        """Error 500 (servidor) → reintenta y finalmente retorna None."""
        api = APIClient(api_key="fake", timeout=1)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        with patch.object(api.session, "get", return_value=mock_response):
            with patch("time.sleep"):  # no esperar en tests
                result = api._request("estaciones", retry=2)
        assert result is None

    def test_error_403_no_reintenta(self):
        """Error 403 (cliente) → NO reintenta, retorna None directamente."""
        api = APIClient(api_key="fake", timeout=1)
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        call_count = 0
        original_get = api.session.get

        def counting_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response

        with patch.object(api.session, "get", side_effect=counting_get):
            result = api._request("estaciones", retry=3)
        assert result is None
        assert call_count == 1  # solo 1 intento, no 3

    def test_error_404_no_reintenta(self):
        """Error 404 → no reintenta."""
        api = APIClient(api_key="fake", timeout=1)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        with patch.object(api.session, "get", return_value=mock_response):
            result = api._request("estaciones", retry=3)
        assert result is None

    def test_json_invalido_retorna_none(self):
        """Si la respuesta no es JSON válido → retorna None."""
        api = APIClient(api_key="fake", timeout=1)
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "<html>not json</html>"
        with patch.object(api.session, "get", return_value=mock_response):
            result = api._request("estaciones")
        assert result is None


# ========================================================================
# 3. Context manager
# ========================================================================

class TestContextManager:
    """Tests del context manager (with)."""

    def test_context_manager_abre_y_cierra(self):
        """INIAClient funciona como context manager."""
        with INIAClient(api_key="fake", cache=False) as client:
            assert client is not None
            assert hasattr(client, "get_stations")
        # después de salir del with, la sesión se cierra
        # (no debe lanzar error)

    def test_api_client_context_manager(self):
        """APIClient también funciona como context manager."""
        with APIClient(api_key="fake") as api:
            assert api.api_key == "fake"


# ========================================================================
# 4. Respuesta de la API "wrapping"
# ========================================================================

class TestAPIResponse:
    """Tests del parseo de respuesta de la API."""

    def test_respuesta_con_wrapper_response(self):
        """API devuelve {'response': [...]} → extrae la lista."""
        api = APIClient(api_key="fake")
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"response": [{"id": 1}]}
        with patch.object(api.session, "get", return_value=mock_response):
            result = api._request("test")
        assert result == [{"id": 1}]

    def test_respuesta_sin_wrapper(self):
        """API devuelve lista directa → la retorna tal cual."""
        api = APIClient(api_key="fake")
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{"id": 1}]
        with patch.object(api.session, "get", return_value=mock_response):
            result = api._request("test")
        assert result == [{"id": 1}]

    def test_api_retorna_string_error(self):
        """Si la API retorna un string en vez de lista → get_stations retorna []."""
        api = APIClient(api_key="fake")
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"response": "Error: key inválida"}
        with patch.object(api.session, "get", return_value=mock_response):
            result = api.get_stations()
        assert result == []
