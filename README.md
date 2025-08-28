# 🚗 Detecção e Contagem de Veículos com OpenCV  

Este projeto utiliza **Python + OpenCV** para processar vídeos e detectar **veículos em movimento** através de técnicas de **subtração de fundo** e **visão computacional**.  
O sistema acompanha o movimento dos carros, filtra ruídos e realiza a **contagem automática** quando cruzam linhas virtuais no vídeo.  

---

## 🚀 Funcionalidades
- Processamento de **vídeos ou sequências de imagens**.  
- Técnicas de **background subtraction** com **MOG2** ou **KNN**.  
- Aplicação de **operações morfológicas** para redução de ruídos.  
- Identificação de objetos em movimento com **contornos e bounding boxes**.  
- Rastreamento simples com:
  - Verificação de movimento contínuo.  
  - Histórico de posições para suavizar trajetórias.  
  - Rejeição de detecções muito rápidas (ruídos).  
- Contagem de veículos que cruzam **linhas horizontais ou verticais** configuradas.  
- Exibição em tempo real:
  - Vídeo original com **bounding boxes** e linhas de contagem.  
  - Máscara de foreground (objetos detectados).  
  - Contador total de veículos.  
- Encerramento do programa ao pressionar **Q**.  

---

## 🖼️ Demonstração
O programa abre duas janelas:  
- **Frame:** vídeo original com veículos detectados, caixas delimitadoras, linhas de contagem e total acumulado.  
- **FG Mask:** máscara binária da subtração de fundo mostrando apenas os objetos em movimento.  

---

## 📦 Requisitos
- Python 3.8+  
- [OpenCV](https://opencv.org/)  
- [NumPy](https://numpy.org/)  

---

## 🔧 Instalação
Clone este repositório e instale as dependências:

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
pip install opencv-python numpy
```

# Execução
Basta rodar o script principal passando o vídeo de entrada (ou usar o padrão videoopencvmp4):
```bash
python contador_carros.py --input seu_video.mp4 --algo MOG2
```
Parâmetros disponíveis:
- --input: caminho do vídeo ou sequência de imagens.
- --algo: algoritmo de subtração de fundo (MOG2 ou KNN).
