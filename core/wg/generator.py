import subprocess
import qrcode
from pathlib import Path

WG_INTERFACE = "wg0"
WG_PORT = 51820
WG_DNS = "1.1.1.1"

WG_CONFIG_DIR = Path("configs")
QR_OUTPUT_DIR = Path("qrcodes")

WG_CONFIG_DIR.mkdir(exist_ok=True)
QR_OUTPUT_DIR.mkdir(exist_ok=True)

def generate_key_pair():
    priv_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    pub_key = subprocess.check_output(["wg", "pubkey"], input=priv_key.encode()).decode().strip()
    return priv_key, pub_key

def build_client_config(priv_key, public_server_key, server_ip, client_ip):
    return f"""[Interface]
PrivateKey = {priv_key}
Address = {client_ip}/32
DNS = {WG_DNS}

[Peer]
PublicKey = {public_server_key}
Endpoint = {server_ip}:{WG_PORT}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

def save_config_and_qr(config_text: str, user_id: int):
    config_path = WG_CONFIG_DIR / f"{user_id}.conf"
    qr_path = QR_OUTPUT_DIR / f"{user_id}.png"

    with open(config_path, "w") as f:
        f.write(config_text)

    img = qrcode.make(config_text)
    img.save(qr_path)

    return config_path, qr_path

def generate_ip(index: int):
    return f"10.66.66.{index + 2}"  # Пример IP на основе индекса