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
app.geometry("800x800") 

# Variable global para recordar qué casilla fue la última activa
ultima_entrada_activa = None

def registrar_foco(event):
    """Guarda cual casilla de texto tiene el cursor parpadeando actualmente."""
    global ultima_entrada_activa
    ultima_entrada_activa = event.widget

# ==========================================================
# Inserción de simbolos interactivos (Historial de foco)
# ==========================================================
def insertar_simbolo(simbolo):
    """
    Inserta el simbolo utilizando la última casilla registrada
    e impide que los botones rompan el flujo de texto.
    """
    global ultima_entrada_activa
    
    if ultima_entrada_activa is not None:
        try:
            posicion_cursor = ultima_entrada_activa.index(ctk.INSERT)
            ultima_entrada_activa.insert(posicion_cursor, simbolo)
            
            # Ajuste de comodidad: Si inserta √( ), dejamos el cursor dentro del paréntesis
            if simbolo == "√( )":
                ultima_entrada_activa.icursor(posicion_cursor + 2)
            # Si inserta ||, dejamos el cursor en el medio de las barras
            elif simbolo == "||":
                ultima_entrada_activa.icursor(posicion_cursor + 1)
                
            ultima_entrada_activa.focus() 
        except:
            pass

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

        resultados_validos = [res for res in resultados_evaluacion if res == res]
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
# Cálculo y gráfico (Con preprocesamiento de texto)
# ==========================================================
def calcular_y_graficar():
    try:
        simbolo_variable = sp.Symbol("x")
        
        # --- ALGORITMO DE TRADUCCIÓN DE SÍMBOLOS ---
        texto_funcion = entrada_funcion.get()
        texto_funcion = texto_funcion.replace("√", "sqrt")
        texto_funcion = texto_funcion.replace("π", "pi")
        
        if texto_funcion.count("|") == 2:
            partes = texto_funcion.split("|")
            texto_funcion = f"{partes[0]}abs({partes[1]}){partes[2]}"
            
        expresion_funcion = sp.sympify(texto_funcion)
        
        texto_limite = entrada_limite.get().lower().strip()
        texto_limite = texto_limite.replace("π", "pi")

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
                if abs(x - valor_limite) < 1e-3:
                    valores_y.append(float("nan"))
                    continue
                    
                y = evaluacion_segura(expresion_funcion, simbolo_variable, x)
                
                # Filtro de estabilidad para que picos asintóticos no rompan el gráfico
                if y == y and abs(y) < 10:
                    valores_y.append(y)
                else:
                    valores_y.append(float("nan"))

            eje.plot(valores_x, valores_y, color="blue", label="f(x)", linewidth=2)
            eje.axvline(x=valor_limite, color="red", linestyle="--", label=f"h = {valor_limite}")
            
            # Centramos el eje Y de forma estándar para ver las curvas cómodamente
            eje.set_ylim(-1, 2)

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

# 1. Entrada principal de la función f(x)
entrada_funcion = ctk.CTkEntry(app, placeholder_text="f(x), ej: (2*x + 1)/(x - 5)")
entrada_funcion.pack(pady=10, fill="x", padx=20)
entrada_funcion.bind("<FocusIn>", registrar_foco)

# 2. BARRA DE HERRAMIENTAS MATEMÁTICAS 
marco_botones = ctk.CTkFrame(app, fg_color="transparent")
marco_botones.pack(pady=5)

# Corrección crítica: Ahora inyecta la estructura sintáctica válida completa
boton_raiz = ctk.CTkButton(marco_botones, text=" √ ", width=60, command=lambda: insertar_simbolo("√( )"))
boton_raiz.pack(side="left", padx=5)

boton_pi = ctk.CTkButton(marco_botones, text=" π ", width=60, command=lambda: insertar_simbolo("π"))
boton_pi.pack(side="left", padx=5)

boton_abs = ctk.CTkButton(marco_botones, text=" |x| ", width=60, command=lambda: insertar_simbolo("||"))
boton_abs.pack(side="left", padx=5)

# 3. Entrada del límite 'h'
entrada_limite = ctk.CTkEntry(app, placeholder_text="h (valor o 'inf')")
entrada_limite.pack(pady=10, fill="x", padx=20)
entrada_limite.bind("<FocusIn>", registrar_foco)

# Botón disparador del análisis
boton_analizar = ctk.CTkButton(app, text="Analizar Límite", command=calcular_y_graficar)
boton_analizar.pack(pady=10)

# Etiqueta de salida de resultados
etiqueta_resultado = ctk.CTkLabel(app, text="Resultado:", font=("Arial", 16))
etiqueta_resultado.pack(pady=10)

# Área del Canvas para Matplotlib
figura, eje = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(figura, master=app)
canvas.get_tk_widget().pack(fill="both", expand=True)

app.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

# Dejar la primera casilla activa por defecto al abrir el programa
entrada_funcion.focus()
ultima_entrada_activa = entrada_funcion

app.mainloop()