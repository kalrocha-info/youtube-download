import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import sys
import threading

# 📂 Pasta padrão de saída
PASTA_SAIDA = os.path.expanduser("~\\Downloads")
if not os.path.exists(PASTA_SAIDA):
    PASTA_SAIDA = os.path.dirname(__file__)

# 🛑 Variável de controle para parar o download
PARAR_DOWNLOAD = False
DOWNLOAD_EM_PROGRESSO = False

# 📌 CAMINHO RELATIVO DO FFMPEG (funciona no código e no executável)
if getattr(sys, 'frozen', False):
    CAMINHO_BASE = os.path.dirname(sys.executable)
else:
    CAMINHO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Procura pela pasta do FFmpeg extraída (ffmpeg-*-full_build)
FFMPEG_PASTA = os.path.join(CAMINHO_BASE, "bin", "ffmpeg")
FFMPEG_CAMINHO = None

if os.path.exists(FFMPEG_PASTA):
    # Procura por pasta ffmpeg-*-full_build
    for pasta in os.listdir(FFMPEG_PASTA):
        if pasta.startswith("ffmpeg-") and "full_build" in pasta:
            caminho_encontrado = os.path.join(FFMPEG_PASTA, pasta, "bin")
            if os.path.exists(caminho_encontrado):
                FFMPEG_CAMINHO = caminho_encontrado
                break
    
    # Fallback: tenta pasta "bin" diretamente
    if not FFMPEG_CAMINHO:
        caminho_padrao = os.path.join(FFMPEG_PASTA, "bin")
        if os.path.exists(caminho_padrao):
            FFMPEG_CAMINHO = caminho_padrao

# Última tentativa: busca no PATH do sistema
if not FFMPEG_CAMINHO:
    FFMPEG_CAMINHO = None  # Deixa yt-dlp usar o PATH do sistema

def parar_download():
    global PARAR_DOWNLOAD
    PARAR_DOWNLOAD = True
    texto_status.config(text="🛑 Interrompendo...")
    btn_baixar.config(state="normal")
    btn_parar.config(state="disabled")


