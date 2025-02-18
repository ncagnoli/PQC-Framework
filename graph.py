from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import DataRange1d,NumeralTickFormatter
import pandas as pd

# Carregar os dados
df_server = pd.read_csv("sshd_config_padrao.csv")
df_client = pd.read_csv("perf_client.csv")

# Criar um gráfico
p = figure( title="CPU Cycles por Iteração",
            x_axis_label="Iteração",
            y_axis_label="CPU Cycles",
            width=1024,
            height=768,
            background_fill_color="#fafafa")

#Linhas
p.line(df_server["iteration"], df_server["cycles"], legend_label="Server CPU Cycles", line_color="indigo", line_width=3, line_dash="dotdash")
p.line(df_client["iteration"], df_client["cycles"], legend_label="Client CPU Cycles", line_color="coral", line_width=3 , line_dash="dashed")
#Escala
p.y_range = DataRange1d()

#Desenho
p.yaxis.formatter = NumeralTickFormatter(format="0")
p.legend.location = "top_left"

# Salvar e exibir
output_file("bokeh_plot.html")
show(p)
