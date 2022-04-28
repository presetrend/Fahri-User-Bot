# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import io
import os
import math
import asyncio
import random
import urllib.request
from os import remove

from PIL import Image
from telethon.tl import functions, types
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    InputStickerSetID,
    MessageMediaPhoto,
    MessageMediaUnsupported,
)
from telethon.errors import PackShortNameOccupiedError
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import events
from userbot import (
    S_PACK_NAME as custompack,
    CMD_HELP,
    CMD_HANDLER as cmd,
    bot,
)
from userbot.utils.tools import animator, create_quotly
from userbot.utils import toni_cmd, edit_delete, edit_or_reply

KANGING_STR = [
    "Sedang Mengambil Sticker Ini Ke Pack Anda",
    "Sedang Mengambil Sticker Ini Ke Pack Anda",
]
def verify_cond(geezarray, text):
    return any(i in text for i in geezarray)

async def delpack(xx, conv, cmd, args, packname):
    try:
        await conv.send_message(cmd)
    except YouBlockedUserError:
        await xx.edit("You have blocked the @stickers bot. unblock it and try.")
        return None, None
    await conv.send_message("/delpack")
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.send_message(packname)
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.send_message("Yes, I am totally sure.")
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)

async def newpacksticker(
    xx,
    conv,
    cmd,
    args,
    pack,
    packnick,
    is_video,
    emoji,
    packname,
    is_anim,
    stfile,
    otherpack=False,
    pkang=False,
):
    try:
        await conv.send_message(cmd)
    except YouBlockedUserError:
        await xx.edit("You have blocked the @stickers bot. unblock it and try.")
        if not pkang:
            return None, None, None
        return None, None
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.send_message(packnick)
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    if is_video:
        await conv.send_file("animate.webm")
    elif is_anim:
        await conv.send_file("AnimatedSticker.tgs")
        os.remove("AnimatedSticker.tgs")
    else:
        stfile.seek(0)
        await conv.send_file(stfile, force_document=True)
    rsp = await conv.get_response()
    if not verify_cond(custompack, rsp.text):
        await xx.edit(
            f"Failed to add sticker, use @Stickers bot to add the sticker manually.\n**error :**{rsp}"
        )
        if not pkang:
            return None, None, None
        return None, None
    await conv.send_message(emoji)
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.get_response()
    await conv.send_message("/publish")
    if is_anim:
        await conv.get_response()
        await conv.send_message(f"<{packnick}>")
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.send_message("/skip")
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.get_response()
    await conv.send_message(packname)
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    if not pkang:
        return otherpack, packname, emoji
    return pack, packname


