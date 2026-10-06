import os
import threading
import webbrowser
from pathlib import Path

import joblib
import numpy as np
from flask import Flask, request, jsonify, send_from_directory

try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH     = BASE_DIR / "model" / "spam_model.pkl"
VECTORIZER_PATH = BASE_DIR / "model" / "vectorizer.pkl"
INDEX_PATH     = BASE_DIR / "index.html"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Modelo não encontrado em {MODEL_PATH}")
if not VECTORIZER_PATH.exists():
    raise FileNotFoundError(f"Vetorizador não encontrado em {VECTORIZER_PATH}")
if not INDEX_PATH.exists():
    raise FileNotFoundError(f"index.html não encontrado em {INDEX_PATH}")

model      = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

app = Flask(__name__, static_folder=None)
if HAS_CORS:
    CORS(app)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/classificar", methods=["POST"])
def classificar():
    try:
        payload = request.get_json(force=True)
        texto = payload.get("texto", "").strip()

        if not texto:
            return jsonify({"error": "texto vazio"}), 400

        vec = vectorizer.transform([texto])
        probabilidade = round(float(model.predict_proba(vec)[0][1]) * 100)
        predicao = int(model.predict(vec)[0])

        # Descobre quais palavras do texto existem no vocabulário do vetorizador
        # e pega o peso TF-IDF de cada uma para identificar os gatilhos
        feature_names = vectorizer.get_feature_names_out()
        scores = vec.toarray()[0]
        indices_ativos = scores.nonzero()[0]

        palavras_gatilho = sorted(
            [{"palavra": feature_names[i], "peso": round(float(scores[i]), 4)}
             for i in indices_ativos],
            key=lambda x: x["peso"],
            reverse=True
        )[:10]  # top 10 palavras com maior peso

        return jsonify({
            "probabilidade": probabilidade,
            "predicao": predicao,
            "gatilhos": palavras_gatilho,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def abrir_navegador(porta: int) -> None:
    try:
        webbrowser.open(f"http://localhost:{porta}")
    except Exception:
        pass


def main() -> None:
    porta = int(os.environ.get("PORT", 8000))
    threading.Timer(1.2, abrir_navegador, args=(porta,)).start()
    print("Classificador de Spam")
    print(f"Servidor rodando em http://localhost:{porta}")
    print("Pressione Ctrl+C para encerrar.")
    app.run(host="127.0.0.1", port=porta, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
