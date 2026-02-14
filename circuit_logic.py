from typing import List, Dict, Optional

class CircuitLogic:
    """
    Handles the boolean logic for switching and the decision trees for troubleshooting.
    We reverse-engineered this from Chapter 9 because the original spec file ghosted us.
    """

    def __init__(self):
        # State memory for that 3-way switch rizz
        self.switches = {"A": False, "B": False} 
        self.breaker_status = "ON"

    def solve_3way_switch(self, toggle_a: bool, toggle_b: bool) -> str:
        """
        Simulates a standard residential 3-way switch loop (traveler system).
        
        Logic:
            The light state is an XOR gate of the two switches.
            If they are different, current flows. If they are same, no flow.
            (Note: Real world is physically complex, but logic is XOR).

        Args:
            toggle_a (bool): State of switch at door.
            toggle_b (bool): State of switch at bed.

        Returns:
            str: "LIT" if the bulb is glowing, "DARK" if it's nap time.
            
        Reference:
            Inferred from Chapter 5: Wire Color Coding (Yellow/Blue travelers).
        """
        # Python's XOR is !=
        is_lit = (toggle_a != toggle_b)
        return "LIT" if is_lit else "DARK"

    def troubleshoot_no_power(self, voltage_at_panel: float, breaker_tripped: bool, continuity_ohms: float) -> str:
        """
        Runs the Chapter 9 diagnostic tree for 'No Power to Circuit'.
        
        Flowchart (Fig 9-3 Inferred):
        1. Check Breaker -> If tripped, reset.
        2. Check Panel Voltage -> If 0, it's a utility problem (or main).
        3. Check Continuity -> If infinite (OL), wire is cut.
        
        Args:
            voltage_at_panel (float): Voltage measured at the source.
            breaker_tripped (bool): True if the handle is floppy or red.
            continuity_ohms (float): Resistance reading to the load.

        Returns:
            str: The diagnosis. No cap.
            
        Reference:
            Chapter 9, Page 78: "No Power to Circuit" Scenarios.
        """
        if breaker_tripped:
            return "DIAGNOSIS: Breaker tripped. Reset it. If it pops again, you got a short, fam."
        
        if voltage_at_panel < 100: # Assuming 120V nominal
            return "DIAGNOSIS: No voltage at panel. Call the power company or check the main lug."
        
        if continuity_ohms > 1000: # High resistance or OL
            return "DIAGNOSIS: Open circuit. You got a cut wire or a loose wire nut somewhere."
            
        return "DIAGNOSIS: Everything looks valid... check the GFCI or the bulb itself."

    def calculate_conduit_fill_logic(self, wire_type: str, count: int) -> float:
        """
        Determines the max fill factor based on count logic.
        
        Logic:
            1 wire = 53%
            2 wires = 31% (The weird zone)
            3+ wires = 40% (Standard)
            
        Args:
            wire_type (str): THHN, XHHW, etc.
            count (int): How many conductors.

        Returns:
            float: The decimal max fill allowed.
            
        Reference:
            Chapter 3 & Flashcards 9-11.
        """
        if count == 1:
            return 0.53
        elif count == 2:
            return 0.31
        elif count >= 3:
            return 0.40
        return 0.0

    def get_troubleshooting_checklist(self) -> List[str]:
        """
        Returns the 'Systematic Troubleshooting Methodology' steps.
        
        Reference:
            Chapter 9, Page 76-77.
        """
        return [
            "1. Problem Definition (Don't guess, assess)",
            "2. Safety Prep (LOTO or you're toast)",
            "3. Visual Inspection (Look with your eyes, not your hands)",
            "4. Diagnostic Testing (Multimeter time)",
            "5. Isolation (Divide and conquer)",
            "6. Solution (Fix it and flex)"
        ]

# --- Quick Test of the Logic ---
if __name__ == "__main__":
    logic = CircuitLogic()
    
    # Test 1: 3-Way Switch
    print(f"Switch A Up, Switch B Down: {logic.solve_3way_switch(True, False)}")
    print(f"Switch A Up, Switch B Up:   {logic.solve_3way_switch(True, True)}")
    
    # Test 2: Troubleshooting
    print(logic.troubleshoot_no_power(120, False, 999999))
