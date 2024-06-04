from loguru import logger

from session_options import SessionOptions
from utils import (
    generate_password,
    encrypt_string,
    use_key_encryption,
    validate_customs,
    encrypt_customs,
    format_attachments,
)
import utils.messages as msg


def get_password(options: SessionOptions, password_id: str) -> dict:
    return options.http_session.get(
        url=f"{options.host}/passwords/{password_id}",
        headers=options.request_headers,
    )


def get_attachments(password_item: dict, options: SessionOptions) -> list | None:
    attachments = password_item.get("attachments")
    if not attachments:
        logger.warning(f"Password with ID {password_item.get('id')} has no attachments")
        return None
    return [
        get_attachment(password_item.get("id"), attachment["id"], options)
        for attachment in attachments
    ]


def get_attachment(password_id: str, attachment_id: str, options: SessionOptions) -> dict:
    return options.http_session.get(
        url=f"{options.host}/passwords/{password_id}/attachment/{attachment_id}",
        headers=options.request_headers,
    )


def search_passwords(options: SessionOptions, search_params: dict) -> dict:
    """
    search_params = {
        "query": "",
        "tags": [],
        "colors": [],
        "vaultId": None,
        "includeShared": False,
        "includeShortcuts": False,
    }
    """
    search_result = options.http_session.post(
        url=f"{options.host}/passwords/search",
        json=search_params,
        headers=options.request_headers,
    )

    if not search_result:
        logger.warning(msg.PASSWORDS_NOT_FOUND)
    if isinstance(search_result, dict) and "errorMessage" in search_result:
        logger.error(search_result["errorMessage"])
        raise Exception
    return search_result


def add_password(fields: dict, vault: dict, vault_password: str, options: SessionOptions) -> dict:
    if not fields:
        fields = {}

    encryption_key = (
        generate_password() if options.use_master_password else vault_password
    )

    fields["cryptedPassword"] = encrypt_string(fields["password"], encryption_key, options)
    if use_key_encryption(vault):
        fields["cryptedKey"] = encrypt_string(encryption_key, vault_password, options)
    fields.pop("password", None)

    if "custom" in fields and len(fields["custom"]) > 0:
        validate_customs(fields["custom"])
        fields["custom"] = encrypt_customs(fields["custom"], encryption_key, options)

    if "attachments" in fields and len(fields["attachments"]) > 0:
        fields["attachments"] = format_attachments(fields["attachments"], encryption_key)

    fields.setdefault("name", "")

    return options.http_session.post(
        url=f"{options.host}/passwords",
        json=fields,
        headers=options.request_headers,
    )


def delete_password(password_id: str, options: SessionOptions) -> None:
    options.http_session.delete(
        url=f"{options.host}/passwords/{password_id}",
        headers=options.request_headers,
    )
    logger.success(f"Deletion of password with id {password_id} completed successfully")


def get_inbox_passwords(options: SessionOptions) -> dict:
    return options.http_session.get(
        url=f"{options.host}/sharing/inbox/list",
        headers=options.request_headers,
    )


def get_inbox_password(inbox_password_id: str, options: SessionOptions) -> dict:
    return options.http_session.post(
        url=f"{options.host}/sharing/inbox/{inbox_password_id}",
        headers=options.request_headers,
    )
