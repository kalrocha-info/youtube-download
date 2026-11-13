import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from queue import Empty, Queue
from threading import Event, Thread

from youtube_download.downloader import (
    DownloadCancelled,
    DownloadRequest,
    DownloadValidationError,
    run_download,
)
from youtube_download.ffmpeg_locator import resolve_ffmpeg_path

# 📂 Pasta padrão de saída
PASTA_SAIDA = os.path.expanduser("~\\Downloads")
if not os.path.exists(PASTA_SAIDA):
    PASTA_SAIDA = os.path.dirname(__file__)

DOWNLOAD_EM_PROGRESSO = False
EVENTOS_DOWNLOAD = Queue()
CANCELAR_DOWNLOAD = Event()
CONTINUAR_DOWNLOAD = Event()
CONTINUAR_DOWNLOAD.set()

FFMPEG_CAMINHO = resolve_ffmpeg_path()
AUDIO_FORMATOS = {"mp3", "m4a", "wav", "flac"}
AUDIO_QUALIDADES = ["320kbps", "256kbps", "192kbps", "128kbps"]
VIDEO_QUALIDADES = ["Melhor qualidade", "1080p", "720p", "480p"]

def parar_download():
    if not DOWNLOAD_EM_PROGRESSO:
        return

    CANCELAR_DOWNLOAD.set()
    CONTINUAR_DOWNLOAD.set()
    texto_status.config(text="🛑 Interrompendo...")
    btn_parar.config(state="disabled")
    btn_pausar.config(state="disabled")


def alternar_pausa_download():
    if not DOWNLOAD_EM_PROGRESSO:
        return

    if CONTINUAR_DOWNLOAD.is_set():
        CONTINUAR_DOWNLOAD.clear()
        btn_pausar.config(text="▶ RETOMAR")
        texto_status.config(text="⏸ Pausando...")
    else:
        CONTINUAR_DOWNLOAD.set()
        btn_pausar.config(text="⏸ PAUSAR")
        texto_status.config(text="⏳ Retomando...")


def baixar_thread(request, cancel_event, continue_event, event_queue):
    try:
        def progress_hook(d):
            if cancel_event.is_set():
                raise DownloadCancelled("Download interrompido pelo usuário")

            if not continue_event.is_set():
                event_queue.put(("paused", None))
                continue_event.wait()
                if cancel_event.is_set():
                    raise DownloadCancelled("Download interrompido pelo usuário")
                event_queue.put(("resumed", None))

            if d['status'] == 'downloading':
                percentual = d.get('_percent_str', 'N/A')
                velocidade = d.get('_speed_str', 'N/A')
                event_queue.put(("progress", f"⏳ Baixando... {percentual} - {velocidade}"))
            elif d['status'] == 'finished':
                event_queue.put(("progress", "📦 Finalizando e convertendo..."))

        run_download(request, FFMPEG_CAMINHO, progress_hook)
        event_queue.put(("success", f"✅ Pronto! Salvo em:\n{request.output_dir}"))

    except DownloadCancelled:
        event_queue.put(("cancelled", "🛑 Download interrompido!"))
    except DownloadValidationError as e:
        event_queue.put(("validation_error", str(e)))
    except OSError as e:
        event_queue.put(("os_error", str(e)))
    except Exception as e:
        event_queue.put(("download_error", str(e)))
    finally:
        event_queue.put(("complete", None))


