import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from adaptive_chess.analysis.charts import generate_experiment_charts


def parse_args() -> argparse.Namespace:
    """
    Parsuje argumenty przekazane z terminala.

    Returns:
        Konfiguracja generowania wykresów.
    """
    parser = argparse.ArgumentParser(
        description="Generate charts from chess experiment results CSV."
    )

    parser.add_argument(
        "--input-csv",
        type=str,
        required=True,
        help="Path to input CSV with match results.",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/charts",
        help="Directory for generated PNG charts.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Generuje wykresy PNG na podstawie CSV z wynikami eksperymentów.
    """
    args = parse_args()

    chart_paths = generate_experiment_charts(
        input_csv_path=args.input_csv,
        output_dir=args.output_dir,
    )

    if not chart_paths:
        print("CSV nie zawiera danych. Nie wygenerowano wykresów.")
        return

    print("Wygenerowano wykresy:")

    for chart_path in chart_paths:
        print(f"- {chart_path}")


if __name__ == "__main__":
    main()