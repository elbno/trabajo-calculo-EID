import sympy as sp
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# configuracion basica como el titulo y el tamaño de la ventana
app = ctk.CTk()
app.title("Visualizador de Límites - MATE1133")
app.geometry("800x600")

# la funcion que se ejecuta al presionar el boton
def calcular_y_graficar():
    try:
        # lee lo que pone el usuario
        funcion_texto = entrada_funcion.get() #recuadro superior
        h_texto = entrada_h.get() # recuadro inferior
        
        # define x como variable matematica
        x = sp.Symbol('x')
        
        # Convertir el texto a una expresión matematica de SymPy
        f_x = sp.sympify(funcion_texto)
        h_valor = sp.sympify(h_texto)
        
        #calcul del limite
        limite_resultado = sp.limit(f_x, x, h_valor)
        etiqueta_resultado.configure(text=f"Resultado del Límite: {limite_resultado}")
        
        
        # limpia el grafico que habia antes para que no se sobreponga con el anterior y genere problemas
        ax.clear()
        
        
        h_float = float(h_valor.evalf())
        rango_x_min = h_float - 5
        rango_x_max = h_float + 5

         
        # Esto transforma la expresion de sympy en una funcion ejecutable para Python 
        f_num = sp.lambdify(x, f_x, modules=['math'])
        
        # Creamos los puntos para el eje X 
        puntos = 200
        paso = (rango_x_max - rango_x_min) / puntos
        x_valores = [rango_x_min + i * paso for i in range(puntos + 1)]
        
        # Evaluamos los valores en Y 
        y_valores = []
        for val in x_valores:
            try:
                y_valores.append(f_num(val))
            except (ValueError, ZeroDivisionError):
                y_valores.append(float('nan')) # estp ignora los puntos donde no existe la función
        
        # Graficar en el eje de Matplotlib
        ax.plot(x_valores, y_valores, label=f"f(x) = {funcion_texto}", color="blue")
        ax.axvline(x=h_float, color="red", linestyle="--", label=f"x = {h_texto}")
        ax.grid(True)
        ax.legend()
        
        
        canvas.draw()
        
    except Exception as e:
        etiqueta_resultado.configure(text=f"Error: {e}")


# los recuadros donde se ingresan los datos
entrada_funcion = ctk.CTkEntry(app, placeholder_text="Ingresa f(x). Ej: (x**2 - 1)/(x - 1)")
entrada_funcion.pack(pady=10)

entrada_h = ctk.CTkEntry(app, placeholder_text="Valor de h (hacia donde tiende x)")
entrada_h.pack(pady=10)

# los botones
boton_calcular = ctk.CTkButton(app, text="Calcular y Graficar", command=calcular_y_graficar)
boton_calcular.pack(pady=10)

# Etiqueta para el resultado
etiqueta_resultado = ctk.CTkLabel(app, text="Resultado del Límite: ", font=("Arial", 14, "bold"))
etiqueta_resultado.pack(pady=10)

# Integracion del Lienzo de Matplotlib en CustomTkinter
fig, ax = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(fig, master=app)
canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

# para poder iniciar todo esto
app.mainloop()
