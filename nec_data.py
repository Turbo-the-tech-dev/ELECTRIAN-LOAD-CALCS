# nec_data.py
# Source: study_flashcards.md

NEC_TABLES = {
    #
    "grounding_conductors": {
        # Rating of Overcurrent Device : Size of Copper EGC (AWG)
        15: 14,
        20: 12,  #
        60: 10,  #
        100: 8,
        200: 6
    },
    
    #
    "bending_multipliers": {
        10: 6.0,   # Cosecant of 10
        22.5: 2.6, #
        30: 2.0,   #
        45: 1.4,   #
        60: 1.2
    },

    #
    "shrink_per_inch": {
        # Shrink per inch of rise
        30: 0.25,   # 1/4 inch
        22.5: 0.1875, # 3/16 inch
        45: 0.375   # 3/8 inch
    }
}
