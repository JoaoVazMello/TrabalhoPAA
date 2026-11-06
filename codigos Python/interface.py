import tkinter as tk
from tkinter import ttk, filedialog
import csv

# =====================================================================
# Variáveis de controlo e Dados
# =====================================================================
arquivos_carregados = {"estacoes": False, "linhas": False}
dados_estacoes = {}
dados_linhas = []

mapa_cores = {"Azul": "#0052cc", "Verde": "#00875a", "Amarela": "#ffc400", "Vermelha": "#de350b"}

def verificar_prontidao():
    if arquivos_carregados["estacoes"] and arquivos_carregados["linhas"]:
        btn_executar.config(state="normal")
        desenhar_mapa()

def carregar_arquivo_estacoes():
    caminho = filedialog.askopenfilename(title="Selecione o ficheiro de Estações")
    if caminho:
        dados_estacoes.clear()
        with open(caminho, mode='r', encoding='utf-8') as f:
            leitor = csv.reader(f)
            next(leitor)
            for linha in leitor:
                if len(linha) >= 4:
                    dados_estacoes[int(linha[0])] = {"nome": linha[1], "x": int(linha[2]), "y": int(linha[3])}
        arquivos_carregados["estacoes"] = True
        lbl_status_estacoes.config(text="Estações: Lidas com sucesso", fg="green")
        verificar_prontidao()

def carregar_arquivo_linhas():
    caminho = filedialog.askopenfilename(title="Selecione o ficheiro de Linhas")
    if caminho:
        dados_linhas.clear()
        with open(caminho, mode='r', encoding='utf-8') as f:
            leitor = csv.reader(f)
            next(leitor)
            for linha in leitor:
                if len(linha) >= 3:
                    dados_linhas.append({"origem": int(linha[0]), "destino": int(linha[1]), "cor": linha[2]})
        arquivos_carregados["linhas"] = True
        lbl_status_linhas.config(text="Linhas: Lidas com sucesso", fg="green")
        verificar_prontidao()

def desenhar_mapa():
    canvas_mapa.delete("all")
    
    # Desenha as linhas normais
    for linha in dados_linhas:
        origem = dados_estacoes.get(linha["origem"])
        destino = dados_estacoes.get(linha["destino"])
        if origem and destino:
            cor_tk = mapa_cores.get(linha["cor"], "black")
            canvas_mapa.create_line(origem["x"], origem["y"], destino["x"], destino["y"], fill=cor_tk, width=4)

    # Desenha as estações normais
    raio = 14
    for id_est, info in dados_estacoes.items():
        x, y = info["x"], info["y"]
        canvas_mapa.create_oval(x - raio, y - raio, x + raio, y + raio, fill="white", outline="#333", width=2)
        letra_estacao = info["nome"].split()[-1]
        canvas_mapa.create_text(x, y, text=letra_estacao, font=("Arial", 9, "bold"), fill="#333")
    
    canvas_mapa.config(scrollregion=canvas_mapa.bbox("all"))


# =====================================================================
#DESTACAR O RESULTADO NO GRAFO
# =====================================================================
def destacar_resultado_no_grafo(caminho_ids):
    # Primeiro redesenhamos o mapa limpo para apagar testes anteriores
    desenhar_mapa()
    
    # Destacar as linhas por onde o algoritmo passou
    for i in range(len(caminho_ids) - 1):
        id_origem = caminho_ids[i]
        id_destino = caminho_ids[i+1]
        
        origem = dados_estacoes.get(id_origem)
        destino = dados_estacoes.get(id_destino)
        
        if origem and destino:
            # Desenha uma linha grossa por cima (ex: roxo para destacar)
            canvas_mapa.create_line(origem["x"], origem["y"], destino["x"], destino["y"], fill="#9b59b6", width=8)

    #  Destacar as estações por onde o algoritmo passou
    raio = 16
    for id_est in caminho_ids:
        info = dados_estacoes.get(id_est)
        if info:
            x, y = info["x"], info["y"]
            # Estação destacada em amarelo com borda vermelha
            canvas_mapa.create_oval(x - raio, y - raio, x + raio, y + raio, fill="#ffeaa7", outline="#d63031", width=3)
            letra_estacao = info["nome"].split()[-1]
            canvas_mapa.create_text(x, y, text=letra_estacao, font=("Arial", 10, "bold"), fill="#2d3436")

# =====================================================================
# INTEGRAÇÃO COM OS ALGORITMOS 
# =====================================================================
def executar_algoritmo():
    problema = combo_problema.get()
    algoritmo = var_algoritmo.get()
    
    resultado_texto = ""
    caminho_visitado = []
    
    if algoritmo == "Força bruta":
        resultado_texto, caminho_visitado = simular_teste_unico(problema, algoritmo)
    elif algoritmo == "Branch-and-bound":
        resultado_texto, caminho_visitado = simular_teste_unico(problema, algoritmo)
    elif algoritmo == "Heurística":
        resultado_texto, caminho_visitado = simular_teste_unico(problema, algoritmo)
        
    # Atualiza o texto na interface
    lbl_resultado_texto.config(text=resultado_texto)
    
    # CHAMA A FUNÇÃO QUE DESENHA O DESTAQUE NO GRAFO
    if caminho_visitado:
        destacar_resultado_no_grafo(caminho_visitado)
    
    canvas_mapa.create_text(250, 30, text="✨ Grafo atualizado com o trajeto!", fill="green", font=("Arial", 12, "bold"))


