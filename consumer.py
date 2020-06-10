import pathlib
import textwrap
import typing
from email.message import EmailMessage

import aiosmtplib
import faust
from faust.agents import current_agent

import httpx
import settings
import yarl
from records import MessageRecord
from services import ObjectStoreService
from splinter import Browser


class ConsumerApp(faust.App):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.object_store_service = self.service(
            ObjectStoreService(  # noqa
                server_url=settings.OBJECT_STORE_URL,
                access_key=settings.OBJECT_STORE_ACCESS_KEY,
                secret_key=settings.OBJECT_STORE_SECRET_KEY,
                bucket_name=settings.OBJECT_STORE_BUCKET_NAME,
            )
        )


app = ConsumerApp(settings.CONSUMER_GROUP_ID)

message_topic = app.topic("messages", value_type=MessageRecord)
email_topic = app.topic("emails", value_type=MessageRecord)


def take_screenshot(message: MessageRecord) -> pathlib.Path:
    browser = None
    try:
        browser = Browser(headless=True, incognito=True)
        browser.visit(message.url)
        return pathlib.Path(browser.screenshot(suffix=".png", full=True))
    finally:
        browser.quit()


@app.agent(message_topic, sink=[email_topic])
async def consumer(messages):
    agent = current_agent()
    async for message in messages:
        message: MessageRecord
        agent.app.log.info(f"Received new message {message}")

        async with httpx.AsyncClient() as client:
            response = await client.get(message.url)

        if response.status_code == 200:
            agent.app.log.info(f"Execute Splinter for {message}")
            path: pathlib.Path = await agent.app.loop.run_in_executor(
                None, take_screenshot, message
            )
            agent.app.log.info(f"Screenshot of {message}")

            result = await agent.app.object_store_service.store_image(
                f"{message.identifier}.png", path.read_bytes()
            )
            agent.app.log.info(f"Stored into Object Store {result}")

            yield message


@app.agent(email_topic)
async def email_handler(stream):
    agent = current_agent()
    async for message in stream:
        message: MessageRecord
        email = EmailMessage()
        email["From"] = "no-reply@screenshotter.ie"
        email["To"] = message.email
        email["Subject"] = f"Screenshot {message.identifier}"
        email["X-Identifier"] = message.identifier
        email.add_header("X-Identifier", str(message.identifier))
        email.add_header("X-URL", message.url)
        screenshot_url = yarl.URL(settings.BASE_URL).with_path(
            f"{message.identifier}.png"
        )

        email.set_content(
            textwrap.dedent(
                f"""
        Hi,

        You can download your screenshot of this url [1] at this address [2]

        [1]: {message.url}
        [2]: {screenshot_url}
        """
            )
        )
        # email.add_alternative()
        print(f"{agent.name} {agent.app} {message=} {screenshot_url}")
        await aiosmtplib.send(message=email, hostname="localhost", port=1025)
