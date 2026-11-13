import csv
import json
import math
import statistics
from time import perf_counter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font

# --- ESTRUTURAS DE DADOS E CONFIGURAÇÕES GLOBAIS ---
dados_estacoes, dados_linhas = {}, []
arquivos_carregados = {"estacoes": False, "linhas": False}
posicoes, caminho_destacado = {}, []
grafo = {}
zoom, ajustado = 1.0, True
regiao = (0, 0, 1, 1)

CORES = {
    "Azul": "#0052cc", "Verde": "#00875a", "Amarela": "#ffc400",
    "Vermelha": "#de350b", "Oliva": "#9f9825", "Rosa": "#c04191",
    "Verde-clara": "#83c491", "Verde-limao": "#b6bd00",
    "Marrom": "#8d5e2a", "Azul-clara": "#98d4e2", "Roxa": "#662483"
}

FUNDO, BRANCO, TEXTO, CINZA = "#F2F5FA", "white", "#16243A", "#65758D"
ESCURO, AZUL, ROXO, BORDA = "#142440", "#2962E2", "#8456D8", "#DCE4EF"

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# --- MÓDULO DE DADOS E ARQUIVOS ---
def carregar(tipo):
    arquivo = filedialog.askopenfilename(title=f"Carregar {tipo}", filetypes=[("CSV", "*.csv")])
    if not arquivo:
        return
    try:
        with open(arquivo, encoding="utf-8-sig", newline="") as f:
            linhas = list(csv.reader(f))[1:]
            
        if tipo == "estacoes":
            novos = {int(l[0]): {"nome": l[1], "x": int(l[2]), "y": int(l[3])} for l in linhas if len(l) >= 4}
            if not novos: raise ValueError("Não há estações válidas.")
            dados_estacoes.clear(); dados_estacoes.update(novos)
        else:
            novos = [{"origem": int(l[0]), "destino": int(l[1]), "cor": l[2]} for l in linhas if len(l) >= 3]
            if not novos: raise ValueError("Não há linhas válidas.")
            dados_linhas[:] = novos
            
    except (OSError, ValueError) as e:
        messagebox.showerror("Erro no CSV", str(e))
        return

    arquivos_carregados[tipo] = True
    status_label = status_e if tipo == "estacoes" else status_l
    status_label.config(text=f"Carregadas: {len(novos)}", fg="#16966C")

    if all(arquivos_carregados.values()):
        grafo.clear()
        grafo.update(construir_grafo())
        for b in (executar_btn, zoom_mais, zoom_menos, zoom_ajustar): 
            b.config(state="normal")
        caminho_destacado.clear()
        calcular_posicoes()
        ajustar_zoom()
        resumo.config(text=f"{len(dados_estacoes)} estações  •  {len(dados_linhas)} conexões")
        combo_inicial["values"] = sorted(dados_estacoes)
        if combo_inicial.get() not in [
            str(i) for i in dados_estacoes
        ]:
            combo_inicial.current(0)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# --- MÓDULO DE IMPLEMNTAÇAO E ALGORTIMOS NO GRAFO ---

## IMPLEMENTAÇAO DO GRAFO EM LISTA DE ADJACENCIA

def construir_grafo():
    grafo = {}

    for vertices in dados_estacoes:
        grafo[vertices] = set()

    for arestas in dados_linhas:
        grafo[arestas["origem"]].add(arestas["destino"])
        grafo[arestas["destino"]].add(arestas["origem"])
    
    return  {
        estacao: sorted(vizinhos)
        for estacao, vizinhos in grafo.items()
    }

## ------------------------------------------ RESOLUÇÂO DO PROBLEMA A ------------------------------------------

## Implementaçao força bruta
def forca_bruta(grafo, inicial):

    ## vetor auxiliar verificar se o vertice ja foi visitado
    visitados = {}
    
    ## vetor auxiliar para ver o caminho que foi percorrido
    caminho = [inicial]

    ## Dicionario para guardar melhor caminho
    melhor = {
        "maximo": 0,
        "caminho": []
    }

    ## preenchendo vetor todo com falso
    for vertice in grafo:
        visitados[vertice] = False

    ## igual a 1 pois ja conta a primeira estacao
    contador = 1
    ## ponto inicial
    raiz = inicial
    ## onde comecou
    atual = raiz
    ## ja colocando o inicial como visitado sempre
    visitados[atual] = True
    
    ## chama a funçao que vai fazer a recursao
    busca(atual, inicial, visitados, contador, grafo, caminho, melhor)
    
    return melhor