@toni_cmd(pattern=r"(?:tikel|kang)\s?(.)?")
async def kang(args):
    user = await args.client.get_me()
    if not user.username:
        user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    emojibypass = False
    is_video = False
    is_anim = False
    emoji = None

    if not message:
        return await edit_delete(
            args, "**Silahkan Reply Ke Pesan Media Untuk Mencuri Sticker itu!**"
        )

    if isinstance(message.media, MessageMediaPhoto):
        xx = await edit_or_reply(args, f"`{random.choice(KANGING_STR)}`")
        photo = io.BytesIO()
        photo = await args.client.download_media(message.photo, photo)
    elif isinstance(message.media, MessageMediaUnsupported):
        await edit_delete(
            args, "**File Tidak Didukung, Silahkan Reply ke Media Foto/GIF !**"
        )
    elif message.message:
        xx = await edit_or_reply(args, f"`{random.choice(KANGING_STR)}`")
        photo = await create_quotly(message)
    elif message.file and "image" in message.file.mime_type.split("/"):
        xx = await edit_or_reply(args, f"`{random.choice(KANGING_STR)}`")
        photo = io.BytesIO()
        await args.client.download_file(message.media.document, photo)
        if (
            DocumentAttributeFilename(file_name="sticker.webp")
            in message.media.document.attributes
        ):
            emoji = message.media.document.attributes[1].alt
            if emoji != "✨":
                emojibypass = True
    elif message.file and "tgsticker" in message.file.mime_type:
        xx = await edit_or_reply(args, f"`{random.choice(KANGING_STR)}`")
        await args.client.download_file(message.media.document, "AnimatedSticker.tgs")
        attributes = message.media.document.attributes
        for attribute in attributes:
            if isinstance(attribute, DocumentAttributeSticker):
                emoji = attribute.alt
        emojibypass = True
        is_anim = True
        photo = 1
    elif message.media.document.mime_type in ["video/mp4", "video/webm"]:
        if message.media.document.mime_type == "video/webm":
            xx = await edit_or_reply(args, f"`{random.choice(KANGING_STR)}`")
            await args.client.download_media(message.media.document, "Video.webm")
        else:
            xx = await edit_or_reply(args, "`Downloading...`")
            await animator(message, args, xx)
            await xx.edit(f"`{random.choice(KANGING_STR)}`")
        is_video = True
        emoji = "✨"
        emojibypass = True
        photo = 1
    else:
        return await edit_delete(
            args, "**File Tidak Didukung, Silahkan Reply ke Media Foto/GIF !**"
        )
    if photo:
        splat = args.text.split()
        if not emojibypass:
            emoji = "✨"
        pack = 1
        if len(splat) == 3:
            pack = splat[2]
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                pack = int(splat[1])
            else:
                emoji = splat[1]

        packname = f"Sticker_u{user.id}_Ke{pack}"
        if custompack is not None:
            packnick = f"{custompack}"
        else:
            f_name = f"@{user.username}" if user.username else user.first_name
            packnick = f"Sticker Pack {f_name}"

        cmd = "/newpack"
        file = io.BytesIO()

        if is_video:
            packname += "_vid"
            packnick += " (Video)"
            cmd = "/newvideo"
        elif is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        else:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")

        response = urllib.request.urlopen(
            urllib.request.Request(f"http://t.me/addstickers/{packname}")
        )
        htmlstr = response.read().decode("utf8").split("\n")

        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with args.client.conversation("@Stickers") as conv:
                try:
                    await conv.send_message("/addsticker")
                except YouBlockedUserError:
                    await args.client(UnblockRequest("@Stickers"))
                    await conv.send_message("/addsticker")
                await conv.get_response()
                await args.client.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                limit = "50" if (is_anim or is_video) else "120"
                while limit in x.text:
                    pack += 1
                    if custompack is not None:
                        packname = f"Sticker_u{user.id}_Ke{pack}"
                        packnick = f"{custompack}"
                    else:
                        f_name = (
                            f"@{user.username}" if user.username else user.first_name
                        )
                        packname = f"Sticker_u{user.id}_Ke{pack}"
                        packnick = f"Sticker Pack {f_name}"
                    await xx.edit(
                        "`Membuat Sticker Pack Baru "
                        + str(pack)
                        + " Karena Sticker Pack Sudah Penuh`"
                    )
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Gagal Memilih Pack.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        await args.client.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        await args.client.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file("AnimatedSticker.tgs")
                            remove("AnimatedSticker.tgs")
                        elif is_video:
                            await conv.send_file("Video.webm")
                            remove("Video.webm")
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        await args.client.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        await conv.get_response()
                        await args.client.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        await args.client.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        await args.client.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await args.client.send_read_acknowledge(conv.chat_id)
                        return await xx.edit(
                            "`Sticker ditambahkan ke pack yang berbeda !"
                            "\nIni pack yang baru saja dibuat!"
                            f"\nTekan [Sticker Pack](t.me/addstickers/{packname}) Untuk Melihat Sticker Pack",
                            parse_mode="md",
                        )
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                elif is_video:
                    await conv.send_file("Video.webm")
                    remove("Video.webm")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    return await xx.edit(
                        "**Gagal Menambahkan Sticker, Gunakan @Stickers Bot Untuk Menambahkan Sticker Anda.**"
                    )
                await conv.send_message(emoji)
                await args.client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/done")
                await conv.get_response()
                await args.client.send_read_acknowledge(conv.chat_id)
        else:
            await xx.edit("`Membuat Sticker Pack Baru`")
            async with args.client.conversation("@Stickers") as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUserError:
                    await args.client(UnblockRequest("@Stickers"))
                    await conv.send_message(cmd)
                await conv.get_response()
                await args.client.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                await args.client.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                elif is_video:
                    await conv.send_file("Video.webm")
                    remove("Video.webm")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    return await xx.edit(
                        "**Gagal Menambahkan Sticker, Gunakan @Stickers Bot Untuk Menambahkan Sticker.**"
                    )
                await conv.send_message(emoji)
                await args.client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")
                await conv.get_response()
                await args.client.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                await args.client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                await args.client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await args.client.send_read_acknowledge(conv.chat_id)

        await xx.edit(
            "** Sticker Berhasil Ditambahkan!**"
            f"\n      >> **[KLIK DISINI](t.me/addstickers/{packname})** <<\n**Untuk Menggunakan Stickers**",
            parse_mode="md",
        )


