import os
import glob
import asyncio
from telethon import TelegramClient, events, connection

API_ID = 35073883
API_HASH = "9e646621b6bb33307c05f80f44529fed"

TOOL_PATH = os.path.expanduser("/home/daytona/apkpatcher/APKPatcher.jar")
DOWNLOAD_DIR = os.path.expanduser("/home/daytona/apkpatcher/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# استخدام وضع الاتصال عبر HTTP لتجاوز جدار الحماية
client = TelegramClient(
    'apk_session',
    API_ID,
    API_HASH,
    connection=connection.ConnectionHttp
)

@client.on(events.NewMessage(chats='me'))
async def handle_saved_messages(event):
    message = event.message

    if message.file and message.file.name and message.file.name.lower().endswith('.apk'):
        file_name = message.file.name
        reply_msg = await event.reply(f"⏳ جاري تنزيل الملف `{file_name}`...")

        file_path = os.path.join(DOWNLOAD_DIR, f"{message.id}_{file_name}")
        await client.download_media(message, file=file_path)

        await reply_msg.edit("🚀 جاري تطبيق الباتشات وتعديل التطبيق...")

        cmd = ["java", "-jar", TOOL_PATH, "-i", file_path, "-ssl", "-paid", "-rmads"]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        out_files = [
            f for f in glob.glob(f"{DOWNLOAD_DIR}/*.apk")
            if str(message.id) in f and not f.endswith(os.path.basename(file_path))
        ]

        if out_files:
            patched_file = out_files[0]
            await reply_msg.edit("⬆️ تم الانتهاء بنجاح! جاري رفع الملف المعدل...")
            
            await client.send_file(
                'me',
                file=patched_file,
                caption=f"✅ تم تعديل وتوقيع الملف بنجاح:\n`{file_name}`",
                force_document=True
            )
            await reply_msg.delete()

            for f in [file_path, patched_file]:
                if os.path.exists(f):
                    os.remove(f)
        else:
            err = (stdout.decode() + stderr.decode())[:400]
            await reply_msg.edit(f"❌ فشل التعديل:\n`{err}`")
            if os.path.exists(file_path):
                os.remove(file_path)

async def main():
    await client.start()
    print("⚡ السكربت جاهز ويعمل الآن... أرسل أي ملف APK إلى 'الرسائل المحفوظة' (Saved Messages).")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
