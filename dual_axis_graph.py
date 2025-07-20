import argparse
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import DataRange1d, NumeralTickFormatter, LinearAxis, HoverTool, Legend

def create_dual_axis_plot(server_csv, client_csv, output_html):
    """
    Reads performance data and generates an interactive Bokeh plot with a dual Y-axis
    for comparing CPU Cycles and Instructions.

    Args:
        server_csv (str): Path to the server's performance data CSV file.
        client_csv (str): Path to the client's performance data CSV file.
        output_html (str): Path to save the output HTML file.
    """
    try:
        df_server = pd.read_csv(server_csv)
        df_client = pd.read_csv(client_csv)
    except FileNotFoundError as e:
        print(f"Error: {e}. Please provide valid file paths.")
        return

    # Create a new plot
    p = figure(
        title="CPU Performance: Cycles & Instructions per Iteration",
        x_axis_label="Iteration",
        y_axis_label="CPU Cycles",
        width=1200,
        height=800,
        background_fill_color="#f3f3f3"
    )

    # --- Primary Y-Axis (CPU Cycles) ---
    server_cycles = p.line(
        df_server["iteration"], df_server["cycles"],
        line_color="dodgerblue", line_width=3, alpha=0.8
    )
    client_cycles = p.line(
        df_client["iteration"], df_client["cycles"],
        line_color="purple", line_width=3, alpha=0.8
    )
    p.y_range = DataRange1d()
    p.yaxis.formatter = NumeralTickFormatter(format="0,0")

    # --- Secondary Y-Axis (CPU Instructions) ---
    p.extra_y_ranges = {"instructions_range": DataRange1d()}
    p.add_layout(
        LinearAxis(y_range_name="instructions_range", axis_label="CPU Instructions"),
        'right'
    )
    server_instructions = p.line(
        df_server["iteration"], df_server["instructions"],
        line_width=3, line_dash="dashed", color="darkorange", alpha=0.9,
        y_range_name="instructions_range"
    )
    client_instructions = p.line(
        df_client["iteration"], df_client["instructions"],
        line_width=3, line_dash="dashed", color="red", alpha=0.9,
        y_range_name="instructions_range"
    )
    p.extra_y_ranges["instructions_range"].formatter = NumeralTickFormatter(format="0,0")

    # --- Tools and Styling ---
    hover = HoverTool(tooltips=[
        ("Iteration", "@x"),
        ("Cycles", "@y{0,0}"),
        ("Instructions", "@instructions{0,0}") # Requires mapping 'instructions' in ColumnDataSource
    ])
    # Note: For hover to work on both axes, a more complex ColumnDataSource setup is needed.
    # This implementation keeps it simple and hovers over the primary Y-axis.
    p.add_tools(HoverTool(tooltips=[("Iteration", "@x"), ("Value", "@y{0,0}")]))

    # --- Legend ---
    legend = Legend(items=[
        ("Server CPU Cycles", [server_cycles]),
        ("Client CPU Cycles", [client_cycles]),
        ("Server CPU Instructions", [server_instructions]),
        ("Client CPU Instructions", [client_instructions])
    ], location="top_left")
    p.add_layout(legend)
    p.legend.click_policy = "hide"
    p.legend.background_fill_alpha = 0.8

    # --- Title and Label Styling ---
    p.title.text_font_size = "18pt"
    p.xaxis.axis_label_text_font_size = "12pt"
    p.yaxis.axis_label_text_font_size = "12pt"
    p.xaxis.major_label_text_font_size = "10pt"
    p.yaxis.major_label_text_font_size = "10pt"

    # --- Output ---
    output_file(output_html)
    show(p)
    print(f"Plot saved to {output_html}")


def main():
    """
    Main function to parse command-line arguments and generate the plot.
    """
    parser = argparse.ArgumentParser(description="Generate a dual-axis Bokeh plot for CPU cycles and instructions.")
    parser.add_argument("server_csv", help="Path to the server performance CSV file.")
    parser.add_argument("client_csv", help="Path to the client performance CSV file.")
    parser.add_argument(
        "-o", "--output",
        default="dual_axis_plot.html",
        help="Output HTML file name (default: dual_axis_plot.html)."
    )
    args = parser.parse_args()

    create_dual_axis_plot(args.server_csv, args.client_csv, args.output)

if __name__ == "__main__":
    main()
