"""
Local preview script to render meeting_report.html from a local meeting JSON.
Usage:
  python -m src.report_preview --input json/<meeting_id>/meeting.json --output preview.html
"""
import argparse
import json
from pathlib import Path

from .models import Meeting
from .report_generator import ReportGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render meeting HTML from local JSON for preview")
    parser.add_argument("--input", required=True, help="Path to meeting.json")
    parser.add_argument("--output", default="preview.html", help="Output HTML file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meeting = Meeting.from_dict(data)

    generator = ReportGenerator()
    html = generator.generate_html_report(meeting)
    if html is None:
        raise SystemExit("Failed to render HTML.")

    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    print(f"Preview written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
