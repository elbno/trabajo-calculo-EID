import sympy as sp
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os


# ==========================================================
# Window Configuration
# ==========================================================

app = ctk.CTk()
app.title("Robust Limit Analyzer - MATE1133")
app.geometry("800x750")


# ==========================================================
# Safe Evaluation Function
# ==========================================================

def safe_evaluate(function_expression,variable_symbol,evaluation_value):
    try:
        result = function_expression.subs(variable_symbol,evaluation_value).evalf()
        if result.is_real:
            return float(result)
        return float("nan")
    except:
        return float("nan")

# ==========================================================
# Limit Analysis Function
# ==========================================================

def analyze_limit(function_expression,variable_symbol,limit_value):
    # ------------------------------------------------------
    # Limits at Infinity
    # ------------------------------------------------------

    if (limit_value == float("inf") or limit_value == float("-inf")):
        test_points = [1e2,1e3,1e4,1e5,1e6]
        evaluation_results = []
        for point in test_points:
            if limit_value > 0:
                current_value = point
            else:
                current_value = -point
            current_result = safe_evaluate(function_expression,variable_symbol,current_value)
            evaluation_results.append(current_result)
        valid_results = [
            result
            for result in evaluation_results
            if result == result
        ]
        if valid_results:
            if len(valid_results) > 1:
                last_result = valid_results[-1]
                previous_result = valid_results[-2]
                difference = abs(
                    last_result -
                    previous_result
                )
            else:
                difference = 0
            if difference < 0.05:
                return (
                    f"Converges to: "
                    f"{valid_results[-1]:.4f}"
                )
        return "Approaches Infinity / Does Not Converge"

    # ------------------------------------------------------
    # Limits at a Specific Point
    # ------------------------------------------------------

    approach_steps = [1e-1,1e-2,1e-3,1e-4,1e-5,1e-6]
    side_results = []
    for step in approach_steps:

        right_side_value = safe_evaluate(function_expression,variable_symbol,limit_value + step)
        left_side_value = safe_evaluate(function_expression,variable_symbol,limit_value - step)
        if abs(right_side_value) > 1e5:
            return "Approaches Infinity (Asymptote)"
        if abs(left_side_value) > 1e5:
            return "Approaches Infinity (Asymptote)"
        right_side_is_valid = (right_side_value == right_side_value)
        left_side_is_valid = (left_side_value == left_side_value)
        if (right_side_is_valid and left_side_is_valid):
            side_results.append((left_side_value,right_side_value))
    if not side_results:
        return "Indeterminate"
    last_pair = side_results[-1]
    left_limit_estimate = last_pair[0]
    right_limit_estimate = last_pair[1]
    side_difference = abs(left_limit_estimate -right_limit_estimate)
    if side_difference > 0.5:
        return "Does Not Exist (Oscillation)"
    average_result = (left_limit_estimate + right_limit_estimate) / 2
    return f"{average_result:.6f}"


# ==========================================================
# Main Calculation Function
# ==========================================================

def calculate_and_plot():
    try:
        variable_symbol = sp.Symbol("x")

        function_expression = sp.sympify(
            function_input.get()
        )
        limit_text = (
            limit_input.get()
            .lower()
            .strip()
        )
        if (
            limit_text == "inf"
            or
            limit_text == "oo"
            or
            limit_text == "infinito"
        ):

            limit_value = float("inf")
        elif (
            limit_text == "-inf"
            or
            limit_text == "-oo"
            or
            limit_text == "-infinito"
        ):

            limit_value = float("-inf")
        else:

            limit_value = float(
                sp.sympify(limit_text).evalf()
            )
        limit_result = analyze_limit(
            function_expression,
            variable_symbol,
            limit_value
        )
        result_label.configure(
            text=f"Result: {limit_result}"
        )
        axis.clear()

        # --------------------------------------------------
        # Plot for Infinity Limits
        # --------------------------------------------------

        if (
            limit_value == float("inf")
            or
            limit_value == float("-inf")
        ):
            x_values = [
                value
                for value in range(1, 100)
            ]
            y_values = []
            for x_value in x_values:

                current_y = safe_evaluate(
                    function_expression,
                    variable_symbol,
                    x_value
                )
                y_values.append(
                    current_y
                )
            axis.plot(
                x_values,
                y_values,
                color="blue",
                label="f(x)"
            )
            if limit_value > 0:
                graph_title = (
                    "Behavior as x Approaches Infinity"
                )
            else:
                graph_title = (
                    "Behavior as x Approaches -Infinity"
                )
            axis.set_title(
                graph_title
            )
        # --------------------------------------------------
        # Plot for Finite Limits
        # --------------------------------------------------

        else:

            display_range = 5

            x_values = []

            for index in range(201):

                current_x = (
                    limit_value
                    - display_range
                    + (
                        index
                        * (
                            2 * display_range
                        )
                        / 200
                    )
                )

                x_values.append(
                    current_x
                )

            y_values = []

            for x_value in x_values:

                current_y = safe_evaluate(
                    function_expression,
                    variable_symbol,
                    x_value
                )

                if abs(current_y) < 50:
                    y_values.append(
                        current_y
                    )
                else:
                    y_values.append(
                        float("nan")
                    )

            axis.plot(
                x_values,
                y_values,
                color="blue",
                label="f(x)"
            )

            axis.axvline(
                x=limit_value,
                color="red",
                linestyle="--",
                label=f"h = {limit_value}"
            )

        axis.grid(True)
        axis.legend()

        canvas.draw()

    except Exception as error:

        result_label.configure(
            text=f"Error: {error}"
        )


# ==========================================================
# Close Application
# ==========================================================

def close_application():

    app.destroy()
    os._exit(0)


# ==========================================================
# Interface Elements
# ==========================================================

function_input = ctk.CTkEntry(
    app,
    placeholder_text=(
        "f(x), example: "
        "(2*x + 1)/(x - 5)"
    )
)

function_input.pack(
    pady=10,
    fill="x",
    padx=20
)

limit_input = ctk.CTkEntry(
    app,
    placeholder_text=(
        "h (value or 'inf')"
    )
)

limit_input.pack(
    pady=10,
    fill="x",
    padx=20
)

analyze_button = ctk.CTkButton(
    app,
    text="Analyze Limit",
    command=calculate_and_plot
)

analyze_button.pack(
    pady=10
)

result_label = ctk.CTkLabel(
    app,
    text="Result:",
    font=("Arial", 16)
)

result_label.pack(
    pady=10
)


# ==========================================================
# Graph Area
# ==========================================================

figure, axis = plt.subplots(
    figsize=(5, 4)
)

canvas = FigureCanvasTkAgg(
    figure,
    master=app
)

canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)


# ==========================================================
# Window Events
# ==========================================================

app.protocol("WM_DELETE_WINDOW",close_application)

app.mainloop()