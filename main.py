import sympy as sp
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

# Configuración inicial
app = ctk.CTk()
app.title("Analizador Robusto de Límites - MATE1133")
app.geometry("800x750")

def safe_eval(expr, sym, val):
    try:
        resultado = expr.subs(sym, val).evalf()
        return float(resultado) if resultado.is_real else float('nan')
    except:
        return float('nan')

def analizar_limite(f_expr, x_sym, h_val):
    if h_val == float('inf') or h_val == float('-inf'):
        puntos = [1e2, 1e3, 1e4, 1e5, 1e6]
        res = [safe_eval(f_expr, x_sym, p if h_val > 0 else -p) for p in puntos]
        valid_res = [r for r in res if not (r != r)]
        if valid_res and abs(valid_res[-1] - valid_res[-2] if len(valid_res)>1 else 0) < 0.05:
            return f"Converge a: {valid_res[-1]:.4f}"
        return "Tiende a Infinito / No converge"

    pasos = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6]
    resultados = []
    for p in pasos:
        v_der = safe_eval(f_expr, x_sym, h_val + p)
        v_izq = safe_eval(f_expr, x_sym, h_val - p)
        if abs(v_der) > 1e5 or abs(v_izq) > 1e5: return "Tiende a Infinito (Asíntota)"
        if not (v_der != v_der) and not (v_izq != v_izq):
            resultados.append((v_izq, v_der))
    
    if not resultados: return "Indeterminado"
    if abs(resultados[-1][0] - resultados[-1][1]) > 0.5:
        return "No existe (Oscilación)"
    
    promedio = (resultados[-1][0] + resultados[-1][1]) / 2
    return f"{promedio:.6f}"

def calcular_y_graficar():
    try:
        x = sp.Symbol('x')
        f_x = sp.sympify(entrada_funcion.get())
        
        h_text = entrada_h.get().lower()
        if h_text in ['inf', 'oo', 'infinito']: h_val = float('inf')
        elif h_text in ['-inf', '-oo', '-infinito']: h_val = float('-inf')
        else: h_val = float(sp.sympify(h_text).evalf())
        
        resultado = analizar_limite(f_x, x, h_val)
        etiqueta_resultado.configure(text=f"Resultado: {resultado}")
        
        ax.clear()
        if h_val in [float('inf'), float('-inf')]:
            rango_x = [i for i in range(1, 100)]
            y_vals = [safe_eval(f_x, x, v) for v in rango_x]
            ax.plot(rango_x, y_vals, color="blue", label="f(x)")
            ax.set_title(f"Tendencia al {'Infinito' if h_val > 0 else '-Infinito'}")
        else:
            rango = 5
            x_vals = [h_val - rango + (i * (2*rango)/200) for i in range(201)]
            y_vals = [safe_eval(f_x, x, v) for v in x_vals]
            y_vals_clean = [y if abs(y) < 50 else float('nan') for y in y_vals]
            ax.plot(x_vals, y_vals_clean, color="blue", label="f(x)")
            ax.axvline(x=h_val, color="red", linestyle="--", label=f"h={h_val}")
        
        ax.grid(True)
        ax.legend()
        canvas.draw()
    except Exception as e:
        etiqueta_resultado.configure(text=f"Error: {e}")

# Lógica para cerrar la app limpiamente
def cerrar_app():
    app.destroy()
    os._exit(0)

# Interfaz
entrada_funcion = ctk.CTkEntry(app, placeholder_text="f(x), ej: (2*x + 1)/(x - 5)")
entrada_funcion.pack(pady=10, fill="x", padx=20)
entrada_h = ctk.CTkEntry(app, placeholder_text="h (valor o 'inf')")
entrada_h.pack(pady=10, fill="x", padx=20)
boton = ctk.CTkButton(app, text="Analizar Límite", command=calcular_y_graficar)
boton.pack(pady=10)
etiqueta_resultado = ctk.CTkLabel(app, text="Resultado: ", font=("Arial", 16))
etiqueta_resultado.pack(pady=10)

fig, ax = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(fig, master=app)
canvas.get_tk_widget().pack(fill="both", expand=True)

# Vincular cierre de ventana a nuestra función de limpieza
app.protocol("WM_DELETE_WINDOW", cerrar_app)
app.mainloop()