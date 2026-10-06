import sys
import joblib

# Carrega modelo e vetorizador
model = joblib.load('model/spam_model.pkl')
vectorizer = joblib.load('model/vectorizer.pkl')

def classificar(texto):
    vec = vectorizer.transform([texto])
    prob = model.predict_proba(vec)[0][1]
    resultado = "🚨 SPAM" if prob > 0.5 else "✅ Ham"
    print(f"{resultado} ({prob:.1%} de probabilidade de spam)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Aceita texto direto como argumento: python main.py "mensagem aqui"
        classificar(" ".join(sys.argv[1:]))
    else:
        # Modo interativo
        print("Classificador de Spam — digite 'sair' para encerrar")
        while True:
            texto = input("\n> ").strip()
            if texto.lower() == "sair":
                break
            if texto:
                classificar(texto)