# Roda a busac efetivamente
def busca(atual, inicial, visitados, contador, grafo, caminho, melhor):
    # verifica o incial e vizinho do atual
    if(inicial in grafo[atual]):
        if(contador > melhor["maximo"] and contador > 2):
            ##salva o maximo obtido
            melhor["maximo"] = contador
            # Crie uma cópia de caminho
            copia = caminho.copy()
            # Adicione a estação inicial à cópia
            copia.append(inicial)
            # Guarde a cópia em melhor["caminho"]
            melhor["caminho"] = copia
              
    # verifica se ainda possuem vizinhos a serem explorados
    for vizinhos in grafo[atual]:
        if visitados[vizinhos] == False:
            visitados[vizinhos] = True
            caminho.append(vizinhos)
            busca(vizinhos, inicial, visitados, contador + 1, grafo, caminho, melhor)
            caminho.pop()
            visitados[vizinhos] = False

## Implementaçao Branch and Bound

def BranchAndBound(grafo, inicial):

    ## vetor auxiliar verificar se o vertice ja foi visitado
    visitados = {}
    
    ## vetor auxiliar para ver o caminho que foi percorrido
    caminho = [inicial]

    ## Dicionario para guardar melhor caminho
    melhor = {
        "maximo": 0,
        "caminho": []
    }

    ## preenchendo vetor todo com falso
    for vertice in grafo:
        visitados[vertice] = False

    ## igual a 1 pois ja conta a primeira estacao
    contador = 1
    ## ponto inicial
    raiz = inicial
    ## onde comecou
    atual = raiz
    ## ja colocando o inicial como visitado sempre
    visitados[atual] = True
    
    ## chama a funçao que vai fazer a recursao
    buscaBranchAndBound(atual, inicial, visitados, contador, grafo, caminho, melhor)
    
    return melhor

def buscaBranchAndBound(atual, inicial, visitados, contador, grafo, caminho, melhor):
    # verifica o incial e vizinho do atual
    if(inicial in grafo[atual]):
        if(contador > melhor["maximo"] and contador > 2):
            ##salva o maximo obtido
            melhor["maximo"] = contador
            # Crie uma cópia de caminho
            copia = caminho.copy()
            # Adicione a estação inicial à cópia
            copia.append(inicial)
            # Guarde a cópia em melhor["caminho"]
            melhor["caminho"] = copia
    
    # copia dos que ainda nao foram visitados
    explorados = visitados.copy()
    
    # Conta restante dos que ainda faltam para ser visitados
    restantes = ContarAlcancaveis(atual, explorados, grafo)
    
    # calcula o upperBound
    ub = contador + restantes
    
    # criterio de poda
    if melhor["maximo"] >= ub:
        return
    
    # verifica se ainda possuem vizinhos a serem explorados
    for vizinhos in grafo[atual]:
        if visitados[vizinhos] == False:
            visitados[vizinhos] = True
            caminho.append(vizinhos)
            buscaBranchAndBound(vizinhos, inicial, visitados, contador + 1, grafo, caminho, melhor)
            caminho.pop()
            visitados[vizinhos] = False


def ContarAlcancaveis(atual, explorados, grafo):
    restantes = 0
    
    for vizinhos in grafo[atual]:
        if explorados[vizinhos] == False:
            explorados[vizinhos] = True
            restantes = restantes + 1 + ContarAlcancaveis(vizinhos, explorados, grafo)
    
    return restantes


## ------------------------------------------ FIM RESOLUÇÂO DO PROBLEMA A ------------------------------------------


## coloquem as outras soluçoes aqui galerinha pra ficar organizadin

## ------------------------------------------ RESOLUÇÂO DO PROBLEMA B ------------------------------------------

## ------------------------------------------ FIM RESOLUÇÂO DO PROBLEMA B ------------------------------------------

