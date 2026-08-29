import sqlite3
import hashlib
import os

DB_NAME = "precision_vrt.db"
UPLOAD_FOLDER = "uploads"

class EquipeManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

    def _get_cursor(self):
        return self.conn.cursor()

    # --- CARGOS ---
    def listar_cargos(self):
        cur = self._get_cursor()
        return cur.execute("SELECT id, nome FROM cargos ORDER BY nome").fetchall()

    def adicionar_cargo(self, nome):
        try:
            cur = self._get_cursor()
            cur.execute("INSERT INTO cargos (nome) VALUES (?)", (nome,))
            self.conn.commit()
            return True, "Cargo adicionado."
        except sqlite3.IntegrityError:
            return False, "Cargo já existe."

    def excluir_cargo(self, id):
        cur = self._get_cursor()
        if cur.execute("SELECT id FROM funcionarios WHERE cargo_id=?", (id,)).fetchone():
            return False, "Existem funcionários vinculados."
        cur.execute("DELETE FROM cargos WHERE id=?", (id,))
        self.conn.commit()
        return True, "Excluído."

    # --- FUNCIONARIOS ---
    def listar_funcionarios(self):
        cur = self._get_cursor()
        return cur.execute("""
            SELECT f.id, f.nome_completo, c.nome, f.cpf, f.telefone, f.ativo
            FROM funcionarios f LEFT JOIN cargos c ON f.cargo_id = c.id
            ORDER BY f.nome_completo
        """).fetchall()

    def adicionar_funcionario(self, nome, cargo_id, cpf, tel, registro):
        cur = self._get_cursor()
        cur.execute("""
            INSERT INTO funcionarios (nome_completo, cargo_id, cpf, telefone, registro_profissional)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, cargo_id, cpf, tel, registro))
        self.conn.commit()
        return cur.lastrowid

    # --- ACESSOS ---
    def listar_acessos(self):
        cur = self._get_cursor()
        return cur.execute("""
            SELECT f.id, f.nome_completo, c.nome, u.login, 
                   CASE WHEN u.id IS NOT NULL THEN 'Ativo' ELSE 'Inativo' END
            FROM funcionarios f
            LEFT JOIN cargos c ON f.cargo_id = c.id
            LEFT JOIN usuarios u ON u.funcionario_id = f.id
            ORDER BY f.nome_completo
        """).fetchall()

    def criar_usuario(self, funcionario_id, login, senha):
        cur = self._get_cursor()
        if cur.execute("SELECT id FROM usuarios WHERE login = ?", (login,)).fetchone():
            return False, "Login já cadastrado."
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        cargo_perm = cur.execute("SELECT c.permissoes_padrao FROM funcionarios f JOIN cargos c ON f.cargo_id = c.id WHERE f.id = ?", (funcionario_id,)).fetchone()
        permissoes = cargo_perm[0] if cargo_perm else '{}'
        try:
            cur.execute("INSERT INTO usuarios (funcionario_id, login, senha_hash, permissoes) VALUES (?, ?, ?, ?)", (funcionario_id, login, senha_hash, permissoes))
            self.conn.commit()
            return True, "Usuário criado."
        except Exception as e:
            return False, str(e)

    def validar_login(self, login, senha):
        cur = self._get_cursor()
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        res = cur.execute("SELECT u.id, f.nome_completo, u.permissoes FROM usuarios u JOIN funcionarios f ON u.funcionario_id = f.id WHERE u.login = ? AND u.senha_hash = ?", (login, senha_hash)).fetchone()
        if res: return {"id": res[0], "nome": res[1], "permissoes": res[2]}
        return None

    # --- IDENTIDADE VISUAL ---
    def get_config_visual(self):
        cur = self._get_cursor()
        res = cur.execute("SELECT * FROM config_visual WHERE id=1").fetchone()
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, res)) if res else {}

    def salvar_config_visual(self, marca, slogan, software, dev, cor):
        cur = self._get_cursor()
        cur.execute("UPDATE config_visual SET marca_nome=?, marca_slogan=?, software_nome=?, desenvolvedor=?, cor_primaria=? WHERE id=1", (marca, slogan, software, dev, cor))
        self.conn.commit()

    def salvar_logo(self, uploaded_file):
        if uploaded_file:
            path = os.path.join(UPLOAD_FOLDER, f"logo.{uploaded_file.name.split('.')[-1]}")
            with open(path, "wb") as f: f.write(uploaded_file.getbuffer())
            cur = self._get_cursor()
            cur.execute("UPDATE config_visual SET logo_path=? WHERE id=1", (path,))
            self.conn.commit()
