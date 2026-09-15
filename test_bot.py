"""
STREET TEST — Test Tekshirish Telegram Boti va Mini App Serveri
Aiogram 3.x + aiohttp WebApp Server
============================================================
Bot Token: 8892124781:AAGTRWY78lfHn3pQoBoIG30zH9OoDQF5N2g
Admin ID: 8039427064
"""

import asyncio
import json
import logging
import os
import sys
import time
import urllib.parse
from typing import Optional, Dict, Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    WebAppInfo, FSInputFile, MenuButtonWebApp, BotCommand
)
from aiohttp import web
import test_db

# ── SOZLAMALAR ────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8892124781:AAGTRWY78lfHn3pQoBoIG30zH9OoDQF5N2g")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8039427064"))
PORT = int(os.getenv("PORT", "8080"))
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://bcc029b8f2861a.lhr.life")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# ── FSM HOLATLARI ─────────────────────────────────────
class RegistrationState(StatesGroup):
    fullname = State()
    phone = State()

class SolveTestState(StatesGroup):
    test_code = State()

class CreateTestState(StatesGroup):
    title = State()
    test_code = State()
    pdf_file = State()
    answers = State()

class UploadPostPdfState(StatesGroup):
    pdf_file = State()

class AddAdminState(StatesGroup):
    tg_id_or_user = State()

class SetTimeLimitState(StatesGroup):
    test_id = State()
    time_limit = State()

# ── KEYBOARDS (TUGMALAR) ──────────────────────────────
def main_menu_kb(user_tg_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🔢 Test kodini kiritish")],
        [KeyboardButton(text="📊 Mening natijalarim"), KeyboardButton(text="👤 Profilim")],
        [KeyboardButton(text="ℹ️ Bot haqida")]
    ]
    if test_db.is_admin(user_tg_id, ADMIN_ID):
        buttons.append([KeyboardButton(text="⚙️ Admin Panel")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def profile_webapp_kb(user_tg_id: int) -> InlineKeyboardMarkup:
    """Shaxsiy profil mini ilovasini ochish tugmasi."""
    app_url = f"{WEBAPP_URL}/app.html"
    buttons = [
        [make_webapp_button("📱 Shaxsiy profilni ochish", app_url, fallback_cb="open_app_info")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def results_webapp_kb() -> InlineKeyboardMarkup:
    """Natijalarni ko'rish mini ilovasi tugmasi."""
    app_url = f"{WEBAPP_URL}/app.html"
    buttons = [
        [make_webapp_button("📊 Asosiy ilovani ochish", app_url, fallback_cb="open_app_info")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def contact_share_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def admin_menu_kb() -> InlineKeyboardMarkup:
    admin_webapp_url = f"{WEBAPP_URL}/admin.html"
    try:
        counts = test_db.get_users_count()
        total_u = counts.get("total", 0)
        pending_u = counts.get("pending", 0)
        btn_text = f"👥 Foydalanuvchilar ({total_u} ta)"
        if pending_u > 0:
            btn_text += f" ⏳ {pending_u} ta yangi"
    except Exception:
        btn_text = "👥 Barcha foydalanuvchilar ro'yxati"

    buttons = [
        [make_webapp_button("📱 Yangi test yaratish (Admin Mini App)", admin_webapp_url, fallback_cb="admin_webapp_info")],
        [InlineKeyboardButton(text="➕ Bot orqali tezkor qo'shish", callback_data="admin_add_test")],
        [InlineKeyboardButton(text="📋 Testlarni boshqarish (O'chirish / Vaqt)", callback_data="admin_manage_tests")],
        [InlineKeyboardButton(text=btn_text, callback_data="admin_view_users")],
        [InlineKeyboardButton(text="👑 Adminlar boshqaruvi", callback_data="admin_manage_admins")],
        [InlineKeyboardButton(text="📊 Test natijalari va reyting", callback_data="admin_leaderboard")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def make_webapp_button(text: str, url: str, fallback_cb: str = "open_webapp_info") -> InlineKeyboardButton:
    """Telegram WebApp faqat HTTPS talab qiladi. Agar HTTP (localhost) bo'lsa callback ishlatiladi."""
    if url.startswith("https://"):
        return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))
    elif url.startswith("http://") and not ("localhost" in url or "127.0.0.1" in url):
        return InlineKeyboardButton(text=text, url=url)
    else:
        return InlineKeyboardButton(text=text, callback_data=fallback_cb)

# ── TEST KARTASINI FOYDALANUVCHIGA YUBORISH (BIR MARTALIK TEKSHIRUV BILAN) ──
async def send_test_card(target_message: Message, test: Dict[str, Any], user_tg_id: int):
    """Test ma'lumotlari, PDF va WebApp tugmasini yuboradi. Agar foydalanuvchi allaqachon topshirgan bo'lsa qayta topshirish taqiqlanadi."""
    existing_sub = test_db.get_user_submission_for_test(test["id"], user_tg_id)
    
    if existing_sub:
        dt = time.strftime("%d.%m.%Y %H:%M", time.localtime(existing_sub["submitted_at"]))
        grade = test_db.calculate_grade(existing_sub.get("score", 0))
        text = (
            f"⛔️ <b>Siz ushbu testni allaqachon topshirgansiz!</b>\n\n"
            f"📖 <b>Test:</b> {test['title']}\n"
            f"🎖 <b>Daraja:</b> <b>{grade}</b> ({existing_sub['score']} ball)\n"
            f"✅ <b>To'g'ri javoblar:</b> {existing_sub['correct_count']} ta\n"
            f"🕒 <b>Topshirilgan vaqt:</b> {dt}\n\n"
            f"⚠️ <i>Qoidalarga ko'ra, har bir testni faqat 1 marta topshirish mumkin. Qayta ishlash huquqi mavjud emas!</i>"
        )
        await target_message.answer(text)
        return

    if test.get("is_active", 1) == 0:
        await target_message.answer(
            f"⛔️ <b>«{test['title']}» testi to'xtatilgan!</b>\nAdmin tomonidan javoblar qabul qilish yopilgan."
        )
        return

    params = {
        "test_id": test["id"],
        "test_code": test["test_code"],
        "title": test["title"],
        "subject": test.get("subject", "Matematika"),
        "user_id": user_tg_id
    }
    encoded_url = f"{WEBAPP_URL}?{urllib.parse.urlencode(params)}"

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [make_webapp_button("📝 Javoblarni topshirish (Mini App)", encoded_url, fallback_cb=f"solve_test_{test['id']}")]
    ])

    time_info = f"⏱ <b>Vaqt chegarasi:</b> {test['time_limit_min']} daqiqa\n" if test.get("time_limit_min", 0) > 0 else ""

    caption = (
        f"📖 <b>{test['title']}</b>\n"
        f"📌 <b>Fan:</b> {test.get('subject', 'Matematika')}\n"
        f"❓ <b>Savollar:</b> 55 ta (1-32 ABCD, 33-35 ABCDEF, 36a-45b Yozma)\n"
        f"{time_info}\n"
        f"⚠️ <i>Eslatma: Testni faqat 1 marta topshirish mumkin! Javoblaringizni belgilab bo'lgach, «Testni yakunlash» tugmasini bosing.</i>"
    )

    sent = False
    if test.get("pdf_file_id"):
        try:
            await target_message.answer_document(
                document=test["pdf_file_id"],
                caption=caption,
                reply_markup=inline_kb
            )
            sent = True
        except Exception as e:
            log.warning(f"PDF yuborishda xatolik: {e}")

    if not sent:
        try:
            await target_message.answer(caption, reply_markup=inline_kb)
        except Exception as e:
            log.error(f"Xabar yuborishda xatolik: {e}")
            await target_message.answer(caption)

# ── BOT HANDLERLARI (FOYDALANUVCHI QISMI) ──────────────

async def check_access(message: Message) -> bool:
    """Foydalanuvchi admin tomonidan tasdiqlanganligini tekshiradi."""
    uid = message.from_user.id
    if test_db.is_admin(uid, ADMIN_ID):
        return True
    u = test_db.get_user(uid)
    if not u:
        await message.answer("⚠️ Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting.")
        return False
    st = u.get("status", "pending")
    if st == "pending":
        await message.answer(
            "⏳ <b>Arizangiz ko'rib chiqilmoqda!</b>\n\n"
            "Admin hali botdan foydalanish huquqini bermagan. Iltimos, admin tasdiqlashini kuting."
        )
        return False
    elif st in ["blocked", "rejected"]:
        await message.answer(
            "⛔️ <b>Sizning botdan foydalanish huquqingiz to'xtatilgan yoki chiqarib yuborilgansiz!</b>\n\n"
            "Murojaat uchun: @eshmbetov"
        )
        return False
    return True

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user = test_db.get_user(user_tg_id)

    if not user:
        await state.set_state(RegistrationState.fullname)
        await message.answer(
            "👋 <b>Assalomu alaykum! Test Tekshirish Tizimiga xush kelibsiz!</b>\n\n"
            "Tizimdan to'liq foydalanish va ruxsat olish uchun ro'yxatdan o'ting.\n\n"
            "✍️ <b>Iltimos, Ism va Familiyangizni kiriting:</b>\n"
            "<i>(Misol: Shaxriyor Eshimbetov)</i>",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        is_adm = test_db.is_admin(user_tg_id, ADMIN_ID)
        st = user.get("status", "pending")
        if not is_adm:
            if st == "pending":
                await message.answer(
                    "⏳ <b>Arizangiz ko'rib chiqilmoqda...</b>\n\n"
                    "Admin hali botdan foydalanishingizga ruxsat bermagan. Iltimos, admin tasdiqlashini kuting."
                )
                return
            elif st in ["blocked", "rejected"]:
                await message.answer(
                    "⛔️ <b>Sizning foydalanish huquqingiz admin tomonidan to'xtatilgan yoki chiqarib yuborilgansiz!</b>\n\n"
                    "Murojaat uchun: @eshmbetov"
                )
                return

        await state.clear()
        await message.answer(
            f"👋 <b>Xush kelibsiz, {user['fullname']}!</b>\n\n"
            "Kerakli bo'limni tanlang yoki to'g'ridan-to'g'ri test kodini yuboring 👇",
            reply_markup=main_menu_kb(user_tg_id)
        )

# Ro'yxatdan o'tish: Ism kiritildi
@router.message(RegistrationState.fullname)
async def reg_fullname(message: Message, state: FSMContext):
    fullname = (message.text or "").strip()
    if len(fullname) < 3:
        await message.answer("⚠️ Iltimos, to'liq ism va familiyangizni kiriting:")
        return

    await state.update_data(fullname=fullname)
    await state.set_state(RegistrationState.phone)
    await message.answer(
        "📱 <b>Endi telefon raqamingizni yuboring:</b>\n\n"
        "Quyidagi <b>«📱 Telefon raqamni yuborish»</b> tugmasini bosing yoki raqamingizni yozing (+998901234567):",
        reply_markup=contact_share_kb()
    )

# Ro'yxatdan o'tish: Kontakt yoki Raqam yuborildi
@router.message(RegistrationState.phone)
async def reg_phone(message: Message, state: FSMContext):
    phone = ""
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text.strip()

    if not phone or len(phone) < 7:
        await message.answer("⚠️ Iltimos, to'g'ri telefon raqam kiriting:")
        return

    data = await state.get_data()
    fullname = data.get("fullname", "Foydalanuvchi")
    user_tg_id = message.from_user.id
    username = message.from_user.username

    is_adm = test_db.is_admin(user_tg_id, ADMIN_ID)
    status = "approved" if is_adm else "pending"

    test_db.add_or_update_user(user_tg_id, fullname, phone, username, status=status)
    await state.clear()

    if is_adm or status == "approved":
        await message.answer(
            f"🎉 <b>Tabriklaymiz, {fullname}!</b>\n\n"
            "Siz tizimdan muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
            "Endi testlarni ishlashingiz mumkin!",
            reply_markup=main_menu_kb(user_tg_id)
        )
    else:
        await message.answer(
            f"⏳ <b>Hurmatli {fullname}!</b>\n\n"
            "Arizangiz qabul qilindi va <b>Adminga ruxsat olish uchun yuborildi</b>.\n\n"
            "Admin arizangizni tasdiqlashi bilan sizga xabar yuboriladi va bot to'liq ishga tushadi!",
            reply_markup=ReplyKeyboardRemove()
        )
        # Adminga tezkor ruxsat berish xabari
        req_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"user_quick_approve_{user_tg_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"user_quick_reject_{user_tg_id}")
            ]
        ])
        admin_alert = (
            f"🔔 <b>Yangi foydalanuvchi botga kirish uchun ruxsat so'ramoqda:</b>\n\n"
            f"👤 <b>Ism:</b> {fullname}\n"
            f"📱 <b>Telefon:</b> <code>{phone}</code>\n"
            f"🆔 <b>Telegram ID:</b> <code>{user_tg_id}</code>\n"
            f"🌐 <b>Username:</b> @{username or 'yo_q'}"
        )
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_alert, reply_markup=req_kb)
        except Exception as e:
            log.warning(f"Adminga so'rov yuborishda xatolik: {e}")

# 1. 🔢 Test kodini kiritish (Prompt)
@router.message(F.text == "🔢 Test kodini kiritish")
@router.message(Command("solve"))
async def enter_test_code_prompt(message: Message, state: FSMContext):
    if not await check_access(message):
        return
    await state.set_state(SolveTestState.test_code)
    await message.answer(
        "🔢 <b>Test kodini kiriting:</b>\n\n"
        "<i>(Masalan: <code>MAT-01</code> yoki <code>101</code>)</i>\n\n"
        "Bekor qilish uchun pastdagi menyudan foydalaning."
    )

# Test kodi kiritildi (FSM)
@router.message(SolveTestState.test_code)
async def process_solve_test_code(message: Message, state: FSMContext):
    if not await check_access(message):
        await state.clear()
        return
    text = (message.text or "").strip()
    if text in ["🔢 Test kodini kiritish", "📊 Mening natijalarim", "👤 Profilim", "ℹ️ Bot haqida", "⚙️ Admin Panel"]:
        await state.clear()
        if text == "📊 Mening natijalarim":
            await show_my_results(message)
        elif text == "👤 Profilim":
            await show_profile(message)
        elif text == "ℹ️ Bot haqida":
            await show_about(message)
        elif text == "⚙️ Admin Panel":
            await admin_panel_handler(message)
        elif text == "🔢 Test kodini kiritish":
            await enter_test_code_prompt(message, state)
        return

    code = text.upper().replace("#", "")
    test = test_db.get_test_by_code(code)
    await state.clear()

    if not test:
        await message.answer(
            f"❌ <b>«{text}» kodi bo'yicha test topilmadi!</b>\n\n"
            f"Iltimos, kodni to'g'ri kiritganingizni tekshiring.",
            reply_markup=main_menu_kb(message.from_user.id)
        )
        return

    await send_test_card(message, test, message.from_user.id)


@router.callback_query(F.data.startswith("solve_test_"))
async def solve_test_cb(call: CallbackQuery):
    test_id = int(call.data.split("_")[2])
    t = test_db.get_test_by_id(test_id)
    if not t:
        await call.answer("Test topilmadi!", show_alert=True)
        return
    
    existing_sub = test_db.get_user_submission_for_test(test_id, call.from_user.id)
    if existing_sub:
        grade = test_db.calculate_grade(existing_sub.get("score", 0))
        await call.answer(f"⛔️ Siz bu testni topshirgansiz! Daraja: {grade} ({existing_sub['score']} ball)", show_alert=True)
        return

    params = {
        "test_id": t["id"],
        "test_code": t["test_code"],
        "title": t["title"],
        "subject": t.get("subject", "Matematika"),
        "user_id": call.from_user.id
    }
    encoded_url = f"{WEBAPP_URL}?{urllib.parse.urlencode(params)}"
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [make_webapp_button("📝 Testni boshlash (Mini App)", encoded_url)]
    ])
    await call.message.answer(
        f"📝 <b>{t['title']}</b> testini yechish uchun quyidagi tugmani bosing 👇",
        reply_markup=reply_kb
    )
    await call.answer()

