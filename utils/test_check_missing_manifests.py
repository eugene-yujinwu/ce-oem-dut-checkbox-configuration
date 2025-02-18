import unittest
from unittest.mock import patch

import check_missing_manifests


class CheckMissingManifestsTests(unittest.TestCase):
    @patch("os.walk")
    def test_get_cid_dirs(self, mock_ow):
        mock_ow.return_value = [
            ("./pc/202502-12345", [], []),
            ("./pc/useless", [], []),
            ("./pc/202502-1234567", [], []),
        ]
        result = check_missing_manifests.get_cid_dirs(".")
        expected_result = {
            "202502-12345": "./pc/202502-12345",
            "202502-1234567": "./pc/202502-1234567",
        }
        self.assertEqual(result, expected_result)

    @patch("check_missing_manifests.get_manifest_data")
    def test_check_missing_manifests_ok(self, mock_gmd):
        cids_in_lab = [
            "202502-12345",
        ]
        cid_dirs = {
            "202502-12345": "path/to/manifest",
        }
        manifest_id_list = [
            "test",
        ]
        mock_gmd.return_value = [
            "test",
        ]
        result = check_missing_manifests.check_missing_manifests(
            cids_in_lab, cid_dirs, manifest_id_list
        )
        self.assertEqual(result, ([], {}))

    @patch("check_missing_manifests.get_manifest_data")
    def test_check_missing_manifests_missing(self, mock_gmd):
        cids_in_lab = [
            "202502-12345",
        ]
        cid_dirs = {
            "202502-12345": "path/to/manifest",
        }
        manifest_id_list = [
            "test",
            "not_here",
        ]
        mock_gmd.return_value = [
            "test",
        ]
        result = check_missing_manifests.check_missing_manifests(
            cids_in_lab, cid_dirs, manifest_id_list
        )
        self.assertEqual(result, ([], {"202502-12345": ["not_here"]}))

    @patch("check_missing_manifests.get_manifest_data")
    def test_check_missing_manifests_no_config(self, mock_gmd):
        cids_in_lab = [
            "202502-12345",
        ]
        cid_dirs = {}
        manifest_id_list = [
            "test",
            "not_here",
        ]
        mock_gmd.side_effect = KeyError
        result = check_missing_manifests.check_missing_manifests(
            cids_in_lab, cid_dirs, manifest_id_list
        )
        self.assertEqual(result, (["202502-12345"], {}))

    @patch("check_missing_manifests.get_manifest_data")
    def test_check_missing_manifests_no_manifest_file(self, mock_gmd):
        cids_in_lab = [
            "202502-12345",
        ]
        cid_dirs = {
            "202502-12345": "path/to/manifest",
        }
        manifest_id_list = [
            "test",
            "not_here",
        ]
        mock_gmd.side_effect = FileNotFoundError
        result = check_missing_manifests.check_missing_manifests(
            cids_in_lab, cid_dirs, manifest_id_list
        )
        self.assertEqual(result, (["202502-12345"], {}))