def simular_teste_unico(problema, algoritmo):
    # Agora a simulação devolve o texto E uma lista de IDs [1, 2, 5, 3] que correspondem a A -> B -> E -> C
    texto = f"Situação: Simulação para testes de Interface\nAlgoritmo: {algoritmo} | Problema: {problema}\nEstações visitadas: A -> B -> E -> C\nTempo de execução: 0.05 segundos"
    ids_visitados = [1, 2, 5, 3] # Baseado nos IDs do ficheiro estacoes.csv
    return texto, ids_visitados


# =====================================================================
# Construção da Janela
# =====================================================================
janela = tk.Tk()
janela.title("Metrô de Paris")
janela.geometry("900x600")
janela.configure(bg="#f8f9fa")

frame_cabecalho = tk.Frame(janela, bg="#f8f9fa")
frame_cabecalho.pack(fill="x", padx=20, pady=15)
tk.Label(frame_cabecalho, text=" Metrô de Paris — Análise de Algoritmos", font=("Arial", 16, "bold"), bg="#f8f9fa").pack(side="left")
ttk.Separator(janela, orient="horizontal").pack(fill="x")

frame_principal = tk.Frame(janela, bg="#f8f9fa")
frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

frame_lateral = tk.Frame(frame_principal, bg="#f8f9fa", width=250)
frame_lateral.pack(side="left", fill="y", padx=(0, 20))

tk.Label(frame_lateral, text="Ficheiros", font=("Arial", 11, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(0, 10))
btn_estacoes = tk.Button(frame_lateral, text="📂 Carregar Estações", command=carregar_arquivo_estacoes, bg="white", relief="ridge", pady=5)
btn_estacoes.pack(fill="x", pady=2)
lbl_status_estacoes = tk.Label(frame_lateral, text="Pendente", bg="#f8f9fa", font=("Arial", 9))
lbl_status_estacoes.pack(anchor="w", pady=(0, 5))

btn_linhas = tk.Button(frame_lateral, text="📂 Carregar Linhas", command=carregar_arquivo_linhas, bg="white", relief="ridge", pady=5)
btn_linhas.pack(fill="x", pady=2)
lbl_status_linhas = tk.Label(frame_lateral, text="Pendente", bg="#f8f9fa", font=("Arial", 9))
lbl_status_linhas.pack(anchor="w", pady=(0, 15))
ttk.Separator(frame_lateral, orient="horizontal").pack(fill="x", pady=10)

tk.Label(frame_lateral, text="Problema", font=("Arial", 11, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(0, 10))
combo_problema = ttk.Combobox(frame_lateral, values=["A — Maior percurso", "B — Instalação de guichês", "C — Períodos de manutenção"], state="readonly")
combo_problema.current(0)
combo_problema.pack(fill="x", pady=(0, 15))

tk.Label(frame_lateral, text="Algoritmo", font=("Arial", 11, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(0, 10))
var_algoritmo = tk.StringVar(value="Força bruta")
tk.Radiobutton(frame_lateral, text="Força bruta", variable=var_algoritmo, value="Força bruta", bg="#f8f9fa").pack(anchor="w")
tk.Radiobutton(frame_lateral, text="Branch-and-bound", variable=var_algoritmo, value="Branch-and-bound", bg="#f8f9fa").pack(anchor="w")
tk.Radiobutton(frame_lateral, text="Heurística", variable=var_algoritmo, value="Heurística", bg="#f8f9fa").pack(anchor="w", pady=(0, 20))

btn_executar = tk.Button(frame_lateral, text="Executar algoritmo", state="disabled", command=executar_algoritmo, bg="#e9ecef", relief="ridge", pady=8, font=("Arial", 10, "bold"))
btn_executar.pack(fill="x", side="bottom", pady=10)

frame_cartao = tk.Frame(frame_principal, bg="white", bd=1, relief="solid")
frame_cartao.pack(side="left", fill="both", expand=True)

tk.Label(frame_cartao, text="Mapa do metrô", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=15)

canvas_mapa = tk.Canvas(frame_cartao, bg="white", highlightthickness=0)
canvas_mapa.pack(fill="both", expand=True, padx=20)
canvas_mapa.create_text(250, 150, text="Carregue os arquivos para ver o mapa real.", fill="gray", font=("Arial", 12))

canvas_mapa.bind('<ButtonPress-1>', lambda event: canvas_mapa.scan_mark(event.x, event.y))
canvas_mapa.bind('<B1-Motion>', lambda event: canvas_mapa.scan_dragto(event.x, event.y, gain=1))

ttk.Separator(frame_cartao, orient="horizontal").pack(fill="x", padx=20, pady=10)

frame_resultado = tk.Frame(frame_cartao, bg="white")
frame_resultado.pack(fill="x", padx=20, pady=(0, 20))

tk.Label(frame_resultado, text="Resultado", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", pady=(0, 5))
lbl_resultado_texto = tk.Label(frame_resultado, text="Estações visitadas: —\nTempo de execução: —", bg="white", justify="left")
lbl_resultado_texto.pack(anchor="w")

janela.mainloop()
