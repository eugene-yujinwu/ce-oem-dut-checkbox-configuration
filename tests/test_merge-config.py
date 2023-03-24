import unittest
import configparser
import os
import importlib

update_module = importlib.import_module("utils.manifest-update")

class checkbox_config_test(unittest.TestCase):

    default_file = "pc/default/checkbox.conf"
    test_file = "tmp_checkbox.conf"

    @staticmethod
    def dump_conf(config_obj):
        tmp_dict = {}
        for section in config_obj.sections():
            tmp_dict.update({section: {}})
            for key in config_obj[section].keys():
                tmp_dict[section].update({key: config_obj[section][key]})

        return tmp_dict

    @staticmethod
    def get_config_obj(filename):
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option

        with open(filename) as fp:
            config.read_file(fp)

        return config

    def setUp(self):
        print("Create an empty file")
        with open(self.test_file, "+w") as fp:
            pass
        return super().setUp()

    def test_combine_default_only(self):
        update_module.checkbox_conf_update(
            "", self.test_file, self.default_file
        )

        dict_expected = self.dump_conf(self.get_config_obj(self.default_file))
        dict_result = self.dump_conf(self.get_config_obj(self.test_file))

        self.assertEqual(
            str(dict_result), str(dict_expected),
            "failed to merge default content"
        )

    def test_combine_user_conf_only(self):
        user_provided_data = (
            "[environment]\n"
            "WPA_BG_SSID = bg-ssid\n"
            "WPA3 = bs-wpa3-ssid"
        )
        update_module.checkbox_conf_update(
            user_provided_data, self.test_file, self.default_file
        )

        default_conf = self.get_config_obj(self.default_file)
        default_conf.read_string(user_provided_data)
        dict_expected = self.dump_conf(default_conf)
        dict_result = self.dump_conf(self.get_config_obj(self.test_file))

        self.assertEqual(
            str(dict_result), str(dict_expected),
            "failed to combined user data and default conf"
        )

    def test_combine_all(self):

        default_conf = self.get_config_obj(self.default_file)
        test_conf = self.get_config_obj(self.test_file)

        config_data = {
            "environment": {
                "WPA_BG_SSID": "fake-ssid",
                "WPA_BG_OPEN": "fake-open-ssid"
            }
        }
        test_conf.read_dict(config_data)
        with open(self.test_file, "w") as fp:
            test_conf.write(fp)

        user_provided_data = (
            "[environment]\n"
            "WPA_BG_SSID = bg-ssid\n"
            "WPA3 = bs-wpa3-ssid"
        )

        update_module.checkbox_conf_update(
            user_provided_data, self.test_file, self.default_file
        )

        default_conf.read_dict(config_data)
        default_conf.read_string(user_provided_data)

        dict_expected = self.dump_conf(default_conf)
        dict_result = self.dump_conf(self.get_config_obj(self.test_file))

        self.assertEqual(
            str(dict_result), str(dict_expected),
            "failed to combine all configuration"
        )

    def tearDown(self):
        print("Remove a test file")
        os.remove(self.test_file)
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()