def processar_eventos_download():
    global DOWNLOAD_EM_PROGRESSO

    while True:
        try:
            event, value = EVENTOS_DOWNLOAD.get_nowait()
        except Empty:
            break

        if event == "progress":
            texto_status.config(text=value)
        elif event == "success":
            texto_status.config(text=value)
            messagebox.showinfo("Sucesso", "Download finalizado com sucesso!")
        elif event == "cancelled":
            texto_status.config(text=value)
        elif event == "paused":
            texto_status.config(text="⏸ Download pausado. Clique em Retomar para continuar.")
        elif event == "resumed":
            texto_status.config(text="⏳ Retomando download...")
        elif event == "validation_error":
            texto_status.config(text="⚠️ Verifique os dados informados")
            messagebox.showwarning("Aviso", value)
        elif event == "os_error":
            texto_status.config(text="❌ Erro ao acessar a pasta de destino")
            messagebox.showerror(
                "Erro",
                f"Não foi possível preparar a pasta de destino:\n{value}",
            )
        elif event == "download_error":
            texto_status.config(text="❌ Erro ao baixar")
            messagebox.showerror("Erro", f"Detalhes:\n{value}")
        elif event == "complete":
            janela.config(cursor="")
            btn_baixar.config(state="normal")
            btn_pausar.config(state="disabled", text="⏸ PAUSAR")
            btn_parar.config(state="disabled")
            CONTINUAR_DOWNLOAD.set()
            DOWNLOAD_EM_PROGRESSO = False

    janela.after(100, processar_eventos_download)


def baixar():
    """Inicia o download em uma thread separada"""
    global DOWNLOAD_EM_PROGRESSO

    if DOWNLOAD_EM_PROGRESSO:
        messagebox.showwarning("Aviso", "Já existe um download em andamento.")
        return

    request = DownloadRequest(
        url=entrada_link.get().strip(),
        output_dir=PASTA_SAIDA,
        media_format=escolha_formato.get(),
        quality=escolha_qualidade.get(),
        custom_name=entrada_nome.get().strip(),
    )

    DOWNLOAD_EM_PROGRESSO = True
    CANCELAR_DOWNLOAD.clear()
    CONTINUAR_DOWNLOAD.set()
    janela.config(cursor="wait")
    texto_status.config(text="⏳ Baixando e convertendo... Aguarde!")
    btn_baixar.config(state="disabled")
    btn_pausar.config(state="normal", text="⏸ PAUSAR")
    btn_parar.config(state="normal")

    thread = Thread(
        target=baixar_thread,
        args=(request, CANCELAR_DOWNLOAD, CONTINUAR_DOWNLOAD, EVENTOS_DOWNLOAD),
        daemon=True,
    )
    thread.start()


def escolher_pasta():
    global PASTA_SAIDA
    pasta_escolhida = filedialog.askdirectory(title="Escolher pasta para salvar os arquivos")
    if pasta_escolhida:
        PASTA_SAIDA = pasta_escolhida
        texto_caminho.config(text=f"📂 Salvar em: {PASTA_SAIDA}")


def abrir_pasta_destino():
    try:
        os.startfile(PASTA_SAIDA)
    except OSError as e:
        messagebox.showerror(
            "Erro",
            f"Não foi possível abrir a pasta de destino:\n{e}",
        )


def main():
    global btn_baixar, btn_pausar, btn_parar, escolha_formato, escolha_qualidade
    global entrada_link, entrada_nome, janela, texto_caminho, texto_status

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

    btn_abrir_pasta = ttk.Button(
        frame_pasta,
        text="📂 Abrir pasta de destino",
        command=abrir_pasta_destino,
    )
    btn_abrir_pasta.pack(side="left", padx=5)

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

    btn_pausar = ttk.Button(
        frame_botoes,
        text="⏸ PAUSAR",
        command=alternar_pausa_download,
        state="disabled",
    )
    btn_pausar.pack(side="left", padx=10, ipadx=12, ipady=6)

    btn_parar = ttk.Button(frame_botoes, text="🛑 PARAR", command=parar_download, state="disabled")
    btn_parar.pack(side="left", padx=10, ipadx=12, ipady=6)

    # Status
    texto_status = ttk.Label(janela, text="Aguardando...", foreground="#555555", font=("Arial", 10))
    texto_status.pack(pady=10)

    janela.after(100, processar_eventos_download)
    janela.mainloop()


if __name__ == "__main__":
    main()
