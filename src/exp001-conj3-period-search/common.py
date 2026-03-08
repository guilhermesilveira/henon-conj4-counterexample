"""Shared symbols and helpers for algebraic proofs."""

from sympy import symbols, expand, simplify, Matrix, Poly, zeros, Rational, diff
import signal
import sys

# === Standard symbols ===
x, y, a, b = symbols('x y a b')

# Standard Hénon parameters
A_VAL = Rational(14, 10)
B_VAL = Rational(3, 10)


def henon(xv, yv):
    """H(x,y) = (1 - a*x^2 + y, b*x)"""
    return (1 - a * xv**2 + yv, b * xv)


def henon_compose(n, xv=None, yv=None):
    """Compute H^n symbolically."""
    if xv is None:
        xv = x
    if yv is None:
        yv = y
    for _ in range(n):
        xv, yv = henon(xv, yv)
    return (expand(xv), expand(yv))


def require_timeout():
    """Enforce that a timeout was set via signal.alarm() before running."""
    # This is a reminder - the actual enforcement is in run_proof()
    pass


def run_proof(func, timeout_sec):
    """Run a proof function with a hard timeout. Kills if exceeded."""
    def handler(signum, frame):
        print(f"✗ TIMEOUT after {timeout_sec}s: {func.__name__}")
        sys.exit(1)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout_sec)
    try:
        func()
    finally:
        signal.alarm(0)  # cancel alarm


def run_experiment(sections, timeout_sec=300):
    """
    Run experiment sections with error isolation.

    Usage:
        run_experiment([
            ("derive k0 equation",  derive_k0),
            ("derive k1 equation",  derive_k1),
            ("parameter sweep",     sweep),
        ], timeout_sec=120)

    Each section runs in its own try/except — one crash does NOT kill the
    rest. Errors are printed immediately AND collected in the final JSON
    summary (which the marathon loop reads to decide CONTINUE vs STOP).

    Exits with code 1 if ANY section failed, 0 if all passed.
    """
    import json, traceback, time

    def _timeout_handler(signum, frame):
        print(f"\n✗ GLOBAL TIMEOUT after {timeout_sec}s — killing experiment")
        sys.exit(1)

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout_sec)

    passed = {}
    failed = {}
    t_start = time.time()

    for name, fn in sections:
        print(f"\n{'─'*60}")
        print(f"SECTION: {name}")
        print(f"{'─'*60}")
        t0 = time.time()
        try:
            result = fn()
            elapsed = time.time() - t0
            passed[name] = result
            print(f"✓ {name}  ({elapsed:.1f}s)")
        except Exception as e:
            elapsed = time.time() - t0
            tb = traceback.format_exc()
            failed[name] = {"error": str(e), "traceback": tb}
            print(f"\n✗ {name} FAILED ({elapsed:.1f}s):")
            print(tb)

    signal.alarm(0)  # cancel global timeout

    # ── Final summary (machine-readable for the marathon loop) ──
    total_elapsed = time.time() - t_start
    summary = {
        "passed":   list(passed.keys()),
        "failed":   list(failed.keys()),
        "errors":   {k: v["error"] for k, v in failed.items()},
        "n_passed": len(passed),
        "n_failed": len(failed),
        "elapsed_s": round(total_elapsed, 1),
    }

    print(f"\n{'='*60}")
    print("EXPERIMENT SUMMARY")
    print(f"{'='*60}")
    print(json.dumps(summary, indent=2))

    if failed:
        print(f"\nSTATUS: PARTIAL — {len(passed)} passed, {len(failed)} failed")
        sys.exit(1)
    else:
        print(f"\nSTATUS: OK — all {len(passed)} sections passed")
        sys.exit(0)
