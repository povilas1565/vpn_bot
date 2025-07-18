import os
from datetime import datetime
import requests

from core.ssh.remote_wg import remove_peer_from_wireguard
from database.db import SessionLocal
from database.models import User, VPNKey, Server

CONFIG_DIR = "configs"
VEESP_API_KEY = "ВАШ_API_КЛЮЧ"

def cleanup_expired_users():
    with SessionLocal() as session:
        now = datetime.utcnow()
        users = session.query(User).filter(User.expire_date < now).all()

        for user in users:
            vpn_key = session.query(VPNKey).filter_by(user_id=user.id).first()
            if not vpn_key:
                continue

            server = session.query(Server).filter_by(id=user.server_id).first()
            if not server:
                continue

            # Удаляем peer через SSH
            success, error = remove_peer_from_wireguard(
                server_ip=server.ip,
                ssh_user=server.ssh_user,
                ssh_password=server.ssh_password,
                public_key=vpn_key.public_key
            )

            if not success:
                print(f"Ошибка удаления пользователя {user.id}: {error}")
                continue

            # Удаляем конфиг и QR
            conf_path = os.path.join(CONFIG_DIR, f"{user.id}.conf")
            qr_path = os.path.join(CONFIG_DIR, f"{user.id}.png")
            for path in [conf_path, qr_path]:
                if os.path.exists(path):
                    os.remove(path)

            session.delete(vpn_key)
            session.delete(user)
            server.users_count = max(0, server.users_count - 1)

        session.commit()

def delete_empty_servers():
    with SessionLocal() as session:
        empty_servers = session.query(Server).filter(Server.users_count == 0).all()

        for server in empty_servers:
            try:
                headers = {"Authorization": f"Bearer {VEESP_API_KEY}"}
                requests.delete(f"https://api.veesp.com/v1/servers/{server.id}", headers=headers)
            except Exception as e:
                print(f"❌ Ошибка удаления сервера {server.id}: {e}")
                continue

            session.delete(server)

        session.commit()