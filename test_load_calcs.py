import pytest
from load_calcs import ElectricalRizz

@pytest.fixture
def rizz():
    return ElectricalRizz()

def test_calculate_voltage_drop_copper(rizz):
    # Test valid copper scenario
    # VD = 2 * K * L * I / CM
    # 2 * 12.9 * 50 * 20 / 6530 = 25800 / 6530 approx 3.95
    # (3.95 / 120) * 100 approx 3.29%
    vd = rizz.calculate_voltage_drop(voltage=120, current=20, length=50, wire_gauge=12, material='copper')
    assert vd == pytest.approx(3.2925, rel=1e-4)

def test_calculate_voltage_drop_aluminum(rizz):
    # Test valid aluminum scenario
    # 2 * 21.2 * 50 * 20 / 6530 = 42400 / 6530 approx 6.49
    # (6.49 / 120) * 100 approx 5.41%
    vd = rizz.calculate_voltage_drop(voltage=120, current=20, length=50, wire_gauge=12, material='aluminum')
    assert vd == pytest.approx(5.4109, rel=1e-4)

def test_calculate_voltage_drop_invalid_gauge(rizz):
    vd = rizz.calculate_voltage_drop(voltage=120, current=20, length=50, wire_gauge=99, material='copper')
    assert vd == -1.0

def test_calculate_voltage_drop_zero_values(rizz):
    assert rizz.calculate_voltage_drop(120, 0, 50, 12) == 0.0
    assert rizz.calculate_voltage_drop(120, 20, 0, 12) == 0.0

def test_check_conduit_fill_1_conductor(rizz):
    # 1 conductor max_fill = 0.53
    assert rizz.check_conduit_fill(conduit_area=1.0, conductor_area_total=0.53, num_conductors=1) is True
    assert rizz.check_conduit_fill(conduit_area=1.0, conductor_area_total=0.54, num_conductors=1) is False

def test_check_conduit_fill_2_conductors(rizz):
    # 2 conductors max_fill = 0.31
    assert rizz.check_conduit_fill(conduit_area=1.0, conductor_area_total=0.31, num_conductors=2) is True
    assert rizz.check_conduit_fill(conduit_area=1.0, conductor_area_total=0.32, num_conductors=2) is False

def test_check_conduit_fill_3_plus_conductors(rizz):
    # 3+ conductors max_fill = 0.40
    assert rizz.check_conduit_fill(conduit_area=1.0, conductor_area_total=0.40, num_conductors=3) is True
    assert rizz.check_conduit_fill(conduit_area=1.0, conductor_area_total=0.41, num_conductors=3) is False
    assert rizz.check_conduit_fill(conduit_area=1.0, conductor_area_total=0.40, num_conductors=4) is True

def test_calculate_offset_shrink_valid_angles(rizz):
    # 10: 0.09, 22.5: 0.19, 30: 0.25, 45: 0.38, 60: 0.58
    assert rizz.calculate_offset_shrink(10, 10) == pytest.approx(0.9)
    assert rizz.calculate_offset_shrink(10, 22.5) == pytest.approx(1.9)
    assert rizz.calculate_offset_shrink(10, 30) == pytest.approx(2.5)
    assert rizz.calculate_offset_shrink(10, 45) == pytest.approx(3.8)
    assert rizz.calculate_offset_shrink(10, 60) == pytest.approx(5.8)

def test_calculate_offset_shrink_invalid_angle(rizz):
    # Should default to 30 (0.25 multiplier)
    assert rizz.calculate_offset_shrink(10, 90) == pytest.approx(2.5)

def test_get_loto_procedure(rizz):
    proc = rizz.get_loto_procedure()
    assert "1. Identify the ops" in proc
    assert "2. Tell the squad" in proc
    assert "3. Shut it down" in proc
    assert "4. Isolate the energy" in proc
    assert "5. Lock it out" in proc
    assert "6. Verify isolation" in proc
    assert len(proc.split('\n')) == 6
