# Guia de Configuração - Câmera Térmica (Thermal Master P3)

Este guia explica como conectar sua câmera térmica **Thermal Master P3** (ou similar) ao sistema "Proof of Humans", mesmo que ela não seja reconhecida diretamente como uma webcam comum.

## O Problema
Câmeras térmicas profissionais (como a P3) muitas vezes funcionam como dispositivos USB genéricos e não como webcams padrão. Por isso, o navegador ou o script podem não listá-las automaticamente.

## A Solução (Ponte via OBS)
Vamos usar o **OBS Studio** (software gratuito) para capturar a imagem do aplicativo da câmera e transformá-la em uma "Webcam Virtual" que nosso sistema consegue ler.

---

### Passo 1: Ver a imagem da câmera
1. Conecte a câmera USB no computador.
2. Abra o software oficial da câmera (Thermal Master, InfiRay, ou similar) ou use um visualizador compatível.
3. Garanta que você está vendo a imagem térmica na tela do seu computador.

### Passo 2: Configurar o OBS Studio
1. Baixe e instale o **OBS Studio** (https://obsproject.com/).
2. Abra o OBS Studio.
3. Na caixa **Fontes** (Sources) na parte inferior, clique no **+** e selecione **Captura de Janela** (Window Capture).
4. Dê um nome (ex: "Camera Termica") e OK.
5. Na lista "Janela", selecione a janela do software da sua câmera térmica. A imagem deve aparecer no OBS.
6. Ajuste o tamanho da imagem na tela preta do OBS para preencher tudo.

### Passo 3: Ativar Câmera Virtual
1. No canto inferior direito do OBS, clique no botão **Iniciar Câmera Virtual** (Start Virtual Camera).
   - *Agora seu computador acha que existe uma webcam chamada "OBS Virtual Camera" transmitindo essa imagem.*

### Passo 4: Rodar o Sistema
1. Abra a pasta do projeto.
2. Dê dois cliques no arquivo `run.bat`.
3. O script vai perguntar o índice da câmera.
   - Digite o número correspondente à **OBS Virtual Camera** (geralmente aparece na lista que o script mostra).
   - Se tiver dúvida, tente `0`, `1` ou `2` até acertar.
4. Quando o servidor iniciar, abra o navegador em `http://localhost:8000`.

Pronto! O sistema vai receber a imagem térmica limpa e fará a detecção de rosto e respiração normalmente.
