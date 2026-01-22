from flask import Flask, request, render_template_string, session, redirect, url_for
import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from uuid import uuid4

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", str(uuid4()))  # nécessaire pour session

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Python Online REPL V3</title>
  <style>
    body { font-family: Arial; padding: 20px; background: #f9f9f9; }
    textarea { width: 100%; height: 200px; font-family: monospace; }
    input { width: 100%; padding: 8px; margin-top: 5px; }
    button { padding: 10px 20px; margin-top: 10px; }
    pre { background: #f4f4f4; padding: 10px; white-space: pre-wrap; }
    img { max-width: 100%; margin-top: 20px; }
  </style>
</head>
<body>
  <h2>🐍 Python Online REPL V3</h2>

  {% if waiting_input %}
    <p>{{ waiting_input }}</p>
    <form method="post">
      <input type="text" name="user_input" autofocus>
      <button type="submit">▶ Envoyer</button>
    </form>
  {% else %}
    <form method="post">
      <textarea name="code" placeholder="Écris ton code Python ici...">{{ code }}</textarea><br>
      <button type="submit">▶ Exécuter</button>
    </form>
  {% endif %}

  {% if output %}
    <h3>Résultat :</h3>
    <pre>{{ output }}</pre>
  {% endif %}

  {% if plot %}
    <h3>Graphique :</h3>
    <img src="data:image/png;base64,{{ plot }}">
  {% endif %}
</body>
</html>
"""

FORBIDDEN = ["import os", "import sys", "subprocess", "open(", "eval", "exec"]

@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    plot_img = ""
    code = ""
    waiting_input = None

    # Réinitialiser session si nouvelle session
    if "exec_state" not in session:
        session["exec_state"] = {}

    state = session["exec_state"]

    if request.method == "POST":
        if "code" in request.form:
            # Première soumission du code
            code = request.form["code"]

            for bad in FORBIDDEN:
                if bad in code:
                    output = "❌ Code interdit pour des raisons de sécurité."
                    return render_template_string(HTML, output=output, plot=plot_img, code=code, waiting_input=waiting_input)

            state["code"] = code
            state["lines"] = code.splitlines()
            state["current_line"] = 0
            state["locals"] = {"plt": plt}
            state["waiting_input"] = None
            session.modified = True

        elif "user_input" in request.form:
            # Soumission d'un input simulé
            state["last_input"] = request.form["user_input"]

    # Exécution ligne par ligne avec gestion input()
    try:
        while state.get("current_line", 0) < len(state.get("lines", [])):
            line = state["lines"][state["current_line"]]

            # Remplacer input() par récupération de l'input de session
            if "input(" in line:
                if "last_input" in state:
                    line_safe = line.replace("input(", f'"{state.pop("last_input")}" #input simulé(')
                else:
                    waiting_input = line.split("input(")[0] + ">>>"
                    session.modified = True
                    return render_template_string(HTML, output=output, plot=plot_img, code=state["code"], waiting_input=waiting_input)

            else:
                line_safe = line

            exec(line_safe, {}, state["locals"])
            state["current_line"] += 1

        # Après exécution
        output = "\n".join(f"{k} = {v}" for k, v in state["locals"].items() if k != "plt")
        
        # Vérifier plot
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        plot_img = base64.b64encode(buf.getvalue()).decode("utf-8")

        # Réinitialiser pour nouvelle session
        session.pop("exec_state")
    except Exception as e:
        output = f"❌ Erreur : {e}"
        session.pop("exec_state")

    return render_template_string(HTML, output=output, plot=plot_img, code=state.get("code",""), waiting_input=waiting_input)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
