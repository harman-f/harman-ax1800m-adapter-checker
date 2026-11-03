from pathlib import Path
import importlib.util, json, unittest
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('adapter',P/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class Fake:
    def __init__(self,platform='AX1800M',version='20261008165747',bad=None):self.platform=platform;self.version=version;self.calls=[];self.bad=bad;self.parts=0
    def request(self,path,data=None,ctype=None):
        self.calls.append((path,data,ctype))
        if path=='/cgi-bin/getversion.cgi':return f'Content-Type: text/html\nplatform:{self.platform}\ncustom:suding\nprotocol_version:{self.version}\nsystem_version:202603120956CA\nproduct_Model:v851se-yunlian-cp\n'
        if path=='/cgi-bin/downfile.cgi':
            self.parts+=1
            if self.bad==self.parts:return 'fail'
            return 'file check success' if b':'+self.md5.encode()+b'.2"' in data else 'success'
        if path.startswith('/cgi-bin/submition.cgi'):return 'success download'
        if path=='/cgi-bin/reboot.cgi':return 'ok'
        raise AssertionError(path)
class Tests(unittest.TestCase):
    def image(self,c):
        r,b=a.image('candidate');c.md5=r['md5'];return r,b
    def test_images(self):
        for k in ['candidate','rollback']:self.assertTrue(a.image(k)[1])
    def test_retained_marker_is_v05_only(self):
        self.assertTrue(a.has_v05_marker('prefix AX_INDEPENDENT v=5 suffix'))
        self.assertFalse(a.has_v05_marker('prefix AX_INDEPENDENT v=3 suffix'))
    def test_check_only_no_install(self):
        c=Fake();r,b=self.image(c);a.upload(c,r,b,False)
        self.assertFalse(any('submition' in x[0] or 'reboot' in x[0] for x in c.calls))
    def test_install_sequence(self):
        c=Fake();r,b=self.image(c);a.upload(c,r,b,True)
        self.assertIn('submition.cgi',c.calls[-2][0]);self.assertEqual(c.calls[-1][0],'/cgi-bin/reboot.cgi')
    def test_wrong_platform_no_upload(self):
        c=Fake(platform='HW301');r,b=self.image(c)
        with self.assertRaises(a.Error):a.upload(c,r,b,True)
        self.assertEqual(len(c.calls),1)
    def test_wrong_version_no_upload(self):
        c=Fake(version='unknown');r,b=self.image(c)
        with self.assertRaises(a.Error):a.upload(c,r,b,True)
        self.assertEqual(len(c.calls),1)
    def test_chunk_failure_no_install(self):
        c=Fake(bad=2);r,b=self.image(c)
        with self.assertRaises(a.Error):a.upload(c,r,b,True)
        self.assertFalse(any('submition' in x[0] for x in c.calls))
    def test_public_host_refused(self):
        with self.assertRaises(a.Error):a.Client('8.8.8.8')
    def test_september_protocol_rejected(self):
        c=Fake(version='20260905144506')
        with self.assertRaises(a.Error):a.probe(c)
    def test_exact_owner_reply(self):
        text='Content-Type: text/html\n\nsuccessfully deleted file: /tmp//wpa_ctrl_1115-0\nsuccessfully deleted file: /tmp//test.h264\nsuccessfully deleted file: /tmp//test.rgb\nsuccessfully deleted file: /tmp//nativeDict.plist\nsuccessfully deleted file: /tmp//hostapd.conf\nsuccessfully deleted file: /tmp//sdDongle.lock\nsuccessfully deleted file: /tmp//sdDongle_3.log\nresult is /tmp/ax_independent_relay_v05_rc2\nwrite data------success'
        self.assertEqual(a.acknowledge(text,'upload','ax_independent_relay_v05_rc2'),'write data------success')
        with self.assertRaises(a.Error):a.acknowledge(text,'upload','ax_independent_relay_v05_rc2',final=True)
    def test_missing_checksum_rejected(self):
        with self.assertRaises(a.Error):a.acknowledge('success','upload','x',final=True)
    def test_noisy_checksum_accepted(self):
        self.assertEqual(a.acknowledge('Content-Type: text/html\n\nfile check success','upload','x',final=True),'file check success')
        self.assertEqual(a.acknowledge('write data------success\nfile check success','upload','x',final=True),'file check success')
    def test_failure_even_with_success_suffix_rejected(self):
        for text in ['file check fail\nsuccess','error: disk full\nwrite data------success','not success','unsuccessful']:
            with self.subTest(text=text):
                with self.assertRaises(a.Error):a.acknowledge(text,'upload','x')
    def test_wrong_destination_rejected(self):
        with self.assertRaises(a.Error):a.acknowledge('result is /tmp/another\nwrite data------success','upload','x')
    def test_install_cgi_header(self):
        self.assertEqual(a.acknowledge('Content-Type: text/html\n\nsuccess download','install','x'),'success download')
    def test_noisy_full_check_still_never_installs(self):
        class Noisy(Fake):
            def request(self,path,data=None,ctype=None):
                r=super().request(path,data,ctype)
                if path=='/cgi-bin/downfile.cgi':return 'Content-Type: text/html\n\nresult is /tmp/ax_independent_relay_v05_rc2\n'+('write data------success' if r=='success' else 'write data------success\n'+r)
                return r
        c=Noisy();r,b=self.image(c);a.upload(c,r,b,False)
        self.assertFalse(any('submition' in x[0] or 'reboot' in x[0] for x in c.calls))
    def test_exact_owner_final_reply(self):
        md5='9a51df97c2e7e4efea373860fff85b1d'
        text='Content-Type: text/html\n\nmd5_str is '+md5+'\nresult is /tmp/ax_independent_relay_v05_rc2\nwrite data------success\nfinal frame\n'+md5+'\nfile check success'
        self.assertEqual(a.acknowledge(text,'upload','ax_independent_relay_v05_rc2',True,md5),'file check success')
        with self.assertRaises(a.Error):a.acknowledge(text.replace(md5,'0'*32,1),'upload','ax_independent_relay_v05_rc2',True,md5)
        with self.assertRaises(a.Error):a.acknowledge(text.replace('\n'+md5+'\n','\n'+'0'*32+'\n'),'upload','ax_independent_relay_v05_rc2',True,md5)
        with self.assertRaises(a.Error):a.acknowledge(text.replace('file check success','file check fail'),'upload','ax_independent_relay_v05_rc2',True,md5)
    def test_owner_final_reply_full_flow(self):
        class FinalNoise(Fake):
            def request(self,path,data=None,ctype=None):
                r=super().request(path,data,ctype)
                if path=='/cgi-bin/downfile.cgi' and r=='file check success':return 'Content-Type: text/html\n\nmd5_str is '+self.md5+'\nresult is /tmp/ax_independent_relay_v05_rc2\nwrite data------success\nfinal frame\n'+self.md5+'\nfile check success'
                return r
        c=FinalNoise();r,b=self.image(c);a.upload(c,r,b,False)
        self.assertEqual(c.parts,(len(b)+10239)//10240)
        self.assertFalse(any('submition' in x[0] or 'reboot' in x[0] for x in c.calls))
    def test_install_timeout_marked_unknown(self):
        class Timeout(Fake):
            def request(self,path,data=None,ctype=None):
                if 'submition.cgi' in path:raise a.Error('timeout')
                return super().request(path,data,ctype)
        c=Timeout();r,b=self.image(c)
        with self.assertRaises(a.Error) as e:a.upload(c,r,b,True)
        self.assertTrue(e.exception.install_requested)
    def test_exact_owner_install_reply(self):
        text='Content-Type: text/html\n\nlibSdAuto.so\nlibSdCommon.so\nlibSdSampleRate.so\nlibSdUtils.so\nsdDongle\nlibSdH.so\ntemp is tar -xvf  /tmp/ax_independent_relay_v05_rc2 -C /usr/data/lib/\nsuccess download'
        self.assertEqual(a.acknowledge(text,'install','ax_independent_relay_v05_rc2'),'success download')
        with self.assertRaises(a.Error):a.acknowledge(text.replace('/usr/data/lib/','/another/'),'install','ax_independent_relay_v05_rc2')
        with self.assertRaises(a.Error):a.acknowledge(text.replace('success download','failed'),'install','ax_independent_relay_v05_rc2')
    def test_install_failure_never_requests_reboot(self):
        class Failed(Fake):
            def request(self,path,data=None,ctype=None):
                r=super().request(path,data,ctype)
                if 'submition.cgi' in path:return 'tar: write error\nsuccess download'
                return r
        c=Failed();r,b=self.image(c)
        with self.assertRaises(a.Error):a.upload(c,r,b,True)
        self.assertFalse(any('reboot.cgi' in x[0] for x in c.calls))
    def test_exact_rollback_unpadded_digest(self):
        md5='fa902131b3c7a11fdd00012b8baceb5a'
        text='Content-Type: text/html\n\nmd5_str is '+md5+'\nresult is /tmp/ax_202610081657\nwrite data------success\nfinal frame\nfa902131b3c7a11fdd012b8baceb5a\nfile check success'
        self.assertEqual(a.acknowledge(text,'upload','ax_202610081657',True,md5),'file check success')
        with self.assertRaises(a.Error):a.acknowledge(text.replace('md5_str is '+md5+'\n',''),'upload','ax_202610081657',True,md5)
        with self.assertRaises(a.Error):a.acknowledge(text.replace('fa902131b3c7a11fdd012b8baceb5a','fa902131b3c7a11fdd012b8baceb5b'),'upload','ax_202610081657',True,md5)
        with self.assertRaises(a.Error):a.acknowledge(text.replace('file check success','file check fail'),'upload','ax_202610081657',True,md5)
    def test_complete_rollback_with_actual_final_reply(self):
        class Rollback(Fake):
            def request(self,path,data=None,ctype=None):
                r=super().request(path,data,ctype)
                if path=='/cgi-bin/downfile.cgi' and r=='file check success':return 'Content-Type: text/html\n\nmd5_str is '+self.md5+'\nresult is /tmp/ax_202610081657\nwrite data------success\nfinal frame\nfa902131b3c7a11fdd012b8baceb5a\nfile check success'
                if 'submition.cgi' in path:return 'Content-Type: text/html\n\nlibSdAuto.so\nlibSdCommon.so\nlibSdSampleRate.so\nlibSdUtils.so\nsdDongle\ntemp is tar -xvf  /tmp/ax_202610081657 -C /usr/data/lib/\nsuccess download'
                return r
        c=Rollback(version='20261008165747');r,b=a.image('rollback');c.md5=r['md5'];a.upload(c,r,b,True)
        self.assertEqual(c.parts,178);self.assertEqual(c.calls[-1][0],'/cgi-bin/reboot.cgi')
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    (P/'validation/UPDATER-TESTS.json').write_text(json.dumps({'tests':r.testsRun,'pass':r.wasSuccessful(),'scope':'fake transport only; no hardware/network accessed'},indent=2)+'\n')
    raise SystemExit(0 if r.wasSuccessful() else 1)

