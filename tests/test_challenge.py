# tests/test_challenge.py
from src.domain.challenge import AnalyticsEngine


def test_calculate_rolling_average_success():
    scores = [10.0, 20.0, 30.0, 40.0]
    window = 2
    expected = [15.0, 25.0, 35.0]
    assert AnalyticsEngine.calculate_rolling_average(scores, window) == expected


def test_calculate_rolling_average_invalid_inputs():
    # Janela maior que os dados
    assert AnalyticsEngine.calculate_rolling_average([10.0], 2) == []
    # Janela negativa ou zero
    assert AnalyticsEngine.calculate_rolling_average([10.0, 20.0], 0) == []
    # Lista vazia
    assert AnalyticsEngine.calculate_rolling_average([], 2) == []


def test_find_critical_errors():
    mock_logs = [
        {"severity": "INFO", "error_code": "INF01"},
        {"severity": "ERROR", "error_code": "ERR01"},
        {"severity": "CRITICAL", "error_code": "ERR02"},
        {"severity": "error", "error_code": "ERR01"},  # duplicado e minúsculo
        {"severity": "WARN", "error_code": "WRN01"},
        {"severity": "CRITICAL"},  # sem error_code
    ]
    expected = {"ERR01", "ERR02"}
    assert AnalyticsEngine.find_critical_errors(mock_logs) == expected
