import logging
import random
from typing import List, Optional

import httpx
import nodriver as uc

from ..state import GTSM
from ..types import LocalStorageKV

TIMEOUT = 10
BASE_URL = "https://www.deepseekv3.com/en/chat/#try-chat"

TEXTAREA_SELECTOR = "textarea"
SUBMIT_BUTTON_SELECTOR = "form > div > button"

CAPTCHA_TEXT = "Human Verification"
CAPTCHA_ELEMENT = """<h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">Human Verification</h3>"""

SAMPLE_MESSAGES: List[str] = [
    "Berapa tanggal hari ini?",
    "Tanggal berapa sekarang?",
    "Hari ini tanggal berapa?",
    "Mohon informasikan tanggal hari ini.",
    "Saya ingin tahu tanggal hari ini.",
    "Bisakah Anda memberitahu tanggal hari ini?",
    "Tolong sebutkan tanggal hari ini.",
    "Saya perlu tahu tanggal hari ini.",
    "Apa tanggal hari ini?",
    "Tolong beritahu saya tanggal hari ini.",
]


class Driver:
    def __init__(self):
        self.config: uc.Config = uc.Config()
        self.browser: Optional[uc.Browser] = None
        self.page: Optional[uc.Tab] = None

    def set_config(self, config: uc.Config):
        assert config is not None, "Config is required"
        self.config = config

    @property
    async def __local_storage(self) -> LocalStorageKV:
        return await self.page.get_local_storage()

    @property
    async def __cookies(self) -> httpx.Cookies:
        c = httpx.Cookies()
        cookies = await self.browser.cookies.get_all()
        for cookie in cookies:
            c.set(cookie.name, cookie.value, cookie.domain, cookie.path)
        return c

    async def __resolve_captcha(self) -> None:
        while True:
            await self.page.wait(1)

            captcha = await self.page.find_element_by_text(CAPTCHA_TEXT, False)
            element = await captcha.get_html()

            if element == CAPTCHA_ELEMENT:
                logging.info("Waiting for captcha to be resolved...")
                continue
            else:
                logging.info("Captcha resolved.")
                break

    async def run(self) -> None:
        try:
            self.browser = await uc.Browser.create(self.config)
            self.page = await self.browser.get(BASE_URL)
            await self.page.set_local_storage({"chatMessages": []})

            input_textarea = await self.page.wait_for(
                TEXTAREA_SELECTOR,
                TEXTAREA_SELECTOR,
                timeout=TIMEOUT,
            )
            await input_textarea.send_keys(random.choice(SAMPLE_MESSAGES))

            submit_button = await self.page.wait_for(
                SUBMIT_BUTTON_SELECTOR,
                SUBMIT_BUTTON_SELECTOR,
                timeout=TIMEOUT,
            )
            await submit_button.click()
            await self.page.wait(2)

            await self.__resolve_captcha()

            # set to global state
            GTSM.set_state(await self.__cookies, await self.__local_storage)
        except Exception as e:
            raise Exception(e)
        finally:
            await self.page.close()
