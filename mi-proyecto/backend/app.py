from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db, init_notes_db

app = Flask(__name__)

# Inicializar base de datos al arrancar Flask
init_db()        # Tabla de usuarios
init_notes_db()  # Tabla de notas privadas

# -----------------------------
# ENDPOINTS GENERALES
# -----------------------------

@app.route("/")
def index():
    return jsonify({"message": "Backend Flask levantado 🚀"})

# Registro de usuario
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email y contraseña obligatorios"}), 400
    
    hashed = generate_password_hash(password)
    
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
        conn.close()
        return jsonify({"message": "Usuario registrado ✅"})
    except Exception:
        return jsonify({"error": "Email ya registrado"}), 400

# Login de usuario
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email y contraseña obligatorios"}), 400
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user["password"], password):
        return jsonify({"message": "Login correcto ✅"})
    else:
        return jsonify({"error": "Email o contraseña incorrectos"}), 401

# -----------------------------
# ENDPOINTS DE NOTAS PRIVADAS
# -----------------------------

# Crear nota
@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    email = data.get("email")

    if not title or not content:
        return jsonify({"error": "Título y contenido obligatorios"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    conn.execute(
        "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
        (user["id"], title, content)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Nota creada ✅"})

# Listar notas propias
@app.route("/notes", methods=["GET"])
def list_notes():
    email = request.args.get("email")
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    notes = conn.execute(
        "SELECT id, title, content, created_at, updated_at FROM notes WHERE user_id = ? ORDER BY created_at DESC",
        (user["id"],)
    ).fetchall()
    conn.close()
    return jsonify([dict(note) for note in notes])

# Editar nota
@app.route("/notes/<int:note_id>", methods=["PUT"])
def edit_note(note_id):
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    email = data.get("email")

    if not title or not content:
        return jsonify({"error": "Título y contenido obligatorios"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    note = conn.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, user["id"])).fetchone()
    if not note:
        conn.close()
        return jsonify({"error": "Nota no encontrada o no tienes permiso"}), 404

    conn.execute(
        "UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (title, content, note_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Nota editada ✅"})

# Borrar nota
@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    data = request.get_json()
    email = data.get("email")

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    note = conn.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, user["id"])).fetchone()
    if not note:
        conn.close()
        return jsonify({"error": "Nota no encontrada o no tienes permiso"}), 404

    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Nota eliminada ✅"})

# -----------------------------
# ARRANQUE DE FLASK
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)