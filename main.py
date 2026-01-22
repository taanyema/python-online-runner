from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# HTML de la page
HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Python Online Runner</title>
  <style>
    body { font-family: Arial; padding: 20px; background: #f9f9f9; }
    textarea { width: 100%; height: 200px; font-family: monospace; }
    input { width: 100%; padding: 8px; margin-top: 5px; }
    button { padding: 10px 20px; margin-top: 10px; }
    pre { background: #f4f4f4; padding: 10px; }
  </style>
</head>
<body>
  <h2>🐍 Python Online Runner</h2>
  <form method="post">
    <textarea name="code" placeholder="Écris ton code Python ici...">{{ code }}</textarea><br>
    <input type="text" name="user_input" placeholder="Entrée simulée ici"><br>
    <button type="submit">▶ Exécuter</button>
  </form>

  {% if output %}
    <h3>Résultat :</h3>
    <pre>{{ output }}</pre>
  {% endif %}
</body>
</html>
"""

# Liste des fonctions ou modules interdits pour la sécurité
FORBIDDEN = ["import os", "import sys", "subprocess", "open(", "eval", "exec"]

@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    code = ""
    user_input = ""

    if request.method == "POST":
        code = request.form["code"]
        user_input = request.form["user_input"]

        # Vérification de sécurité
        for bad in FORBIDDEN:
            if bad in code:
                output = "❌ Code interdit pour des raisons de sécurité."
                return render_template_string(HTML, output=output, code=code)

        # Remplacer toutes les input() par la valeur simulée
        code_safe = code.replace("input(", f'"{user_input}" # input simulé(')

        try:
            local_vars = {}
            exec(code_safe, {}, local_vars)
            # Affiche toutes les variables après exécution
            output = "\n".join(f"{k} = {v}" for k, v in local_vars.items())
        except Exception as e:
            output = f"❌ Erreur : {e}"

    return render_template_string(HTML, output=output, code=code)

# 🔧 Lancement de l'application avec port dynamique (pour Railway)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
