from session_options import SessionOptions


def get_vault(vault_id: str, options: SessionOptions) -> dict:
    return options.http_session.get(
        url=f"{options.host}/vaults/{vault_id}",
        headers=options.request_headers,
    )
