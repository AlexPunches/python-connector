from loguru import logger

import utils.http_client as http_client
import utils.messages as msg


class Users:
    def __init__(self, options):
        self.options = options

    def login(self) -> tuple:
        url = f"{self.options.host}/auth/login/{self.options.api_key}"
        try:
            tokens = self.options.http_session.post(
                url=url,
                json={"useMasterPassword": self.options.use_master_password},
            )
        except http_client.HttpClientError as ex:
            match ex.code:
                case 400:
                    logger.error(
                        "Logon error, possibly MASTER_PASSWORD is specified in environment variables "
                        "with client-side encryption disabled"
                    )
                case 401:
                    logger.error(
                        "Logon error, possibly wrong API_KEY is specified in environment variables"
                    )
                case 404:
                    logger.error(
                        "Logon error, possibly wrong HOST is specified in environment variables"
                    )
                case _:
                    logger.error(f"Logon error, HTTP response status code {ex.code} != 200")
        else:
            logger.success("Logon successful, temporary API Token received")
            token, refresh_token = tokens.get("token"), tokens.get("refreshToken")
            return token, refresh_token

    def get_mk_options(self) -> dict:
        # PBKDF option
        try:
            return self.options.http_session.get(
                url=f"{self.options.host}/user/get-master-key-options",
                headers={"Passwork-Auth": self.options.token},
            )
        except http_client.HttpClientError as ex:
            message = "Failed to retrieve master key options"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def logout(self) -> dict:
        try:
            return self.options.http_session.post(
                url=f"{self.options.host}/auth/logout",
                headers={"Passwork-Auth": self.options.token},
            )
        except http_client.HttpClientError as ex:
            message = "Failed to log out"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def get_user_info(self) -> dict:
        try:
            return self.options.http_session.get(
                url=f"{self.options.host}/user/info",
                headers=self.options.request_headers,
            )
        except http_client.HttpClientError as ex:
            message = f"Failed to get user info"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
