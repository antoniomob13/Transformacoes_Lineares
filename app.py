"""Interface gráfica (Tkinter) do software vetorial de Transformações Lineares.

Toda a matemática é feita pela classe Matriz de transformacoes_lineares.py;
este arquivo só lê os dados do usuário, chama a classe e desenha o resultado.

Execute com:  py app.py
"""
import math
import tkinter as tk
from tkinter import ttk, messagebox

from transformacoes_lineares import Matriz

COR_ATUAL = "#1f4fbf"
FUNDO_ATUAL = "#dbe6fb"
COR_ORIGINAL = "#8a8a8a"
COR_ANCORA = "#d62828"
COR_GRADE = "#e9e9e9"
COR_EIXO = "#555555"

NOMES_TIPO = {"rotacao": "Rotação", "escala": "Escala", "reflexao": "Reflexão"}


# ---------------------------------------------------------------- utilidades

def ler_numero(texto):
    """Converte texto em número aceitando vírgula ou ponto decimal."""
    return float(texto.strip().replace(",", "."))


def rotulo(i):
    return chr(ord("A") + i) if i < 26 else f"P{i + 1}"


def fmt(v):
    v = round(v, 2)
    if v == 0:
        v = 0.0  # evita mostrar "-0"
    return f"{v:g}"


def passo_bonito(bruto):
    """Escolhe um espaçamento de grade 1, 2 ou 5 x 10^n."""
    exp = 10 ** math.floor(math.log10(bruto))
    for m in (1, 2, 5, 10):
        if bruto <= m * exp:
            return m * exp
    return 10 * exp


# ------------------------------------------------------- operações de matriz

def aplicar_operacao(fig, op):
    """Aplica uma operação na figura usando os métodos da classe Matriz."""
    cx, cy = op["cx"], op["cy"]
    if op["tipo"] == "rotacao":
        fig.rotacao(op["angulo"], cx, cy)
    elif op["tipo"] == "escala":
        fig.escalonamento(op["sx"], op["sy"], cx, cy)
    else:
        # espelhamento() da classe não recebe âncora: transladamos antes e depois,
        # igual à fórmula T(x) = A[x - c] + c dos slides.
        fig.somar(-cx, -cy)
        fig.espelhamento(op["eixo"])
        fig.somar(cx, cy)


def inversa(op):
    """Operação inversa (A^-1): desfaz 'op' em torno da mesma âncora."""
    inv = dict(op)
    if op["tipo"] == "rotacao":
        inv["angulo"] = -op["angulo"]  # R(θ)^-1 = R(-θ) = R(θ)^T
    elif op["tipo"] == "escala":
        inv["sx"] = 1 / op["sx"]
        inv["sy"] = 1 / op["sy"]
    # reflexão é a própria inversa
    return inv


def matriz_2x2(op):
    if op["tipo"] == "rotacao":
        r = math.radians(op["angulo"])
        return [[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]]
    if op["tipo"] == "escala":
        return [[op["sx"], 0], [0, op["sy"]]]
    if op["eixo"] == "y":
        return [[-1, 0], [0, 1]]
    return [[1, 0], [0, -1]]


