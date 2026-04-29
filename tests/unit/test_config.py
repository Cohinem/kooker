#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
kooker unit tests: Config
"""

from unittest import TestCase, main
from unittest.mock import patch
from kooker.config import Config
import collections

collections.Callable = collections.abc.Callable
BUILTINS = "builtins"


class ConfigTestCase(TestCase):
    """Test case for the kooker configuration."""

    def test_01_init(self):
        """Test01 Config() constructor."""
        config = Config()
        self.assertIsInstance(config.conf['verbose_level'], int)
        self.assertIsInstance(config.conf['topdir'], str)
        self.assertIs(config.conf['bindir'], None)
        self.assertIs(config.conf['libdir'], None)
        self.assertIs(config.conf['reposdir'], None)
        self.assertIs(config.conf['layersdir'], None)
        self.assertIs(config.conf['containersdir'], None)
        self.assertIsInstance(config.conf['homedir'], str)
        self.assertIsInstance(config.conf['config'], str)
        self.assertIsInstance(config.conf['keystore'], str)
        self.assertIsInstance(config.conf['tmpdir'], str)
        self.assertIsInstance(config.conf['tarball'], str)
        self.assertIsInstance(config.conf['sysdirs_list'], tuple)
        self.assertIsInstance(config.conf['dri_list'], tuple)
        self.assertIsInstance(config.conf['location'], str)
        self.assertIsInstance(config.conf['http_proxy'], str)
        self.assertIsInstance(config.conf['timeout'], int)
        self.assertIsInstance(config.conf['download_timeout'], int)
        self.assertIsInstance(config.conf['ctimeout'], int)
        self.assertIsInstance(config.conf['http_agent'], str)
        self.assertIsInstance(config.conf['http_insecure'], bool)
        self.assertIsInstance(config.conf['dockerio_index_url'], str)
        self.assertIsInstance(config.conf['dockerio_registry_url'], str)

    @patch('kooker.config.ConfigParser.items')
    @patch('kooker.config.ConfigParser.read')
    @patch('kooker.config.os.path.exists')
    def test_02__file_override(self, mock_exists, mock_cpread, mock_cpitems):
        """Test02 Config()._file_override"""
        cfile = "/home/kooker.conf"
        mock_exists.side_effect = [False, False, True]
        mock_cpread.return_value = None
        mock_cpitems.return_value = [("verbose_level", 5)]
        Config()._file_override(cfile)
        self.assertEqual(Config.conf['verbose_level'], 5)

    @patch('kooker.config.os.getenv')
    def test_03__env_override(self, mock_env):
        """Test03 Config()._env_override"""
        # Order of getenv:
        # KOOKER_LOGLEVEL, KOOKER_DIR, KOOKER_BIN, KOOKER_LIB,
        # KOOKER_REPOS, KOOKER_LAYERS
        mock_env.return_value = "5"
        Config()._env_override()
        self.assertEqual(Config.conf['verbose_level'], 5)

    @patch.object(Config, '_env_override')
    @patch.object(Config, '_file_override')
    @patch('kooker.config.Config')
    def test_04_getconf(self, mock_conf, mock_fileover, mock_envover):
        """Test04 Config.getconf()."""
        mock_conf.return_value.conf["topdir"] = "/.kooker"
        config = Config()
        config.getconf()
        self.assertTrue(mock_fileover.called)
        self.assertTrue(mock_envover.called)

    @patch.object(Config, '_file_override')
    @patch('kooker.config.Config')
    def test_05_container(self, mock_conf, mock_fileover):
        """Test05 Config.container()."""
        mock_conf.return_value.conf["topdir"] = "/.kooker"
        config = Config()
        config.container()
        self.assertTrue(mock_fileover.called)


if __name__ == '__main__':
    main()
