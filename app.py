from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = 'ortech_secure_secret_key_change_in_production'
DB_NAME = 'database.db'

# Configurações de Upload de Imagens
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Garante que a pasta de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            discount REAL DEFAULT 0,
            colors TEXT,
            total_stock INTEGER DEFAULT 0,
            color_stock TEXT,
            image_url TEXT,
            category TEXT,
            subcategory TEXT
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN subcategory TEXT")
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Inicializa a base de dados ao iniciar
init_db()

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

# Rota Pública (Home)
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search = request.args.get('search', '')
    if search:
        cursor.execute("SELECT * FROM products WHERE name LIKE ? OR sku LIKE ?", ('%' + search + '%', '%' + search + '%'))
    else:
        cursor.execute("SELECT * FROM products")
        
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Rotas Dedicadas para Categorias e Subcategorias
@app.route('/categoria/<category_name>')
def listar_categoria(category_name):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category_name,))
    products = cursor.fetchall()
    conn.close()
    return render_template('categoria.html', products=products, category_name=category_name, subcategory_name=None)

@app.route('/categoria/<category_name>/<subcategory_name>')
def listar_subcategoria(category_name, subcategory_name):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ? AND subcategory = ?", (category_name, subcategory_name))
    products = cursor.fetchall()
    conn.close()
    return render_template('categoria.html', products=products, category_name=category_name, subcategory_name=subcategory_name)

# Rota de Login do Colaborador
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['collaborator'] = user[1]
            return redirect(url_for('admin'))
        else:
            error = 'Usuário ou senha inválidos.'

    return render_template('login.html', error=error)

@app.route('/produto/<int:product_id>')
def detalhe_produto(product_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return "Produto não encontrado", 404
        
    # Corrigido para carregar 'produto.html' corretamente
    return render_template('produto.html', product=product)

@app.route('/logout')
def logout():
    session.pop('collaborator', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'collaborator' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
        
    conn.close()
    # Mantido como 'admin_2.html' conforme o nome real do seu ficheiro
    return render_template('admin_2.html', products=products, users=users)

@app.route('/save_product', methods=['POST'])
def save_product():
    if 'collaborator' not in session:
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')
    name = request.form.get('name')
    sku = request.form.get('sku')
    description = request.form.get('description', '')
    price = float(request.form.get('price', 0))
    discount = float(request.form.get('discount', 0))
    colors = request.form.get('colors', '')
    total_stock = int(request.form.get('total_stock', 0) or 0)
    color_stock = request.form.get('color_stock', '')
    category = request.form.get('category')
    subcategory = request.form.get('subcategory')
    
    uploaded_images = []
    if 'image_file' in request.files:
        files = request.files.getlist('image_file')
        for file in files:
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                web_path = f"/{file_path.replace(os.sep, '/')}"
                uploaded_images.append(web_path)

    kept_images = request.form.getlist('kept_existing_images')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    final_images_list = []
    if product_id:
        final_images_list.extend(kept_images)
        final_images_list.extend(uploaded_images)
    else:
        if uploaded_images:
            final_images_list.extend(uploaded_images)

    if final_images_list:
        image_url = ",".join(list(dict.fromkeys([img.strip() for img in final_images_list if img.strip()])))
    else:
        image_url = 'https://images.unsplash.com/photo-1523275335684-37898b6baf30'

    if product_id:
        cursor.execute('''
            UPDATE products SET name=?, sku=?, description=?, price=?, discount=?, colors=?, total_stock=?, color_stock=?, image_url=?, category=?, subcategory=?
            WHERE id=?
        ''', (name, sku, description, price, discount, colors, total_stock, color_stock, image_url, category, subcategory, product_id))
    else:
        try:
            cursor.execute('''
                INSERT INTO products (name, sku, description, price, discount, colors, total_stock, color_stock, image_url, category, subcategory)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, sku, description, price, discount, colors, total_stock, color_stock, image_url, category, subcategory))
        except sqlite3.IntegrityError:
            flash('Erro: Já existe um produto cadastrado com este SKU.', 'error')
            conn.close()
            return redirect(url_for('admin'))
            
    conn.commit()
    conn.close()
    flash('Produto salvo com sucesso!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if 'collaborator' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_user', methods=['POST'])
def add_user():
    if 'collaborator' not in session:
        return redirect(url_for('login'))

    username = request.form.get('new_username').strip()
    password = request.form.get('new_password')

    if not is_valid_password(password):
        flash('Erro: A senha deve ter pelo menos 8 caracteres, conter letra maiúscula, minúscula, número e caractere especial.', 'error')
        return redirect(url_for('admin'))

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        flash('Colaborador cadastrado com sucesso!', 'success')
    except sqlite3.IntegrityError:
        flash('Erro: Nome de usuário já cadastrado no sistema.', 'error')
    finally:
        conn.close()

    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    if 'collaborator' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Colaborador removido com sucesso!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)