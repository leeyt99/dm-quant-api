from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import requests

DEFAULT_BASE_URL = "https://gapi-ext.innodealing.com"
DEFAULT_TIMEOUT = 20
DEFAULT_CREDENTIALS_FILE = Path(__file__).resolve().parents[1] / "credentials.local.json"
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"


def _latest_official_wheel() -> Path | None:
    wheels = sorted(ASSETS_DIR.glob("dm_quant_api_client-*.whl"), reverse=True)
    return wheels[0] if wheels else None


OFFICIAL_WHEEL_PATH = _latest_official_wheel()
if OFFICIAL_WHEEL_PATH and str(OFFICIAL_WHEEL_PATH) not in sys.path:
    sys.path.insert(0, str(OFFICIAL_WHEEL_PATH))

OFFICIAL_CLIENT_IMPORT_ERROR: Exception | None = None
try:
    from dm_quant_api_client import DMQuantApiClient as OfficialDMQuantApiClient
except Exception as exc:  # pragma: no cover - depends on local install state
    OfficialDMQuantApiClient = None
    OFFICIAL_CLIENT_IMPORT_ERROR = exc


class DMQuantApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class Credentials:
    app_key: str
    app_secret: str
    base_url: str = DEFAULT_BASE_URL


def _coalesce(*values: str | None) -> str | None:
    for value in values:
        if value:
            return value
    return None


def snake_to_camel(key: str) -> str:
    if "_" not in key:
        return key
    parts = key.split("_")
    head = parts[0]
    tail = [part[:1].upper() + part[1:] for part in parts[1:] if part]
    return head + "".join(tail)


def camel_to_snake(key: str) -> str:
    first_pass = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", key)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first_pass).lower()


