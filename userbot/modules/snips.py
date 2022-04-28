# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module containing commands for keeping global notes. """

from userbot import (
    CMD_HANDLER as cmd,
    CMD_HELP,
    BOTLOG_CHATID,
)
from userbot.events import register
from userbot.utils import toni_cmd


@register(outgoing=True, pattern=r"\$\w*", ignore_unsafe=True, disable_errors=True)
async def on_snip(event):
    """Snips logic."""
    try:
        from userbot.modules.sql_helper.snips_sql import get_snip
    except AttributeError:
        return
    name = event.text[1:]
    snip = get_snip(name)
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    if snip and snip.f_mesg_id:
        msg_o = await event.client.get_messages(
            entity=BOTLOG_CHATID, ids=int(snip.f_mesg_id)
        )
        await event.client.send_message(
            event.chat_id, msg_o.message, reply_to=message_id_to_reply, file=msg_o.media
        )
        await event.delete()
    elif snip and snip.reply:
        await event.client.send_message(
            event.chat_id, snip.reply, reply_to=message_id_to_reply
        )
        await event.delete()


@toni_cmd(pattern="snip (.*)")
async def on_snip_save(event):
    """For .snip command, saves snips for future use."""
    try:
        from userbot.modules.sql_helper.snips_sql import add_snip
    except AtrributeError:
        await event.edit("`Berjalan pada mode Non-SQL!`")
        return
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#ROSE #SNIP\
            \nKEYWORD: {keyword}\
            \n\nThe pesan berikut disimpan sebagai data untuk snip, mohon JANGAN dihapus !!",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID, messages=msg, from_peer=event.chat_id, silent=True
            )
            msg_id = msg_o.id
        else:
            await event.edit(
                "`Menyimpan potongan dengan media memerlukan BOTLOG_CHATID untuk disetel.`"
            )
            return
    elif event.reply_to_msg_id and not string:
        rep_msg = await event.get_reply_message()
        string = rep_msg.text
    success = "`Snip {} successfully. Use` **${}** `anywhere to get it`"
    if add_snip(keyword, string, msg_id) is False:
        await event.edit(success.format("updated", keyword))
    else:
        await event.edit(success.format("saved", keyword))


@toni_cmd(pattern="snips (.*)")
async def on_snip_list(event):
    """For .snips command, lists snips saved by you."""
    try:
        from userbot.modules.sql_helper.snips_sql import get_snips
    except AttributeError:
        await event.edit("`Running on Non-SQL mode!`")
        return

    message = "`No snips available right now.`"
    all_snips = get_snips()
    for a_snip in all_snips:
        if message == "`No snips available right now.`":
            message = "Available snips:\n"
            message += f"`${a_snip.snip}`\n"
        else:
            message += f"`${a_snip.snip}`\n"

    await event.edit(message)


@toni_cmd(pattern="remsnip (.*)")
async def on_snip_delete(event):
    """For .remsnip command, deletes a snip."""
    try:
        from userbot.modules.sql_helper.snips_sql import remove_snip
    except AttributeError:
        await event.edit("`Running on Non-SQL mode!`")
        return
    name = event.pattern_match.group(1)
    if remove_snip(name) is True:
        await event.edit(f"`Successfully deleted snip:` **{name}**")
    else:
        await event.edit(f"`Couldn't find snip:` **{name}**")


CMD_HELP.update(
    {
        "snips": f"✘ **Plugin snips** :\
\n\n  •  **Perintah** : `{cmd}snip` [name | data]\
  \n  •  **Fungsi** : Menyimpan pesan sebagai snip (catatan global) dengan nama. (Bekerja dengan foto, dokumen, dan stiker juga!).\
\n\n  •  **Perintah** : `{cmd}snips` \
  \n  •  **Fungsi** : Dapatkan semua cuplikan yang disimpan.\
\n\n  •  **Perintah** : `{cmd}remsnip` [snip_name]\
  \n  •  **Fungsi** : Menghapus snip yang ditentukan."
    }
)
