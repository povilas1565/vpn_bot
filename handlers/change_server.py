from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from database.db import SessionLocal
from database.models import User, VPNKey, Server
from core.ssh.remote_wg import remove_peer_from_wireguard
from core.wg.provisioner import create_vpn_access
import os

router = Router()


@router.message(F.text == "🔄 Сменить сервер")
async def change_server_handler(message: Message):
    user_id = message.from_user.id
    with SessionLocal() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user or not user.vpn_key:
            await message.answer("🙁 У вас нет активного VPN доступа.")
            return

        vpn_key = session.query(VPNKey).filter_by(user_id=user.id).first()
        server = session.query(Server).filter_by(id=user.server_id).first()
        if not vpn_key or not server:
            await message.answer("⚠️ Не найдены данные подключения.")
            return

        # Удалить пользователя с текущего сервера
        success, err = remove_peer_from_wireguard(
            server_ip=server.ip,
            ssh_user=server.ssh_user,
            ssh_password=server.ssh_password,
            public_key=vpn_key.public_key
        )
        if not success:
            await message.answer(f"⚠️ Ошибка удаления пользователя: {err}")
            return

        # Удаляем конфиг и QR
        for path in [f"configs/{user.id}.conf", f"qrcodes/{user.id}.png"]:
            if os.path.exists(path):
                os.remove(path)

        server.users_count = max(0, server.users_count - 1)
        session.commit()

    # Генерируем новый доступ
    tariff = user.type.lower()
    result, error = await create_vpn_access(user_id, tariff)
    if error:
        await message.answer(error)
        return

    conf_path, qr_path = result
    await message.answer("✅ Сервер успешно сменён!")
    await message.answer_photo(FSInputFile(qr_path), caption="🔐 Новый QR-код")
    await message.answer_document(FSInputFile(conf_path), caption="📄 Новый конфиг")
    await message.answer("🏠 Главное меню", reply_markup=menu)
