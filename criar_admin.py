import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
senha_hash = generate_password_hash('Ortech@2026!')
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', senha_hash))
conn.commit()
conn.close()
print("Usuário criado com sucesso!")