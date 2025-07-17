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