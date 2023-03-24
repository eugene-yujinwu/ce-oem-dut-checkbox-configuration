import unittest
import json
import os
import importlib

update_module = importlib.import_module("utils.manifest-update")

class checkbox_manifest_test(unittest.TestCase):

    default_file = "pc/default/manifest.json"
    test_file = "tmp_manifest.conf"

    def setUp(self):
        with open(self.test_file, "+w") as fp:
            fp.write("{}")
        return super().setUp()

    def test_apply_default_only(self):
        """
        User does not provide manifest, so will apply default manifest
        """
        update_module.manifest_update(
            "", self.test_file, self.default_file
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
            user_provided_data, self.test_file, self.default_file
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

    def tearDown(self):
        os.remove(self.test_file)
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()