import math

class ElectricalRizz:
    """
    Main class for handling that high-voltage fanum tax.
    We keepin' it 100 with the NEC code standards. No cap.
    """

    def calculate_voltage_drop(self, voltage: float, current: float, length: float, wire_gauge: int, material: str = 'copper') -> float:
        """
        Calculates the voltage drop so your circuit doesn't get cooked.
        
        If the drop is > 3%, you're legally losing aura points (NEC 215.2(A)).
        
        Args:
            voltage (float): The system voltage (e.g., 120, 240). Don't be sus.
            current (float): Amps flowin' through the veins.
            length (float): Distance one-way in feet. Straight from Ohio to the panel.
            wire_gauge (int): AWG size. Smaller number = Thicc wire.
            material (str): 'copper' or 'aluminum'. Default is copper because we sigma.

        Returns:
            float: The voltage drop percentage. If it's high, you need to lock in.
        
        Reference:
            Based on Chapter 5: Wire and Cable Systems.
        """
        # K-factor: Copper = 12.9, Aluminum = 21.2 (Approximations for that quick maffs)
        k_factor = 12.9 if material.lower() == 'copper' else 21.2
        
        # Circular Mils (approximate for standard AWG for the stub)
        # Real ones would look this up in NEC Chapter 9, Table 8.
        cmil_map = {
            14: 4110, 12: 6530, 10: 10380, 8: 16510, 6: 26240, 
            4: 41740, 3: 52620, 2: 66360, 1: 83690
        }
        
        if wire_gauge not in cmil_map:
            return -1.0 # Error: We don't mess with that unknown wire gauge.

        if voltage <= 0:
            return -1.0 # Error: Voltage cannot be zero or negative.

        cmils = cmil_map[wire_gauge]
        
        # Formula: VD = 2 * K * L * I / CM
        vd_volts = (2 * k_factor * length * current) / cmils
        vd_percent = (vd_volts / voltage) * 100
        
        return vd_percent

    def check_conduit_fill(self, conduit_area: float, conductor_area_total: float, num_conductors: int) -> bool:
        """
        Checks if your conduit is stuffed harder than a Grimace Shake.
        
        Verifies fill percentage based on NEC Chapter 9, Table 1.
        
        Args:
            conduit_area (float): Total internal area of the pipe.
            conductor_area_total (float): Total area of all wires + insulation.
            num_conductors (int): How many snakes you pullin' through.

        Returns:
            bool: True if you're valid (Sigma), False if you're violating (Beta).
            
        Reference:
            Based on Chapter 3: Conduit Systems.
            1 conductor = 53% max fill
            2 conductors = 31% max fill
            3+ conductors = 40% max fill
        """
        if num_conductors == 1:
            max_fill = 0.53
        elif num_conductors == 2:
            max_fill = 0.31
        else:
            max_fill = 0.40 # The standard fanum tax for 3+ wires
            
        fill_ratio = conductor_area_total / conduit_area
        
        return fill_ratio <= max_fill

    def calculate_offset_shrink(self, obstruction_height: float, angle: float) -> float:
        """
        Calculates how much your pipe is gonna shrink when you bend it.
        Don't let the shrink ghost you.
        
        Args:
            obstruction_height (float): How tall the obstacle is (inches).
            angle (float): The bend angle (10, 22.5, 30, 45, 60).

        Returns:
            float: Total shrink amount in inches. Add this or your fit is mid.
            
        Reference:
            Chapter 3: Bending Fundamentals.
            Multipliers: 30deg = 0.26 shrink/inch.
        """
        # Shrink constants per inch of rise
        shrink_map = {
            10: 0.09, 
            22.5: 0.19, # rounded from 3/16
            30: 0.25,   # 1/4 inch
            45: 0.38,   # 3/8 inch
            60: 0.58
        }
        
        if angle not in shrink_map:
            print("Yo, that angle is sus. We defaultin' to 30.")
            angle = 30
            
        shrink_per_inch = shrink_map[angle]
        total_shrink = obstruction_height * shrink_per_inch
        
        return total_shrink

    def get_loto_procedure(self):
        """
        Prints the LOTO steps so you don't end up on a T-shirt.
        
        Reference:
            Chapter 2: Jobsite Safety.
        """
        steps = [
            "1. Identify the ops (energy sources).",
            "2. Tell the squad (notify personnel).",
            "3. Shut it down, no cap.",
            "4. Isolate the energy (ghost it).",
            "5. Lock it out (throw away the key).",
            "6. Verify isolation (make sure it's dead-dead)."
        ]
        return "\n".join(steps)
