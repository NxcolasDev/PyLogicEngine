# src/main.py
import sys
from src.domain.challenge import AnalyticsEngine


def show_banner() -> None:
    """Exibe o header no estilo terminal/hacker."""
    print("=" * 60)
    print("      PYLOGIC ENGINE - CLI & CLOUD ANALYTICS v1.0      ")
    print("=" * 60)
    print("[ System Ready | Pure Python Mode Active ]\n")


def run_scores_demo() -> None:
    print("\n--- [1] Teste de Média Móvel (Rolling Average) ---")
    raw_input = input("Digite uma lista de pontuações separadas por vírgula (ex: 10,20,30,40): ")
    try:
        scores = [float(x.strip()) for x in raw_input.split(",") if x.strip()]
        window = int(input("Digite o tamanho da janela (window_size): "))
        
        result = AnalyticsEngine.calculate_rolling_average(scores, window)
        print(f"\n[Resultado] Médias Móveis: {result}")
    except ValueError:
        print("\n[Erro] Entrada inválida. Certifique-se de digitar números válidos.")


def run_logs_demo() -> None:
    print("\n--- [2] Teste de Varredura de Logs Críticos ---")
    mock_logs = [
        {"severity": "INFO", "error_code": "INF_01"},
        {"severity": "ERROR", "error_code": "ERR_DATABASE_TIMEOUT"},
        {"severity": "CRITICAL", "error_code": "ERR_AUTH_FAILURE"},
        {"severity": "WARN", "error_code": "WRN_DEPRECATED_API"},
    ]
    print("Analisando lote de logs de exemplo...")
    criticals = AnalyticsEngine.find_critical_errors(mock_logs)
    print(f"\n[Resultado] Códigos Críticos Encontrados: {criticals}")


def main() -> None:
    show_banner()
    while True:
        print("\nMenu Principal:")
        print("1. Executar Média Móvel")
        print("2. Simular Varredura de Logs Críticos")
        print("3. Sair")
        
        choice = input("\nEscolha uma opção (1-3): ").strip()
        
        if choice == "1":
            run_scores_demo()
        elif choice == "2":
            run_logs_demo()
        elif choice == "3":
            print("\nFinalizando PyLogic Engine. Até logo!")
            sys.exit(0)
        else:
            print("\nOpção inválida! Tente novamente.")


if __name__ == "__main__":
    main()