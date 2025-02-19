from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import DataRange1d, NumeralTickFormatter, LinearAxis, HoverTool, Legend, Rect
import pandas as pd

# Carregar os dados
df_server = pd.read_csv("sshd_config_padrao.csv")
df_client = pd.read_csv("perf_client.csv")

# Criar o gráfico com cor sólida no fundo
p = figure(title="📊 Desempenho CPU: Cycles & Instructions por Iteração",
           x_axis_label="Iteração",
           y_axis_label="CPU Cycles",
           width=1000,
           height=900,
           background_fill_color="#f3f3f3")  # Cor sólida em vez de gradiente

# Criar um segundo eixo Y para "Instructions"
p.extra_y_ranges = {"instructions": DataRange1d()}
p.add_layout(LinearAxis(y_range_name="instructions", axis_label="CPU Instructions"), 'right')

# Adicionar Hover Tool para interação
hover = HoverTool(tooltips=[("Iteração", "@x"), ("Valor", "@y")])
p.add_tools(hover)

# Criando um degradê visualmente: um retângulo com transparência
p.rect(x=0, y=0, width=2, height=2, fill_color="lightgray", fill_alpha=0.3)

# Linhas - CPU Cycles (Eixo Esquerdo - Padrão)
server_cycles = p.line(df_server["iteration"], df_server["cycles"], 
                       line_color="dodgerblue", line_width=4, line_dash="solid", alpha=0.8)

client_cycles = p.line(df_client["iteration"], df_client["cycles"], 
                       line_color="purple", line_width=4, line_dash="solid", alpha=0.8)

# Linhas - CPU Instructions (Eixo Direito)
server_instructions = p.line(df_server["iteration"], df_server["instructions"], 
                             line_width=4, line_dash="dotdash", color="darkorange", alpha=0.9, y_range_name="instructions")

client_instructions = p.line(df_client["iteration"], df_client["instructions"], 
                             line_width=4, line_dash="dotdash", color="red", alpha=0.9, y_range_name="instructions")

# Ajuste de escalas
p.y_range = DataRange1d()
p.extra_y_ranges["instructions"] = DataRange1d()

# 🖋 Melhorando os textos (Fonte maior e em negrito)
p.title.text_font_size = "20pt"
p.title.text_font_style = "bold"
p.xaxis.axis_label_text_font_size = "14pt"
p.xaxis.axis_label_text_font_style = "bold"
p.yaxis.axis_label_text_font_size = "14pt"
p.yaxis.axis_label_text_font_style = "bold"
p.xaxis.major_label_text_font_size = "12pt"
p.yaxis.major_label_text_font_size = "12pt"

# 🎨 Personalizando a Legenda
legend = Legend(items=[
    ("Server CPU Cycles", [server_cycles]),
    ("Client CPU Cycles", [client_cycles]),
    ("Server CPU Instructions", [server_instructions]),
    ("Client CPU Instructions", [client_instructions])
])

# Ajustando a posição e estilo da legenda
p.add_layout(legend, 'right')
legend.label_text_font_size = "12pt"
legend.background_fill_color = "#ffffff"  # Fundo branco
legend.background_fill_alpha = 0.8  # Transparência para efeito visual
legend.border_line_width = 2
legend.border_line_color = "black"
legend.spacing = 10
legend.padding = 10

# Formatando os números no eixo Y
p.yaxis.formatter = NumeralTickFormatter(format="0")

# Salvar e exibir
output_file("bokeh_plot_moderno.html")
show(p)
