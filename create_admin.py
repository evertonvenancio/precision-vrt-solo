import sqlite3

conn = sqlite3.connect('precision_vrt.db')
c = conn.cursor()

# Verifica se admin existe
c.execute("SELECT COUNT(*) FROM usuarios WHERE login='admin'")
if c.fetchone()[0] == 0:
    # Hash PBKDF2 real para 'admin123' (usando app.services.auth_service.hash_senha logic)
    # salt: b2b1cf6c24b90112700e318991206f69 (32 bytes hex)
    # key: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 (SHA256 vazio - placeholder)
    # Vamos gerar um hash correto
    import os, hashlib, binascii
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", "admin123".encode(), salt, 100000)
    hash_str = f"{binascii.hexlify(salt).decode()}:{binascii.hexlify(key).decode()}"
    print(f"Hash real gerado: {hash_str}")
    c.execute("INSERT INTO usuarios (login, senha_hash, ativo) VALUES (?, ?, 1)", ('admin', hash_str))
    conn.commit()
    print("Admin criado com hash real!")
else:
    print("Admin já existe")

# Verifica
c.execute("SELECT login, ativo FROM usuarios")
for row in c.fetchall():
    print(f"User: {row[0]}, Ativo: {row[1]}")

conn.close()