@router.callback_query(F.data == "admin_webapp_info")
async def admin_webapp_info_cb(call: CallbackQuery):
    admin_webapp_url = f"{WEBAPP_URL}/admin.html"
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [make_webapp_button("📱 Admin Panelni ochish (Mini App)", admin_webapp_url)],
        [InlineKeyboardButton(text="🔙 Admin Menyuga qaytish", callback_data="admin_back_to_menu")]
    ])
    text = (
        f"📱 <b>Admin Mini App (Kalit va ballar kiritish):</b>\n\n"
        f"Ushbu paneldan 45 ta savolning kalitlari va har biriga alohida ballarni qulay belgilashingiz mumkin!\n\n"
        f"Ochish uchun quyidagi tugmani bosing 👇"
    )
    try:
        await call.message.edit_text(text, reply_markup=reply_kb)
    except Exception:
        await call.message.answer(text, reply_markup=reply_kb)
    await call.answer()

# 2. 📊 Mening natijalarim
@router.message(F.text == "📊 Mening natijalarim")
@router.message(Command("results"))
async def show_my_results(message: Message):
    await message.answer(
        "📊 <b>Barcha test natijalaringiz, to'liq tahlil va to'g'ri kalitlarni asosiy ilovadan ko'rishingiz mumkin.</b>\n\n"
        "Ilovani ochish uchun quyidagi tugmani bosing 👇",
        reply_markup=results_webapp_kb()
    )

