"""

Problema (b): Guichês de venda de passes  ==>  CONJUNTO DOMINANTE MÍNIMO

Modelagem
---------
Grafo não direcionado G = (V, E): V = estações, E = trechos entre estações
consecutivas de uma linha. Um turista não pode caminhar mais que uma estação
até um guichê  <=>  toda estação ou tem guichê, ou é vizinha de uma que tem.
Isso é exatamente o problema do Conjunto Dominante Mínimo (NP-difícil).

Representação interna: cada vértice i tem uma máscara de bits viz[i] com
o seu vizinhança fechada N[i] = {i} U vizinhos(i). Um conjunto S domina o
grafo se a união das máscaras de S cobre todos os bits.

Soluções:
  a) forca_bruta        - testa subconjuntos de tamanho k = 1, 2, ... (exata)
  b) branch_and_bound   - busca com poda por lower/upper bound (exata)
  c) heuristica_gulosa  - guloso de cobertura (tempo polinomial, aproximada)

Uso rápido (para integrar à interface gráfica):
    g = Grafo(nomes, arestas)
    r = resolver(g, "forca_bruta" | "branch_and_bound" | "heuristica")
    r.estacoes  -> lista de nomes das estações com guichê
    r.tempo     -> tempo de execução em segundos
"""

import time
import itertools
from dataclasses import dataclass, field


# Grafo
class Grafo:
    def __init__(self, nomes, arestas):
        """nomes: lista de estações; arestas: lista de pares (nome1, nome2)."""
        self.nomes = list(dict.fromkeys(nomes))          # remove duplicatas, mantém ordem
        self.idx = {n: i for i, n in enumerate(self.nomes)}
        self.n = len(self.nomes)
        self.adj = [set() for _ in range(self.n)]
        for a, b in arestas:
            if a not in self.idx or b not in self.idx or a == b:
                continue
            i, j = self.idx[a], self.idx[b]
            self.adj[i].add(j)
            self.adj[j].add(i)
        # máscara da vizinhança fechada N[i]
        self.viz = [1 << i for i in range(self.n)]
        for i in range(self.n):
            for j in self.adj[i]:
                self.viz[i] |= 1 << j
        self.todos = (1 << self.n) - 1

    def domina(self, conjunto):
        m = 0
        for i in conjunto:
            m |= self.viz[i]
        return m == self.todos


@dataclass
class Resultado:
    metodo: str
    indices: list = field(default_factory=list)
    estacoes: list = field(default_factory=list)
    tempo: float = 0.0
    nos_visitados: int = 0
    completo: bool = True      # False se interrompido por limite de tempo
    # (nesse caso, 'indices' é a melhor solução encontrada até o momento)

    @property
    def quantidade(self):
        return len(self.indices)


class TempoEsgotado(Exception):
    pass


# c) Heurística gulosa  (tempo polinomial)
def _guloso_indices(g):
    """A cada passo escolhe o vértice que domina mais estações ainda
    descobertas. Depois remove guichês redundantes."""
    descoberto = g.todos
    escolhidos = []
    while descoberto:
        melhor, ganho = -1, -1
        for v in range(g.n):
            gv = (g.viz[v] & descoberto).bit_count()
            if gv > ganho:
                melhor, ganho = v, gv
        escolhidos.append(melhor)
        descoberto &= ~g.viz[melhor]
    # limpeza: tenta remover cada guichê se o restante ainda domina tudo
    for v in list(escolhidos):
        resto = [u for u in escolhidos if u != v]
        if g.domina(resto):
            escolhidos = resto
    return escolhidos


def heuristica_gulosa(g):
    """Aproximação gulosa para Conjunto Dominante (equivale ao Set Cover).
    Complexidade: O(k * n * popcount) <= O(n^2)  -> polinomial.
    Garantia: |S| <= (1 + ln(Δ+1)) * OPT, Δ = grau máximo
    (Johnson, 1974; Chvátal, 1979)."""
    t0 = time.perf_counter()
    ind = _guloso_indices(g)
    t = time.perf_counter() - t0
    return Resultado("Heurística gulosa", ind, [g.nomes[i] for i in ind], t, 0, True)


