#!/usr/bin/env python3
import sys
import tkinter as tk
from tkinter import ttk, messagebox


def extrair_campos_linha_a_linha(texto):
    """
    'extrai' o html completo da provisao e extrai os rotulos p/ preencher no pagnet
    """
    lines = texto.splitlines()
    valores = {}
    # rótulos
    rotulos = [
        "CNPJ",
        "Pagnet Empresa",
        "Pagnet Filial",
        "Centro de Custo Solicitante",
        "Pagnet Tipo de Operação Pagto",
        "Pagnet Forma Pagamento",
        "Pagnet Evento para Pagamento",
        "Contrato Sistema jurídico ID",
        "Pagnet Descrição Pagamento",
        "Competência Evento",
        "Serviço de TI",
    ]
    skip_vals = {"", "Selecione um valor...", "Projeto", "T1- Filial", "T2 - Centro de Custo"}
    for rotulo in rotulos:
        idx = max((i for i,l in enumerate(lines) if l.strip().startswith(rotulo)), default=None)
        if idx is None:
            valores[rotulo] = ""
            continue
        k = idx + 1
        while k < len(lines) and not lines[k].strip(): k += 1
        val = lines[k].strip() if k < len(lines) else ""
        j = k + 1
        while j < len(lines) and not lines[j].strip(): j += 1
        nxt = lines[j].strip() if j < len(lines) else None
        if rotulo in ["Pagnet Tipo de Operação Pagto", "Pagnet Evento para Pagamento"]:
            if nxt and not any(nxt.startswith(r) for r in rotulos):
                valores[rotulo] = f"{val} {nxt}".strip()
            else:
                valores[rotulo] = val
        else:
            valores[rotulo] = val
    idx_cc = next((i for i,l in enumerate(lines) if l.strip()=="Centro de Custo"), None)
    idx_cc_def = next((i for i,l in enumerate(lines) if l.strip().startswith("Centro de Custo Definição")), None)
    idx_t2 = next((i for i,l in enumerate(lines) if l.strip().startswith("T2 - Centro de Custo")), None)
    idx_pagnet = next((i for i,l in enumerate(lines) if l.strip()=="Configuração de Pagamento (PAGNET)"), None)
    def_val = ""
    if idx_cc is not None and idx_cc_def is not None:
        for k in range(idx_cc+1, idx_cc_def):
            v = lines[k].strip()
            if v and v not in skip_vals and not v.startswith("Centro de Custo"):
                def_val = v
                break
    valores["Centro de Custo Definição"] = def_val
    code = desc = ""
    if idx_t2 is not None and idx_pagnet is not None:
        for k in range(idx_t2+1, idx_pagnet):
            v = lines[k].strip()
            if not v or v in skip_vals or v.startswith("Centro de Custo"): continue
            code = v
            for m in range(k+1, idx_pagnet):
                w = lines[m].strip()
                if w and w not in skip_vals and not w.startswith("Centro de Custo"): 
                    desc = w
                    break
            break
    valores["Centro de Custo"] = f"{code} {desc}".strip()
    return valores
    
class JanelaCampos(tk.Toplevel):
    def __init__(self, master, campos):
        super().__init__(master)
        self.attributes("-topmost", True)
        try:
            self.iconbitmap(r"C:\Users\bruno\OneDrive\Área de Trabalho\Mag.ico")
        except Exception:
            pass
        self.title("MAG")
        self.geometry("500x800")
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)
        canvas = tk.Canvas(frm)
        sb = ttk.Scrollbar(frm, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        def on_wheel(ev): canvas.yview_scroll(int(-1*(ev.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        for rot, val in campos.items():
            fg = "blue" if val else "red"
            ttk.Label(inner, text=rot+":", foreground=fg, font=("Segoe UI",10,"bold")).pack(anchor="w", pady=(5,0))
            btn = tk.Button(inner, text=val or "<vazio>", width=60,
                            bg="white" if val else "red", fg="black" if val else "white",
                            command=lambda v=val: self.copiar_para_clipboard(v))
            btn.pack(anchor="w", pady=(0,5))
        ttk.Button(self, text="Fechar Janela", command=self.destroy).pack(pady=(5,10))

    def copiar_para_clipboard(self, txt):
        if txt: self.clipboard_clear(); self.clipboard_append(txt)
def main():
    root = tk.Tk()
    try:
        root.iconbitmap(r"C:\Users\bruno\OneDrive\Área de Trabalho\Mag.ico")
    except Exception:
        pass
    root.withdraw()

    while True:
        try:
            txt = root.clipboard_get()
        except tk.TclError:
            retry = messagebox.askretrycancel(
                "MAG",
                "Copie a provisão e tente novamente."
            )
            if not retry:
                root.quit()
                sys.exit()
            continue
        campos = extrair_campos_linha_a_linha(txt)
        janela = JanelaCampos(root, campos)
        root.wait_window(janela)
        if not messagebox.askyesno("MAG", "Deseja processar outro?"):
            break
    root.quit()
if __name__ == "__main__":
    main()