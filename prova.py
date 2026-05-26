from flask import Flask, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pypdf import PdfReader
import os
import mailtrap as mt
from flask import request, redirect, url_for, session
import os
import google.generativeai as genai
import os
from dotenv import load_dotenv
from google import genai 
from google.genai import types
app = Flask(__name__)

from google import genai


# 1. Carrega o arquivo prompt.env
load_dotenv(dotenv_path="prompt.env")

# 2. Pega as variáveis
chave = os.getenv("GOOGLE_API_KEY")
SENHA_ADMIN = os.getenv("SENHA_ADMIN")
EMAIL_ADMIN = "meyejarold@gmail.com"
URL_PLATAFORMA = "http://localhost:5000"

# 3. Validação
if not chave:
    raise ValueError("ERRO: GOOGLE_API_KEY não encontrada no arquivo prompt.env!")


app = Flask(__name__)
app.secret_key = SENHA_ADMIN


client = genai.Client(api_key=chave)


ideias_submetidas = {}

print("Configuração carregada com sucesso!")

def gerar_parecer_ia(texto_pdf):
    try:
        with open('prompt.md', 'r', encoding='utf-8') as f:
            instrucoes = f.read()
        
        conteudo_final = f"{instrucoes}\n\n### Conteúdo para Análise:\n{texto_pdf[:6000]}"
        
      
        models = list(client.models.list())
        
       
        modelo_escolhido = next((m.name for m in models if "flash" in m.name), None)
        
        if not modelo_escolhido:
            # Fallback caso não encontre nenhum flash
            modelo_escolhido = models[0].name
            
        print(f"Usando o modelo: {modelo_escolhido}")

        response = client.models.generate_content(
            model=modelo_escolhido, 
            contents=conteudo_final
        )
        return response.text
    except Exception as e:
        return f"Erro ao processar na IA: {str(e)}"

@app.route('/enviar_ideia', methods=['POST'])
def enviar_ideia():
    nome = request.form['nome']
    email_user = request.form['email']
    pdf = request.files['pdf']
    
    texto_pdf = ""
    leitor = PdfReader(pdf)
    for pagina in leitor.pages:
        texto_pdf += pagina.extract_text() or ""
    
   
    if any(termo in texto_pdf.lower() for termo in ["comissao", "originação"]):
        resultado = "REJEITADO na triagem automática."
    else:
        resultado = gerar_parecer_ia(texto_pdf)
    
    ideia_id = str(len(ideias_submetidas) + 1)
    ideias_submetidas[ideia_id] = {"nome": nome, "email": email_user, "status": "Pendente", "analise": resultado}
    
   
    if "REJEITADO" not in resultado:
        enviar_email_unico(ideia_id, nome, resultado, email_user)
        
    return f"<h3>Processado!</h3><p>{resultado}</p><a href='/'>Voltar</a>"
    
@app.route('/')
def pagina_inicial():
    return f'''
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 30px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333;">BPA Ventures - Portal de Triagem HZN</h2>
            <hr style="border: 0; border-top: 1px solid #eee; margin-bottom: 20px;">
            
            <form method="post" action="/enviar_ideia" enctype="multipart/form-data" style="line-height: 1.5;">
                <label><strong>Nome Completo:</strong></label><br>
                <input type="text" name="nome" required style="width:100%; padding: 8px; margin-bottom:15px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px;"><br>
                
                <label><strong>E-mail:</strong></label><br>
                <input type="email" name="email" required style="width:100%; padding: 8px; margin-bottom:15px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px;"><br>
                
                <label><strong>Telefone:</strong></label><br>
                <input type="text" name="telefone" required style="width:100%; padding: 8px; margin-bottom:15px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px;"><br>
                
                <label><strong>Documento da Ideia (PDF):</strong></label><br>
                <input type="file" name="pdf" accept=".pdf" required style="margin-bottom:20px;"><br>
                
                <button type="submit" style="background:#007BFF; color:white; border:none; padding:12px 20px; cursor:pointer; font-weight:bold; width:100%; border-radius: 4px; font-size: 16px;">Submeter para Triagem Local</button>
            </form>
            <br>
            <p style="text-align: center; font-size: 14px; margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px;">
                🔒 Área do Admin: <a href="/historico" style="color: #007BFF; font-weight: bold; text-decoration: none;">Ver Histórico de Submissões</a>
            </p>
        </div>
    '''





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['senha'] == "1234":  
            session['autenticado'] = True
            return redirect(url_for('historico'))
        return "Senha incorreta! <a href='/login'>Tentar novamente</a>"
    
    return '''
        <form method="post" style="font-family: Arial; padding: 20px;">
            <h3>Acesso Restrito ao Histórico</h3>
            <input type="password" name="senha" placeholder="Digite a senha" required>
            <button type="submit">Entrar</button>
        </form>
    '''



