from flask import Flask, render_template_string, request, redirect, session
from telegram import Bot
import os

app = Flask(__name__)
app.secret_key = "MINHA_CHAVE_SECRETA_123"  # Troque para algo mais seguro depois

# =============================
# CONFIGURAÇÕES DO PAINEL
# =============================
PAINEL_USER = "filipealves"
PAINEL_PASS = "1010"

# =============================
# CONFIGURAÇÕES DO TELEGRAM
# =============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TOKEN DO TELEGRAM NÃO ENCONTRADO! Configure 'TELEGRAM_TOKEN' no Render.")

bot = Bot(token=TELEGRAM_TOKEN)


GUARNICOES = {
    "UR-324": -5058043663,
    "ABTS": -5050134903,
    "UR-325": -5017658843,
    "UR-AC4": -5016835400,
    "ASA - Oficial de Dia": -5072055088,
}

# =============================
# TELA DE LOGIN
# =============================
login_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Login - Painel Bombeiros</title>
<style>
body { font-family: Arial; background:#eee; text-align:center; padding-top:80px; }
input { padding:10px; width:250px; margin:5px; }
button { padding:10px 20px; }
.box { background:white; padding:30px; width:320px; margin:auto; border-radius:10px; }
</style>
</head>
<body>
<div class="box">
<h2>🔐 Login do Painel</h2>
<form method="POST">
<input name="usuario" placeholder="Usuário" required><br>
<input name="senha" type="password" placeholder="Senha" required><br>
<button type="submit">Entrar</button>
</form>
{% if erro %}
<p style="color:red;">{{ erro }}</p>
{% endif %}
</div>
</body>
</html>
"""

# =============================
# PÁGINA PRINCIPAL (PAINEL)
# =============================
painel_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Painel de Alertas</title>
<style>
body { font-family: Arial; background:#f2f2f2; padding:20px; }
.container { max-width:600px; margin:auto; background:white; padding:20px; border-radius:10px; }
select, textarea { width:100%; padding:10px; margin-top:10px; }
button { padding:10px; margin-top:10px; width:100%; }
.checkbox { margin:6px 0; }
.log { margin-top:12px; font-size:13px; color:#333; background:#fafafa; padding:8px; border-radius:6px; max-height:200px; overflow:auto;}
</style>
</head>
<body>
<div class="container">
<h2>🚨 PAINEL DE ALERTAS</h2>

<form method="POST">
<label>Selecione as guarnições:</label><br>
{% for nome in guarnicoes %}
<div class="checkbox"><input type="checkbox" name="grupos" value="{{ nome }}"> {{ nome }}</div>
{% endfor %}

<textarea name="mensagem" placeholder="Digite a mensagem..." rows="5" required></textarea>

<button type="submit">Enviar Alerta</button>
</form>

{% if enviado %}
<p style="color:green;">Mensagem enviada com sucesso!</p>
{% endif %}

<br>
<a href="/logout">🚪 Sair</a>

</div>
</body>
</html>
"""

# =============================
# ROTA LOGIN
# =============================
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        if request.form.get("usuario") == PAINEL_USER and request.form.get("senha") == PAINEL_PASS:
            session["logado"] = True
            return redirect("/")
        else:
            erro = "Usuário ou senha incorretos!"
    return render_template_string(login_html, erro=erro)

# =============================
# ROTA LOGOUT
# =============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =============================
# PÁGINA PRINCIPAL
# =============================
@app.route("/", methods=["GET", "POST"])
def painel():
    if "logado" not in session:
        return redirect("/login")

    enviado = False

    if request.method == "POST":
        grupos = request.form.getlist("grupos")
        mensagem = request.form.get("mensagem", "").strip()

        if not grupos or not mensagem:
            enviado = False
        else:
            for g in grupos:
                if g not in GUARNICOES:
                    continue
                chat_id = GUARNICOES[g]
                texto = (
                    "🚨 *NOVA OCORRÊNCIA* 🚨\n\n"
                    f"👨‍🚒 *Guarnição:* {g}\n"
                    f"📝 *Mensagem:* {mensagem}\n"
                )
                bot.send_message(chat_id=chat_id, text=texto, parse_mode="Markdown")

            enviado = True

    return render_template_string(painel_html, guarnicoes=GUARNICOES.keys(), enviado=enviado)

# =============================
# INICIAR FLASK (RENDER COMPATÍVEL)
# =============================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"Servidor rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
