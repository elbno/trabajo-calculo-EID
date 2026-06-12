import sympy as sp
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

# ==========================================================
# Configuración de la ventana
# ==========================================================
app = ctk.CTk()
app.title("Analizador Robusto de Límites - MATE1133")
app.geometry("800x750")

# ==========================================================
# Evaluación segura
# ==========================================================
def evaluacion_segura(expresion_funcion, simbolo_variable, valor_evaluacion):
    try:
        resultado = expresion_funcion.subs(simbolo_variable, valor_evaluacion).evalf()
        if resultado.is_real:
            return float(resultado)
        return float("nan")
    except:
        return float("nan")

# ==========================================================
# Análisis de límites
# ==========================================================
def analizar_limite(expresion_funcion, simbolo_variable, valor_limite):
    # --- Límites al infinito ---
    if valor_limite in [float("inf"), float("-inf")]:
        puntos_prueba = [1e2, 1e3, 1e4, 1e5, 1e6]
        resultados_evaluacion = []

        for punto in puntos_prueba:
            valor_actual = punto if valor_limite > 0 else -punto
            resultados_evaluacion.append(evaluacion_segura(expresion_funcion, simbolo_variable, valor_actual))

        resultados_validos = [res for res in resultados_evaluacion if res == res] # Filtra NaN
        if not resultados_validos:
            return "Tiende a Infinito / No converge"

        diferencia = 0
        if len(resultados_validos) > 1:
            diferencia = abs(resultados_validos[-1] - resultados_validos[-2])

        if diferencia < 0.05:
            return f"Converge a: {resultados_validos[-1]:.4f}"
        return "Tiende a Infinito / No converge"

    # --- Límites en un punto ---
    pasos_aproximacion = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6]
    resultados_laterales = []

    for paso in pasos_aproximacion:
        valor_derecho = evaluacion_segura(expresion_funcion, simbolo_variable, valor_limite + paso)
        valor_izquierdo = evaluacion_segura(expresion_funcion, simbolo_variable, valor_limite - paso)

        if abs(valor_derecho) > 1e5 or abs(valor_izquierdo) > 1e5:
            return "Tiende a Infinito (Asíntota)"

        if (valor_derecho == valor_derecho) and (valor_izquierdo == valor_izquierdo):
            resultados_laterales.append((valor_izquierdo, valor_derecho))

    if not resultados_laterales:
        return "Indeterminado"

    limite_izquierdo, limite_derecho = resultados_laterales[-1]
    if abs(limite_izquierdo - limite_derecho) > 0.5:
        return "No existe (Oscilación)"

    return f"{(limite_izquierdo + limite_derecho) / 2:.6f}"

# ==========================================================
# Cálculo y gráfico
# ==========================================================
def calcular_y_graficar():
    try:
        simbolo_variable = sp.Symbol("x")
        expresion_funcion = sp.sympify(entrada_funcion.get())
        texto_limite = entrada_limite.get().lower().strip()

        if texto_limite in ["inf", "oo", "infinito"]: valor_limite = float("inf")
        elif texto_limite in ["-inf", "-oo", "-infinito"]: valor_limite = float("-inf")
        else: valor_limite = float(sp.sympify(texto_limite).evalf())

        resultado_limite = analizar_limite(expresion_funcion, simbolo_variable, valor_limite)
        etiqueta_resultado.configure(text=f"Resultado: {resultado_limite}")

        eje.clear()

        # --- Gráfico ---
        if valor_limite in [float("inf"), float("-inf")]:
            valores_x = list(range(1, 100))
            valores_y = [evaluacion_segura(expresion_funcion, simbolo_variable, x) for x in valores_x]
            
            eje.plot(valores_x, valores_y, color="blue", label="f(x)")
            eje.set_title("Tendencia al Infinito" if valor_limite > 0 else "Tendencia al -Infinito")
        else:
            rango = 5
            valores_x = [valor_limite - rango + (i * (2 * rango) / 200) for i in range(201)]
            valores_y = []
            
            for x in valores_x:
                y = evaluacion_segura(expresion_funcion, simbolo_variable, x)
                valores_y.append(y if abs(y) < 50 else float("nan"))

            eje.plot(valores_x, valores_y, color="blue", label="f(x)")
            eje.axvline(x=valor_limite, color="red", linestyle="--", label=f"h = {valor_limite}")

        eje.grid(True)
        eje.legend()
        canvas.draw()

    except Exception as error:
        etiqueta_resultado.configure(text=f"Error: {error}")

# ==========================================================
# Cierre y Componentes UI
# ==========================================================
def cerrar_aplicacion():
    app.destroy()
    os._exit(0)

entrada_funcion = ctk.CTkEntry(app, placeholder_text="f(x), ej: (2*x + 1)/(x - 5)")
entrada_funcion.pack(pady=10, fill="x", padx=20)

entrada_limite = ctk.CTkEntry(app, placeholder_text="h (valor o 'inf')")
entrada_limite.pack(pady=10, fill="x", padx=20)

boton_analizar = ctk.CTkButton(app, text="Analizar Límite", command=calcular_y_graficar)
boton_analizar.pack(pady=10)

etiqueta_resultado = ctk.CTkLabel(app, text="Resultado:", font=("Arial", 16))
etiqueta_resultado.pack(pady=10)

figura, eje = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(figura, master=app)
canvas.get_tk_widget().pack(fill="both", expand=True)

app.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
app.mainloop()