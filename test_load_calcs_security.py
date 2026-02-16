import pytest
from load_calcs import ElectricalRizz

class TestElectricalRizzSecurity:

    def setup_method(self):
        self.rizz = ElectricalRizz()

    def test_zero_voltage_returns_error(self):
        """Test that voltage=0 returns -1.0 error code instead of raising ZeroDivisionError."""
        result = self.rizz.calculate_voltage_drop(voltage=0, current=10, length=100, wire_gauge=12)
        assert result == -1.0, "Should return -1.0 for zero voltage"

    def test_negative_voltage_returns_error(self):
        """Test that negative voltage returns -1.0 error code."""
        result = self.rizz.calculate_voltage_drop(voltage=-120, current=10, length=100, wire_gauge=12)
        assert result == -1.0, "Should return -1.0 for negative voltage"

    def test_valid_inputs_return_percentage(self):
        """Test that valid inputs return a positive float."""
        # K=12.9 (copper), L=100, I=10, CM=6530 (12 AWG), V=120
        # VD_volts = (2 * 12.9 * 100 * 10) / 6530 = 25800 / 6530 ≈ 3.951
        # VD_percent = (3.951 / 120) * 100 ≈ 3.29
        result = self.rizz.calculate_voltage_drop(voltage=120, current=10, length=100, wire_gauge=12)
        assert result > 0
        assert abs(result - 3.29) < 0.1 # approximate check

    def test_zero_length_returns_zero_drop(self):
        """Test that zero length results in 0% drop (valid)."""
        result = self.rizz.calculate_voltage_drop(voltage=120, current=10, length=0, wire_gauge=12)
        assert result == 0.0

    def test_zero_current_returns_zero_drop(self):
        """Test that zero current results in 0% drop (valid)."""
        result = self.rizz.calculate_voltage_drop(voltage=120, current=0, length=100, wire_gauge=12)
        assert result == 0.0
