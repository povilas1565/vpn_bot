import datetime
import requests

from core.ssh.remote_wg import add_peer_to_wireguard
from core.wg.generator import generate_key_pair, build_client_config, save_config_and_qr
from database.db import SessionLocal
from database.models import Server, User, VPNKey

VEESP_API_KEY = "ВАШ_API_КЛЮЧ"

async def create_vpn_access(user_id: int, tariff: str):
    async with SessionLocal() as session:
        # Шаг 1. Найти сервер
        servers = await session.execute(
            Server.__table__.select().where(
                Server.type == tariff.capitalize(),
                Server.users_count < Server.max_users
            )
        )
        server_row = servers.first()
        server = server_row[0] if server_row else None

        # Шаг 2. Если нет — создать
        if not server:
            try:
                server_info = create_new_server_veesp(tariff.lower())
                server = Server(
                    ip=server_info["ip"],
                    ssh_user="root",
                    ssh_password=server_info["password"],
                    type=tariff.capitalize(),
                    users_count=0,
                    max_users=40 if tariff == "base" else 20 if tariff == "silver" else 3
                )
                session.add(server)
                await session.commit()
            except Exception as e:
                return None, f"❌ Ошибка создания сервера: {e}"

        # Шаг 3. Генерация ключей
        priv, pub = generate_key_pair()
        ip = f"10.66.66.{server.users_count + 2}"

        # Добавить peer
        success, error = add_peer_to_wireguard(
            server_ip=server.ip,
            ssh_user=server.ssh_user,
            ssh_password=server.ssh_password,
            public_key=pub,
            allowed_ip=ip
        )

        if not success:
            return None, f"❌ Не удалось добавить peer: {error}"

        config = build_client_config(priv, "SERVER_PUBLIC_KEY", server.ip, ip)
        config_path, qr_path = save_config_and_qr(config, user_id)

        # Шаг 4. Обновление БД
        existing_key = await session.execute(
            VPNKey.__table__.select().where(VPNKey.user_id == user_id)
        )
        existing_key = existing_key.first()
        if existing_key:
            await session.execute(VPNKey.__table__.delete().where(VPNKey.user_id == user_id))

        user = await session.get(User, user_id)
        if not user:
            user = User(
                telegram_id=user_id,
                expire_date=datetime.datetime.utcnow() + datetime.timedelta(days=30),
                server_id=server.id
            )
            session.add(user)
        else:
            user.expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
            user.server_id = server.id

        vpn_key = VPNKey(
            user_id=user.id,
            private_key=priv,
            public_key=pub,
            allowed_ip=ip
        )
        session.add(vpn_key)

        server.users_count += 1
        await session.commit()

        return (config_path, qr_path), None


def create_new_server_veesp(plan: str):
    api_url = "https://api.veesp.com/v1/servers"
    payload = {
        "plan": plan,
        "region": "your-region",
        "os": "ubuntu-20.04"
    }
    headers = {
        "Authorization": f"Bearer {VEESP_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Ошибка создания сервера: {response.text}")