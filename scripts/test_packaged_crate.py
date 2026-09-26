#!/usr/bin/env python3
"""Run tests using only the crate archive produced by cargo package."""
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import tomllib


def main():
    package = tomllib.loads(Path('Cargo.toml').read_text(encoding='utf-8'))['package']
    metadata = json.loads(subprocess.check_output([
        'cargo', 'metadata', '--locked', '--no-deps', '--format-version', '1'], text=True))
    target = Path(metadata['target_directory'])
    stem = package['name'] + '-' + package['version']
    archive = target / 'package' / (stem + '.crate')
    with tempfile.TemporaryDirectory(prefix='oxidize-webpki-package-') as directory:
        with tarfile.open(archive) as source:
            source.extractall(directory, filter='data')
        manifest = Path(directory) / stem / 'Cargo.toml'
        env = dict(os.environ, CARGO_TARGET_DIR=str(target / 'package-tests'))
        subprocess.run(['cargo', 'test', '--locked', '--manifest-path', str(manifest)],
                       env=env, check=True)


if __name__ == '__main__':
    main()
