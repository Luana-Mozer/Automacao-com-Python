import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

# keyboard -> captura os atalhos Ctrl+P e Ctrl+I
# pandas -> le a planilha produtos.csv
# pyautogui -> controla mouse e teclado para fazer a automacao
import keyboard
import pandas as pd
import pyautogui


# pyautogui.write -> escrever um texto
# pyautogui.press -> apertar 1 tecla
# pyautogui.click -> clicar em algum lugar da tela
# pyautogui.hotkey -> combinacao de teclas

# tempo de espera automatico entre cada comando do pyautogui
pyautogui.PAUSE = 0.4

# dados usados no login
URL_LOGIN = "https://dlp.hashtagtreinamentos.com/python/intensivao/login"
EMAIL = "luanamozerengenhariadigital@gmail.com"
SENHA = "sua senha"

# executando -> indica se a automacao esta rodando
# pausa_evento -> controla quando a automacao deve pausar
# parar_evento -> controla quando a automacao deve interromper
# thread_automacao -> guarda a automacao rodando em segundo plano
executando = False
pausa_evento = threading.Event()
parar_evento = threading.Event()
thread_automacao = None


def caminho_arquivo(nome_arquivo):
    # quando o programa vira .exe, os arquivos ficam em outro lugar temporario
    if getattr(sys, "frozen", False):
        # primeiro tenta achar o arquivo ao lado do .exe
        arquivo_ao_lado_do_exe = Path(sys.executable).resolve().parent / nome_arquivo
        if arquivo_ao_lado_do_exe.exists():
            return arquivo_ao_lado_do_exe

        # se nao achar ao lado do .exe, usa o arquivo que foi embutido no executavel
        return Path(sys._MEIPASS) / nome_arquivo

    # quando roda pelo Python normal, procura na mesma pasta do Automacao.py
    return Path(__file__).resolve().parent / nome_arquivo


def atualizar_status(texto):
    # atualiza o texto de status na janela
    # janela.after evita erro quando a automacao esta rodando em outra thread
    janela.after(0, lambda: status_var.set(texto))


def atualizar_botoes():
    # enquanto estiver executando, desativa o Play e libera Pausar/Interromper
    if executando:
        botao_play.config(state="disabled")
        botao_pausar.config(state="normal")
        botao_interromper.config(state="normal")
    else:
        # quando nao estiver executando, libera Play e bloqueia os outros botoes
        botao_play.config(state="normal")
        botao_pausar.config(state="disabled", text="Pausar")
        botao_interromper.config(state="disabled")


def verificar_controle():
    # se estiver pausado, fica parado aqui ate continuar ou interromper
    while pausa_evento.is_set() and not parar_evento.is_set():
        time.sleep(0.2)

    # se o usuario pediu para interromper, encerra a automacao
    if parar_evento.is_set():
        raise SystemExit


def esperar(segundos):
    # espera alguns segundos, mas continua verificando pausa/interrupcao
    fim = time.time() + segundos
    while time.time() < fim:
        verificar_controle()
        time.sleep(0.1)


def executar(acao, *args, **kwargs):
    # executa uma acao do pyautogui com verificacao antes e depois
    verificar_controle()
    resultado = acao(*args, **kwargs)
    verificar_controle()
    return resultado


def rodar_automacao():
    # usa a variavel global para avisar quando a automacao terminar
    global executando

    try:
        atualizar_status("Abrindo navegador...")

        # Passo 1: Abrir o navegador e entrar no site
        executar(pyautogui.press, "win")
        executar(pyautogui.write, "edge")
        esperar(3)
        executar(pyautogui.press, "enter")

        executar(pyautogui.write, URL_LOGIN)
        executar(pyautogui.press, "enter")
        esperar(3)

        atualizar_status("Fazendo login...")

        # Passo 2: Fazer login
        executar(pyautogui.click, x=683, y=372)
        executar(pyautogui.write, EMAIL)
        executar(pyautogui.press, "tab")
        executar(pyautogui.write, SENHA)
        executar(pyautogui.press, "tab")
        executar(pyautogui.press, "enter")
        esperar(3)

        atualizar_status("Lendo produtos.csv...")

        # Passo 3: Importar a base de produtos
        tabela = pd.read_csv(caminho_arquivo("produtos.csv"))

        # Passo 4: Cadastrar os produtos
        for linha in tabela.index:
            # mostra na janela qual produto esta sendo cadastrado
            atualizar_status(f"Cadastrando produto {linha + 1} de {len(tabela)}...")

            # clica no primeiro campo do formulario
            executar(pyautogui.click, x=557, y=249)

            # preenche codigo e passa para o proximo campo
            executar(pyautogui.write, str(tabela.loc[linha, "codigo"]))
            executar(pyautogui.press, "tab")

            # preenche marca e passa para o proximo campo
            executar(pyautogui.write, str(tabela.loc[linha, "marca"]))
            executar(pyautogui.press, "tab")

            # preenche tipo e passa para o proximo campo
            executar(pyautogui.write, str(tabela.loc[linha, "tipo"]))
            executar(pyautogui.press, "tab")

            # preenche categoria e passa para o proximo campo
            executar(pyautogui.write, str(tabela.loc[linha, "categoria"]))
            executar(pyautogui.press, "tab")

            # preenche preco unitario e passa para o proximo campo
            executar(pyautogui.write, str(tabela.loc[linha, "preco_unitario"]))
            executar(pyautogui.press, "tab")

            # preenche custo e passa para o proximo campo
            executar(pyautogui.write, str(tabela.loc[linha, "custo"]))
            executar(pyautogui.press, "tab")

            # preenche observacao somente se existir alguma observacao
            obs = tabela.loc[linha, "obs"]
            if not pd.isna(obs):
                executar(pyautogui.write, str(obs))

            # envia o cadastro do produto e volta a tela para o topo
            executar(pyautogui.press, "tab")
            executar(pyautogui.press, "enter")
            executar(pyautogui.scroll, 5000)

        atualizar_status("Automacao finalizada.")
    except SystemExit:
        # acontece quando o usuario clica em Interromper ou aperta Ctrl+I
        atualizar_status("Automacao interrompida.")
    except Exception as erro:
        # mostra uma janela de erro se algo inesperado acontecer
        mensagem_erro = str(erro)
        atualizar_status("Erro na automacao.")
        janela.after(0, lambda: messagebox.showerror("Erro", mensagem_erro))
    finally:
        # sempre limpa os controles e volta os botoes ao estado inicial
        executando = False
        pausa_evento.clear()
        parar_evento.clear()
        janela.after(0, atualizar_botoes)


