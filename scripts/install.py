#!/usr/bin/env python3
"""Install this self-contained skill; never overwrite an existing installation."""
import argparse
import os
from pathlib import Path
import shutil
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('codex', 'agents'), default='codex')
    parser.add_argument('--dest', type=Path, help='Custom skills parent directory')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent
    base = args.dest or (Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills'
                         if args.target == 'codex' else Path.home() / '.agents' / 'skills')
    base = base.expanduser().resolve()
    dest = base / 'hk-job-radar'
    try:
        if dest.exists():
            raise ValueError(f'Already installed: {dest}. Back it up and move it away before reinstalling.')
        if not (source / 'SKILL.md').is_file():
            raise ValueError('Incomplete distribution: SKILL.md is missing')
        if base == source or source in base.parents:
            raise ValueError('Installation directory cannot be inside the source skill')
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.career-install-', dir=base) as stage:
            staged = Path(stage) / 'hk-job-radar'
            shutil.copytree(source, staged, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store', '.git'))
            # Exclusive reservation prevents a concurrent install from replacing an existing skill.
            dest.mkdir()
            try:
                for child in staged.iterdir():
                    shutil.move(str(child), str(dest / child.name))
            except BaseException:
                shutil.rmtree(dest)
                raise
        print(f'Installed: {dest}\nRestart or reopen your assistant to discover the skill.')
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
