import tkinter as tk
from tkinter import ttk, filedialog

# =====================================================================
# Variáveis de controle
# =====================================================================
arquivos_carregados = {"estacoes": False, "linhas": False}

def verificar_prontidao():
    # função que so acende o botão de executar se tiver o arquivo carregado
    if arquivos_carregados["estacoes"] and arquivos_carregados["linhas"]:
        btn_executar.config(state="normal")

def carregar_arquivo_estacoes():
    #função para carregar arquivo localmente
    caminho = filedialog.askopenfilename(title="Selecione o ficheiro de Estações")
    if caminho:
        arquivos_carregados["estacoes"] = True
        lbl_status_estacoes.config(text="Estações: OK", fg="green")
        verificar_prontidao()

def carregar_arquivo_linhas():
    caminho = filedialog.askopenfilename(title="Selecione o ficheiro de Linhas")
    if caminho:
        arquivos_carregados["linhas"] = True
        lbl_status_linhas.config(text="Linhas: OK", fg="green")
        verificar_prontidao()

def executar_algoritmo():
    problema = combo_problema.get()
    algoritmo = var_algoritmo.get()
    
    # Atualiza a área de resultados na parte inferior do cartão direito
    lbl_resultado_texto.config(text=f"Estações visitadas: Simulação do {problema}\nTempo de execução: -- (Simulado usando {algoritmo})")
    
    # Atualiza o mapa
    canvas_mapa.delete("all")
    canvas_mapa.create_text(250, 150, text="Desenho do trajeto aparecerá aqui", fill="gray", font=("Arial", 12))

# =====================================================================
# Construção da Janela (O Ecrã Principal)
# =====================================================================
janela = tk.Tk()
janela.title("Metrô de Paris")
janela.geometry("900x600")
janela.configure(bg="#f8f9fa") # Uma cor de fundo ligeiramente cinzenta para dar contraste

# --- Cabeçalho Superior ---
frame_cabecalho = tk.Frame(janela, bg="#f8f9fa")
frame_cabecalho.pack(fill="x", padx=20, pady=15)
tk.Label(frame_cabecalho, text=" Metrô de Paris — Análise de Algoritmos", font=("Arial", 16, "bold"), bg="#f8f9fa").pack(side="left")

# Linha de separação debaixodo título
ttk.Separator(janela, orient="horizontal").pack(fill="x")

# --- Estrutura Principal: Duas Colunas ---
# Uma caixa principal para segurar o lado esquerdo e o direito
frame_principal = tk.Frame(janela, bg="#f8f9fa")
frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

# =====================================================================
# Coluna Esquerda: Barra Lateral de Controlos
# =====================================================================
frame_lateral = tk.Frame(frame_principal, bg="#f8f9fa", width=250)
frame_lateral.pack(side="left", fill="y", padx=(0, 20))

# 1. Secção de Ficheiros
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

# 2. Secção de Problema
tk.Label(frame_lateral, text="Problema", font=("Arial", 11, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(0, 10))
combo_problema = ttk.Combobox(frame_lateral, values=["A — Maior percurso", "B — Instalação de guichês", "C — Períodos de manutenção"], state="readonly")
combo_problema.current(0)
combo_problema.pack(fill="x", pady=(0, 15))

# 3. Secção de Algoritmo (usando botões de opção redondos)
tk.Label(frame_lateral, text="Algoritmo", font=("Arial", 11, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(0, 10))
var_algoritmo = tk.StringVar(value="Força bruta") # Guarda a escolha feita
tk.Radiobutton(frame_lateral, text="Força bruta", variable=var_algoritmo, value="Força bruta", bg="#f8f9fa").pack(anchor="w")
tk.Radiobutton(frame_lateral, text="Branch-and-bound", variable=var_algoritmo, value="Branch-and-bound", bg="#f8f9fa").pack(anchor="w")
tk.Radiobutton(frame_lateral, text="Heurística", variable=var_algoritmo, value="Heurística", bg="#f8f9fa").pack(anchor="w", pady=(0, 20))

# 4. Botão de Executar
btn_executar = tk.Button(frame_lateral, text="Executar algoritmo", state="disabled", command=executar_algoritmo, bg="#e9ecef", relief="ridge", pady=8, font=("Arial", 10, "bold"))
btn_executar.pack(fill="x", side="bottom", pady=10)

# =====================================================================
# Coluna Direita: O Quadro do Mapa e Resultados
# =====================================================================
# fundo branco com borda 
frame_cartao = tk.Frame(frame_principal, bg="white", bd=1, relief="solid")
frame_cartao.pack(side="left", fill="both", expand=True)

# Título do mapa
tk.Label(frame_cartao, text="Mapa do metrô", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=15)

# A tela de desenho
canvas_mapa = tk.Canvas(frame_cartao, bg="white", highlightthickness=0)
canvas_mapa.pack(fill="both", expand=True, padx=20)
canvas_mapa.create_text(250, 150, text="(O desenho do grafo aparecerá aqui)", fill="gray", font=("Arial", 12))

# Linha que separa o mapa da zona de resultados
ttk.Separator(frame_cartao, orient="horizontal").pack(fill="x", padx=20, pady=10)

# Zona de Resultados na parte inferior do cartão
frame_resultado = tk.Frame(frame_cartao, bg="white")
frame_resultado.pack(fill="x", padx=20, pady=(0, 20))

tk.Label(frame_resultado, text="Resultado", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", pady=(0, 5))
lbl_resultado_texto = tk.Label(frame_resultado, text="Estações visitadas: —\nTempo de execução: —", bg="white", justify="left")
lbl_resultado_texto.pack(anchor="w")

# para iniciar a janela
janela.mainloop()