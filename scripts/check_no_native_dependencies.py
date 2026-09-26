#!/usr/bin/env python3
"""Reject native sources/toolchains in this host's production dependency graph.

The gate inspects normal/build edges and source packages. It complements builds
with CC/CXX disabled; it is not an audit of arbitrary build-script behavior.
"""
import json
import os
from pathlib import Path
import subprocess

FORBIDDEN = {'cc', 'cmake', 'bindgen', 'autotools', 'meson', 'ring',
             'aws-lc-sys', 'openssl-sys', 'libz-sys', 'zstd-sys'}
NATIVE = {'.c', '.cc', '.cpp', '.cxx', '.s', '.asm', '.a', '.lib',
          '.so', '.dll', '.dylib', '.o', '.obj'}


def main():
    host = next(line.removeprefix('host: ') for line in
                subprocess.check_output(['rustc', '-vV'], text=True).splitlines()
                if line.startswith('host: '))
    tree = subprocess.check_output([
        'cargo', 'tree', '--locked', '--target', host, '--edges', 'normal,build',
        '--prefix', 'none', '--format', '{p}', '--no-dedupe'], text=True)
    selected = {tuple(line.split()[:2]) for line in tree.splitlines()}
    metadata = json.loads(subprocess.check_output([
        'cargo', 'metadata', '--locked', '--filter-platform', host,
        '--format-version', '1'], text=True))
    packages = [p for p in metadata['packages']
                if (p['name'], 'v' + p['version']) in selected]
    if not packages:
        raise RuntimeError('Empty production dependency graph')
    errors = []
    for package in packages:
        name = package['name']
        if name in FORBIDDEN or package.get('links'):
            errors.append(f'{name}: native toolchain or links metadata')
        root = Path(package['manifest_path']).parent
        for directory, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {'target', '.git'}]
            for filename in files:
                source = Path(directory) / filename
                if source.suffix.lower() in NATIVE:
                    errors.append(f'{name}: native source {source.relative_to(root)}')
    print(json.dumps({'host': host,
                      'packages': sorted(p['name'] + '@' + p['version'] for p in packages),
                      'errors': errors}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
