from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("rules"))
async def cmd_rules(message: Message):
    text = (
        "🃏 <b>KAGE POKER — Qoidalar va Tushuntirish</b>\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 <b>Bot qanday ishlaydi?</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Bu bot Telegram guruhlarida haqiqiy Texas Hold'em o'ynash uchun yaratilgan.\n\n"
        "• Guruhga botni qo'shasiz\n"
        "• /poker buyrug'i bilan stol ochasiz\n"
        "• Do'stlaringiz JOIN qilib qo'shiladi\n"
        "• O'yin boshlangach har kimga 2 tadan yashirin karta private chat orqali yuboriladi\n"
        "• Stolga ochiq kartalar chiqadi va o'ynaysiz\n\n"
        "<b>Asosiy buyruqlar:</b>\n"
        "/start — Botni ishga tushirish\n"
        "/profile — Profilingiz va balans\n"
        "/poker — Stol ochish (guruhda)\n"
        "/rules — Shu qoidalar\n"
        "/help — Qisqa yordam\n"
        "/send — Chip yuborish\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎮 <b>O'yin qanday bo'ladi? (Texas Hold'em)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Har bir o'yinchiga <b>2 ta yashirin karta</b> beriladi.\n"
        "Stolga jami <b>5 ta ochiq karta</b> chiqadi.\n"
        "Eng kuchli 5 ta kartalik kombinatsiyani yig'gan odam yutadi.\n\n"

        "<b>O'yin bosqichlari:</b>\n"
        "1. Pre-flop — 2 ta yashirin karta tarqatiladi\n"
        "2. Flop — Stolga 3 ta ochiq karta\n"
        "3. Turn — Stolga 1 ta ochiq karta\n"
        "4. River — Stolga oxirgi 1 ta ochiq karta\n"
        "5. Showdown — Kartalar ochiladi, g'olib aniqlanadi\n\n"

        "<b>Harakatlar:</b>\n"
        "• Fold — O'yinni tashlash\n"
        "• Check — Stavka qo'ymasdan o'tkazish\n"
        "• Call — Stavkani tenglashtirish\n"
        "• Raise — Stavkani oshirish\n"
        "• All-in — Butun chipni qo'yish\n\n"

        "<b>Kombinatsiyalar (kuchli → kuchsiz):</b>\n"
        "1. Royal Flush\n"
        "2. Straight Flush\n"
        "3. Four of a Kind\n"
        "4. Full House\n"
        "5. Flush\n"
        "6. Straight\n"
        "7. Three of a Kind\n"
        "8. Two Pair\n"
        "9. One Pair\n"
        "10. High Card\n\n"

        "💰 O'yin faqat <b>virtual chip</b> bilan olib boriladi.\n"
        "Real pul yo'q."
    )

    await message.answer(text)