import time
from ortools.sat.python import cp_model

class NQueensCPSATSolver:
    def __init__(self, n):
        self.n = n

    def solve(self, time_limit=60):
        n = self.n

        mdl = cp_model.CpModel()

        # q[i]  = cột đặt hậu tại hàng i
        q = [
            mdl.NewIntVar(0, n - 1, f"q_{i}") 
            for i in range(n)
        ]

        # Không có hai quân hậu nào cùng cột
        mdl.AddAllDifferent(q)

        # Không có hai quân hậu nào trên cùng một đường chéo
        mdl.AddAllDifferent([
            q[i] - i
            for i in range(n)
        ])

        mdl.AddAllDifferent([
            q[i] + i
            for i in range(n)
        ])

        # time
        start_time = time.perf_counter()

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit

        status = solver.Solve(mdl)
        elapsed = time.perf_counter() - start_time

        # result
        if status in (
            cp_model.OPTIMAL,
            cp_model.FEASIBLE,
        ):
            positions = [
                (i, solver.Value(q[i]))
                for i in range(n)
            ]
            return True, elapsed, positions
    
        if status == cp_model.INFEASIBLE:
            return False, elapsed, None

        if status in (cp_model.UNKNOWN, cp_model.MODEL_INVALID):
            return None, elapsed, None

        return None, elapsed, None
        

        