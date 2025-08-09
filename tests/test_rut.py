"""Tests for RutNumber class and validation."""

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from pydantic_type_chile_rut import RutNumber


class TestRutNumber:
    """Test cases for RutNumber validation and formatting."""

    def test_valid_rut_creation(self):
        """Test creating RutNumber with valid number and dv."""
        rut = RutNumber(12345678, "5")
        assert rut.number == 12345678
        assert rut.dv == "5"
        assert str(rut) == "12345678-5"

    def test_rut_with_dots_formatting(self):
        """Test formatting RUT with dots."""
        rut = RutNumber(12345678, "5")
        assert rut.with_dots() == "12.345.678-5"
        assert rut.formatted == "12.345.678-5"

    def test_rut_representation(self):
        """Test string representation of RutNumber."""
        rut = RutNumber(12345678, "5")
        assert repr(rut) == "RutNumber(number=12345678, dv='5')"

    def test_small_numbers(self):
        """Test RUT with small numbers."""
        rut = RutNumber(1, "9")
        assert rut.with_dots() == "1-9"
        assert str(rut) == "1-9"

        rut = RutNumber(1234, "5")
        assert rut.with_dots() == "1.234-5"

    def test_zero_rut(self):
        """Test RUT with zero number."""
        rut = RutNumber(0, "0")
        assert rut.number == 0
        assert rut.dv == "0"
        assert str(rut) == "0-0"
        assert rut.with_dots() == "0-0"


class TestRutValidation:
    """Test RUT validation in Pydantic models."""

    def setup_method(self) -> None:
        """Set up test model."""

        class TestModel(BaseModel):
            rut: RutNumber

        self.TestModel = TestModel

    def test_valid_inputs(self):
        """Test various valid RUT input formats."""
        valid_cases = [
            ("12.345.678-5", 12345678, "5", "12.345.678-5"),
            ("12345678-5", 12345678, "5", "12.345.678-5"),
            ("123456785", 12345678, "5", "12.345.678-5"),  # no hyphen
            ("15.345.678-k", 15345678, "K", "15.345.678-K"),  # lowercase k
            ("0-0", 0, "0", "0-0"),
            ("00000000-0", 0, "0", "0-0"),  # with leading zeros
            ("8.888.888-K", 8888888, "K", "8.888.888-K"),
            ("1-9", 1, "9", "1-9"),
            ("1234-3", 1234, "3", "1.234-3"),
        ]

        for raw_input, expected_number, expected_dv, expected_formatted in valid_cases:
            model = self.TestModel(rut=raw_input)
            assert model.rut.number == expected_number
            assert model.rut.dv == expected_dv
            assert model.rut.formatted == expected_formatted

    def test_invalid_inputs(self):
        """Test various invalid RUT inputs."""
        invalid_cases = [
            "12345678-4",  # wrong check digit
            "ABC",  # not numeric
            "1-0",  # wrong check digit for 1 (should be 9)
            "12.345.678-",  # missing check digit
            "",  # empty string
            "-",  # just hyphen
            "K",  # just check digit
            "123.456.789-0",  # too long
            "12345678-X",  # invalid check digit
            "12345678-10",  # check digit too long
            " ",  # just space
            "12345678",  # missing check digit completely
            "123456789012345678-5",  # way too long
        ]

        for invalid_input in invalid_cases:
            with pytest.raises(ValidationError):
                self.TestModel(rut=invalid_input)

    def test_type_adapter(self):
        """Test using TypeAdapter directly."""
        adapter = TypeAdapter(RutNumber)

        rut = adapter.validate_python("12.345.678-5")
        assert isinstance(rut, RutNumber)
        assert rut.number == 12345678
        assert rut.dv == "5"
        assert str(rut) == "12345678-5"
        assert rut.with_dots() == "12.345.678-5"

    def test_edge_cases(self):
        """Test edge cases and special characters."""
        # Test different dash types
        model = self.TestModel(rut="12345678–5")  # en dash
        assert model.rut.number == 12345678
        assert model.rut.dv == "5"

        model = self.TestModel(rut="12345678—5")  # em dash
        assert model.rut.number == 12345678
        assert model.rut.dv == "5"

        # Test with spaces
        model = self.TestModel(rut=" 12.345.678-5 ")
        assert model.rut.number == 12345678
        assert model.rut.dv == "5"

    def test_minimum_maximum_valid_ruts(self):
        """Test minimum and maximum valid RUT ranges."""
        # Minimum valid RUT
        model = self.TestModel(rut="1-9")
        assert model.rut.number == 1
        assert model.rut.dv == "9"

        # Large valid RUT
        model = self.TestModel(rut="99999999-9")
        assert model.rut.number == 99999999
        assert model.rut.dv == "9"

    def test_leading_zeros_handling(self):
        """Test handling of leading zeros."""
        model = self.TestModel(rut="00001234-3")
        assert model.rut.number == 1234
        assert model.rut.dv == "3"
        assert str(model.rut) == "1234-3"

    def test_k_check_digit_cases(self):
        """Test various cases with K as check digit."""
        # Test both uppercase and lowercase k
        for k_char in ["k", "K"]:
            model = self.TestModel(rut=f"15345678-{k_char}")
            assert model.rut.number == 15345678
            assert model.rut.dv == "K"  # Should always be uppercase
            assert model.rut.formatted == "15.345.678-K"


