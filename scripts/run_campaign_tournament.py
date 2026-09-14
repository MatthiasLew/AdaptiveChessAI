"""Resume a frozen tournament from its last committed match."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from adaptive_chess.experiments.campaign_tournament import run_tournament


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign")
    parser.add_argument("--max-half-moves", type=int, default=200)
    args = parser.parse_args()
    run_tournament(args.campaign, args.max_half_moves)


if __name__ == "__main__":
    main()
