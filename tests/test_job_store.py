import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('job_store', ROOT / 'scripts/job_store.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def job(**kw):
    return dict(company='示例公司', title='开发实习', url='https://example.com/jobs/1',
                types=['daily_internship'], verified_at='2026-10-24T10:00:00+08:00', **kw)


class StoreTests(unittest.TestCase):
    def test_identity_upgrade_and_old_link(self):
        first = m.ingest([], [job()])
        update = job(official_url='https://careers.example.com/1', official_company_id='co', job_id='1')
        second = m.ingest(first, [update])
        self.assertEqual(first[0]['key'], second[0]['key'])
        third = job(); third['url'] = update['official_url']
        self.assertEqual(len(m.ingest(second, [third])), 1)
        self.assertEqual(len(m.ingest(second, [job()])), 1)

    def test_stale_and_partial(self):
        rows = m.ingest([], [job(status='open', cities=['深圳'])])
        stale = job(status='closed'); stale['verified_at'] = '2026-10-23T00:00:00+08:00'
        self.assertEqual(m.ingest(rows, [stale]), rows)
        update = job(); update['title'] = 'Python开发'
        result = m.ingest(rows, [update])[0]
        self.assertEqual(result['cities'], ['深圳'])
        self.assertEqual(len(result['history']), 1)

    def test_bad_data_and_conflicts(self):
        for bad in [job(status='invented'), job(official_url=123), job(job_id=123)]:
            with self.assertRaises((ValueError, TypeError)):
                m.ingest([], [bad])
        rows = m.ingest([], [job(official_company_id='co', job_id='1')])
        with self.assertRaises(ValueError):
            m.ingest(rows, [job(official_company_id='co', job_id='2')])
        with self.assertRaises(ValueError):
            m.ingest(rows + rows, [])

    def test_ambiguous_merge_rejected(self):
        a = job(); b = job(); b['url'] = 'https://example.com/2'
        rows = m.ingest([], [a, b])
        with self.assertRaises(ValueError):
            m.ingest(rows, [job(official_url=b['url'])])

    def test_url_routes_and_parameter_order(self):
        self.assertEqual(m.clean_url('https://example.com/?x=2&x=1&utm_source=a#job/3'),
                         'https://example.com/?x=2&x=1#job/3')

    def test_cli_lock_and_no_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Path(temp) / 'jobs.jsonl'; inp = Path(temp) / 'input.json'
            inp.write_text(json.dumps([job()]))
            cmd = [sys.executable, str(ROOT / 'scripts/job_store.py'), '--store', str(store), 'ingest', '--input', str(inp)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            before = store.read_bytes()
            lock = Path(str(store) + '.lock'); lock.mkdir()
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            self.assertEqual(store.read_bytes(), before)
            lock.rmdir()
            inp.write_text(json.dumps([job(), job(status='bad')]))
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            self.assertEqual(store.read_bytes(), before)

    def test_install_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            cmd = [sys.executable, str(ROOT / 'scripts/install.py'), '--dest', temp]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            installed = Path(temp) / 'hk-job-radar' / 'SKILL.md'
            self.assertTrue(installed.is_file())
            before = installed.read_bytes()
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            self.assertEqual(installed.read_bytes(), before)

if __name__ == '__main__':
    unittest.main()