async def resize_photo(photo):
    image = Image.open(photo)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if size1 > size2:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        maxsize = (512, 512)
        image.thumbnail(maxsize)

    return image

@toni_cmd(pattern="delsticker ?(.*)")
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await edit_delete(event, "**Mohon Reply ke Sticker yang ingin anda Hapus.**")
        return
    reply_message = await event.get_reply_message()
    chat = "@Stickers"
    if reply_message.sender.bot:
        await edit_delete(event, "**Mohon Reply ke Sticker.**")
        return
    xx = await edit_or_reply(event, "`Processing...`")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=429000)
            )
            await conv.send_message("/delsticker")
            await conv.get_response()
            await asyncio.sleep(2)
            await event.client.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            await conv.send_message("/delsticker")
            await conv.get_response()
            await asyncio.sleep(2)
            await event.client.forward_messages(chat, reply_message)
            response = await response
        if response.text.startswith(
            "Sorry, I can't do this, it seems that you are not the owner of the relevant pack."
        ):
            await xx.edit("**Maaf, Sepertinya Anda bukan Pemilik Sticker pack ini.**")
        elif response.text.startswith(
            "You don't have any sticker packs yet. You can create one using the /newpack command."
        ):
            await xx.edit("**Anda Tidak Memiliki Stiker untuk di Hapus**")
        elif response.text.startswith("Please send me the sticker."):
            await xx.edit("**Tolong Reply ke Sticker yang ingin dihapus**")
        elif response.text.startswith("Invalid pack selected."):
            await xx.edit("**Maaf Paket yang dipilih tidak valid.**")
        else:
            await xx.edit("**Berhasil Menghapus Stiker.**")


@toni_cmd(pattern="csticker ?(.*)")
async def pussy(args):
    "To kang a sticker." 
    message = await args.get_reply_message()
    user = await args.client.get_me()
    userid = user.id
    if message and message.media:
        if message.file and "video/mp4" in message.file.mime_type:
            xx = await edit_or_reply(args, "__⌛ Downloading..__")
            sticker = await animator(message, args, xx)
            await edit_or_reply(xx, f"`{random.choice(KANGING_STR)}`")
        else:
            await edit_delete(args, "`Reply to video/gif...!`")
            return
    else:
        await edit_delete(args, "`I can't convert that...`")
        return
    cmd = "/newvideo"
    packname = f"tonic_{userid}_temp_pack"
    response = urllib.request.urlopen(
        urllib.request.Request(f"http://t.me/addstickers/{packname}")
    )
    htmlstr = response.read().decode("utf8").split("\n")
    if (
        "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
        not in htmlstr
    ):
        async with args.client.conversation("@Stickers") as xconv:
            await delpack(
                xx,
                xconv,
                cmd,
                args,
                packname,
            )
    await xx.edit("`Hold on, making sticker...`")
    async with args.client.conversation("@Stickers") as conv:
        otherpack, packname, emoji = await newpacksticker(
            xx,
            conv,
            "/newvideo",
            args,
            1,
            "Tonic-Userbot",
            True,
            "😂",
            packname,
            False,
            io.BytesIO(),
        )
    if otherpack is None:
        return
    await xx.delete()
    await args.client.send_file(
        args.chat_id,
        sticker,
        force_document=True,
        caption=f"**[Sticker Preview](t.me/addstickers/{packname})**\n*__It will remove automatically on your next convert.__",
        reply_to=message,
    )
    if os.path.exists(sticker):
        os.remove(sticker)