@app.route('/historico')
def historico():
   
    if not session.get('autenticado'):
        return redirect(url_for('login'))
        
    
    tabela_rows = ""
    for ide_id, dados in ideias_submetidas.items():
        
        tabela_rows += f'''
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{ide_id}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{dados['nome']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{dados['email']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{dados['status']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; white-space: pre-line;">{dados['analise']}</td>
        </tr>
        '''
    
    return f'''
    <h2 style="font-family: Arial;">Histórico de Submissões</h2>
    <table style="width: 100%; border-collapse: collapse; font-family: Arial;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th>ID</th><th>Nome</th><th>E-mail</th><th>Status</th><th>Análise IA</th>
            </tr>
        </thead>
        <tbody>{tabela_rows}</tbody>
    </table>
    <br><a href="/">Voltar</a> | <a href="/logout">Sair</a>
    '''

@app.route('/logout')
def logout():
    session.pop('autenticado', None)
    return "Desconectado com sucesso! <a href='/'>Ir para a página inicial</a>"

@app.route('/decisao/<ideia_id>/<status>')
def decisao(ideia_id, status):
    # 1. Atualiza o status
    if ideia_id in ideias_submetidas:
        ideias_submetidas[ideia_id]['status'] = status
        email_proponente = ideias_submetidas[ideia_id]['email']
        nome_proponente = ideias_submetidas[ideia_id]['nome']
        
       
        enviar_feedback_proponente(email_proponente, nome_proponente, status)
        
        return f'''
            <div style="font-family: sans-serif; padding: 20px;">
                <h2>Ação concluída!</h2>
                <p>Status alterado para <strong>{status}</strong>.</p>
                <p>E-mail de feedback enviado para: {email_proponente}</p>
                <br>
                <a href="/historico">Voltar ao Histórico</a>
            </div>
        '''
    else:
        return "Erro: ID não encontrado."


def enviar_email_unico(ideia_id, nome, resultado, email_proponente):
    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login("947fa3e2b6c505", "fdf8e6049571c0") 
            
            mensagem = f"""Subject: Triagem de Ideia: {nome}
MIME-Version: 1.0
Content-Type: text/html; charset="utf-8"

<h2>Relatório de Triagem - HZN</h2>
<p><strong>Proponente:</strong> {nome}</p>
<p><strong>E-mail de Contato:</strong> {email_proponente}</p>
<div style="background: #f4f4f4; padding: 15px; border-left: 5px solid #007bff;">
    <pre>{resultado}</pre>
</div>
<br>
<a href="http://localhost:5000/decisao/{ideia_id}/Aprovado" style="background-color: #28a745; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">APROVAR</a>
<a href="http://localhost:5000/decisao/{ideia_id}/Reprovado" style="background-color: #dc3545; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">REPROVAR</a>
"""
          
            server.sendmail("triagem@bpa.com", "meyejaroldadmin@exemplo.com", mensagem.encode("utf-8"))
        print(" E-mail enviado com sucesso!")
    except Exception as e:
        print(f" Erro: {e}")

def enviar_feedback_proponente(email_destino, nome, status):
    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login("947fa3e2b6c505", "fdf8e6049571c0")
            
           
            msg = f"""Subject: Atualização do seu Projeto - BPA Ventures
MIME-Version: 1.0
Content-Type: text/html; charset="utf-8"

<h2>Olá, {nome}!</h2>
<p>O status da sua submissão na BPA Ventures foi atualizado para: <strong>{status.upper()}</strong>.</p>
<p>Em breve, nossa equipe entrará em contato com mais detalhes.</p>
"""
            server.sendmail("triagem@bpa.com", email_destino, msg.encode("utf-8"))
        print(f" Feedback enviado para {email_destino}")
    except Exception as e:
        print(f" Erro ao enviar feedback: {e}")
if __name__ == '__main__':
    app.run(debug=True)