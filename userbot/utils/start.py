from telethon import Button

from userbot import BOTLOG, BOTLOG_CHATID, LOGS, tgbot




async def startupmessage():
    """
    Start up message in telegram logger group
    """
    try:
        if BOTLOG:
            await tgbot.send_file(
                BOTLOG_CHATID,
                "https://telegra.ph/file/02e0ce30552175837c554.jpg",
                caption="✨ **Fahri UserBot Telah Diaktifkan**!!\n━━━━━━━━━━━━━━━\n➠ **VERSI USERBOT** - 5.0@master\n━━━━━━━━━━━━━━━\n➠ **Powered By:** @PRESETREND ",
                buttons=[(Button.url("DUKUNGAN", "https://t.me/Presetrend"),)],
            )
    except Exception as e:
        LOGS.error(e)
        return None