def multiplicar_2x2(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def texto_matriz(m):
    return f"[[{fmt(m[0][0])}, {fmt(m[0][1])}], [{fmt(m[1][0])}, {fmt(m[1][1])}]]"


def descrever(op):
    c = f"c({fmt(op['cx'])}, {fmt(op['cy'])})"
    if op["tipo"] == "rotacao":
        return f"Rotação {fmt(op['angulo'])}° em {c}"
    if op["tipo"] == "escala":
        return f"Escala Sx={fmt(op['sx'])}, Sy={fmt(op['sy'])} em {c}"
    return f"Reflexão eixo {op['eixo']} em {c}"


# ------------------------------------------------------------------ interface

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software Vetorial — Transformações Lineares")
        self.geometry("1180x780")
        self.minsize(950, 640)

        self.fig = None          # objeto Matriz com a figura atual
        self.original = []       # pontos originais [(x, y), ...]
        self.historico = []      # operações já aplicadas (pilha p/ reversão)
        self.fila = []           # operações aguardando aplicação em sequência
        self.entradas = []       # campos (x, y) de cada ponto

        estilo = ttk.Style(self)
        if "vista" in estilo.theme_names():
            estilo.theme_use("vista")
        self.cor_fundo = estilo.lookup("TFrame", "background") or "#f0f0f0"

        esquerda = ttk.Frame(self, padding=10)
        esquerda.pack(side="left", fill="y")
        direita = ttk.Frame(self, padding=(0, 10, 10, 10))
        direita.pack(side="left", fill="both", expand=True)

        self._montar_pontos(esquerda)
        self._montar_transformacao(esquerda)
        self._montar_historico(esquerda)
        self._montar_desenho(direita)

        self.gerar_campos()

    # ---------------------------------------------------------- 1. pontos
    def _montar_pontos(self, pai):
        sec = ttk.LabelFrame(pai, text=" 1. Figura ", padding=8)
        sec.pack(fill="x")

        linha = ttk.Frame(sec)
        linha.pack(fill="x")
        ttk.Label(linha, text="Quantidade de pontos:").pack(side="left")
        self.qtd = tk.IntVar(value=4)
        ttk.Spinbox(linha, from_=1, to=40, width=5, textvariable=self.qtd,
                    command=self.gerar_campos).pack(side="left", padx=6)
        ttk.Button(linha, text="Gerar campos", command=self.gerar_campos).pack(side="left")

        caixa = ttk.Frame(sec)
        caixa.pack(fill="x", pady=6)
        tela = tk.Canvas(caixa, height=140, width=270, highlightthickness=0, bg=self.cor_fundo)
        barra = ttk.Scrollbar(caixa, orient="vertical", command=tela.yview)
        self.frame_pontos = ttk.Frame(tela)
        tela.create_window((0, 0), window=self.frame_pontos, anchor="nw")
        self.frame_pontos.bind(
            "<Configure>", lambda e: tela.configure(scrollregion=tela.bbox("all")))
        tela.configure(yscrollcommand=barra.set)
        tela.pack(side="left", fill="x", expand=True)
        barra.pack(side="right", fill="y")

        botoes = ttk.Frame(sec)
        botoes.pack(fill="x")
        ttk.Button(botoes, text="Limpar tudo", command=self.limpar_tudo).pack(side="left")
        ttk.Button(botoes, text="Desenhar figura", command=self.desenhar_figura).pack(side="right")

    def gerar_campos(self):
        try:
            n = max(1, min(40, int(self.qtd.get())))
        except (tk.TclError, ValueError):
            return
        antigos = [(ex.get(), ey.get()) for ex, ey in self.entradas]
        for w in self.frame_pontos.winfo_children():
            w.destroy()
        self.entradas = []
        for i in range(n):
            ttk.Label(self.frame_pontos, text=f"{rotulo(i)}:", width=4).grid(row=i, column=0, pady=1)
            ttk.Label(self.frame_pontos, text="x").grid(row=i, column=1)
            ex = ttk.Entry(self.frame_pontos, width=8)
            ex.grid(row=i, column=2, padx=(2, 8))
            ttk.Label(self.frame_pontos, text="y").grid(row=i, column=3)
            ey = ttk.Entry(self.frame_pontos, width=8)
            ey.grid(row=i, column=4, padx=2)
            if i < len(antigos):
                ex.insert(0, antigos[i][0])
                ey.insert(0, antigos[i][1])
            self.entradas.append((ex, ey))

    def limpar_tudo(self):
        """Apaga a figura, os pontos digitados, a sequência e o histórico."""
        self.fig = None
        self.original = []
        self.historico.clear()
        self.fila.clear()
        self.info_matriz.set("")
        for ex, ey in self.entradas:
            ex.delete(0, "end")
            ey.delete(0, "end")
        self.ax.set("0")
        self.ay.set("0")
        self._atualizar()

    def desenhar_figura(self):
        pontos = []
        for i, (ex, ey) in enumerate(self.entradas):
            try:
                pontos.append((ler_numero(ex.get()), ler_numero(ey.get())))
            except ValueError:
                messagebox.showerror("Ponto inválido",
                                     f"Preencha x e y do ponto {rotulo(i)} com números.")
                return
        self.original = pontos
        # A classe Matriz espera 2 x N: linha 0 = todos os X, linha 1 = todos os Y
        self.fig = Matriz([[p[0] for p in pontos], [p[1] for p in pontos]])
        self.historico.clear()
        self.fila.clear()
        self.info_matriz.set("")
        self._atualizar()

    # --------------------------------------------------- 2. transformação
    def _montar_transformacao(self, pai):
        sec = ttk.LabelFrame(pai, text=" 2. Transformação ", padding=8)
        sec.pack(fill="x", pady=8)

        self.tipo = tk.StringVar(value="rotacao")
        linha = ttk.Frame(sec)
        linha.pack(fill="x")
        for chave, nome in NOMES_TIPO.items():
            ttk.Radiobutton(linha, text=nome, value=chave, variable=self.tipo,
                            command=self._trocar_parametros).pack(side="left", padx=(0, 10))

        params = ttk.Frame(sec)
        params.pack(fill="x", pady=6)
        self.frames_param = {}

        f = ttk.Frame(params)
        ttk.Label(f, text="Ângulo θ (graus):").pack(side="left")
        self.angulo = tk.StringVar(value="90")
        ttk.Entry(f, width=8, textvariable=self.angulo).pack(side="left", padx=6)
        self.frames_param["rotacao"] = f

        f = ttk.Frame(params)
        ttk.Label(f, text="Sx:").pack(side="left")
        self.sx = tk.StringVar(value="2")
        ttk.Entry(f, width=7, textvariable=self.sx).pack(side="left", padx=(4, 12))
        ttk.Label(f, text="Sy:").pack(side="left")
        self.sy = tk.StringVar(value="3")
        ttk.Entry(f, width=7, textvariable=self.sy).pack(side="left", padx=4)
        self.frames_param["escala"] = f

        f = ttk.Frame(params)
        ttk.Label(f, text="Eixo:").pack(side="left")
        self.eixo = tk.StringVar(value="y")
        ttk.Radiobutton(f, text="x", value="x", variable=self.eixo).pack(side="left", padx=4)
        ttk.Radiobutton(f, text="y", value="y", variable=self.eixo).pack(side="left", padx=4)
        self.frames_param["reflexao"] = f

        anc = ttk.Frame(sec)
        anc.pack(fill="x")
        ttk.Label(anc, text="Âncora c:  x").pack(side="left")
        self.ax = tk.StringVar(value="0")
        ttk.Entry(anc, width=6, textvariable=self.ax).pack(side="left", padx=(2, 6))
        ttk.Label(anc, text="y").pack(side="left")
        self.ay = tk.StringVar(value="0")
        ttk.Entry(anc, width=6, textvariable=self.ay).pack(side="left", padx=2)
        ttk.Button(anc, text="Centro da figura", command=self.ancora_no_centro).pack(side="left", padx=6)
        self.ax.trace_add("write", lambda *_: self._desenhar())
        self.ay.trace_add("write", lambda *_: self._desenhar())

        botoes = ttk.Frame(sec)
        botoes.pack(fill="x", pady=(8, 0))
        ttk.Button(botoes, text="Aplicar agora", command=self.aplicar_agora).pack(side="left")
        ttk.Button(botoes, text="Adicionar à sequência", command=self.adicionar_fila).pack(side="right")

        ttk.Label(sec, text="Sequência (transformações múltiplas):").pack(anchor="w", pady=(8, 2))
        self.lista_fila = tk.Listbox(sec, height=4, activestyle="none")
        self.lista_fila.pack(fill="x")
        botoes = ttk.Frame(sec)
        botoes.pack(fill="x", pady=(4, 0))
        ttk.Button(botoes, text="Limpar", command=self.limpar_fila).pack(side="left")
        ttk.Button(botoes, text="Aplicar sequência", command=self.aplicar_fila).pack(side="right")

        self._trocar_parametros()

    def _trocar_parametros(self):
        for chave, f in self.frames_param.items():
            if chave == self.tipo.get():
                f.pack(fill="x")
            else:
                f.pack_forget()

    def _ancora(self):
        return ler_numero(self.ax.get()), ler_numero(self.ay.get())

    def ancora_no_centro(self):
        if self.fig is None:
            return
        xs, ys = self.fig.matriz_atl
        self.ax.set(fmt((min(xs) + max(xs)) / 2))
        self.ay.set(fmt((min(ys) + max(ys)) / 2))

    def ler_operacao(self):
        """Lê os campos da tela e monta a operação, ou None se houver erro."""
        try:
            cx, cy = self._ancora()
        except ValueError:
            messagebox.showerror("Âncora inválida", "Informe números para a âncora (x, y).")
            return None
        tipo = self.tipo.get()
        op = {"tipo": tipo, "cx": cx, "cy": cy}
        try:
            if tipo == "rotacao":
                op["angulo"] = ler_numero(self.angulo.get())
            elif tipo == "escala":
                op["sx"], op["sy"] = ler_numero(self.sx.get()), ler_numero(self.sy.get())
                if op["sx"] == 0 or op["sy"] == 0:
                    messagebox.showerror("Escala inválida",
                                         "Sx e Sy não podem ser 0 (a matriz não teria inversa).")
                    return None
            else:
                op["eixo"] = self.eixo.get()
        except ValueError:
            messagebox.showerror("Valor inválido", "Preencha os parâmetros com números.")
            return None
        return op

    def _precisa_figura(self):
        if self.fig is None:
            messagebox.showinfo("Sem figura", "Primeiro insira os pontos e clique em \"Desenhar figura\".")
            return True
        return False

    def aplicar_agora(self):
        if self._precisa_figura():
            return
        op = self.ler_operacao()
        if op:
            aplicar_operacao(self.fig, op)
            self.historico.append(op)
            self.info_matriz.set(f"Matriz aplicada: {texto_matriz(matriz_2x2(op))}")
            self._atualizar()

    def adicionar_fila(self):
        op = self.ler_operacao()
        if op:
            self.fila.append(op)
            self._atualizar_listas()

    def limpar_fila(self):
        self.fila.clear()
        self._atualizar_listas()

    def aplicar_fila(self):
        if self._precisa_figura() or not self.fila:
            return
        composta = [[1, 0], [0, 1]]
        for op in self.fila:
            aplicar_operacao(self.fig, op)
            self.historico.append(op)
            composta = multiplicar_2x2(matriz_2x2(op), composta)  # ... C·B·A
        # Se todas usam a mesma âncora, a sequência equivale a uma única matriz M = C·B·A
        ancoras = {(op["cx"], op["cy"]) for op in self.fila}
        if len(ancoras) == 1:
            self.info_matriz.set(f"Matriz composta (…C·B·A): {texto_matriz(composta)}")
        else:
            self.info_matriz.set(f"{len(self.fila)} transformações aplicadas em sequência")
        self.fila.clear()
        self._atualizar()

    # ------------------------------------------------------- 3. reversão
    def _montar_historico(self, pai):
        sec = ttk.LabelFrame(pai, text=" 3. Histórico e reversão ", padding=8)
        sec.pack(fill="both", expand=True)
        self.lista_hist = tk.Listbox(sec, height=5, activestyle="none")
        self.lista_hist.pack(fill="both", expand=True)
        botoes = ttk.Frame(sec)
        botoes.pack(fill="x", pady=(6, 0))
        ttk.Button(botoes, text="Desfazer última", command=self.desfazer).pack(side="left")
        ttk.Button(botoes, text="Reverter tudo", command=self.reverter_tudo).pack(side="right")

    def desfazer(self):
        if self.fig is None or not self.historico:
            return
        op = self.historico.pop()
        inv = inversa(op)
        aplicar_operacao(self.fig, inv)
        self.info_matriz.set(f"Inversa aplicada: {texto_matriz(matriz_2x2(inv))}")
        self._atualizar()

    def reverter_tudo(self):
        """Aplica as inversas na ordem contrária: A^-1 · B^-1 · C^-1 [x - c] + c."""
        if self.fig is None or not self.historico:
            return
        while self.historico:
            aplicar_operacao(self.fig, inversa(self.historico.pop()))
        self.info_matriz.set("Todas as inversas aplicadas: figura de volta ao original")
        self._atualizar()

    # ---------------------------------------------------------- desenho
    def _montar_desenho(self, pai):
        self.canvas = tk.Canvas(pai, bg="white", highlightthickness=1,
                                highlightbackground="#c8c8c8")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._desenhar())

        self.info_matriz = tk.StringVar()
        ttk.Label(pai, textvariable=self.info_matriz, font=("Consolas", 10),
                  foreground=COR_ATUAL).pack(anchor="w", pady=(6, 0))
        self.info_pontos = tk.StringVar()
        ttk.Label(pai, textvariable=self.info_pontos, font=("Consolas", 10),
                  justify="left").pack(anchor="w")

    def _atualizar(self):
        self._atualizar_listas()
        self._desenhar()
        if self.fig is None:
            self.info_pontos.set("")
            return
        xs, ys = self.fig.matriz_atl
        self.info_pontos.set(
            "X: [ " + "  ".join(f"{fmt(v):>7}" for v in xs) + " ]\n"
            "Y: [ " + "  ".join(f"{fmt(v):>7}" for v in ys) + " ]")

    def _atualizar_listas(self):
        self.lista_fila.delete(0, "end")
        for i, op in enumerate(self.fila, 1):
            self.lista_fila.insert("end", f"{i}. {descrever(op)}")
        self.lista_hist.delete(0, "end")
        for i, op in enumerate(self.historico, 1):
            self.lista_hist.insert("end", f"{i}. {descrever(op)}")

    def _desenhar(self):
        c = self.canvas
        c.delete("all")
        w, h = max(c.winfo_width(), 50), max(c.winfo_height(), 50)
        if self.fig is None:
            c.create_text(w / 2, h / 2, fill="#888", font=("Segoe UI", 12),
                          text="Informe os pontos e clique em \"Desenhar figura\"", justify="center")
            return

        atual = list(zip(*self.fig.matriz_atl))
        try:
            ancora = self._ancora()
        except ValueError:
            ancora = None

        # Enquadra figura original, atual, origem e âncora mantendo proporção 1:1
        todos = self.original + atual + [(0, 0)] + ([ancora] if ancora else [])
        xmin, xmax = min(p[0] for p in todos), max(p[0] for p in todos)
        ymin, ymax = min(p[1] for p in todos), max(p[1] for p in todos)
        dx, dy = max(xmax - xmin, 1), max(ymax - ymin, 1)
        margem = 45
        esc = min((w - 2 * margem) / dx, (h - 2 * margem) / dy)
        ox = w / 2 - esc * (xmin + xmax) / 2
        oy = h / 2 + esc * (ymin + ymax) / 2

        def tela(x, y):
            return ox + esc * x, oy - esc * y

        # grade e eixos
        wx0, wx1 = -ox / esc, (w - ox) / esc
        wy0, wy1 = (oy - h) / esc, oy / esc
        passo = passo_bonito(max(wx1 - wx0, wy1 - wy0) / 14)
        eixo_y_tela = min(max(oy, 12), h - 12)
        eixo_x_tela = min(max(ox, 22), w - 12)
        for k in range(math.ceil(wx0 / passo), math.floor(wx1 / passo) + 1):
            x = ox + esc * k * passo
            c.create_line(x, 0, x, h, fill=COR_GRADE)
            if k != 0:
                c.create_text(x, eixo_y_tela + 10, text=fmt(k * passo), fill="#888", font=("Segoe UI", 8))
        for k in range(math.ceil(wy0 / passo), math.floor(wy1 / passo) + 1):
            y = oy - esc * k * passo
            c.create_line(0, y, w, y, fill=COR_GRADE)
            if k != 0:
                c.create_text(eixo_x_tela - 6, y, text=fmt(k * passo), fill="#888",
                              font=("Segoe UI", 8), anchor="e")
        c.create_line(0, oy, w, oy, fill=COR_EIXO)
        c.create_line(ox, 0, ox, h, fill=COR_EIXO)

        def poligono(pontos, **kw):
            coords = [v for p in pontos for v in tela(*p)]
            if len(pontos) >= 3:
                c.create_polygon(coords, **kw)
            elif len(pontos) == 2:
                c.create_line(coords, fill=kw.get("outline"), width=kw.get("width", 1),
                              dash=kw.get("dash"))

        # figura atual (preenchida) e original (tracejada por cima)
        poligono(atual, fill=FUNDO_ATUAL, outline=COR_ATUAL, width=2)
        poligono(self.original, fill="", outline=COR_ORIGINAL, width=1, dash=(5, 4))

        for i, (x, y) in enumerate(self.original):
            sx, sy = tela(x, y)
            c.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill=COR_ORIGINAL, outline="")
            c.create_text(sx + 7, sy - 8, text=rotulo(i), fill=COR_ORIGINAL, font=("Segoe UI", 9))
        linha = "'" if self.historico else ""
        for i, (x, y) in enumerate(atual):
            sx, sy = tela(x, y)
            c.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill=COR_ATUAL, outline="white")
            c.create_text(sx + 8, sy - 9, text=rotulo(i) + linha, fill=COR_ATUAL,
                          font=("Segoe UI", 10, "bold"))

        if ancora:
            sx, sy = tela(*ancora)
            c.create_line(sx - 6, sy - 6, sx + 6, sy + 6, fill=COR_ANCORA, width=2)
            c.create_line(sx - 6, sy + 6, sx + 6, sy - 6, fill=COR_ANCORA, width=2)
            c.create_text(sx + 8, sy + 10, anchor="w", fill=COR_ANCORA, font=("Segoe UI", 9),
                          text=f"c({fmt(ancora[0])}, {fmt(ancora[1])})")

        # legenda
        c.create_rectangle(10, 10, 24, 22, fill=FUNDO_ATUAL, outline=COR_ATUAL, width=2)
        c.create_text(30, 16, anchor="w", text="Figura atual", font=("Segoe UI", 9))
        c.create_line(10, 34, 24, 34, fill=COR_ORIGINAL, dash=(5, 4))
        c.create_text(30, 34, anchor="w", text="Figura original", font=("Segoe UI", 9))
        c.create_text(30, 52, anchor="w", text="Âncora c", fill=COR_ANCORA, font=("Segoe UI", 9))
        c.create_line(12, 46, 22, 56, fill=COR_ANCORA, width=2)
        c.create_line(12, 56, 22, 46, fill=COR_ANCORA, width=2)


if __name__ == "__main__":
    App().mainloop()
