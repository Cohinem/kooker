#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
kooker unit tests: KookerCLI
"""

from unittest import TestCase, main
from unittest.mock import Mock, patch
from kooker.config import Config
from kooker.cmdparser import CmdParser
from kooker.cli import KookerCLI
import collections

collections.Callable = collections.abc.Callable
BUILTIN = "builtins"
BOPEN = BUILTIN + '.open'


class KookerCLITestCase(TestCase):
    """Test KookerTestCase() command line interface."""

    def setUp(self):
        Config().getconf()
        Config().conf['hostauth_list'] = ("/etc/passwd", "/etc/group")
        Config().conf['cmd'] = "/bin/bash"
        Config().conf['cpu_affinity_exec_tools'] = \
            (["numactl", "-C", "%s", "--", ],
             ["taskset", "-c", "%s", ])
        Config().conf['valid_host_env'] = "HOME"
        Config().conf['username'] = "user"
        Config().conf['userhome'] = "/"
        Config().conf['oskernel'] = "4.8.13"
        Config().conf['location'] = ""
        Config().conf['keystore'] = "KEYSTORE"

        str_local = 'kooker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

    def tearDown(self):
        self.lrepo.stop()

    @patch('kooker.cli.LocalFileAPI')
    @patch('kooker.cli.KeyStore')
    @patch('kooker.cli.DockerIoAPI')
    def test_01_init(self, mock_dockerio, mock_ks, mock_lfapi):
        """Test01 KookerCLI() constructor."""
        # Test Config().conf['keystore'] starts with /
        Config().conf['keystore'] = "/xxx"
        KookerCLI(self.local)
        self.assertTrue(mock_dockerio.called)
        self.assertTrue(mock_lfapi.called)

        # Test Config().conf['keystore'] does not starts with /
        Config().conf['keystore'] = "xx"
        KookerCLI(self.local)
        self.assertTrue(mock_ks.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.FileUtil.isdir')
    def test_02__cdrepo(self, mock_isdir, mock_dockerio):
        """Test02 KookerCLI()._cdrepo()."""
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc._cdrepo(cmdp)
        self.assertFalse(status)
        self.assertFalse(mock_isdir.called)

        argv = ["kooker"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_isdir.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc._cdrepo(cmdp)
        self.assertFalse(status)
        self.assertTrue(mock_isdir.called)

        argv = ["kooker"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_isdir.return_value = True
        self.local.setup.return_value = None
        udoc = KookerCLI(self.local)
        status = udoc._cdrepo(cmdp)
        self.assertTrue(status)
        self.assertTrue(self.local.setup.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.DockerIoAPI.is_repo_name')
    @patch('kooker.cli.Msg')
    def test_03__check_imagespec(self, mock_msg, mock_reponame,
                                 mock_dockerio):
        """Test03 KookerCLI()._check_imagespec()."""
        mock_msg.level = 0
        mock_reponame.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc._check_imagespec("")
        self.assertEqual(status, (None, None))

        mock_reponame.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc._check_imagespec("AAA")
        self.assertEqual(status, ("AAA", "latest"))

        mock_reponame.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc._check_imagespec("AAA:45")
        self.assertEqual(status, ("AAA", "45"))

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.DockerIoAPI.is_repo_name')
    @patch('kooker.cli.Msg')
    def test_04__check_imagerepo(self, mock_msg, mock_reponame,
                                 mock_dockerio):
        """Test04 KookerCLI()._check_imagerepo()."""
        mock_msg.level = 0
        mock_reponame.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc._check_imagerepo("")
        self.assertEqual(status, None)

        mock_reponame.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc._check_imagerepo("AAA")
        self.assertEqual(status, "AAA")

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_05__set_repository(self, mock_msg, mock_dockerio):
        """Test05 KookerCLI()._set_repository()."""
        mock_msg.level = 0
        regist = "registry.io"
        idxurl = "dockerhub.io"
        imgrepo = "dockerhub.io/myimg:1.2"
        mock_dockerio.set_proxy.return_value = None
        mock_dockerio.set_registry.side_effect = [None, None, None, None]
        mock_dockerio.set_index.side_effect = [None, None, None, None]
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc._set_repository(regist, idxurl, imgrepo, True)
        self.assertTrue(status)
        self.assertTrue(mock_dockerio.set_proxy.called)
        self.assertTrue(mock_dockerio.set_registry.called)
        self.assertTrue(mock_dockerio.set_index.called)

        regist = ""
        idxurl = ""
        imgrepo = "https://dockerhub.io/myimg:1.2"
        mock_dockerio.set_proxy.return_value = None
        mock_dockerio.set_registry.side_effect = [None, None, None, None]
        mock_dockerio.set_index.side_effect = [None, None, None, None]
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc._set_repository(regist, idxurl, imgrepo, False)
        self.assertTrue(status)

    @patch('kooker.cli.DockerIoAPI')
    def test_06__split_imagespec(self, mock_dockerio):
        """Test06 KookerCLI()._split_imagespec()."""
        imgrepo = ""
        res = ("", "", "", "")
        udoc = KookerCLI(self.local)
        status = udoc._split_imagespec(imgrepo)
        self.assertEqual(status, res)

        imgrepo = "dockerhub.io/myimg:1.2"
        res = ("", "dockerhub.io", "myimg", "1.2")
        udoc = KookerCLI(self.local)
        status = udoc._split_imagespec(imgrepo)
        self.assertEqual(status, res)

        imgrepo = "https://dockerhub.io/myimg:1.2"
        res = ("https:", "dockerhub.io", "myimg", "1.2")
        udoc = KookerCLI(self.local)
        status = udoc._split_imagespec(imgrepo)
        self.assertEqual(status, res)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.os.path.exists')
    @patch('kooker.cli.Msg')
    def test_07_do_mkrepo(self, mock_msg, mock_exists, mock_dockerio):
        """Test07 KookerCLI().do_mkrepo()."""
        mock_msg.level = 0

        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_mkrepo(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_exists.called)

        argv = ["kooker", "mkrepo"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        self.local.setup.return_value = None
        self.local.create_repo.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_mkrepo(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_exists.called)
        self.assertTrue(self.local.setup.called)
        self.assertTrue(self.local.create_repo.called)

        argv = ["kooker", "mkrepo"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        self.local.setup.return_value = None
        self.local.create_repo.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_mkrepo(cmdp)
        self.assertEqual(status, 0)

    # def test_08__search_print_lines(self):
    #     """Test08 KookerCLI()._search_print_lines()."""

    # @patch('cli.DockerIoAPI.search_get_page')
    # @patch('cli.HostInfo.termsize')
    # def test_09__search_repositories(self, mock_termsz, mock_doiasearch):
    #     """Test09 KookerCLI()._search_repositories()."""
    #     repo_list = [{"count": 1, "next": "", "previous": "",
    #                   "results": [
    #                       {
    #                           "repo_name": "lipcomputing/ipyrad",
    #                           "short_description": "Docker to run ipyrad",
    #                           "star_count": 0,
    #                           "pull_count": 188,
    #                           "repo_owner": "",
    #                           "is_automated": True,
    #                           "is_official": False
    #                       }]}]
    #     mock_termsz.return_value = (40, "")
    #     mock_doiasearch.return_value = repo_list
    #     udoc = KookerCLI(self.local)
    #     status = udoc._search_repositories("ipyrad")
    #     self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    def test_10__list_tags(self, mock_dockerio):
        """Test10 KookerCLI()._list_tags()."""
        mock_dockerio.get_tags.return_value = ["t1"]
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc._list_tags("t1")
        self.assertEqual(status, 0)

        mock_dockerio.get_tags.return_value = None
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc._list_tags("t1")
        self.assertEqual(status, 1)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.KeyStore.get')
    @patch.object(KookerCLI, '_search_repositories')
    @patch.object(KookerCLI, '_list_tags')
    @patch.object(KookerCLI, '_split_imagespec')
    @patch.object(KookerCLI, '_set_repository')
    def test_11_do_search(self, mock_setrepo, mock_split, mock_listtags,
                          mock_searchrepo, mock_ksget, mock_dockerio):
        """Test11 KookerCLI().do_search()."""
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_search(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "search", "--list-tags", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_split.return_value = ("d1", "d2", "ipyrad", "d3")
        mock_dockerio.search_init.return_value = None
        mock_ksget.return_value = "v2token1"
        mock_dockerio.set_v2_login_token.return_value = None
        mock_listtags.return_value = ["t1", "t2"]
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc.do_search(cmdp)
        self.assertEqual(status, ["t1", "t2"])
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_dockerio.search_init.called)
        self.assertTrue(mock_ksget.called)
        self.assertTrue(mock_dockerio.set_v2_login_token.called)
        self.assertTrue(mock_listtags.called)

        argv = ["kooker", "search", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_split.return_value = ("d1", "d2", "ipyrad", "d3")
        mock_dockerio.search_init.return_value = None
        mock_ksget.return_value = "v2token1"
        mock_dockerio.set_v2_login_token.return_value = None
        mock_searchrepo.return_value = 0
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc.do_search(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_searchrepo.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch('kooker.cli.LocalFileAPI.load')
    @patch.object(KookerCLI, '_check_imagerepo')
    def test_12_do_load(self, mock_chkimg, mock_load, mock_msg,
                        mock_dockerio):
        """Test12 KookerCLI().do_load()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "load", "-i", "ipyrad", "ipyimg"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_load.called)

        argv = ["kooker", "load", "-i", "ipyrad", "ipyimg"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = True
        mock_load.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_load.called)

        argv = ["kooker", "load", "-i", "ipyrad", "ipyimg"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = True
        mock_load.return_value = ['docker-repo1', 'docker-repo2']
        udoc = KookerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch('kooker.cli.os.path.exists')
    @patch('kooker.cli.LocalFileAPI.save')
    @patch.object(KookerCLI, '_check_imagespec')
    def test_13_do_save(self, mock_chkimg, mock_save, mock_exists,
                        mock_msg, mock_dockerio):
        """Test13 KookerCLI().do_save()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "save", "-o", "ipyrad", "ipyimg:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_exists.called)
        self.assertFalse(mock_chkimg.called)
        self.assertFalse(mock_save.called)

        argv = ["kooker", "save", "-o", "ipyrad", "ipyimg:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        mock_chkimg.return_value = ("ipyimg", "latest")
        mock_save.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_save.called)

        argv = ["kooker", "save", "-o", "ipyrad", "ipyimg:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        mock_chkimg.return_value = ("ipyimg", "latest")
        mock_save.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertTrue(mock_exists.called)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(mock_save.called)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.LocalFileAPI.import_toimage')
    @patch('kooker.cli.LocalFileAPI.import_tocontainer')
    @patch('kooker.cli.LocalFileAPI.import_clone')
    @patch('kooker.cli.Msg')
    @patch.object(KookerCLI, '_check_imagespec')
    def test_14_do_import(self, mock_chkimg, mock_msg, mock_impclone,
                          mock_impcont, mock_impimg, mock_dockerio):
        """Test14 KookerCLI().do_import()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_chkimg.called)
        self.assertFalse(mock_impclone.called)
        self.assertFalse(mock_impcont.called)
        self.assertFalse(mock_impimg.called)

        argv = ["kooker", "import", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_chkimg.called)
        self.assertFalse(mock_impimg.called)

        argv = ["kooker", "import", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(mock_impimg.called)

        argv = ["kooker", "import", "--clone", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_impclone.return_value = "12345"
        udoc = KookerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 0)
        self.assertFalse(mock_impcont.called)
        self.assertTrue(mock_impclone.called)

        argv = ["kooker", "import", "--tocontainer",
                "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_impcont.return_value = "12345"
        udoc = KookerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_impcont.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch('kooker.cli.ContainerStructure')
    def test_15_do_export(self, mock_cs, mock_msg, mock_dockerio):
        """Test15 KookerCLI().do_export()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "export", "-o", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        udoc = KookerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "export", "-o", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_cs.return_value.export_tofile.return_value = False
        self.local.get_container_id.return_value = "12345"
        udoc = KookerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_cs.called)
        self.assertTrue(self.local.get_container_id.called)

        argv = ["kooker", "export", "-o", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_cs.return_value.export_tofile.return_value = True
        self.local.get_container_id.return_value = "12345"
        udoc = KookerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 0)

        argv = ["kooker", "export",
                "--clone", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_cs.return_value.clone_tofile.return_value = True
        self.local.get_container_id.return_value = "12345"
        udoc = KookerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.LocalFileAPI.clone_container')
    @patch('kooker.cli.Msg')
    def test_16_do_clone(self, mock_msg, mock_clone, mock_dockerio):
        """Test16 KookerCLI().do_clone()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_clone(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "clone", "ipyradcont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        udoc = KookerCLI(self.local)
        status = udoc.do_clone(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_clone.called)
        self.assertTrue(self.local.get_container_id.called)

        argv = ["kooker", "clone", "ipyradcont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = "12345"
        mock_clone.return_value = "54321"
        udoc = KookerCLI(self.local)
        status = udoc.do_clone(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_clone.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch('kooker.cli.KeyStore.put')
    @patch.object(KookerCLI, '_set_repository')
    def test_17_do_login(self, mock_setrepo, mock_ksput, mock_msg,
                         mock_dockerio):
        """Test17 KookerCLI().do_login()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_login(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "login", "--username", "u1",
                "--password", "xx"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = True
        mock_dockerio.get_v2_login_token.return_value = "zx1"
        mock_ksput.return_value = 1
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc.do_login(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_dockerio.get_v2_login_token.called)
        self.assertTrue(mock_ksput.called)

        argv = ["kooker", "login", "--username", "u1",
                "--password", "xx"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_dockerio.get_v2_login_token.return_value = "zx1"
        mock_ksput.return_value = 0
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc.do_login(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_dockerio.get_v2_login_token.called)
        self.assertTrue(mock_ksput.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch('kooker.cli.KeyStore')
    @patch.object(KookerCLI, '_set_repository')
    def test_18_do_logout(self, mock_setrepo, mock_ks, mock_msg,
                          mock_dockerio):
        """Test18 KookerCLI().do_logout()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_logout(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "logout", "-a"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_ks.return_value.erase.return_value = 0
        udoc = KookerCLI(self.local)
        status = udoc.do_logout(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_ks.return_value.erase.called)

        argv = ["kooker", "logout"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_ks.return_value.delete.return_value = 1
        udoc = KookerCLI(self.local)
        status = udoc.do_logout(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_ks.return_value.delete.called)

    @patch.object(KookerCLI, '_set_repository')
    @patch.object(KookerCLI, '_check_imagespec')
    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.KeyStore.get')
    @patch('kooker.cli.Msg')
    def test_19_do_pull(self, mock_msg, mock_ksget, mock_dockerio,
                        mock_chkimg, mock_setrepo):
        """Test19 KookerCLI().do_pull()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc.do_pull(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "pull", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_setrepo.return_value = None
        mock_ksget.return_value = "zx1"
        mock_dockerio.set_v2_login_token.return_value = None
        mock_dockerio.get.return_value = False
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc.do_pull(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_ksget.called)
        self.assertTrue(mock_dockerio.set_v2_login_token.called)
        self.assertTrue(mock_dockerio.get.called)

        argv = ["kooker", "pull", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_setrepo.return_value = None
        mock_ksget.return_value = "zx1"
        mock_dockerio.set_v2_login_token.return_value = None
        mock_dockerio.get.return_value = True
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc.do_pull(cmdp)
        self.assertEqual(status, 0)

    @patch.object(KookerCLI, '_check_imagespec')
    @patch('kooker.cli.ContainerStructure')
    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_20__create(self, mock_msg, mock_dockerio,
                        mock_cstruct, mock_chkimg):
        """Test20 KookerCLI()._create()."""
        mock_msg.level = 0
        mock_dockerio.is_repo_name.return_value = False
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc._create("IMAGE:TAG")
        self.assertFalse(status)
        self.assertTrue(mock_msg.return_value.err.called)

        mock_dockerio.is_repo_name.return_value = True
        mock_chkimg.return_value = ("", "TAG")
        mock_cstruct.return_value.create.return_value = True
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc._create("IMAGE:TAG")
        self.assertFalse(status)

        mock_dockerio.is_repo_name.return_value = True
        mock_chkimg.return_value = ("IMAGE", "TAG")
        mock_cstruct.return_value.create.return_value = True
        udoc = KookerCLI(self.local)
        udoc.dockerioapi = mock_dockerio
        status = udoc._create("IMAGE:TAG")
        self.assertTrue(status)

    @patch('kooker.cli.DockerIoAPI')
    @patch.object(KookerCLI, '_create')
    @patch('kooker.cli.Msg')
    def test_21_do_create(self, mock_msg, mock_create, mock_dockerio):
        """Test21 KookerCLI().do_create()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_create.called)

        argv = ["kooker", "create", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_create.return_value = ""
        udoc = KookerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_create.called)

        argv = ["kooker", "create", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_create.return_value = "12345"
        udoc = KookerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 0)
        self.assertFalse(self.local.set_container_name.called)

        argv = ["kooker", "create", "--name=mycont", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_create.return_value = "12345"
        self.local.set_container_name.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 1)
    #    self.assertTrue(self.local.set_container_name.called)

    # def test_22__get_run_options(self):
    #    """Test22 KookerCLI()._get_run_options()"""

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.ExecutionMode')
    @patch('kooker.cli.Msg')
    @patch.object(KookerCLI, 'do_pull')
    @patch.object(KookerCLI, '_create')
    @patch.object(KookerCLI, '_check_imagespec')
    def test_23_do_run(self, mock_chkimg, mock_create, mock_pull,
                       mock_msg, mock_exec, mock_dockerio):
        """Test23 KookerCLI().do_run()."""
        mock_msg.level = 0
        mock_pull.return_value = None
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "run"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_pull.return_value = None
        udoc = KookerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "run", "--location=/tmp/kooker", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_pull.return_value = None
        mock_exec.return_value.get_engine.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_exec.return_value.get_engine.called)

        mock_pull.return_value = None
        exeng_patch = patch("kooker.engine.proot.PRootEngine")
        proot = exeng_patch.start()
        mock_proot = Mock()
        proot.return_value = mock_proot

        argv = ["kooker", "run", "--location=/tmp/kooker", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_pull.return_value = None
        mock_exec.return_value.get_engine.return_value = proot
        proot.run.return_value = 0
        udoc = KookerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(proot.run.called)
        self.assertFalse(self.local.isprotected_container.called)

        argv = ["kooker", "run", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        mock_pull.return_value = None
        mock_exec.return_value.get_engine.return_value = proot
        proot.run.return_value = 0
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.cd_imagerepo.return_value = True
        mock_create.return_value = "12345"
        udoc = KookerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.get_container_id.called)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(self.local.cd_imagerepo.called)
        self.assertTrue(mock_create.called)

        exeng_patch.stop()

    @patch('kooker.cli.DockerIoAPI')
    def test_24_do_images(self, mock_dockerio):
        """Test24 KookerCLI().do_images()."""
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_images(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "images", "-l"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_imagerepos.return_value = [("img1", "tag1")]
        self.local.isprotected_imagerepo.return_value = False
        self.local.cd_imagerepo.return_value = "/img1"
        self.local.get_layers.return_value = [("l1", 1024)]
        udoc = KookerCLI(self.local)
        status = udoc.do_images(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.get_imagerepos.called)
        self.assertTrue(self.local.isprotected_imagerepo.called)
        self.assertTrue(self.local.cd_imagerepo.called)
        self.assertTrue(self.local.get_layers.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.ExecutionMode')
    def test_25_do_ps(self, mock_exec, mock_dockerio):
        """Test25 KookerCLI().do_ps()."""
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_ps(cmdp)
        self.assertEqual(status, 1)

        exeng_patch = patch("kooker.engine.proot.PRootEngine")
        proot = exeng_patch.start()
        mock_proot = Mock()
        proot.return_value = mock_proot
        cdir = "/home/u1/.kooker/containers"
        argv = ["kooker", "ps", "-m", "-s"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_containers_list.return_value = [[cdir, "/", "a"]]
        mock_exec.return_value.get_engine.return_value = proot
        self.local.isprotected_container.return_value = False
        self.local.iswriteable_container.return_value = True
        self.local.get_size.return_value = 1024
        udoc = KookerCLI(self.local)
        status = udoc.do_ps(cmdp)
        self.assertEqual(status, 0)
        exeng_patch.stop()

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_26_do_rm(self, mock_msg, mock_dockerio):
        """Test26 KookerCLI().do_rm()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_rm(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "rm"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_rm(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(self.local.get_container_id.called)

        argv = ["kooker", "rm", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = None
        udoc = KookerCLI(self.local)
        status = udoc.do_rm(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.get_container_id.called)
        self.assertFalse(self.local.isprotected_container.called)

        argv = ["kooker", "rm", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = "12345"
        self.local.isprotected_container.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_rm(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.isprotected_container.called)
        self.assertFalse(self.local.del_container.called)

        argv = ["kooker", "rm", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = "12345"
        self.local.isprotected_container.return_value = False
        self.local.del_container.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_rm(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.del_container.called)

        argv = ["kooker", "rm", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = "12345"
        self.local.isprotected_container.return_value = False
        self.local.del_container.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_rm(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch.object(KookerCLI, '_check_imagespec')
    def test_27_do_rmi(self, mock_chkimg, mock_msg, mock_dockerio):
        """Test27 KookerCLI().do_rmi()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_rmi(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "rmi"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_rmi(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_chkimg.called)
        self.assertFalse(self.local.isprotected_imagerepo.called)

        argv = ["kooker", "rmi", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.isprotected_imagerepo.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_rmi(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.isprotected_imagerepo.called)
        self.assertFalse(self.local.del_imagerepo.called)

        argv = ["kooker", "rmi", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.isprotected_imagerepo.return_value = False
        self.local.del_imagerepo.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_rmi(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.del_imagerepo.called)

        argv = ["kooker", "rmi", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.isprotected_imagerepo.return_value = False
        self.local.del_imagerepo.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_rmi(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.del_imagerepo.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch.object(KookerCLI, '_check_imagespec')
    def test_28_do_protect(self, mock_chkimg, mock_msg, mock_dockerio):
        """Test28 KookerCLI().do_protect()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_protect(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(self.local.get_container_id.called)

        argv = ["kooker", "protect"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = False
        mock_chkimg.return_value = ("", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_protect(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.get_container_id.called)
        self.assertTrue(mock_chkimg.called)
        self.assertFalse(self.local.protect_container.called)
        self.assertFalse(self.local.protect_imagerepo.called)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = False
        mock_chkimg.return_value = ("", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_protect(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = False
        self.local.protect_imagerepo.return_value = True
        mock_chkimg.return_value = ("ipyrad", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_protect(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.protect_imagerepo.called)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = True
        self.local.protect_container.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_protect(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.get_container_id.called)
        self.assertTrue(self.local.protect_container.called)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = True
        self.local.protect_container.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_protect(cmdp)
        self.assertEqual(status, 1)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    @patch.object(KookerCLI, '_check_imagespec')
    def test_29_do_unprotect(self, mock_chkimg, mock_msg, mock_dockerio):
        """Test29 KookerCLI().do_unprotect()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_unprotect(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(self.local.get_container_id.called)

        argv = ["kooker", "protect"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = False
        mock_chkimg.return_value = ("", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_unprotect(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.get_container_id.called)
        self.assertTrue(mock_chkimg.called)
        self.assertFalse(self.local.unprotect_container.called)
        self.assertFalse(self.local.unprotect_imagerepo.called)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = False
        mock_chkimg.return_value = ("", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_unprotect(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = False
        self.local.unprotect_imagerepo.return_value = True
        mock_chkimg.return_value = ("ipyrad", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_unprotect(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.unprotect_imagerepo.called)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = True
        self.local.unprotect_container.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_unprotect(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.get_container_id.called)
        self.assertTrue(self.local.unprotect_container.called)

        argv = ["kooker", "protect", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = True
        self.local.unprotect_container.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_unprotect(cmdp)
        self.assertEqual(status, 1)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_30_do_name(self, mock_msg, mock_dockerio):
        """Test30 KookerCLI().do_name()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_name(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "name"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_name(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.get_container_id.called)
        self.assertFalse(self.local.set_container_name.called)

        argv = ["kooker", "name", "12345", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = True
        self.local.set_container_name.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_name(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.set_container_name.called)

        argv = ["kooker", "name", "12345", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = True
        self.local.set_container_name.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_name(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_31_do_rename(self, mock_msg, mock_dockerio):
        """Test31 KookerCLI().do_rename()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_rename(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "rename", "contname", "newname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.side_effect = ["", ""]
        udoc = KookerCLI(self.local)
        status = udoc.do_rename(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.get_container_id.call_count, 1)

        argv = ["kooker", "rename", "contname", "newname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.side_effect = ["123", "543"]
        udoc = KookerCLI(self.local)
        status = udoc.do_rename(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.get_container_id.call_count, 2)

        argv = ["kooker", "rename", "contname", "newname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.side_effect = ["123", ""]
        self.local.del_container_name.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_rename(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.del_container_name.called)
        self.assertFalse(self.local.set_container_name.called)

        argv = ["kooker", "rename", "contname", "newname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.side_effect = ["123", ""]
        self.local.del_container_name.return_value = True
        self.local.set_container_name.side_effect = [False, True]
        udoc = KookerCLI(self.local)
        status = udoc.do_rename(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.set_container_name.call_count, 2)

        argv = ["kooker", "rename", "contname", "newname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.side_effect = ["123", ""]
        self.local.del_container_name.return_value = True
        self.local.set_container_name.side_effect = [True, True]
        udoc = KookerCLI(self.local)
        status = udoc.do_rename(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.set_container_name.call_count, 1)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_32_do_rmname(self, mock_msg, mock_dockerio):
        """Test32 KookerCLI().do_rmname()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_rmname(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "rmname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_rmname(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(self.local.del_container_name.called)

        argv = ["kooker", "rmname", "contname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.del_container_name.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_rmname(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.del_container_name.called)

        argv = ["kooker", "rmname", "contname"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.del_container_name.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_rmname(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.del_container_name.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch.object(KookerCLI, '_check_imagespec')
    @patch('kooker.cli.json.dumps')
    @patch('kooker.cli.ContainerStructure.get_container_attr')
    @patch('kooker.cli.Msg')
    def test_33_do_inspect(self, mock_msg, mock_csattr, mock_jdump,
                           mock_chkimg, mock_dockerio):
        """Test33 KookerCLI().do_inspect()."""
        cont_insp = {
            "architecture": "amd64",
            "config": {
                "AttachStderr": False,
                "AttachStdin": False,
                "AttachStdout": False,
                "Cmd": [
                    "/bin/bash"
                ],
                "Domainname": "",
                "Entrypoint": None,
                "Env": [
                    "PATH=/usr/local/sbin"
                ],
                "Hostname": "",
                "Image": "sha256:05725a",
                "Labels": {
                    "org.opencontainers.image.vendor": "CentOS"
                },
                "WorkingDir": ""
            },
            "container": "c171c",
            "container_config": {
                "ArgsEscaped": True,
                "Cmd": ["/bin/sh", "-c"],
                "Domainname": "",
                "Env": [
                    "PATH=/usr/local/sbin"
                ],
                "Hostname": "c171c5a1528a",
                "Image": "sha256:05725a",
                "Labels": {
                    "org.label-schema.license": "GPLv2",
                    "org.label-schema.name": "CentOS Base Image",
                    "org.opencontainers.image.vendor": "CentOS"
                },
                "WorkingDir": ""
            },
            "created": "2020-05-05T21",
            "docker_version": "18.09.7",
            "id": "e72c1",
            "os": "linux",
            "parent": "61dc7"
        }

        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        udoc = KookerCLI(self.local)
        status = udoc.do_inspect(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "inspect"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        mock_chkimg.return_value = ("", "latest")
        self.local.cd_imagerepo.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_inspect(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "inspect"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.cd_imagerepo.return_value = True
        self.local.get_image_attributes.return_value = (cont_insp, "")
        mock_jdump.return_value = cont_insp
        udoc = KookerCLI(self.local)
        status = udoc.do_inspect(cmdp)
        self.assertEqual(status, 0)

        argv = ["kooker", "inspect", "-p", "123"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = "123"
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.cd_imagerepo.return_value = True
        self.local.get_image_attributes.return_value = (cont_insp, "")
        mock_csattr.return_value = ("/ROOT/cont", cont_insp)
        mock_jdump.return_value = cont_insp
        udoc = KookerCLI(self.local)
        status = udoc.do_inspect(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch.object(KookerCLI, '_check_imagespec')
    @patch('kooker.cli.Msg')
    def test_34_do_verify(self, mock_msg, mock_chkimg, mock_dockerio):
        """Test34 KookerCLI().do_verify()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        udoc = KookerCLI(self.local)
        status = udoc.do_verify(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "verify", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.cd_imagerepo.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_verify(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "verify", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.cd_imagerepo.return_value = True
        self.local.verify_image.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_verify(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.ExecutionMode')
    @patch('kooker.cli.NvidiaMode')
    @patch('kooker.cli.FileUtil.rchmod')
    @patch('kooker.cli.Unshare.namespace_exec')
    @patch('kooker.cli.MountPoint')
    @patch('kooker.cli.FileBind')
    @patch('kooker.cli.Msg')
    def test_35_do_setup(self, mock_msg, mock_fb, mock_mp,
                         mock_unshr, mock_furchmod, mock_nv, mock_execm,
                         mock_dockerio):
        """Test35 KookerCLI().do_setup()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_setup(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "setup"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.cd_container.return_value = ""
        udoc = KookerCLI(self.local)
        status = udoc.do_setup(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.cd_container.called)

        argv = ["kooker", "setup", "--execmode=P2", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.cd_container.return_value = "/ROOT/cont1"
        self.local.isprotected_container.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_setup(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.isprotected_container.called)

        argv = ["kooker", "setup", "--execmode=P2",
                "--purge", "--fixperm", "--nvidia", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.cd_container.return_value = "/ROOT/cont1"
        self.local.isprotected_container.return_value = False
        mock_msg.level = 0
        mock_fb.return_value.restore.return_value = None
        mock_mp.return_value.restore.return_value = None
        mock_unshr.return_value = None
        mock_furchmod.return_value = None
        mock_nv.return_value.set_mode.return_value = None
        mock_execm.return_value.set_mode.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_setup(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_fb.return_value.restore.called)
        self.assertTrue(mock_mp.return_value.restore.called)
        self.assertTrue(mock_unshr.called)
        self.assertTrue(mock_furchmod.called)
        self.assertTrue(mock_nv.return_value.set_mode.called)
        self.assertTrue(mock_execm.return_value.set_mode.called)

        argv = ["kooker", "setup", "--execmode=P2",
                "--purge", "--fixperm", "--nvidia", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.cd_container.return_value = "/ROOT/cont1"
        self.local.isprotected_container.return_value = False
        mock_msg.level = 0
        mock_fb.return_value.restore.return_value = None
        mock_mp.return_value.restore.return_value = None
        mock_unshr.return_value = None
        mock_furchmod.return_value = None
        mock_nv.return_value.set_mode.return_value = None
        mock_execm.return_value.set_mode.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_setup(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "setup", "mycont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.cd_container.return_value = "/ROOT/cont1"
        self.local.isprotected_container.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_setup(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.KookerTools')
    @patch('kooker.cli.Msg')
    def test_36_do_install(self, mock_msg, mock_utools, mock_dockerio):
        """Test36 KookerCLI().do_install()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_install(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "install", "--force", "--purge"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_utools.return_value.purge.return_value = None
        mock_utools.return_value.install.return_value = False
        udoc = KookerCLI(self.local)
        status = udoc.do_install(cmdp)
        self.assertEqual(status, 1)

        argv = ["kooker", "install", "--force", "--purge"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_utools.return_value.purge.return_value = None
        mock_utools.return_value.install.return_value = True
        udoc = KookerCLI(self.local)
        status = udoc.do_install(cmdp)
        self.assertEqual(status, 0)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_37_do_showconf(self, mock_msg, mock_dockerio):
        """Test37 KookerCLI().do_showconf()."""
        mock_msg.level = 0
        argv = ["kooker", "showconf"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_showconf(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_msg.return_value.out.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_38_do_version(self, mock_msg, mock_dockerio):
        """Test38 KookerCLI().do_version()."""
        mock_msg.level = 0
        argv = ["kooker", "version"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_version(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_msg.return_value.out.called)

    @patch('kooker.cli.DockerIoAPI')
    @patch('kooker.cli.Msg')
    def test_39_do_help(self, mock_msg, mock_dockerio):
        """Test39 KookerCLI().do_help()."""
        mock_msg.level = 0
        argv = ["kooker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = KookerCLI(self.local)
        status = udoc.do_help(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_msg.return_value.out.called)


if __name__ == '__main__':
    main()
