"""Public checks for student-edited notebooks. Mock checks remain outside notebook 05."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(number: str) -> bool:
    paths = list((ROOT / 'notebooks' / 'exercises').glob(f'{number}_*.ipynb'))
    if len(paths) != 1:
        raise ValueError(f'expected one exercise notebook for {number}')
    from build_notebooks import COURSE
    tasks = next(row[3] for row in COURSE if row[0] == number)
    notebook = json.loads(paths[0].read_text())
    ns = {'__name__': '__student_notebook__'}
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            exec(''.join(cell['source']), ns)
    failures = 0
    for heading, _, _, _, check_source, _ in tasks:
        try:
            exec(check_source, ns)
            print(f'PASS {heading}')
        except Exception as exc:
            failures += 1
            print(f'FAIL {heading}: {type(exc).__name__}: {exc}')
    return failures == 0


if __name__ == '__main__':
    number = sys.argv[1] if len(sys.argv) > 1 else '01'
    if number not in {'01','02','03','04','05'}:
        raise SystemExit('Choose 01, 02, 03, 04, or 05')
    raise SystemExit(0 if check(number) else 1)
