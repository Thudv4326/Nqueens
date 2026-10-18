import time
import csv

from sat_solver import NQueensSATSolver
from cplex_cp_solver import NQueensCplexCPSolver
from cplex_mip_solver import NQueensCplexMIPSolver
from gurobi_solver import NQueensGurobiSolver
from cp_sat_solver import NQueensCPSATSolver


SIZES = [4, 8, 10, 20]

TIME_LIMIT = 60
CSV_FILE = "results.csv"

def validate_solution(n, positions):
    if positions is None or len(positions) != n:
        return False

    if any(
        not (0 <= r < n and 0 <= c < n) 
        for r, c in positions
    ):
        return False

    rows = [r for r, c in positions]
    cols = [c for r, c in positions]

    return (
        len(set(rows)) == n and
        len(set(cols)) == n and
        len({r - c for r, c in positions}) == n and
        len({r + c for r, c in positions}) == n
    )

def run_solver(name, n, solver_func):
    print(f"  Running {name}...", flush=True)

    start_time = time.perf_counter()

    try:
        is_sat, reported_time, solution = solver_func(n)
        wall_time = time.perf_counter() - start_time

        valid = (
            solution is not None and
            validate_solution(n, solution)
        )

        if solution is not None and not valid:
            status = "INVALID"
        elif is_sat and valid:
            status = "SAT"
        else:
            status = "No_solution"

        result = {
            "N": n,
            "Solver": name,
            "Status": status,
            "Valid_solution": valid,
            "solve_time_seconds": reported_time,
            "wall_time_seconds": wall_time,
            "error": "",
        }

        print(
            f"   Status: {status}, "
            f"Time={reported_time:.4f}s"
        )

    except Exception as e:
        result = {
            "N": n,
            "Solver": name,
            "Status": "ERROR" ,
            "Valid_solution": False,
            "solve_time_seconds": "",
            "wall_time_seconds": time.perf_counter() - start_time,
            "error": repr(e),
        }

        print(f"    ERROR: {e}")

    return result


def main():
    results = []

    for n in SIZES:
        print(f"\n{'=' * 40}")
        print(f"N = {n}")
        print(f"{'=' * 40}")

        # SAT: phiên bản hiện tại chưa nhận time_limit
        results.append(
            run_solver(
                "SAT",
                n,
                lambda: NQueensSATSolver(
                    n=n,
                    encoding_type="seqcounter",
                    solver_name="cadical195",
                ).solve(),
            )
        )

        # CPLEX CP
        results.append(
            run_solver(
                "CPLEX CP",
                n,
                lambda: NQueensCplexCPSolver(n).solve(
                    time_limit=TIME_LIMIT
                ),
            )
        )

        # CPLEX MIP
        results.append(
            run_solver(
                "CPLEX MIP",
                n,
                lambda: NQueensCplexMIPSolver(n).solve(
                    time_limit=TIME_LIMIT
                ),
            )
        )

        # Gurobi
        results.append(
            run_solver(
                "Gurobi",
                n,
                lambda: NQueensGurobiSolver(n).solve(
                    time_limit=TIME_LIMIT
                ),
            )
        )

        # OR-Tools CP-SAT
        results.append(
            run_solver(
                "CP-SAT",
                n,
                lambda: NQueensCPSATSolver(n).solve(
                    time_limit=TIME_LIMIT
                ),
            )
        )

    # Lưu tất cả kết quả vào CSV
    fieldnames = [
        "N",
        "solver",
        "status",
        "valid_solution",
        "solve_time_seconds",
        "wall_time_seconds",
        "error",
    ]

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {CSV_FILE}")


if __name__ == "__main__":
    main()

# for n in SIZES:
#     """Test SAT solver"""
#     sat_solver = NQueensSATSolver(
#         n = n,
#         encoding_type = "product",
#         solver_name = "cadical195",
#     )
#     is_sat, time_used, solution = sat_solver.solve()

#     print(
#         f"N={n}: "
#         f"SAT={is_sat}, "
#         f"Time={time_used:.4f}s"
#     )

#     if solution is not None:
#         print("Solution:", solution)    

#     """Test Cplex CP solver"""
#     cp_solver = NQueensCplexCPSolver(n)
#     cp_sat, cp_time, cp_sol = cp_solver.solve(time_limit=60)

#     print( 
#         f"N={n}: "
#         f"SAT={cp_sat}, "
#         f"Time={cp_time:.4f}s"
#     )

#     if cp_sol is not None:
#         print("Solution:", cp_sol)

#     """Test Cplex MIP solver"""
#     mip_solver = NQueensCplexMIPSolver(n)
#     mip_sat, mip_time, mip_sol = mip_solver.solve(time_limit=200)

#     print(
#         f"N={n}: "
#         f"MIP={mip_sat}, "
#         f"Time={mip_time:.4f}s"
#     )

#     if mip_sol is not None:
#         print("Solution:", mip_sol)

#     """Test Gurobi solver"""
#     solver = NQueensGurobiSolver(n)
#     gurobi_sat, gurobi_time, gurobi_sol = solver.solve(time_limit=200)

#     print(
#         f"N={n}: "
#         f"Gurobi={gurobi_sat}, "
#         f"Time={gurobi_time:.4f}s"
#     )

#     if gurobi_sol is not None:
#         print("Solution:", gurobi_sol)

#     """Test CP-SAT solver"""
#     solver = NQueensCPSATSolver(n)
#     cp_sat, cp_time, cp_sol = solver.solve(time_limit=200)

#     print(
#         f"N={n}: "
#         f"CP-SAT={cp_sat}, "
#         f"Time={cp_time:.4f}s"
#     )

#     if cp_sol is not None:
#         print("Solution:", cp_sol)