# 3. 👤 Profil
@router.message(F.text == "👤 Profilim")
@router.message(Command("profile"))
async def show_profile(message: Message):
    user = test_db.get_user(message.from_user.id)
    if not user:
        await message.answer("Profil topilmadi. /start buyrug'ini bosing.")
        return

    submissions = test_db.get_user_submissions(message.from_user.id)
    tests_count = len(submissions)
    dt = time.strftime("%d.%m.%Y", time.localtime(user["registered_at"]))

    await message.answer(
        f"👤 <b>{user['fullname']}</b>\n"
        f"📱 {user['phone']}\n"
        f"📋 Ishlangan testlar: <b>{tests_count} ta</b>\n"
        f"📅 Ro'yxatdan: {dt}\n\n"
        f"📲 <i>Batafsil ma'lumot uchun shaxsiy profilni oching:</i>",
        reply_markup=profile_webapp_kb(message.from_user.id)
    )

# 4. ℹ️ Bot haqida
@router.message(F.text == "ℹ️ Bot haqida")
@router.message(Command("help"))
async def show_about(message: Message):
    await message.answer(
        "🤖 <b>Test Tekshirish Tizimi Boti</b>\n\n"
        "Ushbu bot orqali siz:\n"
        "• PDF formatidagi testlarni yuklab olishingiz;\n"
        "• Telegram Mini App orqali 45 talik testlarga javob belgilashingiz;\n"
        "• Maxsus matematik klaviaturadan foydalanib yopiq savollarni kiritishingiz;\n"
        "• Natijalarni bir zumda tekshirib, xatolaringiz ustida ishlashingiz mumkin!\n\n"
        "📞 <b>Murojaat uchun:</b> @eshmbetov"
    )

# 5. 📱 Mini App buyrug'i
@router.message(Command("app"))
async def open_app_command(message: Message):
    await message.answer(
        "📱 <b>RASH TEST Mini App tizimiga kirish:</b>\n\n"
        "Quyidagi tugmani bosing 👇",
        reply_markup=results_webapp_kb()
    )

# ── ADMIN PANEL HANDLERLARI ───────────────────────────

@router.message(F.text == "⚙️ Admin Panel")
async def admin_panel_handler(message: Message):
    if not test_db.is_admin(message.from_user.id, ADMIN_ID):
        await message.answer("⛔️ Bu bo'lim faqat bot administratori uchun!")
        return

    await message.answer(
        "⚙️ <b>ADMIN BOSHQARUV PANELI</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang 👇",
        reply_markup=admin_menu_kb()
    )

# 1. Tezkor test qo'shish (Fan so'ralmaydi — har doim Matematika)
@router.callback_query(F.data == "admin_add_test")
async def admin_start_add_test(call: CallbackQuery, state: FSMContext):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    await state.set_state(CreateTestState.title)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel_create_test")]
    ])
    text = (
        "➕ <b>Yangi test qo'shish (1/4):</b>\n\n"
        "Test nomini kiriting:\n<i>(Masalan: Matematika Blok Test #1)</i>"
    )
    try:
        await call.message.edit_text(text, reply_markup=cancel_kb)
    except Exception:
        await call.message.answer(text, reply_markup=cancel_kb)
    await call.answer()

@router.callback_query(F.data == "admin_cancel_create_test")
async def admin_cancel_create_test_cb(call: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "⚙️ <b>ADMIN BOSHQARUV PANELI</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang 👇"
    )
    try:
        await call.message.edit_text(text, reply_markup=admin_menu_kb())
    except Exception:
        await call.message.answer(text, reply_markup=admin_menu_kb())
    await call.answer("Bekor qilindi.")

@router.message(CreateTestState.title)
async def admin_test_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip(), subject="Matematika")
    await state.set_state(CreateTestState.test_code)
    await message.answer(
        "➕ <b>Test unikal kodini kiriting (2/4):</b>\n<i>(Masalan: 101 yoki MAT-01)</i>"
    )

@router.message(CreateTestState.test_code)
async def admin_test_code(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    existing = test_db.get_test_by_code(code)
    if existing:
        await message.answer("⚠️ Bu kod bilan test allaqachon mavjud! Boshqa kod kiriting:")
        return

    await state.update_data(test_code=code)
    await state.set_state(CreateTestState.pdf_file)
    await message.answer(
        "➕ <b>Testning PDF faylini yuboring (3/4):</b>\n"
        "<i>(Fayl sifatida .pdf yuklang yoki 'yoq' deb yozing)</i>"
    )

@router.message(CreateTestState.pdf_file)
async def admin_test_pdf(message: Message, state: FSMContext):
    pdf_id = None
    pdf_name = None

    if message.document:
        pdf_id = message.document.file_id
        pdf_name = message.document.file_name
    elif (message.text or "").lower() == "yoq":
        pdf_id = None
    else:
        await message.answer("⚠️ Iltimos, PDF fayl yuboring yoki 'yoq' deb yozing:")
        return

    await state.update_data(pdf_file_id=pdf_id, pdf_file_name=pdf_name)
    await state.set_state(CreateTestState.answers)

    admin_webapp_url = f"{WEBAPP_URL}/admin.html"
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [make_webapp_button("📱 Kalitlarni Mini Appda tugmalar bilan kiritish", admin_webapp_url, fallback_cb="admin_webapp_info")]
    ])

    await message.answer(
        "➕ <b>To'g'ri javoblar kalitini kiriting (4/4):</b>\n\n"
        "Quyidagi namuna shaklida yuboring:\n"
        "<code>1a2b3c4d...34a 35f 36a:12 36b:5 37a:√3 37b:2.5 ... 45a:10 45b:4</code>\n\n"
        "<i>(Yoki quyidagi tugma orqali Mini Appda tugmalarni bosib, ballarini belgilab kiritishingiz mumkin 👇)</i>",
        reply_markup=inline_kb
    )

def parse_answers_input(text: str) -> Dict[str, str]:
    """Admin kiritgan kalitlarni 1..32 (ABCD), 33..35 (ABCDEF), 36a..45b (ochiq javob) ko'rinishida lug'atga aylantiradi."""
    answers = {}
    cleaned = text.replace(",", " ").replace(";", " ")
    
    import re
    # 1. 36a-45b qismlarini topish (ochiq javoblar: har qanday son, belgi, amal)
    for match in re.finditer(r'(\d{2}[a-bA-B])\s*[:=\-]?\s*([^\s]+)', cleaned):
        key = match.group(1).lower()
        val = match.group(2).strip()
        answers[key] = val

    # 2. 1-35 savollar
    for match in re.finditer(r'(\b\d{1,2}\b)\s*[:=\-]?\s*([A-Fa-f])\b', cleaned):
        num = int(match.group(1))
        if 1 <= num <= 35:
            answers[str(num)] = match.group(2).upper()

    # Agar qisqa formatda kiritilgan bo'lsa
    raw_letters = re.findall(r'[A-Fa-f]', text)
    if len(answers) < 10 and len(raw_letters) >= 35:
        for idx in range(min(35, len(raw_letters))):
            answers[str(idx + 1)] = raw_letters[idx].upper()

    # Default to'ldirish
    for q in range(1, 33):
        if str(q) not in answers:
            answers[str(q)] = "A"
    for q in [33, 34, 35]:
        if str(q) not in answers:
            answers[str(q)] = "A"
    for q in range(36, 46):
        for sub in ["a", "b"]:
            key = f"{q}{sub}"
            if key not in answers:
                answers[key] = "1"

    return answers

@router.message(CreateTestState.answers)
async def admin_save_test(message: Message, state: FSMContext):
    if message.text in ["📚 Mavjud testlar", "📊 Mening natijalarim", "👤 Profilim", "ℹ️ Bot haqida", "⚙️ Admin Panel"]:
        await state.clear()
        if message.text == "📚 Mavjud testlar":
            await show_active_tests(message)
        elif message.text == "⚙️ Admin Panel":
            await admin_panel_handler(message)
        return

    answers = parse_answers_input(message.text or "")
    data = await state.get_data()

    success = test_db.create_test(
        test_code=data.get("test_code", "TEST-01"),
        title=data.get("title", "Yangi Test"),
        subject="Matematika",
        answers=answers,
        pdf_file_id=data.get("pdf_file_id"),
        pdf_file_name=data.get("pdf_file_name")
    )
    await state.clear()

    if success:
        await message.answer(
            f"✅ <b>Test muvaffaqiyatli saqlandi!</b>\n\n"
            f"📖 <b>Nomi:</b> {data['title']}\n"
            f"📌 <b>Fani:</b> Matematika\n"
            f"🔢 <b>Kodi:</b> <code>#{data['test_code']}</code>\n"
            f"🔑 <b>Kalitlar soni:</b> {len(answers)} ta javob saqlandi.\n\n"
            f"Foydalanuvchilar endi '📚 Mavjud testlar' bo'limi orqali topshirishlari mumkin!",
            reply_markup=admin_menu_kb()
        )
    else:
        await message.answer("❌ Testni saqlashda xatolik yuz berdi.", reply_markup=admin_menu_kb())

