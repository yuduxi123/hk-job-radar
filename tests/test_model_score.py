import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('model_score',ROOT/'scripts/model_score.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def config():
    return dict(mode='api',base_url='https://provider.example/v1',model='example-model',api_key_env='TEST_CAREER_KEY')
def data(state='met',status='open'):
    return dict(profile='Fictional Python student; no private contact details.',job=dict(title='Engineer Intern',description='Python role',url='https://example.com/job'),evidence=dict(status=status,core_match=True,requirements=[dict(requirement='graduation',hard=True,state=state,evidence='Candidate confirmed date' if state=='met' else 'Not confirmed')]))
def content(score=92):return json.dumps(dict(score=score,reason='技术吻合',gaps=[]))
class FakeOpener:
    def __init__(self):self.request=None
    def open(self,request,timeout):
        self.request=request;self.timeout=timeout
        return io.BytesIO(json.dumps(dict(choices=[dict(message=dict(content=content()))])).encode())
class ModelTests(unittest.TestCase):
    def test_request_and_gate_integration(self):
        client=FakeOpener()
        with patch.dict(os.environ,TEST_CAREER_KEY='test-only-not-a-real-key'):
            r=m.score(config(),data('unknown'),Path('/tmp/config.json'),opener=client)
        self.assertEqual(r['score'],79);self.assertEqual(r['grade'],'B')
        self.assertEqual(client.request.full_url,'https://provider.example/v1/chat/completions')
        body=json.loads(client.request.data)
        self.assertNotIn('test-only-not-a-real-key',json.dumps(body))
        self.assertEqual(body['model'],'example-model')
    def test_conflict_cannot_be_overridden(self):
        gate=m.prepare_input(data('not_met'))
        r=m.parse_result(content(100),gate)
        self.assertEqual((r['score'],r['grade'],r['recommendable']),(59,'C',False))
    def test_low_model_score_downgrades_a(self):
        self.assertEqual(m.parse_result(content(30),m.prepare_input(data()))['grade'],'C')
    def test_rejects_insecure_or_embedded_credentials(self):
        for url in ['http://remote.example/v1','https://key@api.example/v1','https://api.example/?key=secret','https://api.example/v1/chat/completions']:
            c=config();c['base_url']=url
            with self.assertRaises(m.SafeError):m.validate_config(c)
    def test_loopback_requires_explicit_option(self):
        c=config();c['base_url']='http://127.0.0.1:1234/v1'
        with self.assertRaises(m.SafeError):m.validate_config(c)
        c['allow_local_http']=True;self.assertEqual(m.validate_config(c),c)
    def test_refuses_redirects(self):
        with self.assertRaises(m.SafeError):m.NoRedirect().redirect_request(None,None,302,'',{},'https://other.example')
    def test_malformed_model_output_is_not_a_score(self):
        for raw in ['not json','[]','{"score":true,"reason":"x","gaps":[]}',content(101)]:
            with self.assertRaises(m.SafeError):m.parse_result(raw,m.prepare_input(data()))
    def test_closed_no_provider_call(self):
        with self.assertRaises(m.SafeError):m.score(config(),data(status='closed'),Path('/tmp/no-config'))
    def test_http_errors_do_not_leak_provider_body(self):
        class Broken:
            def open(self,*args,**kwargs):raise HTTPError('https://x',401,'SECRET',{},None)
        with patch.dict(os.environ,TEST_CAREER_KEY='test-only-key'):
            with self.assertRaisesRegex(m.SafeError,'HTTP 401') as e:m.score(config(),data(),Path('/tmp/config.json'),Broken())
        self.assertNotIn('SECRET',str(e.exception))
    def test_key_permissions_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'key';m.write_private(p,'test-only-key')
            if os.name!='nt':self.assertEqual(p.stat().st_mode & 0o777,0o600)
            with self.assertRaises(m.SafeError):m.write_private(p,'replacement')
    def test_cli_preview_works_without_key_and_never_sends(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'config.json').write_text(json.dumps(config()));(p/'input.json').write_text(json.dumps(data()))
            r=subprocess.run([sys.executable,str(ROOT/'scripts/model_score.py'),'score','--config',str(p/'config.json'),'--input',str(p/'input.json')],capture_output=True,text=True,env={k:v for k,v in os.environ.items() if k!='TEST_CAREER_KEY'})
            self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)['mode'],'preview')
