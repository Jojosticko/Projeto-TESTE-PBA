# Projeto de Submissão de Ideias - BPA Ventures

Este projeto é uma aplicação web desenvolvida para a coleta e avaliação de ideias, utilizando processamento de linguagem natural (IA) para análise qualitativa e um fluxo de gestão centralizado.

##  Tecnologias Utilizadas
- **Linguagem:** Python 3.10+
- **Framework Web:** Flask (rotas e gerenciamento de requisições).
- **IA (LLM):** Google Gemini SDK (`google-genai`) para análise de submissões.
- **Segurança:** Variáveis de ambiente (`os.getenv`), `.gitignore` e Autenticação HTTP Basic.

##  Arquitetura e Decisões Técnicas
- **Segurança de Dados:** Implementamos um arquivo `prompt.env` (excluído do repositório via `.gitignore`) para garantir que segredos como `GOOGLE_API_KEY` e `ADMIN_PASSWORD` nunca sejam expostos.
- **Processamento:** A lógica de análise de ideias é desacoplada através do arquivo `prompt.md`, permitindo ajustes nas "System Instructions" da IA sem a necessidade de alterar o código-fonte principal.
- **Autenticação:** As rotas administrativas (`/historico` e `/decisao`) possuem proteção via *Basic Auth*, garantindo que apenas administradores com as credenciais corretas possam gerir as submissões.
- **Experiência do Usuário (UX):** Interfaces centralizadas com feedback visual claro após a submissão e ações de gestão.


##  Guia de Configuração

### Pré-requisitos
Certifique-se de ter o Python instalado e instale as dependências:
```bash
pip install flask google-genai


### Fluxo
O sistema opera em um ciclo de processamento seguro, onde a IA atua como um filtro inteligente entre o proponente e o administrador:

```mermaid
graph LR
    A[Usuário/Proponente] -->|Envia Ideia| B(Flask App)
    B -->|Consulta prompt.md| C{Google Gemini}
    C -->|Retorna Análise| B
    B -->|Armazena em memória| D[(ideias_submetidas)]
    D -->|Autenticação| E[Admin /historico]
    E -->|Decisão| F[Feedback via Email]


Detalhamento das Etapas:
Entrada: O usuário submete a ideia através da interface web.

Processamento: O prova.py lê as diretrizes de comportamento em prompt.md e envia o contexto para o Google Gemini.

Persistência: A submissão é armazenada temporariamente(poderá ser substituido por um banco de dado real) no dicionário ideias_submetidas, ficando pronta para análise imediata.

Governança (Tomada de Decisão): O administrador acessa a rota protegida (/historico), autentica-se com a senha do prompt.env e tem autonomia para tomar a decisão sobre a ideia desde o momento do seu recebimento.

Comunicação: Ao validar ou rejeitar a ideia, o sistema dispara automaticamente o feedback para o e-mail do proponente, fechando o ciclo.  