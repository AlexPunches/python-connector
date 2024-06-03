from rest_modules import is_failed_status_code
import utils.http_client as http_client


def get_vault(vault_id: str, options):
    requests: http_client.HttpClientProtocol = options.http_session
    # receive vault item
    response = requests.get(
        url=f"{options.host}/vaults/{vault_id}",
        headers=options.request_headers,
    )
    if is_failed_status_code(prefix=f"Vault with ID {vault_id} not found", status_code=response.status_code):
        raise Exception
    return response.json().get("data")
