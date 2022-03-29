import requests
import constants


def buildUrl(
    site: str,
    action: str,
    query: str
) -> str:
    return (f"https://{site}"
            f"/w/api.php?action={action}&format=json"
            f"&{query}")


def getCentralAuthInfo(username: str) -> str:
    api_url = buildUrl(
        'meta.wikimedia.org',
        'query',
        f"meta=globaluserinfo&guiuser={username}&guiprop=groups%7Cunattached%7Cmerged"
    )
    response = requests.get(api_url)
    return response.text
