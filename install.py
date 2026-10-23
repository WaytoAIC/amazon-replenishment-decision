"""Install the Skill inside an explicitly selected project; never configures credentials."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def install(source, project, target, dest):
    project = Path(project).expanduser().resolve(strict=True)
    if not project.is_dir() or project == Path.home() or project == Path('/'):
        raise ValueError('Choose a business project, not the home or filesystem root')
    dest = Path(dest).expanduser().resolve() if dest else project / (
        '.agents/skills' if target == 'codex' else 'skills') / 'project-replenishment-decision'
    if dest == project or project not in dest.parents:
        raise ValueError('Destination must be inside the selected project')
    if dest.exists():
        raise ValueError('Destination already exists; review and back it up before an upgrade')
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Source does not contain SKILL.md')
    files = [source / 'SKILL.md']
    for folder in ('references', 'scripts', 'tests', 'agents'):
        for f in sorted((source / folder).rglob('*')):
            if f.is_file() and f.suffix in ('.md', '.py', '.yaml') and '__pycache__' not in f.parts:
                if f.is_symlink() or source.resolve() not in f.resolve().parents:
                    raise ValueError('Unexpected source symlink')
                files.append(f)
    dest.mkdir(parents=True)
    for f in files:
        output = dest / f.relative_to(source)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, output)
    print('Installed project-replenishment-decision:', dest)
    print('Run first-use onboarding; no MCP credentials or business rules have been configured.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', choices=['codex', 'openclaw'], default='codex')
    p.add_argument('--project', required=True)
    p.add_argument('--dest')
    p.add_argument('--repo', help='Optional GitHub owner/repository source')
    p.add_argument('--ref', help='Optional remote branch/tag (requires --repo)')
    a = p.parse_args()
    if a.ref and not a.repo:
        p.error('--ref requires --repo')
    if a.repo:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', a.repo):
            p.error('Expected GitHub owner/repository')
        if a.ref and a.ref.startswith('-'):
            p.error('Invalid ref')
        with tempfile.TemporaryDirectory(prefix='replenishment-skill-') as t:
            source = Path(t) / 'source'
            subprocess.run(['git', 'clone', '--depth', '1', '--branch', a.ref or 'main',
                            'https://github.com/' + a.repo + '.git', str(source)], check=True)
            install(source, a.project, a.target, a.dest)
    else:
        install(Path(__file__).resolve().parent, a.project, a.target, a.dest)


if __name__ == '__main__':
    main()
