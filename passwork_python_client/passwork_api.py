import pathlib
import sys

from loguru import logger

sys.path.append(str(pathlib.Path(__file__).resolve().parent))

from session_options import SessionOptions
from rest_modules.passwords import (
    get_password,
    get_attachments,
    search_passwords,
    add_password,
    delete_password,
    get_inbox_passwords,
    get_inbox_password,
)
from rest_modules.vaults import get_vault
from utils import (
    get_vault_password,
    get_encryption_key,
    get_customs,
    decrypt_and_save_password_attachment,
    decrypt_string,
    get_inbox_encryption_key,
)
import utils.http_client as http_client
import utils.messages as msg


class PassworkAPI:
    """Interface for interacting with a methods from rest-modules."""
    def __init__(self, options_override: dict | None = None):
        """session_options stores data for making requests to the API, and for encryption and decryption functions."""
        self.session_options = SessionOptions(options_override)

    def login(self):
        """Creates an API session using the login() method from the Users class and gets the tokens,
        then stores them in the session_options
        REST Endpoint: POST /auth/login/{apiKey}
        """
        self.session_options.login()
        self.session_options.create_headers()

    def logout(self):
        """Closes an API session.
        REST Endpoint: POST /auth/logout
        """
        self.session_options.logout()

    def get_user_info(self):
        self.session_options.get_user_info()

    def get_password(self, password_id: str) -> dict:
        """Retrieves a password by its identifier.
        REST Endpoint: GET /passwords/{password_id}
        Args:
            password_id (str): The identifier of the password to retrieve

        Returns:
            The retrieved password object dict
        """
        try:
            return get_password(self.session_options, password_id)
        except http_client.HttpClientError as ex:
            message = f"Password with ID {password_id} not found"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def get_vault(self, vault_id: str) -> dict:
        """Retrieves a vault by its identifier.
        REST Endpoint: GET /vaults/{vault_id}
        Args:
            vault_id (str): The identifier of the vault to retrieve

        Returns:
            The retrieved vault object dict
        """
        # receive vault item
        try:
            return get_vault(vault_id=vault_id, options=self.session_options)
        except http_client.HttpClientError as ex:
            message = f"Vault with ID {vault_id} not found"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def get_vault_password(self, vault_item: dict) -> str:
        """Retrieves the password for a given vault item.

        Args:
            vault_item: The vault item for which to retrieve the vault password

        Returns:
            The password of the vault item, or an empty string if not using a master password(client-side encryption)
        """
        return get_vault_password(vault_item, self.session_options.master_key) \
            if self.session_options.use_master_password else ""

    def get_password_encryption_key(self, password_item: dict, vault_password: str) -> str:
        """Decrypts the encryption key for a password item.

        Args:
            password_item: The password item
            vault_password: The password of the vault

        Returns:
            The encryption key
        """
        return get_encryption_key(password_item, vault_password, self.session_options.use_master_password)

    def get_password_plain_text(self, password_item: dict, password_encryption_key: str) -> str:
        """Decrypts a password item to plain text.

        Args:
            password_item: The item containing the encrypted password
            password_encryption_key: The encryption key for decrypting the password

        Returns:
            The decrypted password in plain text
        """
        return decrypt_string(password_item["cryptedPassword"], password_encryption_key, self.session_options)

    def get_customs(self, password_item: dict, password_encryption_key: str) -> list[dict]:
        """Retrieves custom passwords for a password item, decrypted.

        Args:
            password_item: The item containing encrypted custom fields
            password_encryption_key: The encryption key

        Returns:
            The decrypted custom fields
        """
        return get_customs(password_item, password_encryption_key, self.session_options)

    def get_attachments(self, password_item: dict, password_encryption_key: str, download_path: str):
        """Retrieves and decrypts attachments for a password item
        than saves results into downloaded_attachments folder.

        REST Endpoint: GET /passwords/{id}/attachment/{attachmentId}

        Args:
            password_item: The item containing encrypted attachments
            password_encryption_key: The encryption key
            download_path: Path for downloading attachments
        """

        try:
            attachments = get_attachments(password_item=password_item, options=self.session_options)
        except http_client.HttpClientError as ex:
            message = f"Failed to get attachments for password ID {password_item}"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex
        else:
            if not attachments:
                return None
            [decrypt_and_save_password_attachment(attachment, password_encryption_key, download_path)
             for attachment in attachments]

    def delete_password(self, password_id: str):
        """Deletes a password by its identifier.

        Args:
            password_id: The identifier of the password to be deleted
        """
        try:
            delete_password(password_id, self.session_options)
        except http_client.HttpClientError as ex:
            message = f"Error when deleting password with id {password_id}"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def search_password(self, **kwargs) -> list:
        """Searches for passwords matching given criteria.

        REST Endpoint: POST /passwords/search

        Args:
        The search criteria are specified as keyword arguments:
            query: str,
            tags: list[str],
            colors: list[str],
            vaultId: str | None,
            includeShared: bool,
            includeShortcuts: bool

        Returns:
            Array of password items
        """
        search_params = kwargs
        search_results = search_passwords(self.session_options, search_params)
        return search_results

    def add_password(self, password_adding_fields: dict, vault_item: dict, vault_password: str) -> dict:
        """Adds a new password.

        REST Endpoint: POST /passwords

        password_adding_fields = {
            "vaultId": str,
            "name": str,
            "url": str,
            "login": str,
            "description": str,
            "folderId": str | None,
            "password": str,
            "shortcutId": str | None,
            "tags": List[str],
            "snapshot": str | None,
            "color": int,
            "custom": [
                {
                    "name": str,
                    "value": str,
                    "type": str
                }
            ],
            "attachments": [
                {
                    "path": str,
                    "name": str
                }
            ]
        }

        Args:
            password_adding_fields: The fields required for adding the password
            vault_item: The vault item under which the new password will be added
            vault_password: The password of the vault

        Returns:
            Dict with added password data
        """
        try:
            return add_password(
                password_adding_fields,
                vault_item,
                vault_password,
                options=self.session_options,
            )
        except http_client.HttpClientError as ex:
            message = "Error when adding a new password"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def get_inbox_passwords(self) -> list[dict]:
        """Retrieves a list of all inbox passwords from the configured source.

        REST Endpoint: POST /sharing/inbox/list

        Returns:
        list[dict]: A list of dictionaries, where each dictionary represents an inbox password.
        """
        try:
            return get_inbox_passwords(self.session_options)
        except http_client.HttpClientError as ex:
            message = "Error when getting list of inbox passwords"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def get_inbox_password(self, inbox_password_id: str) -> dict:
        """Retrieves a specific inbox password based on its ID.

        REST Endpoint: POST /sharing/inbox/{inbox_password_id}

        Args:
            inbox_password_id (str): The unique identifier of the inbox password to retrieve.

        Returns:
            dict: A dictionary containing the details of the requested inbox password.
        """
        try:
            return get_inbox_password(inbox_password_id, self.session_options)
        except http_client.HttpClientError as ex:
            message = f"Error when getting inbox password id: {inbox_password_id}"
            logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
            raise ex

    def get_inbox_encryption_key(self, inbox_password) -> str:
        """Decrypts the encryption key for a password item.

        Args:
            inbox_password: Inbox password item

        Returns:
            str: The encryption key
        """

        return get_inbox_encryption_key(inbox_password, self.session_options)
