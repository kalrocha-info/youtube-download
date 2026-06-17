import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading

from downloader import (
    DownloadCancelled,
    DownloadRequest,
    DownloadValidationError,
    run_download,
)
from ffmpeg_locator import resolve_ffmpeg_path

# 📂 Pasta padrão de saída
PASTA_SAIDA = os.path.expanduser("~\\Downloads")
if not os.path.exists(PASTA_SAIDA):
    PASTA_SAIDA = os.path.dirname(__file__)

# 🛑 Variável de controle para parar o download
PARAR_DOWNLOAD = False
DOWNLOAD_EM_PROGRESSO = False

FFMPEG_CAMINHO = resolve_ffmpeg_path()
AUDIO_FORMATOS = {"mp3", "m4a", "wav", "flac"}
AUDIO_QUALIDADES = ["320kbps", "256kbps", "192kbps", "128kbps"]
VIDEO_QUALIDADES = ["Melhor qualidade", "1080p", "720p", "480p"]

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
    formato = escolha_formato.get()
    qualidade = escolha_qualidade.get()
    nome_customizado = entrada_nome.get().strip()

    request = DownloadRequest(
        url=link,
        output_dir=PASTA_SAIDA,
        media_format=formato,
        quality=qualidade,
        custom_name=nome_customizado,
    )

    try:
        janela.config(cursor="wait")
        texto_status.config(text="⏳ Baixando e convertendo... Aguarde!")
        btn_baixar.config(state="disabled")
        btn_parar.config(state="normal")
        janela.update()

        # Hook para verificar se o usuário clicou em parar
        def progress_hook(d):
            if PARAR_DOWNLOAD:
                raise DownloadCancelled("Download interrompido pelo usuário")
            if d['status'] == 'downloading':
                percentual = d.get('_percent_str', 'N/A')
                velocidade = d.get('_speed_str', 'N/A')
                texto_status.config(text=f"⏳ Baixando... {percentual} - {velocidade}")
                janela.update()
            elif d['status'] == 'finished':
                texto_status.config(text="📦 Finalizando e convertendo...")
                janela.update()

        run_download(request, FFMPEG_CAMINHO, progress_hook)

        if not PARAR_DOWNLOAD:
            texto_status.config(text=f"✅ Pronto! Salvo em:\n{PASTA_SAIDA}")
            messagebox.showinfo("Sucesso", "Download finalizado com sucesso!")
        else:
            texto_status.config(text="🛑 Download interrompido!")

    except DownloadCancelled:
        texto_status.config(text="🛑 Download interrompido!")
    except DownloadValidationError as e:
        texto_status.config(text="⚠️ Verifique os dados informados")
        messagebox.showwarning("Aviso", str(e))
    except OSError as e:
        texto_status.config(text="❌ Erro ao acessar a pasta de destino")
        messagebox.showerror("Erro", f"Não foi possível preparar a pasta de destino:\n{str(e)}")
    except Exception as e:
        texto_status.config(text="❌ Erro ao baixar")
        messagebox.showerror("Erro", f"Detalhes:\n{str(e)}")

    finally:
        janela.config(cursor="")
        btn_baixar.config(state="normal")
        btn_parar.config(state="disabled")
        DOWNLOAD_EM_PROGRESSO = False


def baixar():
    """Inicia o download em uma thread separada"""
    if DOWNLOAD_EM_PROGRESSO:
        messagebox.showwarning("Aviso", "Já existe um download em andamento.")
        return

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

    def atualizar_qualidades(_event=None):
        opcoes = AUDIO_QUALIDADES if escolha_formato.get() in AUDIO_FORMATOS else VIDEO_QUALIDADES
        escolha_qualidade.config(values=opcoes)
        if escolha_qualidade.get() not in opcoes:
            escolha_qualidade.set(opcoes[0])

    escolha_formato.bind("<<ComboboxSelected>>", atualizar_qualidades)
    atualizar_qualidades()

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
