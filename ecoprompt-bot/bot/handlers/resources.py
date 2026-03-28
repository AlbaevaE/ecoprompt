from aiogram import F, Router
from aiogram.types import Message

router = Router()

# TODO: Replace with your actual links
RESOURCES_URL = "https://drive.google.com/drive/folders/1VcdM5ye-scL1ddixPlcL2logrDoAV2nq?usp=sharing"  # e.g. Notion, Google Sheets, or NotebookLM link


@router.message(F.text.in_(["📖 Ресурсы", "📖 Ресурстар"]))
async def show_resources(message: Message, t=None, **kwargs):
    text = t("resources_title")
    if RESOURCES_URL:
        text += f"\n\n🔗 {RESOURCES_URL}"
    else:
        text += "\n\n⏳ Скоро здесь появятся ссылки / Жакында шилтемелер кошулат"
    await message.answer(text)
