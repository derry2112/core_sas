# pylint: disable=C0116, W0613, C0303, C0301, C0305

from uuid import uuid4

from user_agents import parse

from app.models.V1.identifierModel import UserAuthIdentifier


async def get_device_info(user_id: int, user_agent_string: str, ip_address: str):
    user_agent = parse(user_agent_string)
    device_info = {
        "browser": user_agent.browser.family,
        "browser_version": user_agent.browser.version_string,
        "os": user_agent.os.family,
        "os_version": user_agent.os.version_string,
        "device": user_agent.device.family,
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
    }

    device_id = str(uuid4())

    await UserAuthIdentifier.create(
        user_id=user_id,
        user_agent=user_agent_string,
        ip_address=ip_address,
        device_id=device_id,
    )

    return device_info
