from Instruction import Instruction


class HazardUnit:
    def __init__(self):
        self.RAW = 0
        self.WAR = 0
        self.WAW = 0
        self.control = 0
        self.correct_predictions = 0
        self.total_branches = 0

    def detect_hazard(self, current_instr: Instruction, previous_instr: Instruction) -> str | None:
        """
        Detects data hazards (RAW) between the current and previous instructions.

        Args:
            current_instr (Instruction): The instruction in the current pipeline stage.
            previous_instr (Instruction): The instruction in the previous pipeline stage.

        Returns:
            str | None: The type of hazard detected ('RAW', 'WAW', 'WAR') or None if no hazard.
        """
        if not current_instr or not previous_instr:
            return None

        # RAW: current instruction reads a register that previous instruction will write
        # Only hazard if the previous instruction hasn't completed write-back yet
        if (previous_instr.rd and current_instr.rs1) and (previous_instr.rd == current_instr.rs1):
            self.RAW += 1
            return 'RAW'
        if (previous_instr.rd and current_instr.rs2) and (previous_instr.rd == current_instr.rs2):
            self.RAW += 1
            return 'RAW'
        return None

    def detect_hazard_waw_war(self, instr1: Instruction, instr2: Instruction) -> str | None:
        """
        Detects WAW and WAR hazards between two instructions.

        Args:
            instr1 (Instruction): The first instruction.
            instr2 (Instruction): The second instruction.

        Returns:
            str | None: The type of hazard detected ('WAW', 'WAR') or None if no hazard.
        """
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

    def update_control_hazard(self, actual_taken: bool, predicted_taken: bool) -> None:
        """
        Updates branch prediction accuracy metrics.

        Args:
            actual_taken (bool): Whether the branch was actually taken.
            predicted_taken (bool): Whether the branch was predicted to be taken.   
        """
        self.total_branches += 1
        if actual_taken == predicted_taken:
            self.correct_predictions += 1
        else:
            self.control += 1

    def get_branch_accuracy(self) -> float:
        """
        Returns the branch prediction accuracy as a percentage.
        """
        if self.total_branches == 0:
            return 0.0
        return 100.0 * self.correct_predictions / self.total_branches