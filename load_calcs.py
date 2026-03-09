# ELECTRICIAN-LOAD-CALCS – 2026 edition • NEC 2026 Neutral Demand Updates
# Incorporates proposed / adopted NEC 2026 changes to 220.61:
# - Expanded 220.61(C) exceptions for modern loads
# - 60% neutral reduction cap on 4-wire 3φ wye (down from 70%)
# - Explicit treatment of EVSE, energy storage, PV inverter backfeed
# - Clarified non-linear load neutral sizing (harmonic contribution)

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Final, Tuple
import math
from functools import cached_property

# ──────────────────────────────────────────────────────────────────────────────
# NEC 2026 NEUTRAL REFERENCES (key changes from 2023)
# ──────────────────────────────────────────────────────────────────────────────

NEC_220_61_A = "Maximum current on any neutral conductor after demand factors"
NEC_220_61_B = "4-wire, 3-phase wye → 60% max neutral reduction if balanced"
NEC_220_61_C = "Additional reductions: ranges 70%, dryers 70%, EVSE/PV limited"
NEC_220_61_D = "Nonlinear loads (LED, electronic ballasts, VFDs) → 173% penalty possible"
NEC_310_15_B_5 = "Neutral conductor ampacity adjustment for harmonics"

KW_PER_VA: Final[float] = 0.001
VA_PER_KW: Final[float] = 1000.0


class VoltageSystem(Enum):
    SINGLE_PHASE_120_240 = auto()
    THREE_PHASE_208Y_120  = auto()
    THREE_PHASE_480Y_277  = auto()
    SINGLE_PHASE_208      = auto()


@dataclass(frozen=True)
class DemandFactorRule:
    min_va: float
    max_va: float | None
    factor: float


LIGHTING_DEMAND_FACTORS: Final[List[DemandFactorRule]] = [
    DemandFactorRule(     0,  10_000, 1.00),
    DemandFactorRule(10_000, 120_000, 0.35),
    DemandFactorRule(120_000,     None, 0.25),
]


COOKING_DEMAND_FACTORS: Final[Dict[int, float]] = {
    1:0.80, 2:0.75, 3:0.70, 4:0.65, 5:0.60, 6:0.55, 7:0.50, 8:0.45, 9:0.40, 10:0.38
}


@dataclass
class LoadComponent:
    name: str
    va: float
    quantity: int = 1
    phases: int = 1
    neutral_factor: float = 1.0 # 1.0 normal, 1.73 for high-harmonic
    is_240v_balanced: bool = False # pure 240 V → 0 neutral
    is_evse: bool = False
    is_pv_inverter: bool = False

    @property
    def total_va(self) -> float:
        return self.va * self.quantity


@dataclass
class MotorLoad(LoadComponent):
    hp: float
    voltage: float
    nameplate_fla: Optional[float] = None
    noncoincident_with: Optional[str] = None

    @cached_property
    def nec_flc(self) -> float:
        if self.nameplate_fla is not None:
            return self.nameplate_fla
        
        ratio = self.voltage / 230.0
        if self.phases == 1:
            table = {0.5:5.8, 0.75:7.2, 1.0:8.0, 1.5:10, 2:12, 3:17, 5:28}
            return table.get(self.hp, self.hp * 5.6) * ratio
        else:
            table = {0.5:2.3, 0.75:3.0, 1.0:3.6, 1.5:5.2, 2:6.8, 3:9.6, 5:15.2}
            base = table.get(self.hp, self.hp * 2.75)
            # Table 430.250 note: 230V base, adjust for 208V/460V
            if self.voltage in (208, 460, 480):
                return base * (230 / self.voltage)
            return base * ratio

    @cached_property
    def va(self) -> float:
        return self.nec_flc * self.voltage * (math.sqrt(3) if self.phases == 3 else 1.0)


