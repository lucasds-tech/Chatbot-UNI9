from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = 'unismart.db'

def buscar_resposta(pergunta):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT resposta FROM faq WHERE pergunta LIKE ?", ('%' + pergunta + '%',))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def buscar_preco_por_nome(nome_servico):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, preco FROM servicos WHERE LOWER(nome) = LOWER(?)", (nome_servico,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def listar_servicos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM servicos")
    servicos = cursor.fetchall()
    conn.close()
    return [s[0] for s in servicos]

def listar_precos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, preco FROM servicos")
    servicos = cursor.fetchall()
    conn.close()
    return servicos

def salvar_avaliacao(nota):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS avaliacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, nota INTEGER NOT NULL, data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute("INSERT INTO avaliacoes (nota) VALUES (?)", (nota,))
    conn.commit()
    conn.close()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    mensagem = data.get('message', '').strip()
    mensagem_lower = mensagem.lower()

    # comandos exatos 'especificamente''
    if mensagem_lower in ['serviços', 'ver serviços', 'lista de serviços', 'quais serviços']:
        servicos = listar_servicos()
        reply = "Aqui estão os serviços disponíveis:\n" + "\n".join(f"- {s}" for s in servicos)
        reply += "\n\nDigite o nome do serviço para saber o preço, ou digite 'menu' para outras opções."
        return jsonify({'reply': reply})

    if mensagem_lower.startswith('preço') or mensagem_lower.startswith('quanto custa') or mensagem_lower.startswith('quanto é'):
        servicos = listar_precos()
        for nome, preco in servicos:
            if nome.lower() in mensagem_lower:
                return jsonify({'reply': f"O preço do serviço '{nome}' é R$ {preco:.2f}"})
        return jsonify({'reply': "Qual serviço você gostaria de saber o preço? Digite o nome do serviço."})

    # Verifica se a mensagem enviada é a info/nome exato de algum serviço
    preco_servico = buscar_preco_por_nome(mensagem)
    if preco_servico:
        nome, preco = preco_servico
        return jsonify({'reply': f"O preço do serviço '{nome}' é R$ {preco:.2f}"})

    if mensagem.isdigit() and 1 <= int(mensagem) <= 5:
        salvar_avaliacao(int(mensagem))
        mensagens = {
            1: "Sentimos muito pela sua experiência. Vamos melhorar!",
            2: "Lamentamos não ter atingido suas expectativas. Obrigado pelo feedback.",
            3: "Agradecemos sua avaliação. Estamos sempre buscando melhorar!",
            4: "Muito obrigado! Ficamos felizes que tenha gostado.",
            5: "😍 Uau! Agradecemos imensamente sua avaliação máxima!"
        }
        return jsonify({'reply': mensagens[int(mensagem)]})

    if mensagem_lower in ['avaliação', 'avaliar', 'avaliar atendimento']:
        reply = "Por favor, avalie nosso atendimento de 1 (péssimo) a 5 (excelente)."
        return jsonify({'reply': reply})

    if mensagem_lower in ['menu', 'opções', 'opcao', 'opções do menu']:
        reply = ("Menu de opções:\n"
                 "- serviços: ver lista de serviços\n"
                 "- preços: saber preços dos serviços\n"
                 "- avaliação: avaliar atendimento\n"
                 "- funções: saber o que o chatbot faz\n")
        return jsonify({'reply': reply})

    if mensagem_lower in ['funções', 'o que você faz?', 'o que você faz']:
        resposta = buscar_resposta("o que você faz?")
        if resposta:
            return jsonify({'reply': resposta})

    # Consultar o FAQ geral
    resposta = buscar_resposta(mensagem_lower)
    if resposta:
        return jsonify({'reply': resposta})

    # Retorna isso caso algo não seja encontrado
    return jsonify({'reply': "Desculpe, não entendi. Digite 'menu' para ver as opções disponíveis."})

if __name__ == '__main__':
    app.run(debug=True)
