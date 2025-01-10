import os
import tempfile
import chardet
from deep_translator import GoogleTranslator
from tkinter import filedialog, messagebox
import sys
from colorama import Fore, Back, Style, init

# Inicializa o colorama para suportar diferentes terminais
init(autoreset=True)

def exibir_boas_vindas():
    mensagem = r'''
  ____   ____ _   _ 
 |  _ \ / ___| \ | |
 | |_) | |  _|  \| |
 |  __/| |_| | |\  |
 |_|    \____|_| \_|
                    
'''
    print(Fore.CYAN + mensagem)  # Cor azul para a arte
    print(Fore.YELLOW + "Bem-vindo ao PGN Translator!\n")  # Cor amarela

SUBSTITUICOES_GERAIS = {
    "Evento": "Event",
    "Rodada": "Round",
    "Branco": "White",
    "Brancas": "White",
    "Preto": "Black",
    "Pretas": "Black",
    "Resultado": "Result",
    "Local": "Site",
    "ECO": "ECO",
    "FEN": "FEN",
    "Contagem de camadas": "PlyCount",
    "Contagem de Jogadas": "PlyCount",
    "Contagem de jogadas": "PlyCount",
    "Anotador": "Annotator",
    "Data": "Date",
    "Fonte": "Source",
    "OO": "O-O",
    "Configuração": "SetUp",
}

SUBSTITUICOES_ESPECIFICAS = {
    "Date do evento": "EventDate",
    "Date da fonte": "SourceDate",
    "Date de origem": "OriginDate",
    "Date da Source": "SourceDate",
    "Date do Event": "EventDate",
    "Date da Origem": "OriginDate",
}

piece_mapping = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"
}

simbolos_xadrez = {
    "♔": "K",  # Rei
    "♕": "Q",  # Dama
    "♖": "R",  # Torre
    "♗": "B",  # Bispo
    "♘": "N",  # Cavalo
    "♙": "P"   # Peão
}

def processar_pasta():
    def selecionar_pasta_origem():
        pasta = filedialog.askdirectory(
            title="Selecione a pasta contendo os arquivos"
        )
        return pasta

    def selecionar_pasta_saida():
        pasta = filedialog.askdirectory(
            title="Selecione a pasta onde os arquivos traduzidos serão salvos"
        )
        return pasta

    def salvar_arquivo_final(conteudo, pasta_saida, nome_base, extensao, pasta_relativa):
        # Cria as subpastas dentro da pasta de saída, mantendo a estrutura de subpastas
        pasta_destino = os.path.join(pasta_saida, pasta_relativa)
        os.makedirs(pasta_destino, exist_ok=True)  # Cria a subpasta, se não existir
        caminho_saida = os.path.join(pasta_destino, f"{nome_base}-BR{extensao}")
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return caminho_saida

    def buscar_arquivos(pasta, extensoes=(".pgn", ".txt")):
        arquivos_encontrados = []
        for root, _, files in os.walk(pasta):  # Percorrendo recursivamente as subpastas
            for file in files:
                if file.lower().endswith(extensoes):
                    arquivos_encontrados.append(os.path.join(root, file))
        return arquivos_encontrados

    def ler_arquivo(caminho):
        with open(caminho, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            file_encoding = result['encoding']
        with open(caminho, 'r', encoding=file_encoding) as f:
            return f.read()

    def traduzir(conteudo, source_lang='auto', target_lang='pt', max_chars=4000):
        chunks = [conteudo[i:i + max_chars] for i in range(0, len(conteudo), max_chars)]
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = ""
        for idx, chunk in enumerate(chunks):
            progresso = f"Traduzindo bloco {idx + 1}/{len(chunks)}..."
            sys.stdout.write(f"\r{Fore.GREEN + progresso}")  # Mensagem de progresso em verde
            sys.stdout.flush()
            translated += translator.translate(chunk) + "\n"
        sys.stdout.write("\n")
        return translated

    def substituir(conteudo, substituicoes):
        for original, nova in substituicoes.items():
            conteudo = conteudo.replace(original, nova)
        return conteudo

    def atualizar_progresso_geral(atual, total):
        progresso = f"Progresso Geral: {atual}/{total} arquivos processados."
        sys.stdout.write(f"\r{Fore.MAGENTA + progresso}")  # Mensagem de progresso geral em amarelo
        sys.stdout.flush()

    exibir_boas_vindas()

    pasta_origem = selecionar_pasta_origem()
    if not pasta_origem:
        messagebox.showerror(Fore.RED + "Erro", "Nenhuma pasta selecionada.")
        return

    pasta_saida = selecionar_pasta_saida()
    if not pasta_saida:
        messagebox.showerror(Fore.RED + "Erro", "Nenhuma pasta de saída selecionada.")
        return

    arquivos = buscar_arquivos(pasta_origem)
    if not arquivos:
        messagebox.showinfo(Fore.CYAN + "Aviso", "Nenhum arquivo .pgn ou .txt encontrado na pasta selecionada.")
        return

    total_arquivos = len(arquivos)

    for idx, arquivo in enumerate(arquivos, start=1):
        print(f"\n{Fore.CYAN + 'Processando arquivo'} {idx}/{total_arquivos}: {arquivo}")
        try:
            extensao = os.path.splitext(arquivo)[1].lower()
            nome_base = os.path.splitext(os.path.basename(arquivo))[0]

            # Obtendo a estrutura de subpasta dentro da pasta de origem
            pasta_relativa = os.path.relpath(os.path.dirname(arquivo), pasta_origem)

            print(f"{Fore.YELLOW}[1/6] Lendo arquivo inicial...")
            conteudo = ler_arquivo(arquivo)

            print(f"{Fore.YELLOW}[2/6] Convertendo letras para símbolos...")
            for letra, simbolo in piece_mapping.items():
                conteudo = conteudo.replace(letra, simbolo)

            print(f"{Fore.YELLOW}[3/6] Traduzindo conteúdo...")
            conteudo = traduzir(conteudo)

            print(f"{Fore.YELLOW}[4/6] Aplicando substituições gerais...")
            conteudo = substituir(conteudo, SUBSTITUICOES_GERAIS)

            print(f"{Fore.YELLOW}[5/6] Aplicando substituições específicas...")
            conteudo = substituir(conteudo, SUBSTITUICOES_ESPECIFICAS)

            print(f"{Fore.YELLOW}[6/6] Convertendo símbolos para letras...")
            for simbolo, letra in simbolos_xadrez.items():
                conteudo = conteudo.replace(simbolo, letra)

            print(f"{Fore.GREEN}Salvando resultado final...")
            salvar_arquivo_final(conteudo, pasta_saida, nome_base, extensao, pasta_relativa)
        except Exception as e:
            print(f"{Fore.RED}Erro ao processar o arquivo {arquivo}: {e}")
        
        atualizar_progresso_geral(idx, total_arquivos)

    print(f"\n{Fore.GREEN}Todos os arquivos foram processados com sucesso.")
    messagebox.showinfo(Fore.GREEN + "Concluído", "Todos os arquivos foram processados com sucesso!")
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    processar_pasta()
