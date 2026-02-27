# Proof of Humans (MVP) - Thermal & Respiration Liveness

Este projeto é um MVP (Produto Mínimo Viável) para validação de identidade e presença humana ("Proof of Humanity") utilizando câmeras térmicas e análise de padrões respiratórios, sem a necessidade de hardware proprietário complexo (como "Orbs").

## 🎯 Objetivo

Provar que há um humano vivo na frente da câmera através de:
1.  **Detecção Térmica Facial**: Identificação de rosto em espectro térmico.
2.  **Liveness por Respiração**: Análise de frequência respiratória (RPM) baseada na variação de temperatura nas vias aéreas.
3.  **Consistência Biométrica**: Verificação de identidade (1:1) ou unicidade.
4.  **Emissão de Prova**: Geração de um "Human Proof" assinado criptograficamente.

## 🚀 Tecnologias

-   **Linguagem**: Python 3.8+
-   **Backend**: FastAPI (Assíncrono)
-   **Processamento de Imagem**: OpenCV, NumPy
-   **Simulação de Hardware**: Módulo de câmera térmica mockado (para desenvolvimento sem hardware real).
-   **Frontend**: HTML5/JS (Cliente de demonstração simples).

## 📂 Estrutura do Projeto

```
/backend        # API FastAPI e endpoints
/pipeline       # Lógica core (Detecção, Respiração, Biometria)
/device         # Abstração de hardware (Câmera Térmica)
/client         # Interface web para teste
/tests          # Scripts de teste e debug
```

## 🛠️ Instalação e Execução

1.  **Clone o repositório** (se ainda não o fez):
    ```bash
    git clone https://github.com/seu-usuario/proof-of-humans.git
    cd proof-of-humans
    ```

2.  **Crie e ative um ambiente virtual**:
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o servidor**:
    ```bash
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```

5.  **Acesse o cliente de teste**:
    Abra o arquivo `client/index.html` no seu navegador ou acesse `http://localhost:5173` se estiver usando um servidor de desenvolvimento web.

## 🧪 Testes

Você pode rodar o script de fluxo completo para simular um cadastro e verificação:
```bash
python tests/test_flow.py
```

## 🔒 Segurança (MVP)

-   Assinatura digital dos proofs gerados.
-   Detecção de replay attacks via desafio-resposta (instruções de respiração).
-   Validação de vivacidade (Liveness) passiva e ativa.

## 📝 Licença

[MIT](LICENSE)
