import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from adaptive_chess.analysis.csv_report import analyze_results_csv


def parse_args() -> argparse.Namespace:
    """
    Parsuje argumenty przekazane z terminala.

    Returns:
        Konfiguracja analizy CSV.
    """
    parser = argparse.ArgumentParser(
        description="Analyze chess experiment results exported to CSV."
    )

    parser.add_argument(
        "--input-csv",
        type=str,
        required=True,
        help="Path to input CSV with match results.",
    )

    parser.add_argument(
        "--output-report",
        type=str,
        default=None,
        help="Optional path for saving text report.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Wczytuje CSV z wynikami eksperymentów i generuje raport tekstowy.
    """
    args = parse_args()

    report = analyze_results_csv(
        input_path=args.input_csv,
        output_report_path=args.output_report,
    )

    print(report)

    if args.output_report is not None:
        print(f"Zapisano raport: {args.output_report}")


if __name__ == "__main__":
    main()