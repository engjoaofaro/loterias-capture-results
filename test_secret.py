import os
import unittest

from secret import get_api_token


class FakeSM:
    def __init__(self, value=None, fail=False):
        self.value = value
        self.fail = fail

    def get_secret_value(self, SecretId=None):
        if self.fail:
            raise Exception("AccessDenied")
        return {"SecretString": self.value}


class TestGetApiToken(unittest.TestCase):
    def setUp(self):
        os.environ.pop("SECRET_NAME", None)
        os.environ.pop("TOKEN", None)

    def test_sem_secret_name_usa_env(self):
        os.environ["TOKEN"] = "env-token"
        self.assertEqual(get_api_token(use_cache=False), "env-token")

    def test_com_secret_name_le_do_secrets_manager(self):
        os.environ["SECRET_NAME"] = "loterias/apiloterias-token"
        os.environ["TOKEN"] = "env-token"
        self.assertEqual(get_api_token(client=FakeSM(value="secret-token"), use_cache=False), "secret-token")

    def test_falha_no_secrets_manager_cai_para_env(self):
        os.environ["SECRET_NAME"] = "loterias/apiloterias-token"
        os.environ["TOKEN"] = "env-token"
        self.assertEqual(get_api_token(client=FakeSM(fail=True), use_cache=False), "env-token")


if __name__ == "__main__":
    unittest.main()
