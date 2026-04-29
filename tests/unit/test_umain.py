#!/usr/bin/env python
"""
kooker unit tests: UMain
"""

from unittest import TestCase, main
from unittest.mock import patch
from kooker.umain import UMain
from kooker.config import Config
import collections

collections.Callable = collections.abc.Callable


class UMainTestCase(TestCase):
    """Test UMain() class main kooker program."""

    def setUp(self):
        Config().getconf()

    def tearDown(self):
        pass

    def test_01_init(self):
        """Test01 UMain(argv) constructor."""
        argv = ["kooker", "-h"]
        udoc = UMain(argv)
        self.assertEqual(udoc.argv, argv)

    @patch('kooker.umain.Msg')
    @patch('kooker.umain.KookerCLI')
    @patch('kooker.umain.LocalRepository')
    @patch('kooker.umain.os.geteuid')
    def test_02__prepare_exec(self, mock_getuid,
                              mock_local, mock_ucli, mock_msg):
        """Test02 UMain()._prepare_exec()."""
        argv = ["kooker", "-h"]
        mock_msg.level = 0
        mock_msg.VER = 4
        mock_getuid.return_value = 0
        with patch('sys.exit') as mock_exit:
            umain = UMain(argv)
            umain._prepare_exec()
            self.assertTrue(mock_exit.called)

        argv = ["kooker", "-h", "--debug", "--insecure"]
        mock_msg.level = 0
        mock_msg.VER = 4
        mock_getuid.return_value = 100
        mock_local.return_value.is_repo.return_value = True
        mock_local.return_value.create_repo.return_value = None
        mock_ucli.return_value = None
        umain = UMain(argv)
        umain._prepare_exec()
        self.assertTrue(mock_getuid.called)
        self.assertTrue(mock_local.return_value.is_repo.called)
        self.assertTrue(mock_ucli.called)

    @patch('kooker.umain.Msg')
    @patch('kooker.umain.KookerCLI')
    def test_03_execute(self, mock_ucli, mock_msg):
        """Test03 UMain().execute()."""
        mock_msg.level = 0
        argv = ['kooker', '--allow-root', '-h']
        mock_ucli.return_value.do_help.return_value = 0
        umain = UMain(argv)
        status = umain.execute()
        self.assertTrue(mock_ucli.return_value.do_help.called)
        self.assertEqual(status, 0)

        argv = ['kooker', '--allow-root', '--version']
        mock_ucli.return_value.do_version.return_value = 0
        umain = UMain(argv)
        status = umain.execute()
        self.assertTrue(mock_ucli.return_value.do_version.called)
        self.assertEqual(status, 0)

        argv = ['kooker', '--allow-root', 'install']
        mock_ucli.return_value.do_install.return_value = 0
        umain = UMain(argv)
        status = umain.execute()
        self.assertTrue(mock_ucli.return_value.do_install.called)
        self.assertEqual(status, 0)

        argv = ['kooker', '--allow-root', 'showconf']
        mock_ucli.return_value.do_showconf.return_value = 0
        umain = UMain(argv)
        status = umain.execute()
        self.assertTrue(mock_ucli.return_value.do_showconf.called)
        self.assertEqual(status, 0)

        argv = ['kooker', '--allow-root', 'rm']
        mock_ucli.return_value.do_rm.return_value = 0
        umain = UMain(argv)
        status = umain.execute()
        self.assertTrue(mock_ucli.return_value.do_rm.called)
        self.assertEqual(status, 0)

        argv = ['kooker', '--allow-root', 'faking']
        umain = UMain(argv)
        status = umain.execute()
        self.assertEqual(status, 1)


if __name__ == '__main__':
    main()
