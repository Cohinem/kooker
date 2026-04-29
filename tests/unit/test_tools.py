#!/usr/bin/env python
"""
kooker unit tests: KookerTools
"""

# import tarfile
# from tarfile import TarInfo
from unittest import TestCase, main
from unittest.mock import Mock, patch
from io import StringIO
from kooker.config import Config
from kooker.utils.curl import CurlHeader
from kooker.tools import KookerTools
from kooker.utils.curl import GetURLpyCurl
import collections

collections.Callable = collections.abc.Callable
BUILTINS = "builtins"
BOPEN = BUILTINS + '.open'


class KookerToolsTestCase(TestCase):
    """Test KookerTools()."""

    def setUp(self):
        Config().getconf()
        str_local = 'kooker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

    def tearDown(self):
        self.lrepo.stop()

    @patch('kooker.tools.GetURL')
    def test_01_init(self, mock_geturl):
        """Test01 KookerTools() constructor."""
        mock_geturl.return_value = None
        utools = KookerTools(self.local)
        self.assertTrue(mock_geturl.called)
        self.assertEqual(utools.localrepo, self.local)

    @patch.object(GetURLpyCurl, 'is_available')
    @patch('kooker.tools.Msg')
    def test_02__instructions(self, mock_msg, mock_gupycurl):
        """Test02 KookerTools()._instructions()."""
        mock_gupycurl.return_value = True

        utools = KookerTools(self.local)
        utools._instructions()
        self.assertTrue(mock_msg.return_value.out.call_count, 2)

    @patch.object(GetURLpyCurl, 'is_available')
    def test_03__version2int(self, mock_gupycurl):
        """Test03 KookerTools()._version2int()."""
        mock_gupycurl.return_value = True

        utools = KookerTools(self.local)
        status = utools._version2int("2.4")
        self.assertEqual(status, 2004000)

    @patch.object(GetURLpyCurl, 'is_available')
    def test_04__version_isok(self, mock_gupycurl):
        """Test04 KookerTools()._version_isok()."""
        mock_gupycurl.return_value = True

        Config.conf['tarball_release'] = "1.3"
        utools = KookerTools(self.local)
        status = utools._version_isok("2.4")
        self.assertTrue(status)

        Config.conf['tarball_release'] = "2.3"
        utools = KookerTools(self.local)
        status = utools._version_isok("1.4")
        self.assertFalse(status)

    @patch.object(GetURLpyCurl, 'is_available')
    @patch('kooker.tools.FileUtil.getdata')
    def test_05_is_available(self, mock_fuget, mock_gupycurl):
        """Test05 KookerTools().is_available()."""
        mock_gupycurl.return_value = True

        Config.conf['tarball_release'] = "2.3"
        mock_fuget.return_value = "2.3\n"
        utools = KookerTools(self.local)
        status = utools.is_available()
        self.assertTrue(status)

    @patch.object(GetURLpyCurl, 'is_available')
    @patch('kooker.tools.FileUtil.remove')
    @patch('kooker.tools.FileUtil.register_prefix')
    @patch('kooker.tools.os.listdir')
    def test_06_purge(self, mock_lsdir, mock_fureg, mock_furm,
                      mock_gupycurl):
        """Test06 KookerTools().purge()."""
        mock_gupycurl.return_value = True

        mock_lsdir.side_effect = [["f1", "f2"],
                                  ["f3", "f4"],
                                  ["f5", "f6"]]
        mock_fureg.side_effect = [None, None, None, None, None, None]
        mock_furm.side_effect = [None, None, None, None, None, None]
        utools = KookerTools(self.local)
        utools.purge()
        self.assertTrue(mock_lsdir.call_count, 3)
        self.assertTrue(mock_fureg.call_count, 4)
        self.assertTrue(mock_furm.call_count, 4)

    @patch.object(GetURLpyCurl, 'is_available')
    @patch('kooker.tools.GetURL.get')
    @patch('kooker.tools.FileUtil.remove')
    @patch('kooker.tools.FileUtil.mktmp')
    def test_07__download(self, mock_fumktmp, mock_furm, mock_geturl,
                          mock_gupycurl):
        """Test07 KookerTools()._download()."""
        mock_gupycurl.return_value = True

        url = "https://down/file"
        hdr = CurlHeader()
        hdr.data["X-ND-HTTPSTATUS"] = "HTTP/1.1 200 OK"
        mock_fumktmp.return_value = "/tmp/tmpf"
        mock_furm.return_value = None
        mock_geturl.return_value = (hdr, "content type...")
        utools = KookerTools(self.local)
        status = utools._download(url)
        self.assertTrue(mock_fumktmp.called)
        self.assertEqual(status, "/tmp/tmpf")

        url = "https://down/file"
        hdr = CurlHeader()
        hdr.data["X-ND-HTTPSTATUS"] = "HTTP/1.1 401 FAIL"
        mock_fumktmp.return_value = "/tmp/tmpf"
        mock_furm.return_value = None
        mock_geturl.return_value = (hdr, "content type...")
        utools = KookerTools(self.local)
        status = utools._download(url)
        self.assertTrue(mock_furm.called)
        self.assertEqual(status, "")

    # @patch('kooker.tools.os.path.isfile')
    # @patch('kooker.tools.os.path.realpath')
    # @patch('kooker.tools.os.path.exists')
    # @patch.object(KookerTools, '_download')
    # def test_08__get_file(self, mock_downl, mock_exists, mock_rpath,
    #                       mock_isfile):
    #     """Test08 KookerTools()._get_file()."""
    #     url = ""
    #     mock_downl.return_value = ""
    #     mock_exists.return_value = False
    #     mock_isfile.return_value = False
    #     utools = KookerTools(self.local)
    #     status = utools._get_file(url)
    #     self.assertFalse(mock_downl.called)
    #     self.assertTrue(mock_exists.called)
    #     self.assertEqual(status, "")
    #
    #     url = "https://down/file"
    #     mock_downl.return_value = "/tmp/file"
    #     mock_exists.return_value = True
    #     mock_isfile.return_value = True
    #     mock_rpath.return_value = "/tmp/file"
    #     utools = KookerTools(self.local)
    #     status = utools._get_file(url)
    #     self.assertTrue(mock_downl.called)
    #     self.assertTrue(mock_exists.called)
    #     self.assertTrue(mock_isfile.called)
    #     self.assertEqual(status, "/tmp/file")

    # @patch.object(KookerTools, '_version_isok')
    # @patch('kooker.tools.FileUtil.remove')
    # @patch('kooker.tools.FileUtil.getdata')
    # @patch('kooker.tools.os.path.basename')
    # @patch('kooker.tools.FileUtil.mktmpdir')
    # @patch('kooker.tools.os.path.isfile')
    # def test_09__verify_version(self, mock_isfile, mock_fumktmp,
    #                             mock_osbase, mock_fugetdata,
    #                             mock_furm, mock_versionok):
    #     """Test09 KookerTools()._verify_version()."""
    #     tball = "/home/kooker.tar"
    #     mock_isfile.return_value = False
    #     utools = KookerTools(self.local)
    #     status = utools._verify_version(tball)
    #     self.assertTrue(mock_isfile.called)
    #     self.assertEqual(status, (False, ""))
    #
    #     tball = "/home/kooker.tar"
    #     mock_isfile.return_value = True
    #     mock_fumktmp.return_value = ""
    #     utools = KookerTools(self.local)
    #     status = utools._verify_version(tball)
    #     self.assertTrue(mock_isfile.called)
    #     self.assertTrue(mock_fumktmp.called)
    #     self.assertEqual(status, (False, ""))
    #
    #     tball = "/home/kooker.tar"
    #     tinfo1 = TarInfo("kooker_dir/lib/VERSION")
    #     tinfo2 = TarInfo("a")
    #     mock_isfile.return_value = True
    #     mock_fumktmp.return_value = "/home/tmp"
    #     mock_osbase.return_value = "VERSION"
    #     mock_fugetdata.return_value = "1.2.7"
    #     mock_furm.return_value = None
    #     mock_versionok.return_value = True
    #     with patch.object(tarfile, 'open', autospec=True) as open_mock:
    #         open_mock.return_value.getmembers.return_value = [tinfo2, tinfo1]
    #         open_mock.return_value.extract.return_value = None
    #         utools = KookerTools(self.local)
    #         status = utools._verify_version(tball)
    #         self.assertEqual(status, (True, "1.2.7"))
    #         self.assertTrue(mock_furm.called)

    # @patch.object(KookerTools, '_clean_install')
    # @patch('kooker.tools.os.path.basename')
    # @patch('kooker.tools.FileUtil')
    # @patch('kooker.tools.os.path.isfile')
    # def test_10__install(self, mock_isfile, mock_futil, mock_osbase, mock_cleaninstall):
    #     """Test10 KookerTools()._install()."""
    #     tfile = ""
    #     mock_isfile.return_value = False
    #     mock_cleaninstall.return_value = None
    #     utools = KookerTools(self.local)
    #     status = utools._install(tfile)
    #     self.assertFalse(status)
    #
    #     tinfo1 = TarInfo("kooker_dir/bin/ls")
    #     tinfo2 = TarInfo("kooker_dir/lib/lib1")
    #     tfile = "kooker.tar"
    #     mock_isfile.return_value = True
    #     mock_futil.return_value.chmod.return_value = None
    #     mock_futil.return_value.rchmod.side_effect = [None, None, None,
    #                                                   None, None, None]
    #     mock_osbase.side_effect = ["ls", "ls", "lib1", "lib1", "doc", "doc1"]
    #     self.local.create_repo.return_value = None
    #     with patch.object(tarfile, 'open', autospec=True) as open_mock:
    #         open_mock.return_value.getmembers.side_effect = [[tinfo1, tinfo2],
    #                                                          [tinfo1, tinfo2],
    #                                                          [tinfo1, tinfo2]]
    #         open_mock.return_value.extract.side_effect = [None, None]
    #         utools = KookerTools(self.local)
    #         status = utools._install(tfile)
    #         self.assertTrue(status)
    #         self.assertTrue(mock_futil.called)
    #         self.assertTrue(mock_futil.return_value.rchmod.call_count, 4)

    @patch.object(GetURLpyCurl, 'is_available')
    def test_11__get_mirrors(self, mock_gupycurl):
        """Test11 KookerTools()._get_mirrors()."""
        mock_gupycurl.return_value = True

        mirrors = "https://download.a.incd.pt/kooker/kooker-englib-1.2.11.tar.gz"
        utools = KookerTools(self.local)
        status = utools._get_mirrors(mirrors)
        self.assertEqual(status, [mirrors])

    @patch.object(GetURLpyCurl, 'is_available')
    @patch.object(KookerTools, '_get_file')
    @patch.object(KookerTools, '_get_mirrors')
    @patch('kooker.tools.json.load')
    def test_12_get_installinfo(self, mock_jload, mock_mirr, mock_getf,
                                mock_gupycurl):
        """Test12 KookerTools().get_installinfo()."""
        mock_gupycurl.return_value = True

        Config.conf['installinfo'] = "/home/info.json"
        res = {"tarversion": "1.2.7"}
        mock_jload.return_value = {"tarversion": "1.2.7"}
        mock_mirr.return_value = ["/home/info.json"]
        mock_getf.return_value = "info.json"
        subuid_line = StringIO('{"tarversion": "1.2.7"}')
        with patch(BOPEN) as mopen:
            mopen.return_value.__iter__ = (
                lambda self: iter(subuid_line.readline, ''))
            utools = KookerTools(self.local)
            status = utools.get_installinfo()
            self.assertEqual(status, res)

    @patch.object(GetURLpyCurl, 'is_available')
    @patch.object(KookerTools, '_install')
    @patch.object(KookerTools, '_verify_version')
    @patch.object(KookerTools, '_get_file')
    @patch.object(KookerTools, '_get_mirrors')
    @patch('kooker.tools.FileUtil.remove')
    def test_13__install_logic(self, mock_furm, mock_getmirr, mock_getfile,
                               mock_verversion, mock_install, mock_gupycurl):
        """Test13 KookerTools()._install_logic()."""
        mock_gupycurl.return_value = True

        mock_furm.return_value = None
        mock_getmirr.return_value = "https://down.pt/kooker-1.2.7.tar.gz"
        mock_getfile.return_value = "kooker-1.2.7.tar.gz"
        mock_verversion.return_value = (True, "1.2.7")
        mock_install.return_value = True
        utools = KookerTools(self.local)
        status = utools._install_logic(False)
        self.assertTrue(status)
        self.assertTrue(mock_getmirr.called)
        self.assertTrue(mock_getfile.called)
        self.assertTrue(mock_verversion.called)
        self.assertTrue(mock_install.called)

        mock_furm.return_value = None
        mock_getmirr.return_value = "https://down.pt/kooker-1.2.7.tar.gz"
        mock_getfile.return_value = "kooker-1.2.7.tar.gz"
        mock_verversion.return_value = (False, "")
        mock_install.return_value = True
        utools = KookerTools(self.local)
        status = utools._install_logic(True)
        self.assertTrue(status)

        mock_furm.return_value = None
        mock_getmirr.return_value = "https://down.pt/kooker-1.2.7.tar.gz"
        mock_getfile.return_value = "kooker-1.2.7.tar.gz"
        mock_verversion.return_value = (False, "")
        mock_install.return_value = True
        utools = KookerTools(self.local)
        status = utools._install_logic(False)
        self.assertFalse(status)

    @patch.object(GetURLpyCurl, 'is_available')
    @patch('kooker.tools.Msg')
    @patch.object(KookerTools, 'get_installinfo')
    @patch.object(KookerTools, '_install_logic')
    @patch.object(KookerTools, 'is_available')
    def test_14_install(self, mock_isavail, mock_instlog,
                        mock_getinfo, mock_msg, mock_gupycurl):
        """Test14 KookerTools().install()."""
        mock_gupycurl.return_value = True

        mock_msg.level = 0
        Config.conf['autoinstall'] = True
        Config.conf['tarball'] = "kooker-1.2.7.tar.gz"
        Config.conf['tarball_release'] = "1.2.7"
        Config.conf['installretry'] = 2
        mock_isavail.return_value = True
        utools = KookerTools(self.local)
        status = utools.install(False)
        self.assertTrue(status)
        self.assertTrue(mock_isavail.called)

        Config.conf['autoinstall'] = False
        Config.conf['tarball'] = "kooker-1.2.7.tar.gz"
        Config.conf['tarball_release'] = "1.2.7"
        Config.conf['installretry'] = 2
        mock_isavail.return_value = False
        utools = KookerTools(self.local)
        status = utools.install(False)
        self.assertEqual(status, None)
        self.assertFalse(utools._autoinstall)

        Config.conf['autoinstall'] = False
        Config.conf['tarball'] = ""
        Config.conf['tarball_release'] = "1.2.7"
        Config.conf['installretry'] = 2
        mock_isavail.return_value = True
        utools = KookerTools(self.local)
        status = utools.install(False)
        self.assertTrue(status)
        self.assertEqual(utools._tarball, "")

        Config.conf['autoinstall'] = True
        Config.conf['tarball'] = "kooker-1.2.7.tar.gz"
        Config.conf['tarball_release'] = "1.2.7"
        Config.conf['installretry'] = 2
        mock_isavail.return_value = False
        mock_instlog.side_effect = [False, True]
        mock_getinfo.side_effect = [None, None]
        utools = KookerTools(self.local)
        status = utools.install(False)
        self.assertTrue(status)
        self.assertTrue(mock_instlog.call_count, 2)
        self.assertTrue(mock_getinfo.call_count, 2)

        Config.conf['autoinstall'] = True
        Config.conf['tarball'] = "kooker-1.2.7.tar.gz"
        Config.conf['tarball_release'] = "1.2.7"
        Config.conf['installretry'] = 2
        mock_isavail.return_value = False
        mock_instlog.side_effect = [False, False]
        mock_getinfo.side_effect = [None, None]
        utools = KookerTools(self.local)
        status = utools.install(False)
        self.assertFalse(status)


if __name__ == '__main__':
    main()