## ------------------------------------------ RESOLUÇÂO DO PROBLEMA C ------------------------------------------

## ------------------------------------------ FIM RESOLUÇÂO DO PROBLEMA C ------------------------------------------


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# --- MÓDULO DE CÁLCULO DO GRAFO ---
def calcular_posicoes():
    """Comprime vazios e separa nós sem modificar as coordenadas dos CSVs."""
    def eixo(valores):
        v = sorted(set(valores))
        gaps = [b - a for a, b in zip(v, v[1:])]
        limite = 2.8 * statistics.median(gaps) if gaps else 1
        d = {v[0]: 0}
        for a, b in zip(v, v[1:]): d[b] = d[a] + min(b - a, limite)
        return d

    mx = eixo([e["x"] for e in dados_estacoes.values()])
    my = eixo([e["y"] for e in dados_estacoes.values()])
    p = {i: [mx[e["x"]], my[e["y"]]] for i, e in dados_estacoes.items()}
    
    arestas = {(l["origem"], l["destino"]) for l in dados_linhas 
               if l["origem"] in p and l["destino"] in p and l["origem"] != l["destino"]}
    dist = [math.dist(p[a], p[b]) for a, b in arestas if math.dist(p[a], p[b]) > 0]
    fator = 95 / max(1, statistics.median(dist) if dist else 1)
    
    for v in p.values(): 
        v[0], v[1] = v[0] * fator, v[1] * fator

    ids = sorted(p)
    for _ in range(30):
        for a, b in arestas:
            dx, dy = p[b][0] - p[a][0], p[b][1] - p[a][1]
            d = max(.01, math.hypot(dx, dy))
            f = min(4, max(0, (d - 145) * .06)) / d
            p[a][0] += dx * f; p[a][1] += dy * f
            p[b][0] -= dx * f; p[b][1] -= dy * f
            
        for n, a in enumerate(ids):
            for b in ids[n + 1:]:
                dx, dy = p[b][0] - p[a][0], p[b][1] - p[a][1]
                d = math.hypot(dx, dy)
                if d >= 58: continue
                if d < .01: dx, dy, d = .8, .6, 1
                f = (58 - d) * .13 / d
                p[a][0] -= dx * f; p[a][1] -= dy * f

    x0, y0 = min(v[0] for v in p.values()), min(v[1] for v in p.values())
    posicoes.clear()
    posicoes.update({i: (x - x0 + 100, y - y0 + 100) for i, (x, y) in p.items()})


def ponto(i):
    x, y = posicoes[i]
    return x * zoom, y * zoom

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# --- MÓDULO DE RENDERIZAÇÃO DO CANVAS ---
def desenhar_mapa():
    global regiao
    canvas.delete("all")
    if not posicoes:
        canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2,
                           text="Carregue os dois arquivos CSV para visualizar o grafo", fill=CINZA)
        return

    def desenhar_aresta(a, b, cor, largura):
        if a not in posicoes or b not in posicoes: return
        x1, y1 = ponto(a); x2, y2 = ponto(b)
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        if d <= 26: return
        k = 13 / d
        canvas.create_line(x1 + dx * k, y1 + dy * k, x2 - dx * k, y2 - dy * k,
                           fill=cor, width=largura, capstyle="round")

    for l in dados_linhas: 
        desenhar_aresta(l["origem"], l["destino"], CORES.get(l["cor"], CINZA), 3)
        
    for a, b in zip(caminho_destacado, caminho_destacado[1:]): 
        desenhar_aresta(a, b, ROXO, 7)
        
    for i in sorted(posicoes):
        x, y = ponto(i)
        destaque = i in caminho_destacado
        tags = ("estacao", f"id:{i}")
        canvas.create_oval(x-11, y-11, x+11, y+11, fill="#F2E9FF" if destaque else BRANCO,
                           outline=ROXO if destaque else ESCURO, width=2, tags=tags)
        canvas.create_text(x, y, text=str(i), font=fonte_id, fill=TEXTO, tags=tags)

    if mostrar_nomes.get():
        _desenhar_nomes_estacoes()

    x0, y0, x1, y1 = canvas.bbox("all")
    sx = max(0, canvas.winfo_width() - (x1 - x0 + 130)) / 2
    sy = max(0, canvas.winfo_height() - (y1 - y0 + 130)) / 2
    regiao = (x0 - 65 - sx, y0 - 65 - sy, x1 + 65 + sx, y1 + 65 + sy)
    canvas.config(scrollregion=regiao)


