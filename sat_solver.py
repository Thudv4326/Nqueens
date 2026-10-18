import time
import threading

from pysat.formula import CNF
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType

class NQueensSATSolver:
    def __init__(self, n, encoding_type='seqcounter', solver_name='cadical195', time_limit=200):
        self.n = n
        self.encoding_type = encoding_type
        self.solver_name = solver_name
        self.time_limit = time_limit

        self.enc_map = {
            'seqcounter': EncType.seqcounter,
        }

    def _var(self, row, col):
        return row * self.n + col + 1

    def build_cnf(self):
        cnf = CNF()
        n = self.n
        encoding = self.enc_map.get(self.encoding_type, EncType.seqcounter)
        top_id = n * n

        # Mỗi hàng có đúng 1 quân hậu
        for row in range(n):
            row_vars = [
                self._var(row, col) 
                for col in range(n)
            ]
            enc = CardEnc.equals(lits=row_vars, bound=1, encoding=encoding, top_id=top_id)
            cnf.extend(enc)
            top_id = max(top_id, enc.nv)



        # Mỗi cột có đúng 1 quân hậu
        for col in range(n):
            col_vars = [
                self._var(row, col) 
                for row in range(n)
            ]
            enc = CardEnc.equals(lits=col_vars, bound=1, encoding=encoding, top_id=top_id)
            cnf.extend(enc)
            top_id = max(top_id, enc.nv)

        # Mỗi đường chéo có nhiều nhất 1 quân hậu
        for d in range(-n + 1, n):
            diag_vars = [
                self._var(row, col)
                for row in range(n)
                for col in range(n)
                if row - col == d
            ]
            if len(diag_vars) > 1:
                enc = CardEnc.atmost(lits=diag_vars, bound=1, encoding=encoding, top_id=top_id)
                cnf.extend(enc)
                top_id = max(top_id, enc.nv)

        for d in range(2 * n - 1):
            diag_vars = [
                self._var(row, col)
                for row in range(n)
                for col in range(n)
                if row + col == d
            ]
            if len(diag_vars) > 1:
                enc = CardEnc.atmost(lits=diag_vars, bound=1, encoding=encoding, top_id=top_id)
                cnf.extend(enc)
                top_id = max(top_id, enc.nv)
            
        return cnf

    def solve(self, time_limit=200):
        if time_limit is None:
            time_limit = self.time_limit

        start_time = time.perf_counter()
        cnf = self.build_cnf()

        timed_out = threading.Event()

        with Solver(
            name=self.solver_name,
            bootstrap_with=cnf
        ) as solver:

            elapsed = time.perf_counter() - start_time
            remaining = time_limit - elapsed

            if remaining <= 0:
                return None, elapsed, None

            def interrupt_solver():
                timed_out.set()
                solver.interrupt()

            timer = threading.Timer(remaining, interrupt_solver)
            timer.daemon = True
            timer.start()

            try:
                is_sat = solver.solve_limited(
                    expect_interrupt=True
                )
            finally:
                timer.cancel()

            elapsed = time.perf_counter() -start_time

            if timed_out.is_set():
                solver.clear_interrupt()
                return None, elapsed, None
            
            if is_sat is None:
                solver.clear_interrupt()
                return None, elapsed, None

            if not is_sat:
                return False, elapsed, None

            mdl = solver.get_model()
            true_vars = {
                var for var in mdl if var > 0
            }

            positions = []

            for row in range(self.n):
                for col in range(self.n):
                    if self._var(row, col) in true_vars:
                        positions.append((row, col))
                        break

        return True, time.perf_counter() - start_time, positions
        