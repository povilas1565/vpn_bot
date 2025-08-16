import random

import paramiko


def add_peer_to_wireguard(server_ip, ssh_user, ssh_password, public_key, allowed_ip):
    peer_config = f"""
    
[Peer]
PublicKey = {public_key}
AllowedIPs = {allowed_ip}/32
"""

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=ssh_user, password=ssh_password)

        # Добавляем peer через stdin
        cmd = f"echo '{peer_config}' | sudo wg addconf wg0 /dev/stdin"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()  # Ожидаем завершения команды

        ssh.close()
        return True, None

    except Exception as e:
        return False, str(e)


def remove_peer_from_wireguard(server_ip, ssh_user, ssh_password, public_key):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=ssh_user, password=ssh_password)

        cmd = f"sudo wg set wg0 peer {public_key} remove"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        ssh.close()

        if exit_status != 0:
            error_msg = stderr.read().decode()
            return False, f"Ошибка удаления пира: {error_msg}"

        return True, None

    except Exception as e:
        return False, str(e)


def get_wireguard_public_key(server_ip, ssh_user, ssh_password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=ssh_user, password=ssh_password)

        # Команда для получения ключа
        cmd = "sudo cat /etc/wireguard/publickey"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        public_key = stdout.read().decode().strip()
        ssh.close()
        return public_key, None
    except Exception as e:
        return None, str(e)


def setup_wireguard_interface(server_ip, ssh_user, ssh_password, server_index=1):
    """
    Создаёт wg0 на сервере с уникальной подсетью 10.<server_index>.66.0/24 и возвращает server_public_key
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=ssh_user, password=ssh_password)

        # Проверяем private key
        stdin, stdout, stderr = ssh.exec_command("cat /etc/wireguard/server_privatekey 2>/dev/null")
        private_key = stdout.read().decode().strip()

        if not private_key:
            # Генерация ключей
            ssh.exec_command(
                "wg genkey | sudo tee /etc/wireguard/server_privatekey | wg pubkey | sudo tee /etc/wireguard/publickey")
            stdin, stdout, stderr = ssh.exec_command("cat /etc/wireguard/server_privatekey")
            private_key = stdout.read().decode().strip()

        # Читаем public key
        stdin, stdout, stderr = ssh.exec_command("cat /etc/wireguard/publickey")
        public_key = stdout.read().decode().strip()

        # Уникальная подсеть
        subnet = f"10.{server_index}.66.0/24"
        wg_conf = f"""[Interface]
PrivateKey = {private_key}
Address = 10.{server_index}.66.1/24
ListenPort = 51820
SaveConfig = true
PostUp = ufw route allow in on wg0 out on eth0
PostDown = ufw route delete allow in on wg0 out on eth0
"""
        ssh.exec_command(f"echo '{wg_conf}' | sudo tee /etc/wireguard/wg0.conf > /dev/null")

        # Запускаем интерфейс
        ssh.exec_command("sudo systemctl enable wg-quick@wg0")
        ssh.exec_command("sudo systemctl restart wg-quick@wg0")

        ssh.close()
        return public_key, None

    except Exception as e:
        return None, str(e)