@dataclass
class ServiceEquipment:
    voltage_system: VoltageSystem
    lighting_loads: List[LoadComponent] = field(default_factory=list)
    small_appliance: List[LoadComponent] = field(default_factory=lambda: [LoadComponent("Small App", 3000)])
    laundry: Optional[LoadComponent] = field(default_factory=lambda: LoadComponent("Laundry", 1500))
    fixed_appliances: List[LoadComponent] = field(default_factory=list)
    cooking: List[LoadComponent] = field(default_factory=list)
    dryers: List[LoadComponent] = field(default_factory=list)
    motors: List[MotorLoad] = field(default_factory=list)
    evse_loads: List[LoadComponent] = field(default_factory=list) # 2026 explicit
    pv_inverter_loads: List[LoadComponent] = field(default_factory=list) # 2026 explicit
    other_loads: List[LoadComponent] = field(default_factory=list)
    apply_noncoincident_reduction: bool = True
    apply_harmonic_neutral_penalty: bool = True

    @cached_property
    def applied_lighting_demand_va(self) -> float:
        total = sum(l.total_va for l in self.lighting_loads)
        demand, prev = 0.0, 0.0
        for r in LIGHTING_DEMAND_FACTORS:
            segment = min(total, r.max_va or math.inf) - prev
            if segment <= 0: break
            demand += segment * r.factor
            prev = r.max_va or total
        return demand

    @cached_property
    def small_laundry_va(self) -> float:
        return sum(a.total_va for a in self.small_appliance) + (self.laundry.total_va if self.laundry else 0)

    @cached_property
    def fixed_appliance_demand_va(self) -> float:
        total = sum(a.total_va for a in self.fixed_appliances)
        return total * 0.75 if len(self.fixed_appliances) >= 4 else total

    @cached_property
    def cooking_demand_va(self) -> float:
        return sum(c.total_va * COOKING_DEMAND_FACTORS.get(c.quantity, 0.38) for c in self.cooking)

    @cached_property
    def dryer_demand_va(self) -> float:
        return sum(d.total_va for d in self.dryers)

    @cached_property
    def motor_group_demand_va(self) -> float:
        if not self.motors:
            return 0.0
        sorted_motors = sorted(self.motors, key=lambda m: m.nec_flc, reverse=True)
        demand_fla = sorted_motors[0].nec_flc * 1.25 + sum(m.nec_flc for m in sorted_motors[1:])
        base_va = demand_fla * self._system_voltage() * (math.sqrt(3) if self._is_three_phase() else 1.0)

        if self.apply_noncoincident_reduction:
            groups: Dict[str, List[MotorLoad]] = {}
            for m in self.motors:
                if m.noncoincident_with:
                    groups.setdefault(m.noncoincident_with, []).append(m)
            for g in groups.values():
                if len(g) >= 2:
                    max_va_val = max(m.va for m in g)
                    base_va -= (sum(m.va for m in g) - max_va_val)
        return max(0.0, base_va)

    @cached_property
    def calculated_demand_va(self) -> float:
        return round(
            self.applied_lighting_demand_va +
            self.small_laundry_va +
            self.fixed_appliance_demand_va +
            self.cooking_demand_va +
            self.dryer_demand_va +
            self.motor_group_demand_va +
            sum(o.total_va for o in self.other_loads) +
            sum(e.total_va for e in self.evse_loads) +
            sum(p.total_va for p in self.pv_inverter_loads),
            -1
        )

    # ────────────────────────────────────────────────────────────────────────
    # NEUTRAL DEMAND – NEC 2026 220.61 full logic
    # ────────────────────────────────────────────────────────────────────────
    @cached_property
    def neutral_demand_va(self) -> float:
        if self.voltage_system == VoltageSystem.SINGLE_PHASE_120_240:
            return self._neutral_120_240_2026()
        if self.voltage_system in (VoltageSystem.THREE_PHASE_208Y_120, VoltageSystem.THREE_PHASE_480Y_277):
            return self._neutral_3ph_wye_2026()
        return self.calculated_demand_va # fallback

    def _neutral_120_240_2026(self) -> float:
        neutral_va = 0.0
        # 120 V unbalanced loads → full neutral contribution
        for load in self._120v_unbalanced_loads():
            neutral_va += load.total_va * load.neutral_factor
            
        # Ranges & dryers → 70% neutral (220.61(C) retained)
        range_dryer_va = sum(c.total_va for c in self.cooking) + sum(d.total_va for d in self.dryers)
        neutral_va += range_dryer_va * 0.70
        
        # EVSE – 2026: only 70% if Level 2 hardwired and >60 A (approx > 14.4 kVA at 240V)
        evse_va = sum(e.total_va for e in self.evse_loads if e.va > 14400)
        neutral_va += evse_va * 0.70
        
        # PV inverter backfeed – 2026: neutral not reduced below calculated
        pv_va = sum(p.total_va for p in self.pv_inverter_loads)
        neutral_va = max(neutral_va, pv_va)
        
        # Floor: never less than 70% of total demand (conservative 2026 interpretation)
        return max(neutral_va, self.calculated_demand_va * 0.70)

    def _neutral_3ph_wye_2026(self) -> float:
        phase_a, phase_b, phase_c = self._estimated_phase_loads_va()
        max_phase_va = max(phase_a, phase_b, phase_c)
        neutral = max_phase_va
        
        # 2026 change: 60% reduction allowed on 4-wire wye if well-balanced
        if max_phase_va > 0:
            avg = (phase_a + phase_b + phase_c) / 3
            imbalance_pct = max(abs(p - avg) for p in (phase_a, phase_b, phase_c)) / max_phase_va
            if imbalance_pct <= 0.10:
                neutral *= 0.60
                
        # Nonlinear / harmonic loads override reduction (220.61(D) strengthened)
        if self.apply_harmonic_neutral_penalty:
            harmonic_va = sum(l.total_va * (l.neutral_factor - 1.0) for l in self._all_loads() if l.neutral_factor > 1.0)
            neutral += harmonic_va
            
        # EVSE/PV special rules – no reduction below nameplate on neutral
        ev_pv_va = sum(e.total_va for e in self.evse_loads) + \
                   sum(p.total_va for p in self.pv_inverter_loads)
        neutral = max(neutral, ev_pv_va)
        return neutral

    def _120v_unbalanced_loads(self) -> List[LoadComponent]:
        return (
            self.lighting_loads + self.small_appliance +
            ([self.laundry] if self.laundry else []) +
            [a for a in self.fixed_appliances if a.phases == 1]
        )

    def _all_loads(self) -> List[LoadComponent]:
        return (
            self.lighting_loads + self.small_appliance +
            ([self.laundry] if self.laundry else []) +
            self.fixed_appliances + self.cooking + self.dryers +
            self.evse_loads + self.pv_inverter_loads + self.other_loads + 
            [m for m in self.motors]
        )

    def _estimated_phase_loads_va(self) -> Tuple[float, float, float]:
        total = self.calculated_demand_va
        a = total * 0.34
        b = total * 0.33
        c = total * 0.33
        
        for load in self._120v_unbalanced_loads():
            a += load.total_va * 0.5
            b += load.total_va * 0.5
        return a, b, c

    def neutral_amps(self) -> float:
        v_ln = {
            VoltageSystem.SINGLE_PHASE_120_240: 120.0,
            VoltageSystem.THREE_PHASE_208Y_120: 120.0,
            VoltageSystem.THREE_PHASE_480Y_277: 277.0,
        }.get(self.voltage_system, 120.0)
        return self.neutral_demand_va / v_ln

    def amps(self) -> float:
        v = self._system_voltage()
        return self.calculated_demand_va / (v * math.sqrt(3) if self._is_three_phase() else v)

    def _system_voltage(self) -> float:
        return {
            VoltageSystem.SINGLE_PHASE_120_240: 240.0, 
            VoltageSystem.THREE_PHASE_208Y_120: 208.0, 
            VoltageSystem.THREE_PHASE_480Y_277: 480.0, 
            VoltageSystem.SINGLE_PHASE_208: 208.0
        }[self.voltage_system]

    def _is_three_phase(self) -> bool:
        return self.voltage_system in (VoltageSystem.THREE_PHASE_208Y_120, VoltageSystem.THREE_PHASE_480Y_277)


# ──────────────────────────────────────────────────────────────────────────────
# EXAMPLE – 2026 neutral behavior
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    svc = ServiceEquipment(VoltageSystem.SINGLE_PHASE_120_240)
    svc.lighting_loads = [LoadComponent("Lighting", 2850 * 3.0)]
    svc.small_appliance = [LoadComponent("Small App", 3000)]
    svc.laundry = LoadComponent("Laundry", 1500)
    svc.cooking = [LoadComponent("Range", 12000)]
    svc.dryers = [LoadComponent("Dryer", 5000)]
    svc.evse_loads = [LoadComponent("Level 2 EVSE", 9600, is_evse=True)]
    svc.motors = [MotorLoad("AC", hp=5.0, voltage=240.0, phases=1, nameplate_fla=27.0)]
    
    print(f"Total demand VA     : {svc.calculated_demand_va:,.0f} VA")
    print(f"Neutral demand VA   : {svc.neutral_demand_va:,.0f} VA")
    print(f"Neutral amps @120 V : {svc.neutral_amps():.1f} A")
    print(f"Neutral reduction   : {svc.neutral_demand_va / svc.calculated_demand_va:.1%}")
