import os
import time
import multiprocessing

# ===============================
# Funções de Apoio (Originais)
# ===============================

def consolidar_resultados(resultados):
    resumo = {"linhas": 0, "palavras": 0, "caracteres": 0, 
              "contagem": {"erro": 0, "warning": 0, "info": 0}}
    for r in resultados:
        resumo["linhas"] += r["linhas"]
        resumo["palavras"] += r["palavras"]
        resumo["caracteres"] += r["caracteres"]
        for chave in resumo["contagem"]:
            resumo["contagem"][chave] += r["contagem"][chave]
    return resumo

def processar_arquivo(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.readlines()
    
    res = {"linhas": len(conteudo), "palavras": 0, "caracteres": 0, 
           "contagem": {"erro": 0, "warning": 0, "info": 0}}
    
    for linha in conteudo:
        palavras = linha.split()
        res["palavras"] += len(palavras)
        res["caracteres"] += len(linha)
        for p in palavras:
            if p in res["contagem"]:
                res["contagem"][p] += 1
        for _ in range(1000): # Simulação de carga
            pass
    return res

# =======================================
# Lógica do Produtor-Consumidor (Paralela)
# =======================================

def trabalhador(fila_arquivos, fila_resultados):
    """Consumidor: Processa arquivos da fila até receber None."""
    while True:
        caminho = fila_arquivos.get()
        if caminho is None: 
            break
        resultado = processar_arquivo(caminho)
        fila_resultados.put(resultado)

def executar_paralelo(pasta, num_processos):
    arquivos = [os.path.join(pasta, f) for f in os.listdir(pasta) 
                if os.path.isfile(os.path.join(pasta, f))]
    
    # Buffer limitado (maxsize=50) conforme o problema pede
    fila_arquivos = multiprocessing.Queue(maxsize=50)
    fila_resultados = multiprocessing.Queue()

    # Inicialização dos Consumidores
    processos = []
    for _ in range(num_processos):
        p = multiprocessing.Process(target=trabalhador, args=(fila_arquivos, fila_resultados))
        p.start()
        processos.append(p)

    inicio = time.time()

    # Produtor: Alimenta a fila
    for caminho in arquivos:
        fila_arquivos.put(caminho)

    # Finalização: Envia sinal de parada (None) para cada processo
    for _ in range(num_processos):
        fila_arquivos.put(None)

    # Coleta e Consolidação
    resultados_finais = [fila_resultados.get() for _ in range(len(arquivos))]
    
    for p in processos:
        p.join()

    fim = time.time()
    resumo = consolidar_resultados(resultados_finais)
    
    print(f"\n--- RESULTADO ({num_processos} PROCESSOS) ---")
    print(f"Tempo: {fim - inicio:.4f}s | Linhas: {resumo['linhas']} | Erros: {resumo['contagem']['erro']}")
    return fim - inicio

# ===============================
# Experimento
# ===============================

if __name__ == "__main__":
    diretorio = "unieuro-concorrente-202601-atividade3/log2" # Certifique-se que esta pasta existe
    
    if os.path.exists(diretorio):
        for n in [1, 2, 4, 8, 12]:
            executar_paralelo(diretorio, n)
    else:
        print(f"Pasta {diretorio} não encontrada.")
