from flask import Flask, request, render_template_string
import os
import sys
import io

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Python Online Runner</title>
</head>
<body>
  <h2>🐍 Python Online Runner</h2>
  <form method="post">
    <textarea name="code" rows="10" cols="60">{{ code }}</textarea><br><br>
    <input type="text" name="user_input" placeholder="Entrée simulée"><br><br>
    <button type="submit">Exécuter</button>
  </form>

  {% if output %}
    <h3>Résultat :</h3>
    <pre>{{ output }}</pre>
  {% endif %}
</body>
</html>
"""

FORBIDDEN = ["import os", "import sys", "subprocess", "open(", "eval", "exec"]

@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    code = ""

    if request.method == "POST":
        code = request.form.get("code", "")
        user_input = request.form.get("user_input", "")

        for bad in FORBIDDEN:
            if bad in code:
                return render_template_string(
                    HTML, code=code,
                    output="❌ Code interdit pour raisons de sécurité."
                )

        code = code.replace("input()", f'"{user_input}"')

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            exec(code, {})
            output = sys.stdout.getvalue()
        except Exception as e:
            output = f"❌ Erreur : {e}"

        sys.stdout = old_stdout

    return render_template_string(HTML, code=code, output=output)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
