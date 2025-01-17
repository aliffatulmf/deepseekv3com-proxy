from pathlib import WindowsPath

import httpx

DEFAULT_MODEL: str = "deepseek-chat"
TARGET_URL: str = "https://www.deepseekv3.com/api/chat"
EFS: str = "data: [DONE]\n\n"

HEADERS: httpx.Headers = httpx.Headers(
    {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
)

# Browser configuration
CHROME_DATA_DIR: str = WindowsPath("resources/chrome-user-data").resolve().as_posix()
CHROME_EXECUTABLE: str = WindowsPath("resources/chrome-win/chrome.exe").resolve().as_posix()
