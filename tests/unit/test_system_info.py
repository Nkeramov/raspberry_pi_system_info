from typing import Any

import pytest
from src.rpi_system_info.core.system_info import ModelType, RPiSystemInfo


class TestDecodeRevisionCode:
    @pytest.mark.parametrize(
        "code, expected",
        [
            (
                "0x9020e0",
                {
                    "model_type": ModelType.RPI_3A_PLUS,
                    "revision": "1.0",
                    "memory_size": 512,
                    "cpu_model": "BCM2837",
                    "manufacturer": "Sony UK",
                    "overvoltage_allowed": False,
                    "otp_programming_allowed": False,
                    "otp_reading_allowed": False,
                },
            ),
            (
                "0xa03111",
                {
                    "model_type": ModelType.RPI_4B,
                    "revision": "1.1",
                    "memory_size": 1024,
                    "cpu_model": "BCM2711",
                    "manufacturer": "Sony UK",
                    "overvoltage_allowed": False,
                    "otp_programming_allowed": False,
                    "otp_reading_allowed": False,
                },
            ),
            (
                "0xd04170",
                {
                    "model_type": ModelType.RPI_5,
                    "revision": "1.0",
                    "memory_size": 8192,
                    "cpu_model": "BCM2712",
                    "manufacturer": "Sony UK",
                    "overvoltage_allowed": False,
                    "otp_programming_allowed": False,
                    "otp_reading_allowed": False,
                },
            ),
        ],
    )
    def test_decode_revision_code_new_style_valid(self, code: str, expected: dict[str, Any]) -> None:
        result = RPiSystemInfo.decode_revision_code(code)
        assert result == expected

    @pytest.mark.parametrize(
        "code, expected",
        [
            (
                "0x0002",
                {
                    "model_type": ModelType.RPI_B,
                    "revision": "1.0",
                    "memory_size": 256,
                    "cpu_model": "BCM2835",
                    "manufacturer": "EGOMAN",
                },
            ),
            (
                "0x0010",
                {
                    "model_type": ModelType.RPI_B_PLUS,
                    "revision": "1.2",
                    "memory_size": 512,
                    "cpu_model": "BCM2835",
                    "manufacturer": "SONY_UK",
                },
            ),
            (
                "0x0012",
                {
                    "model_type": ModelType.RPI_A_PLUS,
                    "revision": "1.1",
                    "memory_size": 256,
                    "cpu_model": "BCM2835",
                    "manufacturer": "SONY_UK",
                },
            ),
            (
                "0x0013",
                {
                    "model_type": ModelType.RPI_B_PLUS,
                    "revision": "1.2",
                    "memory_size": 512,
                    "cpu_model": "BCM2835",
                    "manufacturer": "EMBEST",
                },
            ),
        ],
    )
    def test_decode_revision_code_old_style_valid(self, code: str, expected: dict[str, Any]) -> None:
        result = RPiSystemInfo.decode_revision_code(code)
        assert result == expected

    def test_decode_revision_code_without_prefix(self) -> None:
        result = RPiSystemInfo.decode_revision_code("9020e0")
        assert result["model_type"] == ModelType.RPI_3A_PLUS
        assert "revision" in result
        assert "memory_size" in result
        assert "cpu_model" in result
        assert "manufacturer" in result
        assert "overvoltage_allowed" in result

    def test_decode_revision_code_invalid_not_hex(self) -> None:
        with pytest.raises(ValueError, match="Invalid revision code format"):
            RPiSystemInfo.decode_revision_code("not_hex")

    def test_decode_revision_code_empty_string(self) -> None:
        with pytest.raises(ValueError, match="Revision code cannot be empty or None"):
            RPiSystemInfo.decode_revision_code("")

    def test_decode_revision_code_none(self) -> None:
        with pytest.raises(ValueError, match="Revision code cannot be empty or None"):
            RPiSystemInfo.decode_revision_code(None)  # type: ignore

    def test_decode_revision_code_int(self) -> None:
        with pytest.raises(TypeError, match="Revision code must be a string, got int"):
            RPiSystemInfo.decode_revision_code(123)  # type: ignore

    def test_decode_revision_code_too_short_unknown_old(self) -> None:
        with pytest.raises(ValueError, match="Unknown old board revision code"):
            RPiSystemInfo.decode_revision_code("0x1")

    def test_decode_revision_code_unknown_code(self) -> None:
        with pytest.raises(ValueError, match="Invalid memory size index"):
            RPiSystemInfo.decode_revision_code("0xFFFFFF")

    def test_decode_revision_code_new_style_keys(self) -> None:
        result = RPiSystemInfo.decode_revision_code("0x9020e0")
        expected_keys = {
            "model_type",
            "revision",
            "memory_size",
            "cpu_model",
            "manufacturer",
            "overvoltage_allowed",
            "otp_programming_allowed",
            "otp_reading_allowed",
        }
        assert set(result.keys()) == expected_keys

    def test_decode_revision_code_old_style_keys(self) -> None:
        result = RPiSystemInfo.decode_revision_code("0x0002")
        expected_keys = {
            "model_type",
            "revision",
            "memory_size",
            "cpu_model",
            "manufacturer",
        }
        assert set(result.keys()) == expected_keys
