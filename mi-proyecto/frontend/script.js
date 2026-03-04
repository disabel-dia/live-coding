let currentEmail = "";

// Registrar usuario
function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://localhost:3000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => alert(data.message || data.error));
}

// Login usuario
function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://localhost:3000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            currentEmail = email;
            document.getElementById("auth").style.display = "none";
            document.getElementById("notes-section").style.display = "block";
            listNotes();
        } else {
            alert(data.error);
        }
    });
}

// Crear nota
function createNote() {
    const title = document.getElementById("note-title").value;
    const content = document.getElementById("note-content").value;

    fetch("http://localhost:3000/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: currentEmail, title, content })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.error);
        listNotes();
    });
}

// Listar notas
function listNotes() {
    fetch(`http://localhost:3000/notes?email=${currentEmail}`)
    .then(res => res.json())
    .then(notes => {
        const ul = document.getElementById("notes-list");
        ul.innerHTML = "";

        notes.forEach(note => {
            const li = document.createElement("li");
            li.textContent = note.title + ": " + note.content + " ";

            // Botón Editar
            const editBtn = document.createElement("button");
            editBtn.textContent = "Editar";
            editBtn.onclick = () => {
                const newTitle = prompt("Nuevo título:", note.title);
                const newContent = prompt("Nuevo contenido:", note.content);
                if (newTitle && newContent) {
                    fetch(`http://localhost:3000/notes/${note.id}`, {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email: currentEmail, title: newTitle, content: newContent })
                    })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.message || data.error);
                        listNotes();
                    });
                }
            };
            li.appendChild(editBtn);

            // Botón Borrar
            const deleteBtn = document.createElement("button");
            deleteBtn.textContent = "Borrar";
            deleteBtn.onclick = () => {
                if (confirm("¿Seguro que quieres borrar esta nota?")) {
                    fetch(`http://localhost:3000/notes/${note.id}`, {
                        method: "DELETE",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email: currentEmail })
                    })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.message || data.error);
                        listNotes();
                    });
                }
            };
            li.appendChild(deleteBtn);

            ul.appendChild(li);
        });
    });
}