import time
import gurobipy as gp
from gurobipy import GRB

class NQueensGurobiSolver:
    def __init__(self, n):
        self.n = n

    def solve(self, time_limit=60):
        n = self.n
        mdl = gp.Model("NQueens_Gurobi")

        mdl.Params.OutputFlag = 0
        mdl.Params.TimeLimit = time_limit

        # x[i, j] = 1 if there is a queen at row i, column j
        x = {
            (i, j): mdl.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")
            for i in range(n)
            for j in range(n)
        }

        # Each row has exactly one queen
        for i in range(n):
            mdl.addConstr(
                gp.quicksum(x[i, j] for j in range(n)) == 1,
                name=f"row_{i}",
            )

        # Each column has exactly one queen
        for j in range(n):
            mdl.addConstr(
                gp.quicksum(x[i, j] for i in range(n)) == 1,
                name=f"col_{j}",
            )

        # Almost one queen on the same diagonal ( \ )
        for d in range(-(n-1), n):
            vars_diag = [
                x[i, j]
                for i in range(n)
                for j in range(n)
                if i - j == d
            ]
            if len(vars_diag) > 1:
                mdl.addConstr(
                    gp.quicksum(vars_diag) <= 1,
                    name=f"diag_down_{d}",
                )

        # Almost one queen on the same diagonal ( / )
        for d in range(2*n - 1):
            vars_diag = [
                x[i, j]
                for i in range(n)
                for j in range(n)
                if i + j == d
            ]
            if len(vars_diag) > 1:
                mdl.addConstr(
                    gp.quicksum(vars_diag) <= 1,
                    name=f"diag_up_{d}",
                )

        # time
        start_time = time.perf_counter()
        mdl.optimize()
        elapsed = time.perf_counter() - start_time
        
        if mdl.SolCount > 0:
            positions = [
                (i, j)
                for i in range(n)
                for j in range(n)
                if x[i, j].X > 0.5
            ]
            mdl.dispose()
            return True, elapsed, positions

        status = mdl.Status
        mdl.dispose()

        if status == GRB.INFEASIBLE:
            return False, elapsed, None

        return None, elapsed, None