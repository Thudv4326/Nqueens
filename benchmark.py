import time
import csv
from pathlib import Path

from sat_solver import NQueensSATSolver
from cplex_cp_solver import NQueensCplexCPSolver
from cplex_mip_solver import NQueensCplexMIPSolver
from gurobi_solver import NQueensGurobiSolver
from cp_sat_solver import NQueensCPSATSolver


SIZES = [1000]

TIME_LIMIT = 500
SAT_SOLVER_NAME = "minisat22"
SAT_ENCODING = "seqcounter"

CSV_FILE = Path(__file__).resolve().parent / "results.csv"

CSV_FIELDS = [
    "N",
    "Solver",
    "Status",
    "Valid_solution",
    "Solver_reported_time_seconds",
    "Wall_time_seconds",
    "Error",
]

def validate_solution(n, positions):
    if positions is None or len(positions) != n:
        return False

    try:
        normalized = [
            (int(row), int(col))
            for row, col in positions
        ]
    except (TypeError, ValueError):
        return False

    if any(
        not (0 <= r < n and 0 <= c < n) 
        for r, c in positions
    ):
        return False

    rows = [r for r, c in normalized]
    cols = [c for r, c in normalized]

    return (
        len(set(rows)) == n and
        len(set(cols)) == n and
        len({r - c for r, c in normalized}) == n and
        len({r + c for r, c in normalized}) == n
    )

def run_solver(name, n, solver_func):
    print(f"  Running {name}...", flush=True)

    start_time = time.perf_counter()

    try:
        is_sat, solver_time, solution = solver_func(n)
        
        wall_time = time.perf_counter() - start_time

        valid = (
            solution is not None and
            validate_solution(n, solution)
        )

        if is_sat is True :
            status = "SAT" if valid else "INVALID"
        elif is_sat is False:
            status = "UNSAT"
        elif is_sat is None:
            status = "TIMEOUT"  
        else:
            status = "UNKNOWN"

        result = {
            "N": n,
            "Solver": name,
            "Status": status,
            "Valid_solution": valid,
            "Solver_reported_time_seconds": solver_time,
            "Wall_time_seconds": wall_time,
            "Error": "",
        }

    except Exception as e:
        wall_time = time.perf_counter() - start_time

        result = {
            "N": n,
            "Solver": name,
            "Status": "ERROR" ,
            "Valid_solution": False,
            "Solver_reported_time_seconds": "",
            "Wall_time_seconds": wall_time,
            "Error": repr(e),
        }

        print(f"    ERROR: {e}", flush=True)

    return result


def main():
    results = []

    solver_specs = [
        (
            "SAT",
            lambda n: NQueensSATSolver(
                n=n,
                encoding_type=SAT_ENCODING,
                solver_name=SAT_SOLVER_NAME,
                time_limit=TIME_LIMIT,
            ).solve(),
        ),
        (
            "CPLEX CP",
            lambda n: NQueensCplexCPSolver(n).solve(
                time_limit=TIME_LIMIT
            ),
        ),
        (
            "CPLEX MIP",
            lambda n: NQueensCplexMIPSolver(n).solve(
                time_limit=TIME_LIMIT
            ),
        ),
        (
            "Gurobi",
            lambda n: NQueensGurobiSolver(n).solve(
                time_limit=TIME_LIMIT
            ),
        ),
        (
            "CP-SAT",
            lambda n: NQueensCPSATSolver(n).solve(
                time_limit=TIME_LIMIT
            ),
        ),
    ]

    for n in SIZES:
        print(f"\n{'=' * 40}")
        print(f"N = {n}")
        print(f"{'=' * 40}")

        for solver_name, solve_func in solver_specs:
            result = run_solver(
                solver_name,
                n,
                solve_func,
            )
            results.append(result) 


    # Lưu kết quả vào file .csv
    try:
        with CSV_FILE.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=CSV_FIELDS,
            )
            writer.writeheader()
            writer.writerows(results)
    
    except:
        print(f"\nCannot write {CSV_FILE}. ")
        raise

    print(f"\nResults saved to: {CSV_FILE}")
    print(f"Rows written: {len(results)}")


if __name__ == "__main__":
    main()

