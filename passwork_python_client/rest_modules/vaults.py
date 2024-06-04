from loguru import logger

import utils.http_client as http_client
import utils.messages as msg


def get_vault(vault_id: str, options):
    # receive vault item
    try:
        return options.http_session.get(
            url=f"{options.host}/vaults/{vault_id}",
            headers=options.request_headers,
        )
    except http_client.HttpClientError as ex:
        message = f"Vault with ID {vault_id} not found"
        logger.error(msg.STATUS_CODE_ERROR, message, ex.code)
        raise ex
