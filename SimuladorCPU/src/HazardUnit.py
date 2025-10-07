from Instruction import Instruction


class HazardUnit:
    def __init__(self):
        self.RAW = 0
        self.WAR = 0
        self.WAW = 0
        self.control = 0
        self.correct_predictions = 0
        self.total_branches = 0

    def detect_hazard(self, instr1: Instruction, instr2: Instruction):
        if not instr1 or not instr2:
            return None

        # RAW: instr2 read the registers that instr1 will write
        if (instr1.rd and instr2.rs1) and (instr1.rd == instr2.rs1):
            self.RAW += 1
            return 'RAW'
        if (instr1.rd and instr2.rs2) and (instr1.rd == instr2.rs2):
            self.RAW += 1
            return 'RAW'
        return None

    def detect_hazard_waw_war(self, instr1: Instruction, instr2: Instruction):
        if not instr1 or not instr2:
            return None

        # WAW: both instructions write to the same register
        if (instr1.rd and instr2.rd) and (instr1.rd == instr2.rd):
            self.WAW += 1
            return 'WAW'

        # WAR: instr2 writes to a register that instr1 will read
        if (instr2.rd and instr1.rs1) and (instr2.rd == instr1.rs1):
            self.WAR += 1
            return 'WAR'
        if (instr2.rd and instr1.rs2) and (instr2.rd == instr1.rs2):
            self.WAR += 1
            return 'WAR'
        return None

    def update_control_hazard(self, actual_taken, predicted_taken):
        """
        Updates branch prediction accuracy metrics.
        """
        self.total_branches += 1
        if actual_taken == predicted_taken:
            self.correct_predictions += 1
        else:
            self.control += 1

    def get_branch_accuracy(self):
        if self.total_branches == 0:
            return 0.0
        return 100.0 * self.correct_predictions / self.total_branches