# a) Força bruta
def forca_bruta(g, limite_tempo=None):
    """Testa todos os subconjuntos de tamanho 1, 2, 3, ... e devolve o
    primeiro que domina o grafo (portanto de tamanho mínimo).
    Complexidade: O( sum_{k<=OPT} C(n,k) * n ) -> exponencial."""
    t0 = time.perf_counter()
    testados = 0
    viz, todos = g.viz, g.todos
    for k in range(1, g.n + 1):
        for comb in itertools.combinations(range(g.n), k):
            testados += 1
            m = 0
            for v in comb:
                m |= viz[v]
            if m == todos:
                t = time.perf_counter() - t0
                return Resultado("Força bruta", list(comb), [g.nomes[i] for i in comb],
                                 t, testados, True)
            if limite_tempo and (testados & 0x3FFF) == 0 \
                    and time.perf_counter() - t0 > limite_tempo:
                ind = _guloso_indices(g)     # só para devolver algo útil
                return Resultado("Força bruta (tempo esgotado)", ind,
                                 [g.nomes[i] for i in ind],
                                 time.perf_counter() - t0, testados, False)
    return Resultado("Força bruta", [], [], time.perf_counter() - t0, testados, True)


# b) Branch-and-bound
def branch_and_bound(g, limite_tempo=None):
    """Árvore de decisão: escolhe-se uma estação ainda NÃO dominada v; algum
    vértice de N[v] obrigatoriamente precisa receber guichê, então ramifica-se
    sobre os candidatos de N[v] (escolhendo o v com MENOS candidatos).
    Após explorar o ramo "c entra", c é proibido nos ramos seguintes
    (evita soluções repetidas).

    Upper bound : melhor solução conhecida (começa com a gulosa).
    Lower bound : |escolhidos| + ceil(#não dominadas / maior ganho possível),
                  onde o ganho possível é o maior número de estações novas
                  que um único vértice permitido ainda domina.
    Poda: se lower bound >= upper bound, o ramo não pode melhorar."""
    t0 = time.perf_counter()
    viz, todos, n = g.viz, g.todos, g.n

    melhor = _guloso_indices(g)          # upper bound inicial
    estado = {"melhor": melhor, "nos": 0}

    def rec(dominado, escolhidos, proibido):
        estado["nos"] += 1
        if limite_tempo and (estado["nos"] & 0x3FF) == 0 \
                and time.perf_counter() - t0 > limite_tempo:
            raise TempoEsgotado()
        if dominado == todos:
            if len(escolhidos) < len(estado["melhor"]):
                estado["melhor"] = list(escolhidos)
            return
        faltam = todos & ~dominado
        qtd_falta = faltam.bit_count()

        # lower bound (ganho máximo entre vértices permitidos)
        ganho_max = 0
        ganhos = {}
        livres = ((1 << n) - 1) & ~proibido
        m = livres
        while m:
            b = m & -m
            v = b.bit_length() - 1
            m ^= b
            gv = (viz[v] & faltam).bit_count()
            if gv:
                ganhos[v] = gv
                if gv > ganho_max:
                    ganho_max = gv
        if ganho_max == 0:
            return                                   # beco sem saída
        lb = len(escolhidos) + -(-qtd_falta // ganho_max)
        if lb >= len(estado["melhor"]):
            return                                   # PODA

        # escolhe a estação descoberta com menos candidatos permitidos
        alvo, cand_alvo, menor = -1, 0, n + 1
        m = faltam
        while m:
            b = m & -m
            v = b.bit_length() - 1
            m ^= b
            cand = viz[v] & livres
            c = cand.bit_count()
            if c < menor:
                alvo, cand_alvo, menor = v, cand, c
                if c <= 1:
                    break
        if menor == 0:
            return                                   # estação impossível de dominar
        # ordena candidatos por ganho (mais promissores primeiro)
        candidatos = []
        m = cand_alvo
        while m:
            b = m & -m
            candidatos.append(b.bit_length() - 1)
            m ^= b
        candidatos.sort(key=lambda v: -ganhos.get(v, 0))

        prib = proibido
        for c in candidatos:
            escolhidos.append(c)
            rec(dominado | viz[c], escolhidos, prib)
            escolhidos.pop()
            prib |= 1 << c

    completo = True
    try:
        rec(0, [], 0)
    except TempoEsgotado:
        completo = False
    ind = estado["melhor"]
    nome = "Branch-and-bound" + ("" if completo else " (tempo esgotado)")
    return Resultado(nome, ind, [g.nomes[i] for i in ind],
                     time.perf_counter() - t0, estado["nos"], completo)


# Interface única para a GUI
def resolver(g, metodo, limite_tempo=None):
    if metodo == "forca_bruta":
        return forca_bruta(g, limite_tempo)
    if metodo == "branch_and_bound":
        return branch_and_bound(g, limite_tempo)
    if metodo == "heuristica":
        return heuristica_gulosa(g)
    raise ValueError("método desconhecido: " + metodo)


def comparar(g, limite_tempo=None):
    """Roda os três métodos, valida cada solução e imprime comparação."""
    res = [resolver(g, m, limite_tempo)
           for m in ("forca_bruta", "branch_and_bound", "heuristica")]
    for r in res:
        assert g.domina(r.indices), f"{r.metodo}: solução inválida!"
    fb, bb, he = res
    if fb.completo and bb.completo:
        print("Força bruta == Branch-and-bound (mesmo nº de guichês)?",
              fb.quantidade == bb.quantidade)
    print(f"{'Método':32s}{'Guichês':>8s}{'Tempo (s)':>12s}{'Nós/testes':>12s}")
    for r in res:
        print(f"{r.metodo:32s}{r.quantidade:8d}{r.tempo:12.4f}{r.nos_visitados:12d}")
    return res


# Leitura dos arquivos (formato do enunciado)
def ler_estacoes(caminho):
    """Linhas 'Nome x y'. O nome pode ter espaços: x e y são os 2 últimos
    tokens. Devolve {nome: (x, y)}."""
    est = {}
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            p = linha.split()
            if len(p) >= 3:
                est[" ".join(p[:-2])] = (float(p[-2]), float(p[-1]))
    return est


def _separar_par(texto, conhecidas):
    """Separa 'Nome1 Nome2' mesmo quando os nomes têm espaços, usando a lista
    de estações conhecidas. Se houver tab, ';' ou ' | ', usa-os como separador."""
    for sep in ("\t", ";", " | "):
        if sep in texto:
            a, b = texto.split(sep, 1)
            return a.strip(), b.strip()
    p = texto.split()
    for i in range(1, len(p)):
        a, b = " ".join(p[:i]), " ".join(p[i:])
        if a in conhecidas and b in conhecidas:
            return a, b
    return None


def ler_linhas(caminho, conhecidas):
    """Formato: 'LinhaN cor k' seguido de k linhas 'Nome1 Nome2'.
    Devolve lista de (linha, cor, [(a, b), ...])."""
    linhas, atual, restantes = [], None, 0
    with open(caminho, encoding="utf-8") as f:
        for bruto in f:
            texto = bruto.strip()
            if not texto:
                continue
            if restantes == 0:
                p = texto.split()
                atual = (p[0], p[1], [])
                restantes = int(p[2])
                linhas.append(atual)
            else:
                par = _separar_par(texto, conhecidas)
                if par:
                    atual[2].append(par)
                restantes -= 1
    return linhas


def grafo_de_arquivos(arq_estacoes, arq_linhas, linhas_usadas=None):
    """Monta o Grafo. linhas_usadas: ex. {'Linha1','Linha4'} para testar com
    menos linhas (só entram estações que aparecem nos trechos)."""
    est = ler_estacoes(arq_estacoes)
    todas = ler_linhas(arq_linhas, set(est))
    if linhas_usadas:
        todas = [l for l in todas if l[0] in linhas_usadas]
    arestas = [par for _, _, trechos in todas for par in trechos]
    nomes = sorted({x for par in arestas for x in par})
    return Grafo(nomes, arestas)


# Demonstração / teste sem os arquivos (grafo sintético tipo metrô)
def _grafo_sintetico(n_linhas, comp, seed=1):
    """Linhas = caminhos de 'comp' estações; cada linha cruza a anterior em
    uma estação (como as baldeações do metrô)."""
    import random
    rnd = random.Random(seed)
    arestas, nomes, prev = [], [], None
    for L in range(n_linhas):
        est = [f"L{L}_E{i}" for i in range(comp)]
        if prev:
            est[rnd.randrange(comp)] = rnd.choice(prev)      # baldeação
        nomes += est
        arestas += list(zip(est, est[1:]))
        prev = est
    return Grafo(nomes, arestas)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:      # python guiches.py estacoes.txt linhas.txt
        g = grafo_de_arquivos(sys.argv[1], sys.argv[2])
        print(f"{g.n} estações")
        comparar(g, limite_tempo=60)
    else:
        for nl, comp in [(2, 8), (3, 9), (4, 10), (10, 14)]:
            g = _grafo_sintetico(nl, comp)
            print(f"\n=== {nl} linhas, {g.n} estações ===")
            comparar(g, limite_tempo=20)
