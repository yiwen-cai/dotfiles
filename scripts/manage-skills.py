#!/usr/bin/env python3
"""Manifest-owned skill deployment. No shared-root deletion; standard library only."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import uuid

REPO = Path(__file__).resolve().parents[1]


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def exists(path):
    return path.exists() or path.is_symlink()


def fingerprint(path):
    """Hash contents, relative names, permissions, and link text without following links."""
    if not exists(path):
        return None
    h = hashlib.sha256()
    def visit(p, rel):
        mode = p.lstat().st_mode
        h.update(json.dumps([rel, stat.S_IMODE(mode)], ensure_ascii=False).encode())
        if p.is_symlink():
            h.update(b'L' + os.readlink(p).encode())
        elif p.is_dir():
            h.update(b'D')
            for child in sorted(p.iterdir()):
                visit(child, str(Path(rel) / child.name))
        elif p.is_file():
            h.update(b'F' + p.read_bytes())
        else:
            raise ValueError(f'Unsupported file type: {p}')
    visit(path, '.')
    return h.hexdigest()


def copy_item(src, dst):
    if src.is_symlink():
        dst.symlink_to(os.readlink(src))
    elif src.is_dir():
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst)


def remove_item(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex)
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        temp.chmod(0o600)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def no_link_parents(path):
    for parent in [path, *path.parents]:
        if parent.is_symlink():
            raise ValueError(f'Refusing symlink destination ancestor: {parent}')


def validate_package(source):
    entry = source / 'SKILL.md'
    if not entry.exists():
        entry = source / 'SKILL.md.disabled'
    if not entry.is_file():
        raise ValueError(f'Missing skill entry: {source}')
    text = entry.read_text()
    if not text.startswith('---\n') or '\n---' not in text[4:]:
        raise ValueError(f'Invalid frontmatter: {entry}')
    fm = text.split('---', 2)[1]
    name = re.search(r'^name:\s*[\"\']?([^\s\"\']+)', fm, re.M)
    if not name or not re.fullmatch(r'[a-z0-9-]+', name[1]):
        raise ValueError(f'Invalid name: {entry}')
    if not re.search(r'^description:\s*\S', fm, re.M):
        raise ValueError(f'Missing description: {entry}')
    for p in source.rglob('*'):
        if p.is_symlink() and not p.exists():
            raise ValueError(f'Broken package link: {p}')
    return name[1]


def materialize(source, dst):
    validate_package(source)
    copy_item(source, dst)
    disabled = dst / 'SKILL.md.disabled'
    if disabled.exists():
        disabled.rename(dst / 'SKILL.md')


class Manager:
    def __init__(self, repo=REPO, home=None, state=None, bindings=None):
        self.repo = Path(repo).resolve()
        self.home = Path(home or Path.home()).resolve()
        self.state = Path(state or self.home / '.local/state/dotfiles/skills').absolute()
        self.manifest_path = self.repo / 'skills-manifest.json'
        self.manifest = read_json(self.manifest_path)
        if not self.manifest or self.manifest.get('version') != 1:
            raise ValueError('Missing or unsupported skills-manifest.json')
        self.bindings_path = Path(bindings or self.state / 'projects.json')
        self.registry_path = self.state / 'managed.json'

    def source(self, relative):
        p = (self.repo / relative).resolve()
        if not p.is_relative_to(self.repo):
            raise ValueError(f'Source outside repository: {relative}')
        return p

    def desired(self, targets):
        wanted, roots, pending, discovery = {}, [], [], {}
        for name in targets:
            if name == 'projects':
                continue
            target = self.manifest['targets'][name]
            if not target['enabled']:
                continue
            root = self.home / target['path']
            no_link_parents(root)
            roots.append(root)
            # Roots sharing a discovery group are scanned by the same agent, so a name
            # may live in only one of them; separate groups (other tools) may mirror it.
            group = discovery.setdefault(target.get('discovery_group', name), [])
            ids = [s for profile in target['profiles'] for s in self.manifest['profiles'][profile]]
            ids += target.get('optional', [])
            if len(ids) != len(set(ids)):
                raise ValueError(f'Duplicate entries in target: {name}')
            for skill in ids:
                if not re.fullmatch(r'[a-z0-9-]+', skill):
                    raise ValueError(f'Unsafe skill name: {skill}')
                entry = self.manifest['entries'][skill]
                if entry['status'] not in ('global', 'optional'):
                    raise ValueError(f'Cannot globally enable {skill}: {entry["status"]}')
                wanted[str(root / skill)] = {'source': str(self.source(entry['source']))}
                group.append(skill)
        if 'projects' in targets:
            bindings = read_json(self.bindings_path, {})
            for skill in self.manifest['projects']:
                raw = bindings.get(skill)
                if not raw:
                    pending.append(skill)
                    continue
                project = Path(raw).absolute()
                no_link_parents(project)
                if not project.is_dir():
                    raise ValueError(f'Missing bound project: {project}')
                root = project / 'docs/agent-skills'
                no_link_parents(root)
                roots.append(root)
                wanted[str(root / skill)] = {'source': str(self.source(self.manifest['entries'][skill]['source']))}
                agent = project / 'AGENTS.md'
                if agent.is_symlink():
                    raise ValueError(f'Refusing to replace project instruction link: {agent}')
                old = agent.read_text() if agent.exists() else ''
                begin, end = '<!-- dotfiles-skill-route:start -->', '<!-- dotfiles-skill-route:end -->'
                old = re.sub(re.escape(begin) + r'.*?' + re.escape(end) + r'\n?', '', old, flags=re.S)
                relative = f'docs/agent-skills/{skill}/SKILL.md'
                if skill == 'publish-note':
                    old = old.replace('.claude/skills/publish-note/SKILL.md', relative)
                    old = old.replace('（Claude Code 里注册为 `publish-note` skill，其他工具直接当 checklist 读）', '（由本项目 AGENTS.md 按需路由，各工具均可读取）')
                route = self.manifest['projects'][skill]['trigger']
                content = (old.rstrip() + '\n\n' if old.strip() else '') + f'{begin}\n## 项目专属工作流\n\n{route}时，先阅读 [{skill}]({relative})。仅在该场景加载，保留本文件其他项目约定。\n{end}\n'
                wanted[str(agent)] = {'content': content, 'mode': stat.S_IMODE(agent.stat().st_mode) if agent.exists() else 0o644}
                roots.append(agent)  # exact file scope, not the whole project
        # Roots inside one discovery group must not expose the same managed name.
        for name, names in discovery.items():
            if len(names) != len(set(names)):
                raise ValueError(f'Duplicate global skill name in discovery group: {name}')
        return wanted, roots, pending

    def plan(self, targets, adopt=None):
        wanted, roots, pending = self.desired(targets)
        registry = read_json(self.registry_path, {})
        baseline = read_json(Path(adopt), {}) if adopt else {}
        def scoped(p):
            q = Path(p)
            return any(q == r or q.parent == r for r in roots)
        owned = {p: h for p, h in registry.items() if scoped(p)}
        for p, h in baseline.items():
            if scoped(p):
                owned.setdefault(p, h)
        ops, after = [], dict(registry)
        with tempfile.TemporaryDirectory() as tmp:
            for index, path in enumerate(sorted(set(wanted) | set(owned))):
                p = Path(path)
                if p.name == '.system':
                    raise ValueError('Protected .system target')
                no_link_parents(p.parent)
                before = fingerprint(p)
                if path in owned and owned[path] != before:
                    raise ValueError(f'Changed managed/adopted item; preserve edits: {p}')
                if before is not None and path not in owned:
                    raise ValueError(f'Unmanaged collision: {p}')
                spec = wanted.get(path)
                expected = None
                if spec:
                    stage = Path(tmp) / str(index)
                    if 'source' in spec:
                        materialize(Path(spec['source']), stage)
                    else:
                        stage.write_text(spec['content'])
                        stage.chmod(spec['mode'])
                    expected = fingerprint(stage)
                    after[path] = expected
                else:
                    after.pop(path, None)
                if expected != before:
                    ops.append({'path': path, 'before': before, 'after': expected, **(spec or {})})
        unknown = []
        for root in roots:
            if root.is_dir():
                unknown += [str(p) for p in root.iterdir() if not p.name.startswith('.') and str(p) not in wanted and str(p) not in owned]
        return {'version': 1, 'repo': str(self.repo), 'home': str(self.home), 'state': str(self.state),
                'targets': targets, 'adopt': str(Path(adopt).absolute()) if adopt else None,
                'manifest_hash': fingerprint(self.manifest_path), 'bindings_hash': fingerprint(self.bindings_path),
                'registry_before': registry, 'registry_after': after, 'operations': ops,
                'unknown_preserved': sorted(unknown), 'pending_projects': pending}

    @contextlib.contextmanager
    def lock(self):
        no_link_parents(self.state)
        self.state.mkdir(parents=True, exist_ok=True)
        with (self.state / 'lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def apply(self, plan):
        with self.lock():
            if plan != self.plan(plan['targets'], plan.get('adopt')):
                raise ValueError('Stale plan: source, destination, configuration or ownership changed')
            if not plan['operations'] and plan['registry_before'] == plan['registry_after']:
                return {'status': 'unchanged'}
            snapshot = self.state / 'snapshots' / uuid.uuid4().hex
            snapshot.mkdir(parents=True)
            ops = plan['operations']
            journal = {'plan': plan, 'status': 'preparing', 'completed': []}
            atomic_json(snapshot / 'snapshot.json', journal)
            try:
                # Prepare every replacement and backup before the first target mutation.
                for i, op in enumerate(ops):
                    p = Path(op['path'])
                    if exists(p):
                        copy_item(p, snapshot / f'before-{i}')
                    if op['after']:
                        stage = snapshot / f'after-{i}'
                        if 'source' in op:
                            materialize(Path(op['source']), stage)
                        else:
                            stage.write_text(op['content']); stage.chmod(op['mode'])
                        if fingerprint(stage) != op['after']:
                            raise ValueError('Source changed during staging')
                journal['status'] = 'applying'; atomic_json(snapshot / 'snapshot.json', journal)
                for i, op in enumerate(ops):
                    p = Path(op['path'])
                    no_link_parents(p.parent)
                    if fingerprint(p) != op['before']:
                        raise ValueError(f'Destination changed during apply: {p}')
                    # Journal intention before touching the destination, for crash recovery.
                    journal['completed'].append(i); atomic_json(snapshot / 'snapshot.json', journal)
                    self.replace(p, snapshot / f'after-{i}' if op['after'] else None)
                    if fingerprint(p) != op['after']:
                        raise ValueError(f'Post-write verification failed: {p}')
                atomic_json(self.registry_path, plan['registry_after'])
                journal['status'] = 'applied'; atomic_json(snapshot / 'snapshot.json', journal)
            except Exception:
                for i in reversed(journal['completed']):
                    self.replace(Path(ops[i]['path']), snapshot / f'before-{i}' if ops[i]['before'] else None)
                atomic_json(self.registry_path, plan['registry_before'])
                journal['status'] = 'failed-restored'; atomic_json(snapshot / 'snapshot.json', journal)
                raise
            return {'status': 'applied', 'snapshot': str(snapshot), 'operations': len(ops)}

    @staticmethod
    def replace(dst, source):
        no_link_parents(dst.parent)
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Stage on the destination filesystem; never recurse through an existing link.
        stage = dst.with_name('.skill-stage-' + uuid.uuid4().hex)
        old = dst.with_name('.skill-old-' + uuid.uuid4().hex)
        try:
            if source:
                copy_item(source, stage)
            if exists(dst):
                os.replace(dst, old)
            try:
                if source:
                    os.replace(stage, dst)
            except Exception:
                if exists(old):
                    os.replace(old, dst)
                raise
            if exists(old):
                remove_item(old)
        finally:
            if exists(stage):
                remove_item(stage)

    def rollback(self, snapshot):
        with self.lock():
            snapshot = Path(snapshot).absolute()
            if not snapshot.is_relative_to(self.state / 'snapshots'):
                raise ValueError('Snapshot must belong to this state directory')
            journal = read_json(snapshot / 'snapshot.json')
            if journal['status'] != 'applied':
                raise ValueError(f'Cannot rollback snapshot status: {journal["status"]}')
            plan = journal['plan']; registry = read_json(self.registry_path, {})
            changed_keys = set(plan['registry_before']) | set(plan['registry_after'])
            changed_keys = {k for k in changed_keys if plan['registry_before'].get(k) != plan['registry_after'].get(k)}
            for key in changed_keys:
                if registry.get(key) != plan['registry_after'].get(key):
                    raise ValueError(f'Later ownership changes; rollback conflict: {key}')
            for i, op in enumerate(plan['operations']):
                if fingerprint(Path(op['path'])) != op['after']:
                    raise ValueError(f'Later edits; rollback conflict: {op["path"]}')
                if fingerprint(snapshot / f'before-{i}') != op['before']:
                    raise ValueError('Backup integrity mismatch')
            for i, op in reversed(list(enumerate(plan['operations']))):
                self.replace(Path(op['path']), snapshot / f'before-{i}' if op['before'] else None)
            for key in changed_keys:
                if key in plan['registry_before']:
                    registry[key] = plan['registry_before'][key]
                else:
                    registry.pop(key, None)
            atomic_json(self.registry_path, registry)
            journal['status'] = 'rolled-back'; atomic_json(snapshot / 'snapshot.json', journal)
            return {'status': 'rolled-back', 'snapshot': str(snapshot)}

    def validate(self):
        counts = {}
        for name, entry in self.manifest['entries'].items():
            source = self.source(entry['source'])
            if not source.exists():
                raise ValueError(f'Missing source: {name}')
            status = entry['status']; counts[status] = counts.get(status, 0) + 1
            if status in ('global', 'project'):
                if validate_package(source) != name:
                    raise ValueError(f'Entry name differs from manifest: {name}')
            elif (source / 'SKILL.md').exists():
                raise ValueError(f'Inactive entry is discoverable: {source}')
        return counts


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['plan', 'apply', 'check', 'rollback', 'validate'])
    p.add_argument('--repo', type=Path, default=REPO)
    p.add_argument('--home', type=Path)
    p.add_argument('--state', type=Path)
    p.add_argument('--bindings', type=Path)
    p.add_argument('--targets', default='codex,agents,claude')
    p.add_argument('--adopt', type=Path, help='Explicit initial path-to-hash ownership baseline')
    p.add_argument('--out', type=Path)
    p.add_argument('--plan', type=Path)
    p.add_argument('--snapshot', type=Path)
    a = p.parse_args()
    m = Manager(a.repo, a.home, a.state, a.bindings)
    if a.command == 'validate':
        result = m.validate()
    elif a.command == 'apply':
        if not a.plan: p.error('apply requires --plan')
        result = m.apply(read_json(a.plan))
    elif a.command == 'rollback':
        if not a.snapshot: p.error('rollback requires --snapshot')
        result = m.rollback(a.snapshot)
    else:
        result = m.plan(a.targets.split(','), a.adopt)
        if a.command == 'check' and result['operations']:
            print(json.dumps(result, ensure_ascii=False, indent=2)); return 1
    if a.out:
        atomic_json(a.out, result)
        print(json.dumps({'output': str(a.out), 'operations': len(result.get('operations', []))}, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