def _desenhar_nomes_estacoes():
    todos = [(i, *ponto(i)) for i in posicoes]
    ocupados = [(x - 15, y - 15, x + 15, y + 15) for _, x, y in todos]
    for i, x, y in sorted(todos, key=lambda t: (t[2], t[1])):
        nome = dados_estacoes[i]["nome"][:32]
        w = fonte_nome.measure(nome) + 10
        for px, py in ((x + 19, y - 12), (x - 19 - w, y - 12), (x - w / 2, y - 46), (x - w / 2, y + 20)):
            caixa = (px, py, px + w, py + 25)
            if any(px < b[2] + 3 and px + w + 3 > b[0] and py < b[3] + 3 and py + 28 > b[1] for b in ocupados): 
                continue
            canvas.create_rectangle(*caixa, fill=BRANCO, outline=BORDA)
            canvas.create_text(px + 5, py + 12, text=nome, anchor="w", font=fonte_nome, fill=TEXTO, tags=("estacao", f"id:{i}"))
            ocupados.append(caixa)
            break

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# --- CONTROLES DE ZOOM E VISUALIZAÇÃO ---

def centralizar(x, y, cx, cy):
    x0, y0, x1, y1 = regiao
    canvas.xview_moveto((x - cx - x0) / max(1, x1 - x0))
    canvas.yview_moveto((y - cy - y0) / max(1, y1 - y0))


def aplicar_zoom(novo, cx=None, cy=None):
    global zoom, ajustado
    if not posicoes: return
    cx = canvas.winfo_width() / 2 if cx is None else cx
    cy = canvas.winfo_height() / 2 if cy is None else cy
    x, y = canvas.canvasx(cx) / zoom, canvas.canvasy(cy) / zoom
    zoom, ajustado = max(.12, min(5, novo)), False
    desenhar_mapa()
    centralizar(x * zoom, y * zoom, cx, cy)
    lbl_zoom.config(text=f"{zoom:.0%}")


