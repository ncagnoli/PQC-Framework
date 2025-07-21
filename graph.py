import argparse
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import NumeralTickFormatter
import config

def create_plot(server_csv, client_csv, output_html):
    """
    Reads performance data from server and client CSV files and generates an interactive Bokeh plot.

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

    # Create a new plot with a title and axis labels
    p = figure(
        title="CPU Cycles per Iteration",
        x_axis_label="Iteration",
        y_axis_label="CPU Cycles",
        width=config.PLOT_WIDTH,
        height=config.PLOT_HEIGHT,
        background_fill_color=config.PLOT_BG_COLOR
    )

    # Add line renderers with legend labels
    p.line(
        df_server["iteration"],
        df_server["cycles"],
        legend_label="Server CPU Cycles",
        line_color="indigo",
        line_width=3,
        line_dash="dotdash"
    )
    p.line(
        df_client["iteration"],
        df_client["cycles"],
        legend_label="Client CPU Cycles",
        line_color="coral",
        line_width=3,
        line_dash="dashed"
    )

    # Customize the plot
    p.yaxis.formatter = NumeralTickFormatter(format="0,0")  # Format y-axis numbers
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"  # Allows hiding lines by clicking the legend

    # Specify the output file and show the plot
    output_file(output_html)
    show(p)
    print(f"Plot saved to {output_html}")

def main():
    """
    Main function to parse command-line arguments and generate the plot.
    """
    parser = argparse.ArgumentParser(description="Generate a Bokeh plot from server and client performance data.")
    parser.add_argument("server_csv", help="Path to the server performance CSV file.")
    parser.add_argument("client_csv", help="Path to the client performance CSV file.")
    parser.add_argument(
        "-o", "--output",
        default=config.DEFAULT_SINGLE_AXIS_PLOT_OUTPUT,
        help=f"Output HTML file name (default: {config.DEFAULT_SINGLE_AXIS_PLOT_OUTPUT})."
    )
    args = parser.parse_args()

    create_plot(args.server_csv, args.client_csv, args.output)

if __name__ == "__main__":
    main()
