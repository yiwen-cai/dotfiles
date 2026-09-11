import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('manage', Path(__file__).resolve().parents[1] / 'scripts/manage-skills.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class DeploymentTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.repo = self.base / 'repo'; self.repo.mkdir()
        self.home = self.base / 'home'; self.home.mkdir()
        self.source = self.repo / 'skills/alpha'; self.source.mkdir(parents=True)
        (self.source / 'SKILL.md').write_text('---\nname: alpha\ndescription: A specific fixture.\n---\nAlpha\n')
        self.target = self.home / '.codex/skills'; self.target.mkdir(parents=True)
        self.manifest = {'version': 1, 'entries': {'alpha': {'source': 'skills/alpha', 'status': 'global'}},
                         'profiles': {'core': ['alpha']}, 'targets': {'codex': {'enabled': True, 'path': '.codex/skills', 'profiles': ['core']},
                         'claude': {'enabled': False, 'path': '.claude/skills', 'profiles': ['core']}}, 'projects': {}}
        self.save()

    def tearDown(self): self.tmp.cleanup()

    def save(self):
        (self.repo / 'skills-manifest.json').write_text(json.dumps(self.manifest))
        self.manager = m.Manager(self.repo, self.home)

    def apply(self, adopt=None): return self.manager.apply(self.manager.plan(['codex'], adopt))

    def baseline(self, paths):
        p = self.base / 'baseline.json'; p.write_text(json.dumps({str(x): m.fingerprint(x) for x in paths})); return p

    def test_migrate_preserve_unknown_system_idempotent_and_rollback(self):
        old = self.target / 'old'; old.mkdir(); (old / 'data').write_text('original')
        unknown = self.target / 'unknown'; unknown.mkdir(); (unknown / 'data').write_text('user')
        system = self.target / '.system'; system.mkdir(); (system / 'sentinel').write_text('system')
        hashes = [m.fingerprint(p) for p in [old, unknown, system]]
        result = self.apply(self.baseline([old]))
        self.assertFalse(old.exists())
        self.assertEqual(m.fingerprint(self.target / 'alpha'), m.fingerprint(self.source))
        self.assertEqual([m.fingerprint(p) for p in [unknown, system]], hashes[1:])
        self.assertEqual(self.apply()['status'], 'unchanged')
        self.manager.rollback(result['snapshot'])
        self.assertEqual(m.fingerprint(old), hashes[0]); self.assertFalse((self.target / 'alpha').exists())
        self.assertEqual(m.fingerprint(unknown), hashes[1])

    def test_unmanaged_collision(self):
        (self.target / 'alpha').mkdir()
        with self.assertRaisesRegex(ValueError, 'Unmanaged'): self.apply()

    def test_modified_managed_package(self):
        self.apply(); (self.target / 'alpha/SKILL.md').write_text('user edit')
        with self.assertRaisesRegex(ValueError, 'Changed managed'): self.apply()

    def test_stale_source_and_destination(self):
        plan = self.manager.plan(['codex']); (self.source / 'SKILL.md').write_text((self.source / 'SKILL.md').read_text() + 'new')
        with self.assertRaisesRegex(ValueError, 'Stale'): self.manager.apply(plan)
        plan = self.manager.plan(['codex']); (self.target / 'alpha').mkdir()
        with self.assertRaises(ValueError): self.manager.apply(plan)

    def test_target_symlink_does_not_touch_external_directory(self):
        self.target.rmdir(); outside = self.base / 'outside'; outside.mkdir(); (outside / 'sentinel').write_text('keep')
        self.target.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'): self.apply()
        self.assertEqual((outside / 'sentinel').read_text(), 'keep')

    def test_owned_skill_symlink_removed_without_deleting_referent(self):
        outside = self.base / 'outside'; outside.mkdir(); (outside / 'sentinel').write_text('keep')
        old = self.target / 'old'; old.symlink_to(outside)
        result = self.apply(self.baseline([old]))
        self.assertEqual((outside / 'sentinel').read_text(), 'keep')
        self.manager.rollback(result['snapshot']); self.assertTrue(old.is_symlink())

    def test_missing_source_and_broken_link(self):
        (self.source / 'SKILL.md').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing'): self.apply()
        (self.source / 'SKILL.md').write_text('---\nname: alpha\ndescription: fixture\n---\n')
        (self.source / 'broken').symlink_to(self.base / 'missing')
        with self.assertRaisesRegex(ValueError, 'Broken'): self.apply()

    def test_failed_stage_changes_nothing(self):
        plan = self.manager.plan(['codex'])
        original = m.copy_item
        def fail(src, dst):
            if dst.name.startswith('after-'): raise OSError('injected disk error')
            return original(src, dst)
        with patch.object(m, 'copy_item', side_effect=fail):
            with self.assertRaises(OSError): self.manager.apply(plan)
        self.assertFalse((self.target / 'alpha').exists())

    def test_partial_apply_is_restored(self):
        old = self.target / 'old'; old.mkdir(); (old / 'data').write_text('before')
        original = self.manager.replace; calls = []
        def fail_second(dst, source):
            calls.append(str(dst))
            if len(calls) == 2: raise OSError('injected replace error')
            return original(dst, source)
        with patch.object(self.manager, 'replace', side_effect=fail_second):
            with self.assertRaises(OSError): self.apply(self.baseline([old]))
        self.assertFalse((self.target / 'alpha').exists()); self.assertEqual((old / 'data').read_text(), 'before')

    def test_rollback_preserves_later_edit(self):
        result = self.apply(); p = self.target / 'alpha/SKILL.md'; p.write_text('later edit')
        with self.assertRaisesRegex(ValueError, 'Later edits'): self.manager.rollback(result['snapshot'])
        self.assertEqual(p.read_text(), 'later edit')

    def test_disabled_target(self):
        self.assertEqual(self.manager.plan(['claude'])['operations'], [])
        self.assertFalse((self.home / '.claude').exists())

    def test_optional_only_selected_entry_is_enabled(self):
        optional = self.repo / 'optional/beta'; optional.mkdir(parents=True)
        (optional / 'SKILL.md.disabled').write_text('---\nname: beta\ndescription: Fixture\n---\n')
        other = self.repo / 'optional/gamma'; other.mkdir(); (other / 'SKILL.md.disabled').write_text('not selected')
        self.manifest['entries']['beta'] = {'source': 'optional/beta', 'status': 'optional'}
        self.manifest['targets']['codex']['optional'] = ['beta']; self.save()
        self.apply()
        self.assertTrue((self.target / 'beta/SKILL.md').exists()); self.assertFalse((self.target / 'gamma').exists())
        self.assertTrue((optional / 'SKILL.md.disabled').exists())

    def test_project_route_preserves_existing_content_and_is_idempotent(self):
        project = self.base / 'project'; project.mkdir(); agent = project / 'AGENTS.md'; agent.write_text('# Existing rules\nKeep this exactly.\n')
        before = agent.read_text()
        self.manifest['projects']['alpha'] = {'trigger': '处理专属任务'}; self.save()
        self.manager.bindings_path.parent.mkdir(parents=True)
        self.manager.bindings_path.write_text(json.dumps({'alpha': str(project)}))
        plan = self.manager.plan(['projects'], self.baseline([agent])); result = self.manager.apply(plan)
        self.assertTrue(agent.read_text().startswith(before.rstrip()))
        self.assertEqual(self.manager.plan(['projects'])['operations'], [])
        self.manager.rollback(result['snapshot']); self.assertEqual(agent.read_text(), before)

    def test_duplicate_global_names_rejected(self):
        self.manifest['targets']['agents'] = {'enabled': True, 'path': '.agents/skills', 'profiles': ['core']}; self.save()
        with self.assertRaisesRegex(ValueError, 'Duplicate global'): self.manager.plan(['codex', 'agents'])


if __name__ == '__main__': unittest.main()
