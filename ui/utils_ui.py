import os


def centralizar_janela(win, largura, altura):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (largura // 2)
    y = (win.winfo_screenheight() // 2) - (altura // 2)
    win.geometry(f"{largura}x{altura}+{x}+{y}")


def aplicar_icone_padrao(win, icon_path="icon.ico"):
    try:
        if os.path.exists(icon_path):
            win.iconbitmap(icon_path)
    except Exception:
        pass


def configurar_janela(win, largura, altura, titulo=None, resizable=False, icon_path="icon.ico"):
    if titulo:
        win.title(titulo)

    centralizar_janela(win, largura, altura)
    win.resizable(resizable, resizable)
    aplicar_icone_padrao(win, icon_path)


def abrir_filha(master, janela_cls, *args, **kwargs):
    master.withdraw()
    nova = janela_cls(master, *args, **kwargs)

    def ao_fechar():
        try:
            nova.destroy()
        except Exception:
            pass

        try:
            master.deiconify()
        except Exception:
            pass

    nova.protocol("WM_DELETE_WINDOW", ao_fechar)
    return nova