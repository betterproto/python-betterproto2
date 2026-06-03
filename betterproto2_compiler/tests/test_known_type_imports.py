from pathlib import Path

OUTPUTS = Path(__file__).parent / "outputs"


def test_timestamp_output_imports_nano_datetime() -> None:
    generated = (OUTPUTS / "google" / "google" / "protobuf" / "__init__.py").read_text()

    assert "from betterproto2.nano_datetime import NanoDatetime" in generated
    assert "NanoDatetime.from_timestamp" in generated
    assert "dateutil.parser" not in generated


def test_non_timestamp_output_does_not_import_nano_datetime() -> None:
    generated = (OUTPUTS / "bool" / "bool" / "__init__.py").read_text()

    assert "betterproto2.nano_datetime" not in generated
