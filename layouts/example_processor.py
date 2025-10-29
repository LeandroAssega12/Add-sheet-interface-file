from pathlib import Path


def process(file_path: Path) -> None:
    # Example no-op processor: just prints the file size
    try:
        size = file_path.stat().st_size
        print(f"[example_processor] {file_path.name}: {size} bytes")
    except Exception as exc:
        print(f"[example_processor] Failed to process {file_path.name}: {exc}")
