# src/domain/challenge.py
type ScoreList = list[float]


class AnalyticsEngine:
    """Motor de processamento de métricas purista em Python."""

    @staticmethod
    def calculate_rolling_average(scores: ScoreList, window_size: int) -> ScoreList:
        """
        Calcula a média móvel de scores em janelas completas de tamanho window_size.

        Exemplo:
            scores = [10.0, 20.0, 30.0, 40.0], window_size = 2
            Retorno: [15.0, 25.0, 35.0] (médias de [10,20], [20,30], [30,40])
        """
        if not scores or window_size <= 0 or window_size > len(scores):
            return []

        averages = []
        # Percorre a lista até o ponto onde ainda é possível formar uma janela completa
        for i in range(len(scores) - window_size + 1):
            window = scores[i : i + window_size]
            window_average = sum(window) / window_size
            averages.append(round(window_average, 2))
        return averages

    @staticmethod
    def find_critical_errors(logs: list[dict[str, str]]) -> set[str]:
        """
        Varre logs e extrai os códigos de erro ('error_code') únicos
        onde a severidade ('severity') seja 'ERROR' ou 'CRITICAL'.
        """
        critical_codes = set()
        for log in logs:
            severity = log.get("severity", "").upper()
            error_code = log.get("error_code")

            if severity in ("ERROR", "CRITICAL") and error_code:
                critical_codes.add(error_code)

        return critical_codes