def ajustar_zoom():
    global zoom, ajustado
    if not posicoes: return
    xs, ys = zip(*posicoes.values())
    z = min((canvas.winfo_width() - 170) / max(1, max(xs) - min(xs)),
            (canvas.winfo_height() - 100) / max(1, max(ys) - min(ys)))
    zoom, ajustado = max(.12, min(5, z)), True
    desenhar_mapa()
    xs, ys = zip(*(ponto(i) for i in posicoes))
    centralizar((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2,
                canvas.winfo_width() / 2, canvas.winfo_height() / 2)
    lbl_zoom.config(text=f"{zoom:.0%}")


def roda(event):
    cima = getattr(event, "num", 0) == 4 or getattr(event, "delta", 0) > 0
    aplicar_zoom(zoom * (1.25 if cima else .8), event.x, event.y)
    return "break"


def hover(_event):
    itens = canvas.find_withtag("current")
    if itens:
        for tag in canvas.gettags(itens[-1]):
            if tag.startswith("id:"):
                i = int(tag[3:])
                detalhe.config(text=f"Estação: {dados_estacoes[i]['nome']}  (ID {i})")
                break

##------------------ EXECUÇAO DOS ALGORTIMO ---------------------

def executar_algoritmo():
    problema = combo_problema.get()
    algoritmo = var_algoritmo.get()
    
    if problema.startswith("A") and algoritmo == "Força bruta":
        inicial = int(combo_inicial.get())

        inicio = perf_counter()
        resultado = forca_bruta(grafo, inicial)
        tempo = perf_counter() - inicio

        caminho_destacado[:] = resultado["caminho"]

        texto = (
            f"Máximo de estações: {resultado['maximo']}\n"
            f"Caminho: {resultado['caminho']}\n"
            f"Tempo: {tempo:.6f} segundos"
        )
    elif problema.startswith("A") and algoritmo == "Branch-and-bound":
        inicial = int(combo_inicial.get())
        
        inicio = perf_counter()
        resultado = BranchAndBound(grafo, inicial)
        tempo = perf_counter() - inicio
        
        caminho_destacado[:] = resultado["caminho"]
        
        texto = (
            f"Máximo de estações: {resultado['maximo']}\n"
            f"Caminho: {resultado['caminho']}\n"
            f"Tempo: {tempo:.6f} segundos"
        )

    lbl_resultado.config(text=texto)
    desenhar_mapa()
    
##---------------------------------------------------------------
    
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# --- CONSTRUÇÃO DA INTERFACE GRÁFICA (UI) ---
janela = tk.Tk()
janela.title("Metrô de Paris | Análise de Algoritmos")
janela.geometry("1240x790")
janela.minsize(900, 600)
janela.configure(bg=FUNDO)

fonte_id = font.Font(family="Segoe UI", size=9, weight="bold")
fonte_nome = font.Font(family="Segoe UI", size=9)


def criar_label(pai, texto, tamanho=10, cor=TEXTO, negrito=False, **kw):
    return tk.Label(pai, text=texto, bg=pai.cget("bg"), fg=cor,
                    font=("Segoe UI", tamanho, "bold" if negrito else "normal"), **kw)


def criar_botao(pai, texto, comando, primario=False, **kw):
    return tk.Button(pai, text=texto, command=comando, relief="flat", padx=12, pady=9,
                     bg=AZUL if primario else BRANCO, fg=BRANCO if primario else TEXTO, **kw)


# Cabeçalho
cabecalho = tk.Frame(janela, bg=ESCURO, height=88)
cabecalho.pack(fill="x"); cabecalho.pack_propagate(False)
criar_label(cabecalho, "METRÔ DE PARIS", 19, BRANCO, True).pack(anchor="w", padx=28, pady=(12, 0))
criar_label(cabecalho, "Visualização de grafos  /  Análise de algoritmos", 10, "#B9CAEA").pack(anchor="w", padx=28)

# Layout Principal
principal = tk.Frame(janela, bg=FUNDO)
principal.pack(fill="both", expand=True, padx=18, pady=16)

# Painel Lateral (Menu)
lateral = tk.Frame(principal, bg=BRANCO, width=275, highlightbackground=BORDA, highlightthickness=1)
lateral.pack(side="left", fill="y", padx=(0, 16)); lateral.pack_propagate(False)

painel = tk.Frame(lateral, bg=BRANCO)
painel.pack(fill="both", expand=True, padx=17, pady=18)

criar_label(painel, "ARQUIVOS DO GRAFO", 9, CINZA, True).pack(anchor="w", pady=(0, 12))
criar_botao(painel, "Carregar estações (.csv)", lambda: carregar("estacoes")).pack(fill="x")
status_e = criar_label(painel, "Aguardando arquivo", 9, CINZA)
status_e.pack(anchor="w", pady=(4, 12))

criar_botao(painel, "Carregar linhas (.csv)", lambda: carregar("linhas")).pack(fill="x")
status_l = criar_label(painel, "Aguardando arquivo", 9, CINZA)
status_l.pack(anchor="w", pady=(4, 18))

ttk.Separator(painel).pack(fill="x", pady=(0, 18))

criar_label(painel, "PROBLEMA", 9, CINZA, True).pack(anchor="w", pady=(0, 8))
combo_problema = ttk.Combobox(painel, state="readonly", values=[
    "A — Maior percurso", "B — Instalação de guichês", "C — Períodos de manutenção"])
combo_problema.current(0); combo_problema.pack(fill="x", pady=(0, 20))
criar_label(painel, "ESTAÇÃO INICIAL", 9, CINZA, True).pack(anchor="w", pady=(0, 8))
combo_inicial = ttk.Combobox(painel, state="readonly")
combo_inicial.pack(fill="x", pady=(0, 15))

criar_label(painel, "ALGORITMO", 9, CINZA, True).pack(anchor="w", pady=(0, 9))
var_algoritmo = tk.StringVar(value="Força bruta")
for nome in ("Força bruta", "Branch-and-bound", "Heurística"):
    tk.Radiobutton(painel, text=nome, value=nome, variable=var_algoritmo,
                   bg=BRANCO, anchor="w", selectcolor=BRANCO).pack(fill="x", pady=4)

executar_btn = criar_botao(lateral, "Executar algoritimo", executar_algoritmo, True, state="disabled")
executar_btn.pack(side="bottom", fill="x", padx=17, pady=20)

# Cartão do Mapa / Visualização
cartao = tk.Frame(principal, bg=BRANCO, highlightbackground=BORDA, highlightthickness=1)
cartao.pack(side="left", fill="both", expand=True)

barra = tk.Frame(cartao, bg=BRANCO)
barra.pack(fill="x", padx=17, pady=13)

esq = tk.Frame(barra, bg=BRANCO); esq.pack(side="left")
criar_label(esq, "Mapa da rede", 14, TEXTO, True).pack(anchor="w")
resumo = criar_label(esq, "Carregue os dois CSVs para visualizar o grafo", 9, CINZA)
resumo.pack(anchor="w")

dir_frame = tk.Frame(barra, bg=BRANCO); dir_frame.pack(side="right")
zoom_ajustar = criar_botao(dir_frame, "Ajustar", ajustar_zoom, state="disabled")
zoom_ajustar.pack(side="left")
zoom_menos = criar_botao(dir_frame, "−", lambda: aplicar_zoom(zoom/1.25), state="disabled")
zoom_menos.pack(side="left")
lbl_zoom = criar_label(dir_frame, "100%", 10, TEXTO, True, width=6); lbl_zoom.pack(side="left")
zoom_mais = criar_botao(dir_frame, "+", lambda: aplicar_zoom(zoom*1.25), state="disabled")
zoom_mais.pack(side="left")

area = tk.Frame(cartao, bg="#FAFCFF")
area.pack(fill="both", expand=True, padx=17)
area.rowconfigure(0, weight=1); area.columnconfigure(0, weight=1)

canvas = tk.Canvas(area, bg="#FAFCFF", highlightthickness=0, cursor="fleur")
canvas.grid(row=0, column=0, sticky="nsew")
sy = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
sy.grid(row=0, column=1, sticky="ns")
sx = ttk.Scrollbar(area, orient="horizontal", command=canvas.xview)
sx.grid(row=1, column=0, sticky="ew")
canvas.config(xscrollcommand=sx.set, yscrollcommand=sy.set)

rodape = tk.Frame(cartao, bg=BRANCO); rodape.pack(fill="x", padx=17, pady=10)
mostrar_nomes = tk.BooleanVar(value=True)
tk.Checkbutton(rodape, text="Mostrar nomes", variable=mostrar_nomes,
               command=desenhar_mapa, bg=BRANCO).pack(side="left")
criar_label(rodape, "Arraste: mover  •  Roda: zoom  •  Mouse: detalhes", 9, CINZA).pack(side="right")

ttk.Separator(cartao).pack(fill="x", padx=17)

# Rodapé de Resultados
resultado = tk.Frame(cartao, bg=BRANCO, height=135)
resultado.pack(fill="x", padx=19, pady=12); resultado.pack_propagate(False)
criar_label(resultado, "Resultado da execução", 11, TEXTO, True).pack(anchor="w")

lbl_resultado = criar_label(resultado, "Nenhum algoritmo executado ainda.", 9, CINZA,
                            justify="left", anchor="w", wraplength=680)
lbl_resultado.pack(fill="x", pady=(6, 0))

detalhe = criar_label(resultado, "Passe o mouse sobre uma estação para ver seu nome.", 9, AZUL)
detalhe.pack(anchor="w", pady=5)

# Eventos do Canvas
canvas.bind("<ButtonPress-1>", lambda e: canvas.scan_mark(e.x, e.y))
canvas.bind("<B1-Motion>", lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
canvas.bind("<Motion>", hover)
for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
    canvas.bind(evento, roda)
canvas.bind("<Configure>", lambda e: ajustar_zoom() if posicoes and ajustado else None)
resultado.bind("<Configure>", lambda e: lbl_resultado.config(wraplength=e.width-20))

desenhar_mapa()
janela.mainloop()

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////