@toni_cmd(pattern="itos$")
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await edit_delete(
            event, "sir this is not a image message reply to image message"
        )
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await edit_delete(event, "sir, This is not a image ")
        return
    chat = "@buildstickerbot"
    xx = await edit_or_reply(event, "Membuat Sticker..")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=164977173)
            )
            msg = await event.client.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            msg = await event.client.forward_messages(chat, reply_message)
            response = await response
        if response.text.startswith("Hi!"):
            await xx.edit(
                "Can you kindly disable your forward privacy settings for good?"
            )
        else:
            await xx.delete()
            await event.client.send_read_acknowledge(conv.chat_id)
            await event.client.send_message(event.chat_id, response.message)
            await event.client.delete_message(event.chat_id, [msg.id, response.id])


@toni_cmd(pattern="get$")
async def _(event):
    rep_msg = await event.get_reply_message()
    if not event.is_reply or not rep_msg.sticker:
        return await edit_delete(event, "**Harap balas ke stiker**")
    xx = await edit_or_reply(event, "`Mengconvert ke foto...`")
    foto = io.BytesIO()
    foto = await event.client.download_media(rep_msg.sticker, foto)
    im = Image.open(foto).convert("RGB")
    im.save("sticker.png", "png")
    await event.client.send_file(
        event.chat_id,
        "sticker.png",
        reply_to=rep_msg,
    )
    await xx.delete()
    remove("sticker.png")
    
@toni_cmd(pattern="editsticker ?(.*)")
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await edit_delete(event, "**Mohon Reply ke Sticker dan Berikan emoji.**")
        return
    reply_message = await event.get_reply_message()
    emot = event.pattern_match.group(1)
    if reply_message.sender.bot:
        await edit_delete(event, "**Mohon Reply ke Sticker.**")
        return
    xx = await edit_or_reply(event, "`Processing...`")
    if emot == "":
        await xx.edit("**Silahkan Kirimkan Emot Baru.**")
    else:
        chat = "@Stickers"
        async with event.client.conversation(chat) as conv:
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=429000)
                )
                await conv.send_message("/editsticker")
                await conv.get_response()
                await asyncio.sleep(2)
                await event.client.forward_messages(chat, reply_message)
                await conv.get_response()
                await asyncio.sleep(2)
                await conv.send_message(f"{emot}")
                response = await response
            except YouBlockedUserError:
                await event.client(UnblockRequest(chat))
                await conv.send_message("/editsticker")
                await conv.get_response()
                await asyncio.sleep(2)
                await event.client.forward_messages(chat, reply_message)
                await conv.get_response()
                await asyncio.sleep(2)
                await conv.send_message(f"{emot}")
                response = await response
            if response.text.startswith("Invalid pack selected."):
                await xx.edit("**Maaf Paket yang dipilih tidak valid.**")
            elif response.text.startswith(
                "Please send us an emoji that best describes your sticker."
            ):
                await xx.edit(
                    "**Silahkan Kirimkan emoji yang paling menggambarkan stiker Anda.**"
                )
            else:
                await xx.edit(
                    f"**Berhasil Mengedit Emoji Stiker**\n**Emoji Baru:** {emot}"
                )