def iniciar_automacao():
    # inicia a automacao quando clicar em Play
    global executando, thread_automacao

    # se ja estiver rodando, nao inicia outra automacao por cima
    if executando:
        return

    # prepara os controles para uma nova execucao
    executando = True
    pausa_evento.clear()
    parar_evento.clear()
    atualizar_status("Iniciando automacao...")
    atualizar_botoes()

    # roda a automacao em segundo plano para a janela nao travar
    thread_automacao = threading.Thread(target=rodar_automacao, daemon=True)
    thread_automacao.start()


def pausar_ou_continuar():
    # pausa ou continua a automacao pelo botao Pausar/Continuar ou Ctrl+P
    if not executando:
        return

    # se ja esta pausado, continua
    if pausa_evento.is_set():
        pausa_evento.clear()
        botao_pausar.config(text="Pausar")
        atualizar_status("Automacao retomada.")
    else:
        # se esta rodando, pausa
        pausa_evento.set()
        botao_pausar.config(text="Continuar")
        atualizar_status("Automacao pausada.")


def interromper_automacao():
    # interrompe a automacao pelo botao Interromper ou Ctrl+I
    if not executando:
        return

    parar_evento.set()
    pausa_evento.clear()
    atualizar_status("Interrompendo automacao...")


def ao_fechar():
    # se fechar a janela enquanto estiver rodando, pede para a automacao parar
    if executando:
        parar_evento.set()

    # fecha a janela
    janela.destroy()


# cria a janela principal
janela = tk.Tk()
janela.title("Automacao de Produtos")
janela.geometry("360x190")
janela.resizable(False, False)

# variavel que guarda o texto de status mostrado na janela
status_var = tk.StringVar(value="Pronto para iniciar.")

# frame principal com espacamento interno
conteudo = tk.Frame(janela, padx=18, pady=18)
conteudo.pack(fill="both", expand=True)

# titulo da janela
titulo = tk.Label(conteudo, text="Automacao de Produtos", font=("Segoe UI", 14, "bold"))
titulo.pack(anchor="w")

# texto de status que muda durante a automacao
status = tk.Label(conteudo, textvariable=status_var, font=("Segoe UI", 10), anchor="w")
status.pack(fill="x", pady=(8, 16))

# frame que organiza os botoes lado a lado
botoes = tk.Frame(conteudo)
botoes.pack(fill="x")

# botao Play -> chama iniciar_automacao
botao_play = tk.Button(botoes, text="Play", width=12, command=iniciar_automacao)
botao_play.pack(side="left", padx=(0, 8))

# botao Pausar -> chama pausar_ou_continuar
botao_pausar = tk.Button(botoes, text="Pausar", width=12, command=pausar_ou_continuar, state="disabled")
botao_pausar.pack(side="left", padx=(0, 8))

# botao Interromper -> chama interromper_automacao
botao_interromper = tk.Button(
    botoes,
    text="Interromper",
    width=12,
    command=interromper_automacao,
    state="disabled",
)
botao_interromper.pack(side="left")

# texto pequeno mostrando os atalhos
atalhos = tk.Label(
    conteudo,
    text="Atalhos: Ctrl+P pausa/continua | Ctrl+I interrompe",
    font=("Segoe UI", 8),
)
atalhos.pack(anchor="w", pady=(18, 0))

# atalhos do teclado
# Ctrl+P -> pausa ou continua
# Ctrl+I -> interrompe
keyboard.add_hotkey("ctrl+p", lambda: janela.after(0, pausar_ou_continuar))
keyboard.add_hotkey("ctrl+i", lambda: janela.after(0, interromper_automacao))

# quando clicar no X da janela, chama ao_fechar
janela.protocol("WM_DELETE_WINDOW", ao_fechar)

# mantem a janela aberta
janela.mainloop()
