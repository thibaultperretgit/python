"""Completed tutorials execute; exercise notebooks remain valid as users edit them."""
from pathlib import Path
import json
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('path', sorted((ROOT / 'notebooks' / 'solutions').glob('*.ipynb')))
def test_solution_notebook(path):
    import nbformat
    from nbclient import NotebookClient
    notebook = nbformat.read(path, as_version=4)
    NotebookClient(notebook, timeout=90, kernel_name='python3', resources={'metadata': {'path': str(ROOT)}}).execute()


@pytest.mark.parametrize('path', sorted((ROOT / 'notebooks' / 'exercises').glob('*.ipynb')))
def test_exercise_notebook_is_safe_and_syntax_valid(path):
    notebook = json.loads(path.read_text())
    sources = [''.join(cell['source']) for cell in notebook['cells'] if cell['cell_type'] == 'code']
    for index, source in enumerate(sources):
        compile(source, f'{path.name}:code-{index}', 'exec')


@pytest.mark.parametrize('name,variant', [
    ('Quant Assessment.ipynb', 1),
    ('Quant Assesment2.ipynb', 2),
])
def test_long_assessment_metadata_and_scale(name, variant):
    path = ROOT / 'notebooks' / 'exercises' / name
    notebook = json.loads(path.read_text())
    assert len(notebook['cells']) >= 100
    assert notebook['metadata']['assessment']['solution_included'] is False
    if variant == 2:
        assert notebook['metadata']['assessment']['variant'] == 2