# 2. Testlarni boshqarish (O'chirish, To'xtatish/Yoqish, Vaqt)
@router.callback_query(F.data == "admin_manage_tests")
async def admin_manage_tests(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    tests = test_db.get_all_tests()
    if not tests:
        text = "ℹ️ Hozircha bazada birorta ham test yo'q."
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Admin Menyuga qaytish", callback_data="admin_back_to_menu")]
        ])
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await call.message.answer(text, reply_markup=kb)
        await call.answer()
        return

    text = (
        "📋 <b>Barcha testlar ro'yxati va boshqaruvi:</b>\n\n"
        "<i>Boshqarish (to'xtatish / vaqt / o'chirish) uchun kerakli testni tanlang 👇</i>\n\n"
    )
    buttons = []
    for idx, t in enumerate(tests, 1):
        status_icon = "🟢" if t["is_active"] == 1 else "🔴"
        time_str = f"{t['time_limit_min']} daqiqa" if t.get("time_limit_min", 0) > 0 else "Cheksiz"
        text += f"<b>{idx}. #{t['test_code']}</b> — {t['title']} ({status_icon}, ⏱ {time_str})\n"
        buttons.append([InlineKeyboardButton(text=f"{status_icon} #{t['test_code']} — {t['title'][:25]}", callback_data=f"adm_mng_test_{t['id']}")])

    buttons.append([InlineKeyboardButton(text="🔙 Admin Menyuga qaytish", callback_data="admin_back_to_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except Exception:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("adm_mng_test_"))
async def admin_manage_test_card(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    test_id = int(call.data.split("_")[3])
    t = test_db.get_test_by_id(test_id)
    if not t:
        await call.answer("Test topilmadi!", show_alert=True)
        return

    status_str = "🟢 Faol (O'quvchilarga ko'rinadi)" if t["is_active"] == 1 else "🔴 To'xtatilgan (Yashiringan)"
    time_str = f"{t['time_limit_min']} daqiqa" if t.get("time_limit_min", 0) > 0 else "Cheksiz"
    toggle_btn_text = "🔴 To'xtatish" if t["is_active"] == 1 else "🟢 Faollashtirish"

    card_text = (
        f"📖 <b>{t['title']}</b> (<code>#{t['test_code']}</code>)\n"
        f"📌 <b>Fan:</b> {t.get('subject', 'Matematika')}\n"
        f"📊 <b>Holati:</b> {status_str}\n"
        f"⏱ <b>Vaqt chegarasi:</b> {time_str}\n\n"
        f"<i>Boshqarish uchun quyidagi amallardan birini tanlang:</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=toggle_btn_text, callback_data=f"toggle_test_{t['id']}"),
            InlineKeyboardButton(text="⏱ Vaqt", callback_data=f"set_time_prompt_{t['id']}")
        ],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_test_confirm_{t['id']}")],
        [InlineKeyboardButton(text="⬅️ Testlar ro'yxatiga qaytish", callback_data="admin_manage_tests")]
    ])

    try:
        await call.message.edit_text(card_text, reply_markup=kb)
    except Exception:
        await call.message.answer(card_text, reply_markup=kb)
    await call.answer()

# Test holatini o'zgartirish (Toggle Active)
@router.callback_query(F.data.startswith("toggle_test_"))
async def admin_toggle_test_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    test_id = int(call.data.split("_")[2])
    new_status = test_db.toggle_test_status(test_id)
    if new_status is not None:
        status_text = "🟢 Faol" if new_status == 1 else "🔴 To'xtatildi"
        await call.answer(f"Test holati: {status_text}", show_alert=True)
        call.data = f"adm_mng_test_{test_id}"
        await admin_manage_test_card(call)
    else:
        await call.answer("Xatolik yuz berdi!", show_alert=True)

# Test vaqtini belgilash prompt
@router.callback_query(F.data.startswith("set_time_prompt_"))
async def admin_set_time_prompt(call: CallbackQuery, state: FSMContext):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    test_id = int(call.data.split("_")[3])
    await state.update_data(target_test_id=test_id)
    await state.set_state(SetTimeLimitState.time_limit)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"adm_mng_test_{test_id}")]
    ])
    text = (
        "⏱ <b>Test uchun vaqt chegarasini daqiqalarda kiriting:</b>\n\n"
        "<i>(Masalan: 120, 180 yoki cheksiz bo'lishi uchun 0 deb yozing)</i>"
    )
    try:
        await call.message.edit_text(text, reply_markup=cancel_kb)
    except Exception:
        await call.message.answer(text, reply_markup=cancel_kb)
    await call.answer()

@router.message(SetTimeLimitState.time_limit)
async def admin_save_time_limit(message: Message, state: FSMContext):
    data = await state.get_data()
    test_id = data.get("target_test_id")
    try:
        minutes = int(message.text.strip())
        test_db.update_test_time_limit(test_id, minutes)
        await state.clear()
        time_text = f"{minutes} daqiqa" if minutes > 0 else "Cheksiz"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Testga qaytish", callback_data=f"adm_mng_test_{test_id}")],
            [InlineKeyboardButton(text="🔙 Admin Menyuga", callback_data="admin_back_to_menu")]
        ])
        await message.answer(f"✅ Test vaqt chegarasi <b>{time_text}</b> qilib belgilandi!", reply_markup=kb)
    except ValueError:
        await message.answer("⚠️ Iltimos, faqat butun son kiriting (masalan: 120 yoki 0):")

# Testni o'chirish
@router.callback_query(F.data.startswith("del_test_confirm_"))
async def admin_delete_test_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    test_id = int(call.data.split("_")[3])
    test_db.delete_test(test_id)
    await call.answer("🗑 Test muvaffaqiyatli o'chirildi!", show_alert=True)
    await admin_manage_tests(call)

# ── TEZKOR FOYDALANUVCHI TASDIQLASH / RAD ETISH HANDLERLARI ──
@router.callback_query(F.data.startswith("user_quick_approve_"))
async def user_quick_approve_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    uid = int(call.data.split("_")[3])
    test_db.approve_user(uid)
    u = test_db.get_user(uid)
    uname = u["fullname"] if u else f"ID: {uid}"
    await call.message.edit_text(
        f"{call.message.text}\n\n✅ <b>ADMIN TOMONIDAN RUXSAT BERILDI!</b>",
        reply_markup=None
    )
    try:
        await bot.send_message(
            chat_id=uid,
            text=(
                f"🎉 <b>Tabriklaymiz, {uname}!</b>\n\n"
                f"Admin sizga botdan foydalanish huquqini berdi. Endi barcha testlarni yechishingiz mumkin!"
            ),
            reply_markup=main_menu_kb(uid)
        )
    except Exception as e:
        log.warning(f"Foydalanuvchiga ruxsat xabarini yuborishda xatolik: {e}")
    await call.answer("✅ Foydalanuvchiga ruxsat berildi!", show_alert=True)

@router.callback_query(F.data.startswith("user_quick_reject_"))
async def user_quick_reject_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    uid = int(call.data.split("_")[3])
    test_db.reject_user(uid)
    await call.message.edit_text(
        f"{call.message.text}\n\n❌ <b>ADMIN TOMONIDAN RAD ETILDI!</b>",
        reply_markup=None
    )
    try:
        await bot.send_message(
            chat_id=uid,
            text="❌ <b>Kechirasiz, sizning botdan foydalanish arizangiz rad etildi.</b>"
        )
    except Exception:
        pass
    await call.answer("❌ Ariza rad etildi!", show_alert=True)

@router.callback_query(F.data.startswith("ask_pdf_"))
async def ask_pdf_cb(call: CallbackQuery, state: FSMContext):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    test_id = int(call.data.split("_")[2])
    await state.update_data(test_id=test_id)
    await state.set_state(UploadPostPdfState.pdf_file)
    await call.message.edit_text(
        f"{call.message.text}\n\n✅ <i>Siz PDF yuklashni tanladingiz.</i>\n\n"
        f"📥 <b>Iltimos, test uchun PDF faylni yuboring:</b>",
        reply_markup=None
    )

@router.callback_query(F.data.startswith("no_pdf_"))
async def no_pdf_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    await call.message.edit_text(
        f"{call.message.text}\n\n❌ <i>PDF fayl yuklanmadi. Test asosiysiz qabul qilindi.</i>",
        reply_markup=None
    )

@router.message(UploadPostPdfState.pdf_file, F.document)
async def process_post_create_pdf(message: Message, state: FSMContext):
    data = await state.get_data()
    test_id = data.get("test_id")
    if not test_id:
        await message.answer("Xatolik! Test topilmadi.")
        await state.clear()
        return

    pdf_file_id = message.document.file_id
    pdf_file_name = message.document.file_name

    test_db.update_test_pdf(test_id, pdf_file_id, pdf_file_name)
    await message.answer(f"✅ <b>PDF fayl muvaffaqiyatli biriktirildi!</b>\n📄 Fayl: {pdf_file_name}")
    await state.clear()

