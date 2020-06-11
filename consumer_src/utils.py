import pathlib

from common.records import MessageRecord
from splinter import Browser  # type: ignore


def take_screenshot(message: MessageRecord) -> pathlib.Path:
    with Browser(headless=True, incognito=True) as browser:
        browser.visit(message.url)
        return pathlib.Path(browser.screenshot(suffix=".png", full=True))