class TestComputeDv:
    """Test the internal check digit computation."""

    def test_known_check_digits(self):
        """Test check digit computation for known values."""
        from pydantic_type_chile_rut.rut import _compute_dv

        # Test known RUT check digits
        test_cases = [
            ("12345678", "5"),
            ("15345678", "K"),
            ("8888888", "K"),
            ("1", "9"),
            ("1234", "3"),
            ("0", "0"),
        ]

        for body, expected_dv in test_cases:
            assert _compute_dv(body) == expected_dv

    def test_compute_dv_edge_cases(self):
        """Test edge cases for check digit computation."""
        from pydantic_type_chile_rut.rut import _compute_dv

        # Test single digit
        assert _compute_dv("1") == "9"
        assert _compute_dv("0") == "0"

        # Test maximum length
        assert _compute_dv("999999999") == "6"


class TestParseAndValidate:
    """Test the internal parsing and validation function."""

    def test_parse_valid_inputs(self):
        """Test parsing of various valid inputs."""
        from pydantic_type_chile_rut.rut import _parse_and_validate_rut

        test_cases = [
            ("12.345.678-5", "12345678", "5"),
            ("12345678-5", "12345678", "5"),
            ("123456785", "12345678", "5"),
            ("15.345.678-k", "15345678", "K"),
            ("0-0", "0", "0"),
            ("00000000-0", "0", "0"),
        ]

        for input_val, expected_body, expected_dv in test_cases:
            body, dv = _parse_and_validate_rut(input_val)
            assert body == expected_body
            assert dv == expected_dv

    def test_parse_invalid_inputs(self):
        """Test parsing of invalid inputs raises ValueError."""
        from pydantic_type_chile_rut.rut import _parse_and_validate_rut

        invalid_inputs = [
            "ABC",
            "12345678-4",  # wrong check digit
            "",
            "-",
            "K",
            "123456789012345678-5",  # too long
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                _parse_and_validate_rut(invalid_input)


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow(self):
        """Test complete workflow from input to formatted output."""

        class Person(BaseModel):
            name: str
            rut: RutNumber

        person = Person(name="Juan Pérez", rut="12.345.678-5")

        # Test all properties
        assert person.rut.number == 12345678
        assert person.rut.dv == "5"
        assert str(person.rut) == "12345678-5"
        assert person.rut.formatted == "12.345.678-5"
        assert person.rut.with_dots() == "12.345.678-5"

        # Test serialization
        person_dict = person.model_dump()
        assert person_dict["rut"] == "12345678-5"

    def test_multiple_ruts_in_model(self):
        """Test model with multiple RUT fields."""

        class Contract(BaseModel):
            contractor_rut: RutNumber
            client_rut: RutNumber

        contract = Contract(contractor_rut="12.345.678-5", client_rut="15.345.678-K")

        assert contract.contractor_rut.formatted == "12.345.678-5"
        assert contract.client_rut.formatted == "15.345.678-K"