def convert_keys(value: Any, converter: Callable[[str], str]) -> Any:
    if isinstance(value, dict):
        return {
            converter(key) if isinstance(key, str) else key: convert_keys(item, converter)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [convert_keys(item, converter) for item in value]
    return value


def load_credentials(
    *,
    app_key: str | None = None,
    app_secret: str | None = None,
    credentials_file: str | None = None,
    base_url: str | None = None,
) -> Credentials:
    file_path = (
        Path(credentials_file).expanduser()
        if credentials_file
        else DEFAULT_CREDENTIALS_FILE
    )
    file_data: dict[str, Any] = {}

    if file_path.exists():
        text = file_path.read_text(encoding="utf-8").strip()
        if text:
            loaded = json.loads(text)
            if not isinstance(loaded, dict):
                raise ValueError(f"credentials file must be a JSON object: {file_path}")
            file_data = loaded

    resolved_app_key = _coalesce(
        app_key,
        os.getenv("DM_APP_KEY"),
        os.getenv("INNO_APP_KEY"),
        file_data.get("appKey"),
        file_data.get("app_key"),
    )
    resolved_app_secret = _coalesce(
        app_secret,
        os.getenv("DM_APP_SECRET"),
        os.getenv("INNO_SM4_KEY"),
        file_data.get("appSecret"),
        file_data.get("app_secret"),
        file_data.get("sm4Key"),
        file_data.get("sm4_key"),
    )
    resolved_base_url = _coalesce(
        base_url,
        os.getenv("DM_BASE_URL"),
        os.getenv("INNO_BASE_URL"),
        file_data.get("baseUrl"),
        file_data.get("base_url"),
        DEFAULT_BASE_URL,
    )

    if not resolved_app_key or not resolved_app_secret:
        raise ValueError(
            "missing credentials: pass --app-key/--app-secret, set env vars, "
            f"or populate {file_path}"
        )

    return Credentials(
        app_key=resolved_app_key,
        app_secret=resolved_app_secret,
        base_url=resolved_base_url,
    )


class SM4Crypto:
    block_size = 16

    def __init__(self, key: str):
        self.secret_key = self._prepare_key(key)

    def _prepare_key(self, key: str) -> bytes:
        key_bytes = key.encode("utf-8")
        if len(key_bytes) > self.block_size:
            return key_bytes[: self.block_size]
        if len(key_bytes) < self.block_size:
            return key_bytes.ljust(self.block_size, b"\0")
        return key_bytes

    def encrypt(self, plaintext: str) -> str:
        payload = self._pad(plaintext.encode("utf-8"))
        encrypted = self._run_openssl(payload, decrypt=False)
        return base64.urlsafe_b64encode(encrypted).decode("utf-8").rstrip("=")

    def decrypt(self, encrypted_base64: str) -> str:
        padded = encrypted_base64 + "=" * ((4 - len(encrypted_base64) % 4) % 4)
        encrypted = base64.urlsafe_b64decode(padded)
        plaintext = self._run_openssl(encrypted, decrypt=True)
        return self._unpad(plaintext).decode("utf-8")

    def _run_openssl(self, payload: bytes, *, decrypt: bool) -> bytes:
        command = [
            "openssl",
            "enc",
            "-sm4-ecb",
            "-nopad",
            "-nosalt",
            "-K",
            self.secret_key.hex(),
        ]
        if decrypt:
            command.append("-d")

        try:
            result = subprocess.run(
                command,
                input=payload,
                capture_output=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("openssl is required but was not found in PATH") from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"openssl sm4-ecb failed: {stderr}") from exc
        return result.stdout

    def _pad(self, payload: bytes) -> bytes:
        pad_len = self.block_size - (len(payload) % self.block_size)
        if pad_len == 0:
            pad_len = self.block_size
        return payload + bytes([pad_len]) * pad_len

    def _unpad(self, payload: bytes) -> bytes:
        if not payload:
            return payload
        pad_len = payload[-1]
        if pad_len < 1 or pad_len > self.block_size:
            raise ValueError("invalid PKCS7 padding")
        if payload[-pad_len:] != bytes([pad_len]) * pad_len:
            raise ValueError("invalid PKCS7 padding")
        return payload[:-pad_len]


class DMQuantApiClient:
    def __init__(
        self,
        *,
        credentials: Credentials,
        pythonic: bool = True,
        timeout: int | float = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
        session: requests.Session | None = None,
    ):
        self.base_url = credentials.base_url.rstrip("/")
        self.pythonic = pythonic
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = session or requests.Session()
        self.crypto = SM4Crypto(credentials.app_secret)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/144.0.0.0 Safari/537.36"
            ),
            "Content-Type": "application/json",
            "X-Dm-App-Key": credentials.app_key,
        }

    def post_data(
        self,
        data: dict[str, Any] | None,
        api_path: str,
        *,
        return_type: str = "dataframe",
    ) -> pd.DataFrame | dict[str, Any] | list[Any] | str | None:
        payload = data or {}
        if self.pythonic:
            payload = convert_keys(payload, snake_to_camel)

        raw_data = self._post(api_path, payload)
        if self.pythonic:
            raw_data = convert_keys(raw_data, camel_to_snake)

        if return_type == "dict":
            return raw_data
        if return_type != "dataframe":
            raise ValueError("return_type must be 'dataframe' or 'dict'")

        dataframe = to_dataframe(raw_data)
        if self.pythonic:
            dataframe = dataframe.rename(columns=camel_to_snake)
        return dataframe

    def _post(self, api_path: str, data: dict[str, Any]) -> Any:
        if not api_path.startswith("/"):
            raise ValueError("api_path must start with '/'")

        payload = self.crypto.encrypt(
            json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        )
        try:
            response = self.session.post(
                self.base_url + api_path,
                headers=self.headers,
                data=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        except requests.RequestException as exc:
            raise DMQuantApiError(f"request failed: {exc}") from exc

        if response.status_code != 200:
            raise DMQuantApiError(f"http {response.status_code}: {response.text[:500]}")

        response_body: Any
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text

        decrypted = self._decrypt_response_body(response_body)
        if isinstance(decrypted, dict) and "code" in decrypted:
            if decrypted.get("code") != 0:
                raise DMQuantApiError(
                    f"API error: {decrypted.get('message', 'unknown error')}"
                )
            return decrypted.get("data", decrypted)
        return decrypted

    def _decrypt_response_body(self, content: Any) -> Any:
        if isinstance(content, (dict, list)):
            return content

        encrypted_text = content.strip() if isinstance(content, str) else str(content)
        try:
            maybe_json = json.loads(encrypted_text)
        except Exception:
            maybe_json = encrypted_text

        if isinstance(maybe_json, (dict, list)):
            return maybe_json
        if not isinstance(maybe_json, str):
            return maybe_json

        decrypted_text = self.crypto.decrypt(maybe_json)
        stripped = decrypted_text.strip()
        if (stripped.startswith("{") and stripped.endswith("}")) or (
            stripped.startswith("[") and stripped.endswith("]")
        ):
            try:
                return json.loads(stripped)
            except Exception:
                return stripped
        return stripped


class OfficialDMQuantApiClientAdapter:
    def __init__(
        self,
        *,
        credentials: Credentials,
        pythonic: bool = True,
        timeout: int | float = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
        session: requests.Session | None = None,
    ):
        if OfficialDMQuantApiClient is None:
            detail = f": {OFFICIAL_CLIENT_IMPORT_ERROR}" if OFFICIAL_CLIENT_IMPORT_ERROR else ""
            raise DMQuantApiError(f"official dm_quant_api_client is unavailable{detail}")

        self.client = OfficialDMQuantApiClient(
            app_key=credentials.app_key,
            sm4_key=credentials.app_secret,
            base_url=credentials.base_url,
            timeout=timeout,
            verify_ssl=verify_ssl,
            session=session,
            pythonic=pythonic,
        )

    def post_data(
        self,
        data: dict[str, Any] | None,
        api_path: str,
        *,
        return_type: str = "dataframe",
    ) -> pd.DataFrame | dict[str, Any] | list[Any] | str | None:
        try:
            return self.client.post_data(data or {}, api_path, return_type=return_type)
        except Exception as exc:
            raise DMQuantApiError(str(exc)) from exc


def to_dataframe(data: Any) -> pd.DataFrame:
    if data is None:
        return pd.DataFrame()
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            columns = data.get("columns")
            if isinstance(columns, list):
                return pd.DataFrame(data["data"], columns=columns)
            return pd.DataFrame(data["data"])
        if isinstance(data.get("list"), list):
            return pd.DataFrame(data["list"])
        return pd.DataFrame([data])
    raise TypeError(f"unsupported response type for DataFrame conversion: {type(data)}")


def create_client(
    *,
    app_key: str | None = None,
    app_secret: str | None = None,
    credentials_file: str | None = None,
    base_url: str | None = None,
    pythonic: bool = True,
) -> OfficialDMQuantApiClientAdapter | DMQuantApiClient:
    credentials = load_credentials(
        app_key=app_key,
        app_secret=app_secret,
        credentials_file=credentials_file,
        base_url=base_url,
    )
    if OfficialDMQuantApiClient is not None:
        return OfficialDMQuantApiClientAdapter(credentials=credentials, pythonic=pythonic)
    return DMQuantApiClient(credentials=credentials, pythonic=pythonic)
