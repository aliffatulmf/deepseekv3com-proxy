import nodriver as uc

from .config import CHROME_DATA_DIR, CHROME_EXECUTABLE
from .session.selenium import Driver


def run_web() -> None:
    uc_cfg: uc.Config = uc.Config(
        user_data_dir=CHROME_DATA_DIR,
        browser_executable_path=CHROME_EXECUTABLE,
        headless=False,
    )

    session = Driver()
    session.set_config(uc_cfg)
    uc.loop().run_until_complete(session.run())