@toni_cmd(pattern=r"stkrinfo$")
async def get_pack_info(event):
    if not event.is_reply:
        return await edit_delete(event, "**Mohon Balas Ke Sticker**")

    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        return await edit_delete(
            event, "**Balas ke sticker untuk melihat detail pack**"
        )

    try:
        stickerset_attr = rep_msg.document.attributes[1]
        xx = await edit_or_reply(event, "`Processing...`")
    except BaseException:
        return await edit_delete(xx, "**Ini bukan sticker, Mohon balas ke sticker.**")

    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        return await edit_delete(xx, "**Ini bukan sticker, Mohon balas ke sticker.**")

    get_stickerset = await event.client(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            ),
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)

    OUTPUT = (
        f"❍▸ **Nama Sticker:** [{get_stickerset.set.title}](http://t.me/addstickers/{get_stickerset.set.short_name})\n"
        f"❍▸ **Official:** `{get_stickerset.set.official}`\n"
        f"❍▸ **Arsip:** `{get_stickerset.set.archived}`\n"
        f"❍▸ **Sticker Dalam Pack:** `{len(get_stickerset.packs)}`\n"
        f"❍▸ **Emoji Dalam Pack:** {' '.join(pack_emojis)}"
    )

    await xx.edit(OUTPUT)


@toni_cmd(pattern=r"getsticker$")
async def sticker_to_png(sticker):
    if not sticker.is_reply:
        await edit_delete(sticker, "**Harap balas ke stiker**")
        return False
    img = await sticker.get_reply_message()
    if not img.document:
        await edit_delete(sticker, "**Maaf , Ini Bukan Sticker**")
        return False
    xx = await edit_or_reply(sticker, "`Berhasil Mengambil Sticker!`")
    image = io.BytesIO()
    await sticker.client.download_media(img, image)
    image.name = "sticker.png"
    image.seek(0)
    await sticker.client.send_file(
        sticker.chat_id, image, reply_to=img.id, force_document=True
    )
    await xx.delete()


CMD_HELP.update(
    {
        "stickers": f"**Plugin : **`stickers`\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}kang` atau `{cmd}tikel` [emoji]\
        \n  ↳ : **Balas .kang Ke Sticker Atau Gambar Untuk Menambahkan Ke Sticker Pack Mu\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}kang` [emoji] atau `{cmd}tikel` [emoji]\
        \n  ↳ : **Balas {cmd}kang emoji Ke Sticker Atau Gambar Untuk Menambahkan dan costum emoji sticker Ke Pack Mu\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}delsticker` <reply sticker>\
        \n  ↳ : **Untuk Menghapus sticker dari Sticker Pack.\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}editsticker` <reply sticker> <emoji>\
        \n  ↳ : **Untuk Mengedit emoji stiker dengan emoji yang baru.\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}stkrinfo`\
        \n  ↳ : **Untuk Mendapatkan Informasi Sticker Pack.\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}stickers` <nama sticker pack >\
        \n  ↳ : **Untuk Mencari Sticker Pack.\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}csticker`\
        \n  ↳ : **Balas Gif/Video Untuk menjadikan Sticker\
        \n\n  •  **NOTE:** Untuk Membuat Sticker Pack baru Gunakan angka dibelakang `{cmd}kang`\
        \n  •  **CONTOH:** `{cmd}kang 2` untuk membuat dan menyimpan ke sticker pack ke 2\
    "
    }
)


CMD_HELP.update(
    {
        "sticker_v2": f"**Plugin : **`stickers`\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣?? :** `{cmd}getsticker`\
        \n  ↳ : **Balas Ke Stcker Untuk Mendapatkan File 'PNG' Sticker.\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}get`\
        \n  ↳ : **Balas ke sticker untuk mendapatkan foto sticker\
        \n\n  𝘾𝙤𝙢𝙢𝙖𝙣𝙙 :** `{cmd}itos`\
        \n  ↳ : **Balas ke foto untuk membuat foto menjadi sticker\
    "
    }
)