# 3. Barcha foydalanuvchilar ro'yxati va boshqaruvi
@router.callback_query(F.data == "admin_view_users")
async def admin_view_users_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    users = test_db.get_all_users()
    counts = test_db.get_users_count()
    if not users:
        text = "ℹ️ Hozircha ro'yxatdan o'tgan foydalanuvchilar yo'q."
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Admin Menyuga qaytish", callback_data="admin_back_to_menu")]
        ])
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await call.message.answer(text, reply_markup=kb)
        await call.answer()
        return

    text = (
        f"👥 <b>FOYDALANUVCHILAR BOSHQARUVI ({counts['total']} nafar):</b>\n\n"
        f"📊 <b>Jami:</b> {counts['total']} ta | ✅ <b>Faol:</b> {counts['approved']} ta\n"
        f"⏳ <b>Kutilayotganlar:</b> {counts['pending']} ta | ⛔️ <b>Chiqarilganlar:</b> {counts['blocked']} ta\n\n"
        f"<i>Boshqarish (ruxsat berish / chiqarib yuborish / o'chirish) uchun foydalanuvchini tanlang 👇</i>"
    )

    buttons = []
    for u in users[:25]:
        st = u.get("status", "pending")
        if st == "approved":
            icon = "✅"
        elif st == "pending":
            icon = "⏳"
        elif st == "blocked":
            icon = "⛔️"
        else:
            icon = "❌"
        
        btn_label = f"{icon} {u['fullname']} ({u.get('phone', '')})"
        buttons.append([InlineKeyboardButton(text=btn_label, callback_data=f"adm_user_card_{u['tg_id']}")])

    buttons.append([InlineKeyboardButton(text="🔙 Admin Menyuga qaytish", callback_data="admin_back_to_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except Exception:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()

# Foydalanuvchi kartasi va amallar (Ruxsat berish / Chiqarib yuborish / O'chirish)
@router.callback_query(F.data.startswith("adm_user_card_"))
async def adm_user_card_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    uid = int(call.data.split("_")[3])
    u = test_db.get_user(uid)
    if not u:
        await call.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return

    st = u.get("status", "pending")
    if st == "approved":
        st_text = "✅ Ruxsat berilgan (Faol)"
    elif st == "pending":
        st_text = "⏳ Kutilmoqda (Ruxsat berilmagan)"
    elif st == "blocked":
        st_text = "⛔️ Chiqarib yuborilgan (Bloklangan)"
    else:
        st_text = "❌ Rad etilgan"

    dt = time.strftime("%d.%m.%Y %H:%M", time.localtime(u["registered_at"]))
    uname = f"@{u['username']}" if u.get("username") else "mavjud emas"

    text = (
        f"👤 <b>FOYDALANUVCHI MA'LUMOTLARI:</b>\n\n"
        f"👤 <b>Ism:</b> {u['fullname']}\n"
        f"📱 <b>Telefon:</b> <code>{u['phone']}</code>\n"
        f"🆔 <b>Telegram ID:</b> <code>{u['tg_id']}</code>\n"
        f"🌐 <b>Username:</b> {uname}\n"
        f"📌 <b>Holati:</b> <b>{st_text}</b>\n"
        f"📅 <b>Ro'yxatdan o'tgan sana:</b> {dt}\n\n"
        f"<i>Quyidagi tugmalar orqali foydalanuvchini boshqarishingiz mumkin:</i>"
    )

    action_buttons = []
    if st != "approved":
        action_buttons.append([InlineKeyboardButton(text="✅ Botga ruxsat berish", callback_data=f"adm_act_approve_{uid}")])
    if st != "blocked":
        action_buttons.append([InlineKeyboardButton(text="⛔️ Botdan chiqarib yuborish", callback_data=f"adm_act_block_{uid}")])
    action_buttons.append([InlineKeyboardButton(text="🗑 Butunlay o'chirish", callback_data=f"adm_act_del_{uid}")])
    action_buttons.append([InlineKeyboardButton(text="🔙 Foydalanuvchilar ro'yxatiga", callback_data="admin_view_users")])

    kb = InlineKeyboardMarkup(inline_keyboard=action_buttons)
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except Exception:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("adm_act_approve_"))
async def adm_act_approve_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    uid = int(call.data.split("_")[3])
    test_db.approve_user(uid)
    try:
        await bot.send_message(
            chat_id=uid,
            text="🎉 <b>Tabriklaymiz! Admin sizga botdan foydalanish huquqini berdi.</b>",
            reply_markup=main_menu_kb(uid)
        )
    except Exception:
        pass
    await call.answer("✅ Foydalanuvchiga ruxsat berildi!", show_alert=True)
    await admin_view_users_cb(call)

@router.callback_query(F.data.startswith("adm_act_block_"))
async def adm_act_block_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    uid = int(call.data.split("_")[3])
    test_db.block_user(uid)
    try:
        await bot.send_message(
            chat_id=uid,
            text="⛔️ <b>Sizning botdan foydalanish huquqingiz admin tomonidan bekor qilindi va chiqarib yuborildingiz!</b>",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception:
        pass
    await call.answer("⛔️ Foydalanuvchi botdan chiqarib yuborildi!", show_alert=True)
    await admin_view_users_cb(call)

@router.callback_query(F.data.startswith("adm_act_del_"))
async def adm_act_del_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return
    uid = int(call.data.split("_")[3])
    test_db.delete_user(uid)
    await call.answer("🗑 Foydalanuvchi bazadan o'chirildi!", show_alert=True)
    await admin_view_users_cb(call)

# 4. Adminlar boshqaruvi
@router.callback_query(F.data == "admin_manage_admins")
async def admin_manage_admins_cb(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    admins = test_db.get_all_admins()
    text = "👑 <b>Adminlar ro'yxati:</b>\n\n"
    for idx, a in enumerate(admins, 1):
        is_super = " (Bosh Admin)" if a["tg_id"] == ADMIN_ID else ""
        text += f"<b>{idx}. {a.get('fullname', 'Admin')}</b> — <code>{a['tg_id']}</code>{is_super}\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi admin qo'shish", callback_data="admin_add_new_prompt")],
        [InlineKeyboardButton(text="🔙 Admin Menyuga qaytish", callback_data="admin_back_to_menu")]
    ])

    try:
        await call.message.edit_text(text, reply_markup=kb)
    except Exception:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.in_(["admin_back_to_menu", "admin_panel_back"]))
async def admin_back_to_menu_cb(call: CallbackQuery, state: FSMContext = None):
    if state:
        await state.clear()
    text = (
        "⚙️ <b>ADMIN BOSHQARUV PANELI</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang 👇"
    )
    try:
        await call.message.edit_text(text, reply_markup=admin_menu_kb())
    except Exception:
        await call.message.answer(text, reply_markup=admin_menu_kb())
    await call.answer()

@router.callback_query(F.data == "admin_add_new_prompt")
async def admin_add_new_prompt_cb(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Faqat Bosh Admin yangi admin tayinlashi mumkin!", show_alert=True)
        return

    await state.set_state(AddAdminState.tg_id_or_user)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="admin_manage_admins")]
    ])
    text = (
        "👑 <b>Yangi admin qo'shish:</b>\n\n"
        "Admin qilmoqchi bo'lgan foydalanuvchining <b>Telegram ID</b> raqamini kiriting:\n"
        "<i>(Masalan: 123456789)</i>"
    )
    try:
        await call.message.edit_text(text, reply_markup=cancel_kb)
    except Exception:
        await call.message.answer(text, reply_markup=cancel_kb)
    await call.answer()

@router.message(AddAdminState.tg_id_or_user)
async def admin_save_new_admin(message: Message, state: FSMContext):
    try:
        new_tg_id = int(message.text.strip())
        user_info = test_db.get_user(new_tg_id)
        fullname = user_info["fullname"] if user_info else "Admin"
        username = user_info["username"] if user_info else ""

        test_db.add_admin(new_tg_id, fullname, username, added_by=message.from_user.id)
        await state.clear()
        await message.answer(
            f"✅ <b>Yangi admin tayinlandi!</b>\n\n"
            f"👤 <b>Ism:</b> {fullname}\n"
            f"🆔 <b>Telegram ID:</b> <code>{new_tg_id}</code>\n\n"
            f"Endi ushbu foydalanuvchi ham Admin Panelga kira oladi.",
            reply_markup=admin_menu_kb()
        )
    except ValueError:
        await message.answer("⚠️ Iltimos, to'g'ri Telegram ID (raqam) kiriting:")

