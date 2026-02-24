import unittest
from circuit_logic import CircuitLogic

class TestCircuitLogic(unittest.TestCase):
    def setUp(self):
        self.logic = CircuitLogic()

    def test_get_troubleshooting_checklist(self):
        expected = [
            "1. Problem Definition (Don't guess, assess)",
            "2. Safety Prep (LOTO or you're toast)",
            "3. Visual Inspection (Look with your eyes, not your hands)",
            "4. Diagnostic Testing (Multimeter time)",
            "5. Isolation (Divide and conquer)",
            "6. Solution (Fix it and flex)"
        ]
        result = self.logic.get_troubleshooting_checklist()
        self.assertEqual(list(result), expected)
        self.assertEqual(len(result), 6)

if __name__ == "__main__":
    unittest.main()
