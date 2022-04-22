from discord.ext.commands.errors import CommandInvokeError

try:
    with open("message_id.txt", "r") as read_file:
        message_id = int(read_file.readline())
except (FileNotFoundError, ValueError):
    message_id = 0

async def main(client, channel):
    global message_id
    all_messages = []
    status = "Nothing"
    try:
        message = await client.get_messages(channel, limit=5)
    except CommandInvokeError:
        return "ConnectionError"
    for i in range(5):
        all_messages.append(message[i].to_dict())

    for message in all_messages:
        message_text = message["message"]
        if "#Житомирська_область" in message_text and "Повітряна тривога" in message_text and int(message["id"]) > message_id:
            status = "Alert"
            message_id = int(message["id"])
            with open("message_id.txt", "w") as write_file:
                write_file.write(str(message["id"]))
        elif "#Житомирська_область" in message_text and "Відбій тривоги" in message_text and int(message["id"]) > message_id:
            status = "Alert_Stop"
            message_id = int(message["id"])
            with open("message_id.txt", "w") as write_file:
                write_file.write(str(message["id"]))

    return status


async def run(client, channel):
    async with client:
        status = await main(client, channel)
        return status

