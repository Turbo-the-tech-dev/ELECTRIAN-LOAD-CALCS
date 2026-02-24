# motor_calcs.py

def get_motor_protection(fla: float, breaker_type: str = "inverse_time") -> dict:
    """
    Calculates max breaker size for a motor.
    
    Args:
        fla (float): Full Load Amps from nameplate.
        breaker_type (str): 'inverse_time' or 'dual_element_fuse'.
    
    Returns:
        dict: Recommended protection settings.
    """
    # Standard NEC multipliers (implied from general Journeyman knowledge context)
    if breaker_type == "inverse_time":
        multiplier = 2.50 # 250%
    elif breaker_type == "dual_element_fuse":
        multiplier = 1.75 # 175%
    else:
        return {"error": "Unknown breaker type"}
        
    max_ocpd = fla * multiplier
    
    return {
        "motor_fla": fla,
        "max_ocpd_amps": round(max_ocpd, 2),
        "min_wire_temp_rating": "75C" #
    }
