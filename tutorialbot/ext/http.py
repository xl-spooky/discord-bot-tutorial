from collections import abc
from typing import Any, ClassVar

import aiohttp


class HttpClient:
    """HttpClient for performing asynchronous HTTP requests.

    Provides methods to create regular and authentication sessions, and to retrieve content
    or JSON data from a URL, as well as resolve redirects. Tracing is integrated via OpenTelemetry.
    """

    session: ClassVar[aiohttp.ClientSession]
    auth_session: ClassVar[aiohttp.ClientSession]

    @classmethod
    def create_session(cls, timeout: int = 10) -> aiohttp.ClientSession:
        """Create and assign a new aiohttp ClientSession with a specified timeout.

        Args
        ----
            timeout (int, optional):
                Total timeout for requests in seconds. Defaults to 10.

        Returns
        -------
            aiohttp.ClientSession:
                The created client session.
        """
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        session = aiohttp.ClientSession(timeout=timeout_config)
        cls.session = session
        return session

    @classmethod
    def create_auth_session(cls, login: str, password: str) -> aiohttp.ClientSession:
        """Create and assign a new aiohttp ClientSession with basic authentication.

        Args
        ----
            login (str): 
                The login/username for authentication.
            password (str):
                The password for authentication.

        Returns
        -------
            aiohttp.ClientSession:
                The created authenticated client session.
        """
        session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(login, password))
        cls.auth_session = session
        return session

    @classmethod
    async def get_content(cls, url: str, /, header: dict[str, str] | None = None) -> bytes:
        """Retrieve raw content (bytes) from the specified URL.

        This method starts a tracing span, makes a GET request to the URL, raises an error
        if the response is not successful, and returns the content as bytes.

        Args
        ----
            url (str): 
                The URL to retrieve content from.
                header (dict[str, str], optional): Optional HTTP headers. Defaults to None.

        Returns
        -------
            bytes: 
                The response content in bytes.
        """
        async with cls.session.get(url, headers=header) as response:
            response.raise_for_status()
            return await response.content.read()

    @classmethod
    async def get_json(
        cls, url: str, /, header: dict[str, str] | None = None
    ) -> abc.Mapping[str, Any]:
        """Retrieve JSON data from the specified URL.

        Starts a tracing span, sends a GET request to the URL, checks for successful response,
        and returns the JSON-decoded data.

        Args
        ----
            url (str): 
                The URL to retrieve JSON data from.
                header (dict[str, str], optional): Optional HTTP headers. Defaults to None.

        Returns
        -------
            Mapping[str, Any]: 
                The JSON data retrieved from the URL.
        """
        async with cls.session.get(url, headers=header) as response:
            response.raise_for_status()
            return await response.json()

    @classmethod
    async def resolve_redirect(cls, url: str) -> str:
        """Resolve the final URL after following any redirects.

        Starts a tracing span, sends a GET request with redirects allowed, 
        and returns the final URL.

        Args
        ----
            url (str): 
                The initial URL to resolve.

        Returns
        -------
            str:
                The final URL after redirection.
        """
        async with cls.session.get(url, allow_redirects=True) as response:
            response.raise_for_status()
            return str(response.url)
