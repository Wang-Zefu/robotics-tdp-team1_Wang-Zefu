"""
Parallel alpha-parameter benchmark for tactical_engine.py.

This follows the same multiprocessing batch flow as run_behavior_comparison.py,
but compares fixed tactical-engine alpha (α) values directly.
"""

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metrics_collector import MetricsCollector
from simple_soccer_sim3 import SoccerSimulator


def _alpha_label(alpha: float) -> str:
    return f"a{alpha:.2f}".replace('.', 'p')


def _force_fixed_alpha(sim: SoccerSimulator, blue_alpha: float, red_alpha: float) -> None:
    """Freeze both HTSM instances at fixed alpha values for the whole match."""
    for htsm, alpha in ((sim.blue_htsm, blue_alpha), (sim.red_htsm, red_alpha)):
        htsm.current_alpha = alpha
        htsm.target_alpha = alpha
        htsm.drift_speed = 0.0
        htsm.beta = 0.0

    sim.blue_profile = sim.blue_htsm.get_profile()
    sim.red_profile = sim.red_htsm.get_profile()


def _run_one(args_tuple):
    blue_alpha, red_alpha, match_duration, enable_falls, output_dir, match_idx = args_tuple
    config_name = f"{_alpha_label(blue_alpha)}_vs_{_alpha_label(red_alpha)}"

    try:
        sim = SoccerSimulator(
            blue_personality='aggressive',
            red_personality='aggressive',
            enable_falls=enable_falls,
            match_duration=match_duration,
            headless=True,
        )
        _force_fixed_alpha(sim, blue_alpha, red_alpha)

        collector = MetricsCollector(sim)
        while sim.game_state.value != 'MATCH_OVER':
            sim.step()
            collector.record_step()

        summary = collector.get_summary()
        summary['blue_alpha'] = blue_alpha
        summary['red_alpha'] = red_alpha
        summary['config_name'] = config_name

        filename = f"{config_name}_match{match_idx:03d}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)

        return (config_name, match_idx, True, summary['blue_goals'], summary['red_goals'], None)
    except Exception as e:
        return (config_name, match_idx, False, 0, 0, str(e))


def _build_configs(alphas, pairings):
    if pairings:
        configs = []
        for p in pairings:
            parts = p.split('_vs_')
            if len(parts) != 2:
                print(f"  Warning: skipping invalid pairing '{p}' (expected '<blue>_vs_<red>')")
                continue
            try:
                configs.append((float(parts[0]), float(parts[1])))
            except ValueError:
                print(f"  Warning: skipping non-numeric pairing '{p}'")
        return configs

    return list(product(alphas, alphas))


def main():
    parser = argparse.ArgumentParser(description='Run parallel fixed-alpha comparison matches')
    parser.add_argument('--alphas', '-a', type=float, nargs='+', default=[0.2, 0.5, 0.8],
                        help='Alpha values to benchmark (default: 0.2 0.5 0.8).')
    parser.add_argument('--pairings', '-p', nargs='*',
                        help="Optional explicit pairings, e.g. '0.2_vs_0.8 0.5_vs_0.5'.")
    parser.add_argument('--matches', '-m', type=int, default=20,
                        help='Matches per configuration (default: 20).')
    parser.add_argument('--duration', '-d', type=int, default=300,
                        help='Match duration in seconds (default: 300).')
    parser.add_argument('--output', '-o', default='alpha_results',
                        help='Output directory for match JSONs (default: alpha_results/).')
    parser.add_argument('--workers', '-w', type=int,
                        default=min(6, mp.cpu_count()),
                        help=f'Parallel workers (default: min(6, cpu_count)={min(6, mp.cpu_count())})')
    parser.add_argument('--no-falls', action='store_true',
                        help='Disable fall simulation (faster, more deterministic).')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    configs = _build_configs(args.alphas, args.pairings)
    if not configs:
        raise SystemExit('No valid alpha configurations to run.')

    total_matches = len(configs) * args.matches
    workers = min(args.workers, total_matches)

    print('=' * 70)
    print('ALPHA PARAMETER COMPARISON RUNNER  (parallel headless)')
    print('=' * 70)
    print(f'  Alpha configs   : {len(configs)}')
    print(f'  Matches each    : {args.matches}')
    print(f'  Total matches   : {total_matches}')
    print(f'  Match duration  : {args.duration}s (~{args.duration / 60:.1f} sim-min each)')
    print(f'  Worker threads  : {workers}')
    print(f"  Falls           : {'OFF' if args.no_falls else 'ON'}")
    print(f'  Output dir      : {args.output}/')
    print('=' * 70)

    work_items = []
    for blue_alpha, red_alpha in configs:
        for i in range(args.matches):
            work_items.append((blue_alpha, red_alpha, args.duration,
                               not args.no_falls, args.output, i + 1))

    start_time = time.time()
    completed = 0
    errors = 0

    with mp.Pool(processes=workers) as pool:
        for result in pool.imap_unordered(_run_one, work_items):
            config_name, match_idx, success, bg, rg, err = result
            completed += 1

            if success:
                elapsed = time.time() - start_time
                remaining = (elapsed / completed) * (total_matches - completed)
                print(f'  [{completed:3d}/{total_matches}]  {config_name:<20s} '
                      f'match {match_idx:03d}  B{bg}-{rg}R  (ETA {remaining:.0f}s)')
            else:
                errors += 1
                print(f'  [{completed:3d}/{total_matches}]  {config_name} '
                      f'match {match_idx:03d}  ERROR: {err}')

    total_time = time.time() - start_time
    print(f"\n{'=' * 70}")
    print(f'✓ DONE: {completed - errors}/{total_matches} matches in {total_time:.1f}s ({total_time / 60:.1f} min)')
    if errors:
        print(f'  ⚠ {errors} errors')
    print('\n  Next:')
    print(f'    python metrics_analyzer.py --input {args.output} --output alpha_analysis')
    print('=' * 70)


if __name__ == '__main__':
    mp.freeze_support()
    main()
