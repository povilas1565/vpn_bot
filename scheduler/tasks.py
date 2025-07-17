import os
from datetime import datetime

import requests

from core.ssh.remote_wg import remove_peer_from_wireguard
from database.db import SessionLocal
from database.models import User, VPNKey, Server

CONFIG_DIR = "configs"  # где хранятся конфиги и QR
VEESP_API_KEY = "ВАШ_API_КЛЮЧ"

def cleanup_expired_users():
    with SessionLocal() as session:
        now = datetime.utcnow()
        expired_users = session.execute(
            User.__table__.select().where(User.expire_date < now)
        )
        users = expired_users.fetchall()

        for user_row in users:
            user = user_row[0]

            vpn_key = session.get(VPNKey, user.id)
            if not vpn_key:
                continue

            server = session.get(Server, user.server_id)
            if not server:
                continue

            success, error = remove_peer_from_wireguard(
                server.ip,
                server.ssh_user,
                server.ssh_password,
                vpn_key.public_key
            )

            if not success:
                print(f"Ошибка удаления пользователя {user.id} из wg: {error}")
                continue

            # Удаляем файлы
            conf_path = os.path.join(CONFIG_DIR, f"{user.id}.conf")
            qr_path = os.path.join(CONFIG_DIR, f"{user.id}.png")
            for path in [conf_path, qr_path]:
                if os.path.exists(path):
                    os.remove(path)

            session.delete(vpn_key)
            session.delete(user)
            server.users_count -= 1

            session.commit()
            print(f"Удалён пользователь {user.id} и его доступ")

def delete_empty_servers():
    with SessionLocal() as session:
        result = session.execute(Server.__table__.select().where(Server.users_count == 0))
        servers = result.fetchall()

        for row in servers:
            server = row[0]

            try:
                headers = {"Authorization": f"Bearer {VEESP_API_KEY}"}
                requests.delete(f"https://api.veesp.com/v1/servers/{server.id}", headers=headers)
            except Exception as e:
                print(f"Ошибка удаления сервера {server.id}: {e}")
                continue

            session.delete(server)
            session.commit()
            print(f"Удалён сервер {server.id} с IP {server.ip}")