import datetime
import time
import paramiko
import requests

from config import VEESP_TOKEN
from core.ssh.remote_wg import add_peer_to_wireguard, get_wireguard_public_key, setup_wireguard_interface
from core.wg.generator import generate_key_pair, build_client_config, save_config_and_qr
from database.db import SessionLocal
from database.models import Server, User, VPNKey

# Регионы и OS для тарифов
TARIFF_CONFIG = {
    "base": {"region": "fra1", "os": "ubuntu-20.04", "max_users": 40},
    "silver": {"region": "ams1", "os": "ubuntu-22.04", "max_users": 20},
    "gold": {"region": "nyc1", "os": "ubuntu-22.04", "max_users": 3},
}


async def create_vpn_access(user_id: int, tariff: str):
    tariff_lower = tariff.lower()
    cfg = TARIFF_CONFIG.get(tariff_lower, TARIFF_CONFIG["base"])

    async with SessionLocal() as session:
        # 1. Ищем подходящий сервер
        servers = await session.execute(
            Server.__table__.select().where(
                Server.type == tariff.capitalize(),
                Server.users_count < Server.max_users
            )
        )
        server_row = servers.first()
        server = server_row[0] if server_row else None

        if not server:
            try:
                # вычисляем server_index для уникальной подсети
                result = await session.execute(Server.__table__.select())
                all_servers = result.fetchall()
                server_index = len(all_servers) + 1  # например, 1, 2, 3...

                server_info = create_new_server_veesp(
                    plan=tariff_lower,
                    region=cfg["region"],
                    os_version=cfg["os"],
                    server_index=server_index
                )
                server = Server(
                    ip=server_info["ip"],
                    ssh_user="root",
                    ssh_password=server_info["password"],
                    type=tariff.capitalize(),
                    users_count=0,
                    max_users=cfg["max_users"]
                )
                session.add(server)
                await session.commit()
            except Exception as e:
                return None, f"❌ Ошибка создания сервера: {e}"

        # 3. Если нет server_public_key — получаем по SSH
        if not server.server_public_key:
            pubkey, err = get_wireguard_public_key(server.ip, server.ssh_user, server.ssh_password)
            if err:
                return None, f"❌ Не удалось получить server_public_key: {err}"
            server.server_public_key = pubkey
            await session.commit()

        # 4. Генерация клиентских ключей и IP
        priv, pub = generate_key_pair()
        ip = f"10.66.66.{server.users_count + 2}"

        # 5. Добавляем peer на сервере
        success, error = add_peer_to_wireguard(
            server_ip=server.ip,
            ssh_user=server.ssh_user,
            ssh_password=server.ssh_password,
            public_key=pub,
            allowed_ip=ip
        )
        if not success:
            return None, f"❌ Не удалось добавить peer: {error}"

        # 6. Сборка клиентского конфига и генерация QR
        config = build_client_config(priv, server.server_public_key, server.ip, ip)
        config_path, qr_path = save_config_and_qr(config, user_id)

        # 7. Обновление БД
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


def create_new_server_veesp(plan: str, region: str = "fra1", os_version: str = "ubuntu-20.04", server_index: int = 1):
    api_url = "https://api.veesp.com/v1/servers"
    payload = {
        "plan": plan,
        "region": region,
        "os": os_version
    }
    headers = {
        "Authorization": f"Bearer {VEESP_TOKEN}",
        "Content-Type": "application/json"
    }

    # Создаём сервер
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Ошибка создания сервера: {response.text}")
    server_info = response.json()
    server_id = server_info.get("id")

    # Ждём пока сервер будет активен
    status_url = f"{api_url}/{server_id}"
    for _ in range(30):
        resp = requests.get(status_url, headers=headers)
        data = resp.json()
        if data.get("status") == "running":
            ip = data["ip"]
            password = data["password"]
            break
        time.sleep(10)
    else:
        raise Exception("❌ Сервер не поднялся вовремя")

    # Подключаемся по SSH и настраиваем WireGuard с уникальной подсетью
    server_pubkey, err = setup_wireguard_interface(ip, "root", password, server_index=server_index)
    if err:
        raise Exception(f"❌ Ошибка настройки WireGuard на сервере: {err}")

    return {
        "id": server_id,
        "ip": ip,
        "password": password,
        "server_public_key": server_pubkey
    }
