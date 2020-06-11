import textwrap
from email.message import EmailMessage

import aiosmtplib  # type: ignore
from faust.agents import current_agent

import yarl
from common import settings
from common.records import MessageRecord
from consumer_src.topics import email_topic
from faust_consumer import app


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
