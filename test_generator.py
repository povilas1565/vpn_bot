from core.wg.generator import generate_key_pair, build_client_config, save_config_and_qr

if __name__ == "__main__":
    private, public = generate_key_pair()
    config = build_client_config(
        private,
        "SERVER_PUBLIC_KEY_HERE",
        "YOUR_SERVER_IP",
        "10.66.66.2"
    )
    cfg_path, qr_path = save_config_and_qr(config, user_id=123456)
    print(f"✅ Config: {cfg_path}, QR: {qr_path}")