# 5. Natijalar va hisobotlar boshqaruvi
@router.callback_query(F.data == "admin_leaderboard")
async def admin_leaderboard(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    tests = test_db.get_tests_with_stats()
    if not tests:
        text = "⚠️ Hozirda tizimda mavjud testlar yo'q."
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Admin Panelga qaytish", callback_data="admin_panel_back")]
        ])
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await call.message.answer(text, reply_markup=kb)
        await call.answer()
        return

    buttons = []
    msg_list = ""
    for idx, t in enumerate(tests, 1):
        sub_cnt = t.get("submissions_count", 0)
        btn_text = f"📊 #{t['test_code']} — 👥 {sub_cnt} kishi"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"adm_tstat_{t['id']}")])
        msg_list += f"<b>{idx}. #{t['test_code']}</b> — {t['title']}: <b>{sub_cnt} kishi</b>\n"

    buttons.append([InlineKeyboardButton(text="⬅️ Admin Panelga qaytish", callback_data="admin_panel_back")])

    msg_text = (
        "📊 <b>Mavjud Testlar va Ishtirokchilar Soni:</b>\n\n"
        f"{msg_list}\n"
        "<i>Batafsil natijalarni (Matn yoki PDF shaklida) olish uchun kerakli test kodini tanlang 👇</i>"
    )

    try:
        await call.message.edit_text(msg_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except Exception:
        await call.message.answer(msg_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await call.answer()

@router.callback_query(F.data.startswith("adm_tstat_"))
async def admin_test_stats_detail(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    test_id = int(call.data.split("_")[2])
    test = test_db.get_test_by_id(test_id)
    if not test:
        await call.answer("Test topilmadi!", show_alert=True)
        return

    results = test_db.get_test_results_leaderboard(test_id)
    count = len(results)
    avg_score = 0
    if count > 0:
        avg_score = round(sum(r['score'] for r in results) / count, 1)

    text = (
        f"📋 <b>Test ma'lumotlari va hisoboti:</b>\n\n"
        f"📖 <b>Nomi:</b> {test['title']}\n"
        f"🔑 <b>Kodi:</b> <code>#{test['test_code']}</code>\n"
        f"📌 <b>Fani:</b> {test.get('subject', 'Matematika')}\n\n"
        f"👥 <b>Topshirganlar soni:</b> <b>{count} nafar</b>\n"
        f"📈 <b>O'rtacha ball:</b> <b>{avg_score} ball</b>\n\n"
        f"Kerakli hisobot shaklini tanlang 👇"
    )

    buttons = [
        [InlineKeyboardButton(text="📄 Matn shaklida natijalar", callback_data=f"adm_restxt_{test_id}")],
        [InlineKeyboardButton(text="📑 PDF hisobotni yuklab olish", callback_data=f"adm_respdf_{test_id}")],
        [InlineKeyboardButton(text="⬅️ Testlar ro'yxatiga qaytish", callback_data="admin_leaderboard")]
    ]

    try:
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except Exception:
        await call.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await call.answer()

@router.callback_query(F.data.startswith("adm_restxt_"))
async def admin_test_res_text(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    test_id = int(call.data.split("_")[2])
    test = test_db.get_test_by_id(test_id)
    if not test:
        await call.answer("Test topilmadi!", show_alert=True)
        return

    results = test_db.get_test_results_leaderboard(test_id)
    if not results:
        await call.answer("Bu testni hali hech kim topshirmagan!", show_alert=True)
        return

    text = f"🏆 <b>«{test['title']}» Natijalari (Matn ko'rinishida):</b>\n"
    text += f"👥 <b>Jami ishtirokchilar:</b> {len(results)} nafar\n\n"

    for idx, row in enumerate(results[:30], 1):
        grade = test_db.calculate_grade(row["score"])
        text += f"<b>{idx}. {row['fullname']}</b> — <b>{row['score']} ball</b> [🎖 {grade}] ({row['correct_count']} ta to'g'ri)\n"

    if len(results) > 30:
        text += f"\n<i>...va yana {len(results) - 30} nafar ishtirokchi (barchasini ko'rish uchun PDF yuklab oling).</i>"

    buttons = [
        [InlineKeyboardButton(text="📑 PDF hisobotni yuklab olish", callback_data=f"adm_respdf_{test_id}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"adm_tstat_{test_id}")]
    ]

    try:
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except Exception:
        await call.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await call.answer()

@router.callback_query(F.data.startswith("adm_respdf_"))
async def admin_test_res_pdf(call: CallbackQuery):
    if not test_db.is_admin(call.from_user.id, ADMIN_ID):
        return

    test_id = int(call.data.split("_")[2])
    test = test_db.get_test_by_id(test_id)
    if not test:
        await call.answer("Test topilmadi!", show_alert=True)
        return

    results = test_db.get_test_results_leaderboard(test_id)
    if not results:
        await call.answer("Ushbu testni hali hech kim topshirmagan, PDF chiqarib bo'lmaydi.", show_alert=True)
        return

    await call.answer("⏳ PDF hisobot yaratilmoqda...")
    status_msg = await call.message.answer("⏳ <i>PDF reyting jadvali shakllantirilmoqda, iltimos kuting...</i>")

    pdf_path = test_db.generate_test_results_pdf(test_id)
    if pdf_path and os.path.exists(pdf_path):
        try:
            caption = (
                f"📑 <b>«{test['title']}»</b> bo'yicha rasmiy test natijalari va reyting hisoboti.\n\n"
                f"👥 <b>Ishtirokchilar:</b> {len(results)} nafar\n"
                f"🕒 <b>Sana:</b> {time.strftime('%d.%m.%Y %H:%M')}"
            )
            await bot.send_document(
                chat_id=call.from_user.id,
                document=FSInputFile(pdf_path),
                caption=caption
            )
            await status_msg.delete()
        except Exception as e:
            log.error(f"PDF yuborishda xatolik: {e}")
            await status_msg.edit_text(f"⚠️ PDF yuborishda xatolik yuz berdi: {e}")
        finally:
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
            except Exception:
                pass
    else:
        await status_msg.edit_text("⚠️ PDF hisobotini shakllantirishda xatolik yuz berdi.")

# Foydalanuvchi to'g'ridan-to'g'ri test kodini yuborganida
@router.message(F.text)
async def handle_direct_text(message: Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state is not None:
        return

    raw_text = (message.text or "").strip()
    if raw_text in ["🔢 Test kodini kiritish", "📊 Mening natijalarim", "👤 Profilim", "ℹ️ Bot haqida", "⚙️ Admin Panel"]:
        return

    code = raw_text.upper().replace("#", "")
    test = test_db.get_test_by_code(code)
    if test:
        await send_test_card(message, test, message.from_user.id)
    else:
        user_info = test_db.get_user(message.from_user.id)
        name = user_info['fullname'] if user_info else (message.from_user.first_name or "Foydalanuvchi")
        await message.answer(
            f"👋 Salom, <b>{name}</b>!\n\n"
            f"Test topshirish uchun «🔢 Test kodini kiritish» tugmasini bosing yoki menyudan foydalaning 👇",
            reply_markup=main_menu_kb(message.from_user.id)
        )

# ── AIOHTTP MINI APP VEB SERVERI ──────────────────────

async def handle_submit_test_api(request):
    """Mini App dan kelgan javoblarni tekshirish va bot orqali faqat foydalanuvchiga natijani xabar qilish"""
    try:
        data = await request.json()
        test_id = data.get("test_id", 1)
        user_tg_id = data.get("user_tg_id")
        user_answers = data.get("answers", {})

        # Bazada tekshirish va saqlash
        result = test_db.check_and_save_submission(test_id, user_tg_id, user_answers)

        # Foydalanuvchiga Telegram bot orqali shaxsiy natija xabarini yuborish
        if user_tg_id:
            grade = result.get('grade') or test_db.calculate_grade(result.get('score', 0))
            score_val = result.get('score', 0)
            msg_user = (
                f"🎉 <b>Hurmatli {result['fullname']}, sizning natijangiz:</b>\n\n"
                f"📚 <b>Test:</b> {result['test_title']}\n"
                f"🎖 <b>Milliy Sertifikat darajasi:</b> <b>{grade}</b> ({score_val} ball)\n\n"
                f"✅ <b>To'g'ri javoblar:</b> {result['correct_count']} ta\n"
                f"❌ <b>Noto'g'ri javoblar:</b> {result['incorrect_count']} ta\n"
                f"⚪ <b>Belgilanmagan:</b> {result['unanswered_count']} ta\n\n"
                f"🏆 <i>Natijangiz tizimda muvaffaqiyatli qayd etildi!</i>"
            )
            try:
                await bot.send_message(chat_id=user_tg_id, text=msg_user)
            except Exception as ex:
                log.warning(f"Foydalanuvchiga xabar yuborishda xatolik: {ex}")

        # Eslatma: Adminga har bir topshirishda alohida spam xabar yuborilmaydi.
        # Admin natijalarni «📊 Test natijalari va reyting» bo'limida istalgan vaqtda matn yoki PDF ko'rinishida oladi.

        return web.json_response({"success": True, "data": result})

    except Exception as e:
        log.error(f"Submit API Error: {e}", exc_info=True)
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def handle_create_test_api(request):
    """Admin Mini App dan yuborilgan yangi test, kalitlar va ballarni saqlash"""
    try:
        data = await request.json()
        title = data.get("title", "").strip() or "Matematika Milliy Sertifikat Testi"
        test_code = data.get("test_code", "").strip().upper()
        if not test_code:
            test_code = f"MAT-{int(time.time()) % 10000:04d}"
        
        subject = data.get("subject", "Matematika").strip() or "Matematika"
        answers = data.get("answers", {})
        time_limit_min = int(data.get("time_limit_min", 0))
        key_access_code = data.get("key_access_code", "").strip()

        success = test_db.create_test(
            test_code=test_code,
            title=title,
            subject=subject,
            answers=answers,
            time_limit_min=time_limit_min,
            key_access_code=key_access_code
        )

        if success:
            try:
                time_info = f"⏱ <b>Vaqt:</b> {time_limit_min} daqiqa\n" if time_limit_min > 0 else "⏱ <b>Vaqt:</b> Cheksiz\n"
                
                # Fetch the created test from DB to get its ID for the inline keyboard
                t_obj = test_db.get_test_by_code(test_code)
                test_id = t_obj['id'] if t_obj else 0
                
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📥 Ha, PDF yuklayman", callback_data=f"ask_pdf_{test_id}")],
                    [InlineKeyboardButton(text="❌ Yo'q, kerak emas", callback_data=f"no_pdf_{test_id}")]
                ])

                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        f"✅ <b>Yangi test yaratildi va e'lon qilindi!</b>\n\n"
                        f"📖 <b>Nomi:</b> {title}\n"
                        f"📌 <b>Fani:</b> {subject}\n"
                        f"{time_info}"
                        f"🎯 <i>Barcha 45 ta savol kalitlari va ballar muvaffaqiyatli saqlandi!</i>\n\n"
                        f"Ushbu test uchun PDF fayl yuklaysizmi?"
                    ),
                    reply_markup=kb
                )
            except Exception as ex:
                log.warning(f"Adminga xabar yuborishda xatolik: {ex}")

            return web.json_response({"success": True, "message": "Test muvaffaqiyatli saqlandi!"})
        else:
            return web.json_response({"success": False, "message": "Ma'lumotlar bazasiga yozishda xatolik yuz berdi"}, status=400)

    except Exception as e:
        log.error(f"Create Test API Error: {e}", exc_info=True)
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def find_web_file(filename: str) -> str:
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.join(base_dir, 'test_webapp', filename),
        os.path.join(base_dir, 'test_webapp', 'css', filename),
        os.path.join(base_dir, 'test_webapp', 'js', filename),
        os.path.join(base_dir, 'test_webapp', 'img', filename),
        os.path.join(base_dir, filename),
        os.path.join(base_dir, os.path.basename(filename))
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c):
            return c
    return os.path.join(base_dir, filename)

async def handle_index(request):
    return web.FileResponse(await find_web_file('index.html'))

async def handle_admin(request):
    return web.FileResponse(await find_web_file('admin.html'))

async def handle_app(request):
    resp = web.FileResponse(await find_web_file('app.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

async def handle_static_file(request):
    path_name = request.match_info.get('path', '')
    fpath = await find_web_file(path_name)
    if os.path.exists(fpath) and os.path.isfile(fpath):
        resp = web.FileResponse(fpath)
        if any(path_name.endswith(ext) for ext in ['.html', '.js', '.css']):
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
        return resp
    return web.Response(status=404, text="Fayl topilmadi")

# ── ASOSIY MINI APP API ENDPOINTLARI ────────────────────────────────────────

async def handle_app_profile(request):
    """Foydalanuvchi profili va statistikasi (Asosiy Mini App uchun)."""
    try:
        tg_id = int(request.rel_url.query.get('tg_id', 0))
        if not tg_id:
            return web.json_response({"success": False, "message": "tg_id required"}, status=400)

        user = test_db.get_user(tg_id)
        is_admin = test_db.is_admin(tg_id, ADMIN_ID)

        # Foydalanuvchi statistikasi
        submissions = test_db.get_user_submissions(tg_id)
        avg_score = 0.0
        max_score_val = 0
        if submissions:
            scores = [float(s.get('score', s.get('correct_count', 0))) for s in submissions]
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score_val = max(scores) if scores else 0

        # Pending users count for admins
        pending_users = 0
        if is_admin:
            try:
                counts = test_db.get_users_count()
                pending_users = counts.get('pending', 0)
            except Exception:
                pass

        user_data = dict(user) if user else {
            'tg_id': tg_id, 'fullname': 'Foydalanuvchi', 'phone': '—',
            'status': 'pending', 'registered_at': int(time.time())
        }
        user_data['tests_count'] = len(submissions)
        user_data['avg_score'] = round(avg_score, 1)
        user_data['max_score'] = max_score_val
        user_data['has_pin'] = bool(user and user.get('pin_code'))

        return web.json_response({
            "success": True,
            "user": user_data,
            "is_admin": is_admin,
            "pending_users": pending_users
        })
    except Exception as e:
        log.error(f"App Profile API Error: {e}", exc_info=True)
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def handle_app_set_pin(request):
    """Foydalanuvchi PIN kodini bazada saqlash."""
    try:
        data = await request.json()
        tg_id = int(data.get('tg_id', 0))
        pin = str(data.get('pin', '')).strip()
        if not tg_id or len(pin) != 4:
            return web.json_response({"success": False, "message": "4 xonali PIN kerak"}, status=400)
        test_db.set_user_pin(tg_id, pin)
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def handle_app_status(request):
    """Bot va server holatini (online/active) tekshirish."""
    import time
    return web.json_response({
        "success": True,
        "status": "online",
        "bot_active": True,
        "server_time": int(time.time()),
        "uptime": int(time.time())
    }, headers={"Access-Control-Allow-Origin": "*"})

async def handle_app_verify_pin(request):
    """Foydalanuvchi PIN kodini bazadan tekshirish."""
    try:
        data = await request.json()
        tg_id = int(data.get('tg_id', 0))
        pin = str(data.get('pin', '')).strip()
        stored = test_db.get_user_pin(tg_id)
        if stored and stored == pin:
            return web.json_response({"success": True, "valid": True})
        return web.json_response({"success": True, "valid": False})
    except Exception as e:
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def handle_app_compare_keys(request):
    """Parol orqali test kalitlarini va o'quvchi javoblarini solishtirish."""
    try:
        data = await request.json()
        tg_id = int(data.get('tg_id', 0))
        test_id = int(data.get('test_id', 0))
        code = str(data.get('code', '')).strip()

        if not tg_id or not test_id:
            return web.json_response({"success": False, "message": "Noto'g'ri so'rov"}, status=400)

        test = test_db.get_test_by_id(test_id)
        if not test:
            return web.json_response({"success": False, "message": "Test topilmadi"}, status=404)

        expected_code = str(test.get('key_access_code', '')).strip()
        if expected_code and expected_code != code:
            return web.json_response({"success": False, "message": "Parol noto'g'ri!"}, status=403)

        sub = test_db.get_user_submission_for_test(test_id, tg_id)
        if not sub:
            return web.json_response({"success": False, "message": "Siz ushbu testni topshirmagansiz"}, status=400)

        correct_answers = test_db.parse_answers_json(test.get('answers_json', '{}'))
        user_answers = test_db.parse_answers_json(sub.get('answers_json', '{}'))

        return web.json_response({
            "success": True,
            "correct_answers": correct_answers,
            "user_answers": user_answers
        })
    except Exception as e:
        log.error(f"App Compare Keys API Error: {e}", exc_info=True)
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def handle_app_active_tests(request):
    """Faol testlar ro'yxati (user uchun topshirilgan-topshirilmaganligini ham qaytaradi)."""
    try:
        tg_id = int(request.rel_url.query.get('tg_id', 0))
        all_tests = test_db.get_all_tests()
        result = []
        for t in all_tests:
            td = dict(t)
            td.pop('answers_json', None)  # Javoblarni yashirish
            # Foydalanuvchi allaqachon topshirganmi?
            if tg_id:
                existing = test_db.get_user_submission_for_test(t['id'], tg_id)
                td['already_submitted'] = bool(existing)
            else:
                td['already_submitted'] = False
            td['is_planned'] = not bool(t.get('is_active', 1))
            result.append(td)
        return web.json_response({"success": True, "tests": result})
    except Exception as e:
        log.error(f"App Active Tests API Error: {e}", exc_info=True)
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def handle_app_my_results(request):
    """Foydalanuvchining o'z test natijalari tarixi."""
    try:
        tg_id = int(request.rel_url.query.get('tg_id', 0))
        if not tg_id:
            return web.json_response({"success": True, "results": []})
        submissions = test_db.get_user_submissions(tg_id)
        return web.json_response({"success": True, "results": submissions})
    except Exception as e:
        log.error(f"App My Results API Error: {e}", exc_info=True)
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def handle_app_users(request):
    """Admin uchun barcha foydalanuvchilar ro'yxati va statistika."""
    try:
        tg_id = int(request.rel_url.query.get('tg_id', 0))
        if not test_db.is_admin(tg_id, ADMIN_ID):
            return web.json_response({"success": False, "message": "Ruxsat yo'q"}, status=403)

        users = test_db.get_all_users()
        counts = test_db.get_users_count()
        return web.json_response({
            "success": True,
            "users": users,
            "stats": counts
        })
    except Exception as e:
        log.error(f"App Users API Error: {e}", exc_info=True)
        return web.json_response({"success": False, "message": str(e)}, status=400)

async def create_web_app():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/index.html', handle_index)
    app.router.add_get('/admin.html', handle_admin)
    app.router.add_get('/app.html', handle_app)
    app.router.add_post('/api/submit-test', handle_submit_test_api)
    app.router.add_post('/api/create-test', handle_create_test_api)
    # Asosiy Mini App API
    app.router.add_get('/api/app/profile', handle_app_profile)
    app.router.add_get('/api/app/active-tests', handle_app_active_tests)
    app.router.add_get('/api/app/my-results', handle_app_my_results)
    app.router.add_get('/api/app/users', handle_app_users)
    app.router.add_get('/api/app/status', handle_app_status)
    app.router.add_post('/api/app/compare-keys', handle_app_compare_keys)
    app.router.add_post('/api/app/set-pin', handle_app_set_pin)
    app.router.add_post('/api/app/verify-pin', handle_app_verify_pin)
    # Universal Static Route
    app.router.add_get('/css/{path:.*}', handle_static_file)
    app.router.add_get('/js/{path:.*}', handle_static_file)
    app.router.add_get('/img/{path:.*}', handle_static_file)
    app.router.add_get('/{path:[^/]+\\.(?:css|js|png|jpg|jpeg|svg|ico|json)}', handle_static_file)

    return app

async def keep_alive_pinger(url: str):
    """Render.com yoki bulutli server uxlamasligi uchun har 8 daqiqada avtomatik so'rov yuborish (24/7 Keep-Alive)."""
    import aiohttp
    log.info(f"🔄 24/7 Keep-Alive xizmati faollashtirildi: {url}")
    await asyncio.sleep(60) # Ilk urinish 1 daqiqadan so'ng
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/api/app/status", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        log.info("💓 Keep-Alive ping muvaffaqiyatli (Server faol).")
        except Exception as e:
            log.warning(f"Keep-Alive ping xatosi: {e}")
        await asyncio.sleep(480) # Har 8 daqiqada (480s) qaytariladi

# ── AVTOMATIK HTTPS TUNNEL (OGOHLANTIRISHLARSIZ / TO'G'RIDAN-TO'G'RI OCHILUVCHI) ──
async def maintain_tunnel(local_port: int):
    """Telegram Mini App uchun tunnel yoki Railway doimiy HTTPS manzilini sozlaydi."""
    global WEBAPP_URL
    import re

    # Agar Render.com yoki Railway yoki boshqa doimiy domenda ishlayotgan bo'lsa
    render_domain = os.getenv("RENDER_EXTERNAL_URL")
    is_render = os.getenv("RENDER") == "true" or bool(os.getenv("RENDER_SERVICE_ID")) or bool(os.getenv("RENDER_INSTANCE_ID"))
    if render_domain or is_render:
        if not render_domain:
            render_domain = os.getenv("WEBAPP_URL") or "https://rash-test.onrender.com"
        WEBAPP_URL = (render_domain if render_domain.startswith("http") else f"https://{render_domain}").rstrip("/")
        log.info(f"🚀 Render.com Production muhiti aniqlandi: {WEBAPP_URL}")
        try:
            with open("tunnel_url.txt", "w") as f:
                f.write(WEBAPP_URL)
            menu_btn = MenuButtonWebApp(text="Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}/app.html"))
            await bot.set_chat_menu_button(menu_button=menu_btn)
            log.info("✅ Bot menyu tugmasi Render.com doimiy URL ga ulandi!")
        except Exception as e:
            log.error(f"Menu tugmasini yangilashda xatolik: {e}")
        # 24/7 Keep-Alive taskini ishga tushirish (Render uxlamasligi uchun)
        asyncio.create_task(keep_alive_pinger(WEBAPP_URL))
        return

    if railway_domain:
        WEBAPP_URL = f"https://{railway_domain}"
        log.info(f"🚂 Railway Production muhiti aniqlandi: {WEBAPP_URL}")
        try:
            with open("tunnel_url.txt", "w") as f:
                f.write(WEBAPP_URL)
            menu_btn = MenuButtonWebApp(text="Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}/app.html"))
            await bot.set_chat_menu_button(menu_button=menu_btn)
            log.info("✅ Bot menyu tugmasi Railway doimiy URL ga ulandi!")
        except Exception as e:
            log.error(f"Menu tugmasini yangilashda xatolik: {e}")
        return

    env_url = os.getenv("WEBAPP_URL", "")
    if env_url and not any(k in env_url for k in [".lhr.life", ".trycloudflare.com", ".serveo.net", "localhost"]):
        WEBAPP_URL = env_url.rstrip("/")
        log.info(f"🌐 Doimiy WEBAPP_URL sozlamasi aniqlandi: {WEBAPP_URL}")
        try:
            with open("tunnel_url.txt", "w") as f:
                f.write(WEBAPP_URL)
            menu_btn = MenuButtonWebApp(text="Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}/app.html"))
            await bot.set_chat_menu_button(menu_button=menu_btn)
            log.info("✅ Bot menyu tugmasi doimiy URL ga ulandi!")
        except Exception as e:
            log.error(f"Menu tugmasini yangilashda xatolik: {e}")
        return

    providers = [
        ("Cloudflare", ["cloudflared", "tunnel", "--url", f"http://localhost:{local_port}"], r'https://[a-zA-Z0-9\-\.]+\.trycloudflare\.com'),
        ("LocalhostRun", ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-R", f"80:localhost:{local_port}", "nokey@localhost.run"], r'https://[a-zA-Z0-9\-\.]+\.lhr\.life'),
        ("Serveo", ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-R", f"80:localhost:{local_port}", "serveo.net"], r'https://[a-zA-Z0-9\-\.]+\.serveo\.net')
    ]

    while True:
        for name, cmd, pattern in providers:
            try:
                log.info(f"🔌 HTTPS Tunnelga ulanmoqda ({name})...")
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    decoded = line.decode('utf-8', errors='ignore')
                    match = re.search(pattern, decoded)
                    if match:
                        new_url = match.group(0)
                        WEBAPP_URL = new_url
                        log.info(f"✨ JONLI HTTPS MINI APP URL ({name}): {WEBAPP_URL}")
                        try:
                            with open("tunnel_url.txt", "w") as f:
                                f.write(WEBAPP_URL)
                            # Update Bot Menu Button automatically
                            menu_btn = MenuButtonWebApp(text="Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}/app.html"))
                            await bot.set_chat_menu_button(menu_button=menu_btn)
                            log.info("✅ Bot menyu tugmasi Mini App URL ga ulandi!")
                        except Exception as e:
                            log.error(f"Menu tugmasini yangilashda xatolik: {e}")
                await proc.wait()
                log.warning(f"⚠️ {name} aloqasi uzildi. Qayta ulanmoqda...")
            except Exception as e:
                log.error(f"Tunnel xatoligi ({name}): {e}")
            await asyncio.sleep(2)
        await asyncio.sleep(3)

# ── ASOSIY ISHGA TUSHIRISH (MAIN) ─────────────────────
async def main():
    global WEBAPP_URL
    test_db.init_db()

    # 1. aiohttp serverini ishga tushirish (bo'sh portni avtomatik topish)
    app = await create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    current_port = PORT
    site = None
    for attempt in range(10):
        try:
            site = web.TCPSite(runner, '0.0.0.0', current_port)
            await site.start()
            log.info(f"🌐 Mini App Server ishga tushdi: http://localhost:{current_port}")
            break
        except OSError as e:
            if e.errno == 48: # Address already in use
                current_port += 1
            else:
                raise e

    # 2. Fon rejimida HTTPS Tunnelni boshlash
    asyncio.create_task(maintain_tunnel(current_port))

    # 3. Telegram Botni ishga tushirish
    log.info("🤖 Telegram Bot Polling rejimida ishga tushmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # Telegram rasmiy menyu buyruqlarini ro'yxatdan o'tkazish
        try:
            await bot.set_my_commands([
                BotCommand(command="start", description="🚀 Botni ishga tushirish"),
                BotCommand(command="app", description="📱 Test topshirish (Mini App)"),
                BotCommand(command="results", description="📊 Mening natijalarim"),
                BotCommand(command="profile", description="👤 Shaxsiy profilim"),
                BotCommand(command="help", description="ℹ️ Qo'llanma va yordam"),
            ])
            log.info("✅ Telegram Bot rasmiy buyruqlar menyusi o'rnatildi (/start, /app, ...)")
        except Exception as ce:
            log.warning(f"Bot buyruqlarini o'rnatishda ogohlantirish: {ce}")

        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        if runner:
            await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot to'xtatildi.")
