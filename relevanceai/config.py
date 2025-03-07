"""Configuration Settings"""
import configparser
import os

from doc_utils.doc_utils import DocUtils

PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PATH, "config.ini")


class Config(DocUtils):
    """
    Set and change configuration settings

    - Retries - Set the behaviour of retries for failed responses from the API
        - number_of_retries - Number of retries to attempt
        - seconds_between_retries - Seconds to wait between retries

    - Logging - Set the behaviour of logging
         - enable_logging - Whether to log
         - log_to_file - Whether to log to file
         - log_file_name - The name of the file to log to, if logging to file
         - logging_level - Minimum level to log

    - Upload - Set the behaviour of uploads to RelevanceAI
        - target_chunk_mb - Maximum upload size per request

    - API - Set the behaviour of API requests
        - base_url - The base url to access
        - output_format - The format of API responses

    - Dashboard - URLS to various things

    """

    def __init__(self):
        self.config = configparser.ConfigParser()
        self._read_config(CONFIG_PATH)
        super().__init__()

    def _read_config(self, config_path):
        """
        Set up custom config by reading in a file

        Parameters
        ----------
        config_path : string
            Path to config
        """
        self.config.read(config_path)

    @property
    def options(self):
        """View all current config settings"""
        return self.config._sections

    def get_option(self, option):
        """
        View current config settings

        Parameters
        ----------
        option : string
            Setting key
        """
        return self.get_field(option, self.config)

    def set_option(self, option, value):
        """
        Change a config settings

        Parameters
        ----------
        option : string
            Setting key
        value : string
            New setting
        """
        self.set_field(option, self.config, str(value))

    def reset_to_default(self):
        """Reset config to default"""
        self._read_config(CONFIG_PATH)

    @staticmethod
    def _create_default():
        config = configparser.ConfigParser()
        config["retries"] = {"number_of_retries": 3, "seconds_between_retries": 2}
        config["logging"] = {
            "log_to_file": False,
            "logging_level": "ERROR",
            "enable_logging": True,
            "log_file_name": "relevanceai",
        }
        config["upload"] = {"target_chunk_mb": 100, "max_chunk_size": 10000}
        config["api"] = {
            "base_url": "https://gateway-api-aueast.relevance.ai/latest",
            "base_ingest_url": "https://ingest-api-dev-aueast.relevance.ai/latest",
            "output_format": "json",
        }

        config["dashboard"] = {
            "dashboard_request_url": '''"https://us-central1-vectorai-auth.cloudfunctions.net/handleSDKRequest"''',
            "base_dashboard_url": '''"https://cloud.relevance.ai"''',
            "signup_endpoint": '''"/sdk/api"''',
            "search_dashboard_endpoint": '''"/sdk/search"''',
        }

        with open(CONFIG_PATH, "w") as configfile:
            config.write(configfile)

    def __getitem__(self, key):
        """
        Get the config using client.config["api.base_url"]
        """
        return self.get_option(key)

    def __setitem__(self, key: str, value: str):
        """
        Set the config using client.config["api.base_url"] = "https://..."
        """
        return self.set_option(key, value)


CONFIG = Config()

# To create the initial config
if __name__ == "__main__":
    Config._create_default()
