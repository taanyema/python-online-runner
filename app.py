from flask import Flask, render_template, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_code():
    code = request.json.get("code", "")

    if len(code) > 5000:
        return jsonify({"output": "❌ Code trop long"})

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode("utf-8"))
        filename = f.name

    try:
        result = subprocess.run(
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=3
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = "⏱️ Temps d'exécution dépassé"
    except Exception as e:
        output = str(e)

    os.remove(filename)
    return jsonify({"output": output})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Railway donne le port automatiquement
    app.run(host="0.0.0.0", port=port)
