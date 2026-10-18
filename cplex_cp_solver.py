import time
from docplex.cp.model import CpoModel
from docplex.cp.config import context

context.solver.local.execfile = (
    r"C:\Program Files\IBM\ILOG\CPLEX_Studio222"
    r"\cpoptimizer\bin\x64_win64\cpoptimizer.exe"
)

class NQueensCplexCPSolver:
    def __init__(self, n):
        self.n = n

    def solve(self, time_limit=60):
        n = self.n
        mdl = CpoModel(name="NQueens_CP")

        # q[i] = cột đặt hậu tại hàng i
        q = [
            mdl.integer_var(min=0, max=n-1, name=f"q_{i}") 
            for i in range(n)
        ]

        # Mỗi hàng chỉ có một hậu
        # Mỗi biến q[i] đại diện đúng 1 hậu trên hàng i
        # Không có hai hậu nào cùng cột
        mdl.add(mdl.all_diff(q))

        # Không có 2 quân hậu nào trên cùng một đường chéo
        mdl.add(mdl.all_diff([q[i] - i for i in range(n)]))
        mdl.add(mdl.all_diff([q[i] + i for i in range(n)]))

        # time
        start_time = time.perf_counter()
        solution = mdl.solve(
            TimeLimit=time_limit, 
            LogVerbosity='Quiet'
        )
        elapsed = time.perf_counter() - start_time

        if solution is None:
            return None, elapsed, None

        if not solution.is_solution():
            solve_status = str(solution.get_solve_status())

            if "Infeasible" in solve_status:
                return False, elapsed, None
            else:
                return None, elapsed, None

        positions = [
            (i, solution.get_value(q[i])) 
            for i in range(n)
        ]

        return True, elapsed, positions

    