def baixar_thread():
    global PARAR_DOWNLOAD, DOWNLOAD_EM_PROGRESSO
    PARAR_DOWNLOAD = False
    DOWNLOAD_EM_PROGRESSO = True
    
    link = entrada_link.get().strip()
    if not link:
        messagebox.showwarning("Aviso", "⚠️ Cole o link do vídeo ou playlist primeiro!")
        DOWNLOAD_EM_PROGRESSO = False
        return

    formato = escolha_formato.get()
    qualidade = escolha_qualidade.get()
    nome_customizado = entrada_nome.get().strip()
    
    # Remove o placeholder da entrada se ainda estiver lá
    if nome_customizado.startswith("ex:"):
        nome_customizado = ""
    
    # Validar se pasta de saída existe
    try:
        os.makedirs(PASTA_SAIDA, exist_ok=True)
    except:
        messagebox.showerror("Erro", "Impossível criar pasta de destino")
        DOWNLOAD_EM_PROGRESSO = False
        return

    # Define o padrão de nome do arquivo
    if nome_customizado:
        # Se o usuário definiu um nome customizado, usa esse
        outtmpl = os.path.join(PASTA_SAIDA, nome_customizado)
    else:
        # Caso contrário, usa o padrão
        outtmpl = os.path.join(PASTA_SAIDA, "%(title)s.%(ext)s")

    opcoes = {
        'outtmpl': outtmpl,
        'noplaylist': True,  # 🛑 NÃO BAIXA PLAYLIST POR PADRÃO
        'quiet': False,
        'no_warnings': False,
    }
    
    # Adiciona caminho do FFmpeg se foi encontrado
    if FFMPEG_CAMINHO:
        opcoes['ffmpeg_location'] = FFMPEG_CAMINHO

    # 🎧 MODO ÁUDIO
    if formato in ['mp3', 'm4a', 'wav', 'flac']:
        opcoes['format'] = 'bestaudio/best'
        opcoes['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': formato,
            'preferredquality': qualidade.replace('kbps', ''),
        }]

    # 🎬 MODO VÍDEO
    else:
        if qualidade == "Melhor qualidade":
            opcoes['format'] = 'bestvideo+bestaudio/best'
            opcoes['merge_output_format'] = formato
        elif qualidade == "1080p":
            opcoes['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            opcoes['merge_output_format'] = formato
        elif qualidade == "720p":
            opcoes['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            opcoes['merge_output_format'] = formato
        elif qualidade == "480p":
            opcoes['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
            opcoes['merge_output_format'] = formato

    try:
        janela.config(cursor="wait")
        texto_status.config(text="⏳ Baixando e convertendo... Aguarde!")
        btn_baixar.config(state="disabled")
        btn_parar.config(state="normal")
        janela.update()

        # Hook para verificar se o usuário clicou em parar
        def progress_hook(d):
            if PARAR_DOWNLOAD:
                raise Exception("Download interrompido pelo usuário")
            if d['status'] == 'downloading':
                percentual = d.get('_percent_str', 'N/A')
                velocidade = d.get('_speed_str', 'N/A')
                texto_status.config(text=f"⏳ Baixando... {percentual} - {velocidade}")
                janela.update()
            elif d['status'] == 'finished':
                texto_status.config(text="📦 Finalizando e convertendo...")
                janela.update()

        opcoes['progress_hooks'] = [progress_hook]

        with yt_dlp.YoutubeDL(opcoes) as ydl:
            ydl.download([link])

        if not PARAR_DOWNLOAD:
            texto_status.config(text=f"✅ Pronto! Salvo em:\n{PASTA_SAIDA}")
            messagebox.showinfo("Sucesso", "Download finalizado com sucesso!")
        else:
            texto_status.config(text="🛑 Download interrompido!")

    except Exception as e:
        if "interrompido" in str(e):
            texto_status.config(text="🛑 Download interrompido!")
        else:
            texto_status.config(text="❌ Erro ao baixar")
            messagebox.showerror("Erro", f"Detalhes:\n{str(e)}")

    finally:
        janela.config(cursor="")
        btn_baixar.config(state="normal")
        btn_parar.config(state="disabled")
        DOWNLOAD_EM_PROGRESSO = False


def baixar():
    """Inicia o download em uma thread separada"""
    thread = threading.Thread(target=baixar_thread, daemon=True)
    thread.start()


def escolher_pasta():
    global PASTA_SAIDA
    pasta_escolhida = filedialog.askdirectory(title="Escolher pasta para salvar os arquivos")
    if pasta_escolhida:
        PASTA_SAIDA = pasta_escolhida
        texto_caminho.config(text=f"📂 Salvar em: {PASTA_SAIDA}")


# 🖥️ INTERFACE GRÁFICA
if __name__ == "__main__":
    janela = tk.Tk()
    janela.title("🎵 Baixador YouTube - Pacote Completo")
    janela.geometry("750x550")
    janela.resizable(False, False)

    # Título
    titulo = ttk.Label(janela, text="Baixador de Vídeos e Músicas", font=("Arial", 15, "bold"))
    titulo.pack(pady=15)

    # Campo do Link
    ttk.Label(janela, text="🔗 Link do YouTube:").pack(pady=(5, 2))
    entrada_link = ttk.Entry(janela, width=95)
    entrada_link.pack(pady=5, padx=20)

    # 📝 CAMPO PARA NOME CUSTOMIZADO
    ttk.Label(janela, text="📝 Nome do arquivo (deixe em branco para usar o título original):").pack(pady=(10, 2))
    entrada_nome = ttk.Entry(janela, width=95)
    entrada_nome.pack(pady=5, padx=20)
    entrada_nome.insert(0, "ex: minha_musica.%(ext)s")
    
    # Ajuda sobre o nome
    ttk.Label(janela, text="💡 Use %(ext)s para a extensão automática (ex: minha_musica.%(ext)s)", 
              foreground="#666666", font=("Arial", 8)).pack()

    # 📂 ÁREA DE ESCOLHA DE PASTA
    frame_pasta = ttk.Frame(janela)
    frame_pasta.pack(pady=10, fill="x", padx=20)

    btn_escolher_pasta = ttk.Button(frame_pasta, text="📁 Escolher Pasta de Destino", command=escolher_pasta)
    btn_escolher_pasta.pack(side="left", padx=5)

    texto_caminho = ttk.Label(frame_pasta, text=f"📂 Pasta padrão: {PASTA_SAIDA}", foreground="#333333")
    texto_caminho.pack(side="left", padx=10)

    # Linha de escolhas: Formato e Qualidade
    frame_opcoes = ttk.Frame(janela)
    frame_opcoes.pack(pady=15)

    # Formato
    ttk.Label(frame_opcoes, text="📁 Formato:").grid(row=0, column=0, padx=5)
    escolha_formato = ttk.Combobox(frame_opcoes, values=[
        "mp3", "m4a", "wav", "flac",
        "mp4", "webm"
    ], state="readonly", width=14)
    escolha_formato.set("mp3")
    escolha_formato.grid(row=0, column=1, padx=10)

    # Qualidade
    ttk.Label(frame_opcoes, text="🎚️ Qualidade:").grid(row=0, column=2, padx=5)
    escolha_qualidade = ttk.Combobox(frame_opcoes, values=[
        "320kbps", "256kbps", "192kbps", "128kbps",
        "Melhor qualidade", "1080p", "720p", "480p"
    ], state="readonly", width=14)
    escolha_qualidade.set("320kbps")
    escolha_qualidade.grid(row=0, column=3, padx=10)

    # Botões de Download e Parar
    frame_botoes = ttk.Frame(janela)
    frame_botoes.pack(pady=20)
    
    btn_baixar = ttk.Button(frame_botoes, text="⬇️ BAIXAR AGORA", command=baixar)
    btn_baixar.pack(side="left", padx=10, ipadx=12, ipady=6)

    btn_parar = ttk.Button(frame_botoes, text="🛑 PARAR", command=parar_download, state="disabled")
    btn_parar.pack(side="left", padx=10, ipadx=12, ipady=6)

    # Status
    texto_status = ttk.Label(janela, text="Aguardando...", foreground="#555555", font=("Arial", 10))
    texto_status.pack(pady=10)

    janela.mainloop()
