import pathlib

from faust.agents import current_agent

import httpx
from common.records import MessageRecord
from consumer_src.topics import email_topic, message_topic
from consumer_src.utils import take_screenshot
from faust_consumer import app


@app.agent(message_topic, sink=[email_topic])
async def consumer(messages):
    agent = current_agent()
    async for message in messages:
        message: MessageRecord
        agent.app.log.info(f"Received new message {message}")

        async with httpx.AsyncClient() as client:
            response = await client.get(message.url)

        agent.app.log.info(f"Response: {response=}")
        if response.status_code == 200:
            agent.app.log.info(f"Execute Splinter for {message}")
            path: pathlib.Path = await agent.app.loop.run_in_executor(
                None, take_screenshot, message
            )
            agent.app.log.info(f"Screenshot of {message}")

            result = await agent.app.object_store_service.store_object(
                f"{message.identifier}.png", path.read_bytes()
            )
            agent.app.log.info(f"Stored into Object Store {result}")

            yield message
