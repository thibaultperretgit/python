"""Change only the shared setup cell; preserve completed student TODO cells."""
from pathlib import Path
import sys


OLD = ('        "# Run JupyterLab from the project root. Data is synthetic and generated locally.\\n",\n'
       '        "DATA = Path(\'data\')\\n",')
NEW = ('        "# Resolve synthetic data from the installed local package, independent of kernel CWD.\\n",\n'
       '        "import market_simulator\\n",\n'
       '        "DATA = Path(market_simulator.__file__).resolve().parents[1] / \'data\'\\n",')


def main(root: Path) -> None:
    files = sorted((root / 'notebooks').glob('*/*.ipynb'))
    if len(files) != 10:
        raise RuntimeError(f'expected 10 notebooks, found {len(files)}')
    for path in files:
        source = path.read_text()
        if source.count(OLD) != 1:
            raise RuntimeError(f'expected one original setup cell in {path}')
        path.write_text(source.replace(OLD, NEW))
        print(path.relative_to(root))


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
