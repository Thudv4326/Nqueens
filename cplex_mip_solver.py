import time
from docplex.mp.model import Model

class NQueensCplexMIPSolver:
    def __init__(self, n):
        self.n = n

    def solve(self, time_limit=60):
        n = self.n
        mdl = Model(name="NQueens_MIP")

        # x[i, j] = 1 nếu có hậu tại hàng i, cột j;
        x = {
            (i, j): mdl.binary_var(name=f"x_{i}_{j}")
            for i in range(n)
            for j in range(n)
        }

        # Mỗi hàng chỉ có một hậu
        for i in range(n):
            mdl.add_constraint(
                mdl.sum(x[i, j] for j in range(n)) == 1
            )

        # Mỗi cột chỉ có một hậu
        for j in range(n):
            mdl.add_constraint(
                mdl.sum(x[i, j] for i in range(n)) == 1
            )

        # Các đường chéo chính không trùng nhau
        for d in range(-(n-1), n):
            mdl.add_constraint(
                mdl.sum(
                    x[i, j] 
                    for i in range(n) 
                    for j in range(n) 
                    if i - j == d
                ) <= 1
            )

        # Các đường chéo phụ không trùng nhau
        for d in range(2*n - 1):
            mdl.add_constraint(
                mdl.sum(
                    x[i, j] 
                    for i in range(n) 
                    for j in range(n) 
                    if i + j == d
                ) <= 1
            )

        # time
        start_time = time.perf_counter()

        mdl.parameters.timelimit = time_limit
        solution = mdl.solve(log_output=False)
        
        elapsed = time.perf_counter() - start_time

        if solution is None:
            solve_status = str(mdl.solve_details.status).lower()
            mdl.end()

            if "infeasible" in solve_status:
                return False, elapsed, None
            
            return None, elapsed, None

        positions = []

        for i in range(n):
            for j in range(n):
                if solution.get_value(x[i, j]) > 0.5:
                    positions.append((i, j))
                    break

        mdl.end()
        return True, elapsed, positions
