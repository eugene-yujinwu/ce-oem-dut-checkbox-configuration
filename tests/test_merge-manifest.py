import unittest
import json
import os
import sys
import importlib


update_module = importlib.import_module("utils.manifest-update")

class checkbox_manifest_test(unittest.TestCase):

    default_file = "pc/default/manifest.json"
    mini_manifest_file = "pc/default/pc-mini-manifest.json"
    test_file = "tmp_manifest.json"
    target = None


    def setUp(self):
        update_module.DEFAULT_MANIFEST = self.default_file
        update_module.MINI_MANIFEST = self.mini_manifest_file
        self.target = open(os.devnull, "w", encoding="utf-8")
        sys.stdout = self.target

        return super().setUp()

    def test_apply_default_only(self):
        """
        User does not provide manifest, so will apply default full manifest
        """
        update_module.manifest_update(
            "", self.test_file, True
        )

        with open(self.default_file) as fp:
            dict_expected = json.load(fp)

        with open(self.test_file) as fp:
            dict_result = json.load(fp)

        self.assertEqual(
            json.dumps(dict_result, sort_keys=True),
            json.dumps(dict_expected, sort_keys=True),
            "failed to merge default manifest data"
        )

    def test_apply_mini_manifest_only(self):
        """
        User does not provide manifest, so will apply pc-mini manifest
        """
        update_module.manifest_update(
            "", self.test_file, False
        )

        with open(self.mini_manifest_file) as fp:
            dict_expected = json.load(fp)

        with open(self.test_file) as fp:
            dict_result = json.load(fp)

        self.assertEqual(
            json.dumps(dict_result, sort_keys=True),
            json.dumps(dict_expected, sort_keys=True),
            "failed to merge pc-mini manifest data"
        )

    def test_apply_user_data_only(self):
        """
        User does provide manifest, so will apply user data
        """
        user_provided_data = (
            "{\n"
            "  \"com.canonical.certification::has_fake_interface\": true,\n"
            "  \"com.canonical.certification::has_ethernet_adapter\": false\n"
            "}"
        )

        update_module.manifest_update(
            user_provided_data, self.test_file, True
        )

        dict_expected = json.loads(user_provided_data)

        with open(self.test_file) as fp:
            dict_result = json.load(fp)

        self.assertEqual(
            json.dumps(dict_result, sort_keys=True),
            json.dumps(dict_expected, sort_keys=True),
            "failed to merge user provided manifest"
        )

    def test_update_user_data(self):
        """
        User would like to update existing manifest, so will update manifest
        """
        original_data = {
            "com.canonical.certification::has_ethernet_adapter": True,
            "com.canonical.certification::has_camera": True,
            "com.canonical.certification::has_usb_storage": False,
            "com.canonical.certification::has_tpm2_chip": True,
            "com.canonical.certification::has_wlan_adapter": True,
        }
        with open(self.test_file, "+w") as fp:
            json.dump(original_data, fp)

        user_provided_data = (
            "{\n"
            "  \"com.canonical.certification::has_fake_interface\": true,\n"
            "  \"com.canonical.certification::has_ethernet_adapter\": false\n"
            "}"
        )

        update_module.manifest_update(
            user_provided_data, self.test_file, self.default_file
        )

        dict_expected = original_data
        dict_expected.update(json.loads(user_provided_data))

        with open(self.test_file) as fp:
            dict_result = json.load(fp)

        self.assertEqual(
            json.dumps(dict_result, sort_keys=True),
            json.dumps(dict_expected, sort_keys=True),
            "failed to update existing manifest"
        )

    def test_manifest_no_changes(self):
        """
        manifest data is empty, the contents in manifest file should be the same
        """
        dict_expected = {
            "com.canonical.certification::has_ethernet_adapter": True,
            "com.canonical.certification::has_camera": True,
            "com.canonical.certification::has_usb_storage": False,
            "com.canonical.certification::has_tpm2_chip": True,
            "com.canonical.certification::has_wlan_adapter": True,
        }
        with open(self.test_file, "+w") as fp:
            json.dump(dict_expected, fp)

        user_provided_data = ""

        update_module.manifest_update(
            user_provided_data, self.test_file, False
        )

        with open(self.test_file) as fp:
            dict_result = json.load(fp)

        self.assertEqual(
            json.dumps(dict_result, sort_keys=True),
            json.dumps(dict_expected, sort_keys=True),
            "manifest contents has been changes"
        )

    def tearDown(self):
        sys.stdout = sys.__stdout__
        self.target.close()
        os.remove(self.test_file)
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()