# pip install plotly>=5 pandas kaleido
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import textwrap

def wrap_label(txt, width=10):
    return "<br>".join(textwrap.fill(txt, width=width, break_long_words=False).split("\n"))

def parse_key_name(key_str):
    """Extrai nome limpo da chave a partir de key(size)"""
    # Remove parênteses e pega apenas a parte relevante
    # Ex: "RSA(2048)" -> "RSA 2048"
    # Ex: "Ed25519(256)" -> "Ed25519"
    key_str = key_str.replace("(", " ").replace(")", "")
    parts = key_str.split()
    if parts[0] == "Ed25519":
        return "Ed25519"
    return " ".join(parts)

# ============================================
# 1. CARREGAR DADOS
# ============================================
df = pd.read_csv('Experimento - Testes e Resultados - Resultados RESUMIDOS.tsv', 
                 sep='\t', decimal=',')

# Limpar espaços e converter colunas numéricas
df.columns = df.columns.str.strip()
numeric_cols = ['cycles_p50', 'instr_p50', 'ipc_p50', 'bpc_p50']
for col in numeric_cols:
    if df[col].dtype == 'object':
        df[col] = df[col].str.replace(',', '.').astype(float)

# ============================================
# 2. DEFINIR CENÁRIOS
# ============================================
scenarios = {
    1: {
        "title": "Cenário 1 - Algoritmos Clássicos",
        "tests": [1, 2, 3, 4],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    2: {
        "title": "Cenário 2 - Clássico vs KEX PQC (RSA 3072)",
        "tests": [2, 9],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    3: {
        "title": "Cenário 3 - Clássico vs KEX PQC",
        "tests": [3, 4, 10, 11],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    4: {
        "title": "Cenário 4 - Clássicos com KEX PQC",
        "tests": [5, 6, 7, 8, 10, 11],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    5: {
        "title": "Cenário 5 - Clássico → Híbrido → PQC (RSA+FALCON)",
        "tests": [9, 12, 15],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    6: {
        "title": "Cenário 6 - Clássico → Híbrido → PQC (RSA+SPHINCS)",
        "tests": [9, 14, 17],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    7: {
        "title": "Cenário 7 - Clássico → Híbrido → PQC (RSA+ML-DSA)",
        "tests": [9, 13, 19],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    8: {
        "title": "Cenário 8 - Alto Desempenho",
        "tests": [1, 15],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    9: {
        "title": "Cenário 9 - PQC Chaves Menores",
        "tests": [15, 19],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    10: {
        "title": "Cenário 10 - PQC Chaves Maiores",
        "tests": [17, 20],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    11: {
        "title": "Cenário 11 - PQC Chaves Grandes",
        "tests": [16, 18, 21],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    12: {
        "title": "Cenário 12 - FALCON Tamanhos",
        "tests": [15, 16],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    13: {
        "title": "Cenário 13 - SPHINCS Tamanhos",
        "tests": [17, 18],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    },
    14: {
        "title": "Cenário 14 - ML-DSA Tamanhos",
        "tests": [19, 20, 21],
        "groups": [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
    }
}

# ============================================
# 3. FUNÇÃO PARA CRIAR GRÁFICO
# ============================================
def create_chart(scenario_num, chart_type="CeI"):
    """
    Cria gráfico para um cenário específico
    chart_type: "CeI" (Cycles e Instructions) ou "IeB" (IPC e BPC)
    """
    scenario = scenarios[scenario_num]
    tests = scenario["tests"]
    
    # Filtrar dados dos testes
    df_filtered = df[df['Test ID'].isin(tests)].copy()
    
    # Definir grupos e métricas baseado no tipo de gráfico
    if chart_type == "CeI":
        groups_config = [
            {"name": "Client cycles", "role": "client", "metric": "cycles_p50", "axis": "left"},
            {"name": "Server cycles", "role": "server", "metric": "cycles_p50", "axis": "left"},
            {"name": "Client instructions", "role": "client", "metric": "instr_p50", "axis": "right"},
            {"name": "Server instructions", "role": "server", "metric": "instr_p50", "axis": "right"}
        ]
        y1_label, y2_label = "Cycles", "Instructions"
    else:  # IeB
        groups_config = [
            {"name": "Client IPC", "role": "client", "metric": "ipc_p50", "axis": "left"},
            {"name": "Server IPC", "role": "server", "metric": "ipc_p50", "axis": "left"},
            {"name": "Client BPC", "role": "client", "metric": "bpc_p50", "axis": "right"},
            {"name": "Server BPC", "role": "server", "metric": "bpc_p50", "axis": "right"}
        ]
        y1_label, y2_label = "IPC", "BPC"
    
    # Construir groups_data
    groups_data = []
    for gc in groups_config:
        df_group = df_filtered[df_filtered['Role'] == gc['role']]
        bars = []
        for _, row in df_group.iterrows():
            key_name = parse_key_name(row['key(size)'])
            value = row[gc['metric']]
            bars.append((key_name, value))
        groups_data.append({"group": gc['name'], "bars": bars, "axis": gc['axis']})
    
    # Cores e posicionamento
    group_palette = px.colors.qualitative.Safe
    group_colors = {gd["group"]: group_palette[i % len(group_palette)] for i, gd in enumerate(groups_data)}
    
    GROUP_SPACING = 0.8
    group_centers = {gd["group"]: i * GROUP_SPACING for i, gd in enumerate(groups_data)}
    
    # Calcular offsets dinamicamente baseado no número de barras
    num_bars = len(groups_data[0]["bars"])
    if num_bars == 2:
        offsets = [-0.15, 0.15]
        bar_width = 0.25
    elif num_bars == 3:
        offsets = [-0.20, 0.0, 0.20]
        bar_width = 0.18
    elif num_bars == 4:
        offsets = [-0.27, -0.09, 0.09, 0.27]
        bar_width = 0.16
    elif num_bars == 6:
        offsets = [-0.35, -0.21, -0.07, 0.07, 0.21, 0.35]
        bar_width = 0.12
    else:
        offsets = [-0.27, -0.09, 0.09, 0.27]
        bar_width = 0.16
    
    first_group = groups_data[0]["group"]
    last_group = groups_data[-1]["group"]
    leftmost = group_centers[first_group] + min(offsets)
    rightmost = group_centers[last_group] + max(offsets)
    PAD = 0.1
    xmin, xmax = leftmost - PAD, rightmost + PAD
    
    # Criar figura
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    x_tickvals, x_ticktext = [], []
    
    # Adicionar barras
    for gi, gd in enumerate(groups_data):
        gname = gd["group"]
        cx = group_centers[gname]
        use_right = (gd["axis"] == "right")
        gcolor = group_colors[gname]
        
        for idx, (name, value) in enumerate(gd["bars"]):
            x_pos = cx + offsets[idx % len(offsets)]
            x_tickvals.append(x_pos)
            x_ticktext.append(wrap_label(name, width=10))
            
            # Formatar valor
            if chart_type == "CeI":
                text_val = f"{value:,.0f}"
            else:
                text_val = f"{value:.4f}"
            
            fig.add_trace(
                go.Bar(
                    x=[x_pos], y=[value], width=[bar_width],
                    name=gname,
                    legendgroup=gname,
                    showlegend=(idx == 0),
                    marker=dict(color=gcolor, line=dict(width=0)),
                    text=[text_val], textposition="outside", cliponaxis=False,
                    hovertemplate="<b>%{customdata[0]}</b><br>Grupo: %{customdata[1]}<br>Valor: %{y}<extra></extra>",
                    customdata=[[name, gname]],
                ),
                secondary_y=use_right
            )
            
            # Linha tracejada
            if use_right:
                fig.add_shape(
                    type="line", xref="x", yref="y2",
                    x0=x_pos, x1=xmax, y0=value, y1=value,
                    line=dict(dash="dot", width=2, color=gcolor)
                )
            else:
                fig.add_shape(
                    type="line", xref="x", yref="y",
                    x0=xmin, x1=x_pos, y0=value, y1=value,
                    line=dict(dash="dot", width=2, color=gcolor)
                )
    
    # Layout
    fig.update_layout(
        title=dict(
            text=scenario["title"],
            x=0.5, xanchor="center",
            font=dict(size=32, family="Inter, Segoe UI, Roboto, Arial")
        ),
        template="plotly_white",
        bargap=0.06,
        margin=dict(l=70, r=70, t=90, b=260),
        plot_bgcolor="rgba(250,250,252,1)",
        paper_bgcolor="white",
        showlegend=False,
        uniformtext_minsize=9,
        uniformtext_mode="hide",
        width=1200,
        height=800
    )
    
    # Eixo X
    fig.update_xaxes(
        range=[xmin, xmax],
        tickvals=x_tickvals,
        ticktext=x_ticktext,
        tickfont=dict(size=16),
        automargin=True,
        showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)"
    )
    
    # Anotações dos grupos
    for gd in groups_data:
        cx = group_centers[gd["group"]]
        fig.add_annotation(
            x=cx, xref="x",
            y=0, yref="paper",
            text=f"<b>{gd['group']}</b>",
            showarrow=False,
            yshift=-70,
            font=dict(size=22, color="rgba(0,0,0,0.75)"),
            align="center"
        )
    
    # Eixos Y
    fig.update_yaxes(
        title_text=y1_label,
        secondary_y=False,
        title_font=dict(size=26),
        title_standoff=12,
        zeroline=False,
        gridcolor="rgba(0,0,0,0.08)",
        showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
        tickfont=dict(size=18)
    )
    fig.update_yaxes(
        title_text=y2_label,
        secondary_y=True,
        title_font=dict(size=26),
        title_standoff=12,
        zeroline=False,
        showgrid=True,
        showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
        tickfont=dict(size=18)
    )
    
    return fig

# ============================================
# 4. GERAR TODOS OS GRÁFICOS
# ============================================
print("Gerando gráficos...")
for scenario_num in range(1, 15):
    # Gráfico CeI
    fig_cei = create_chart(scenario_num, "CeI")
    filename_cei = f"cenario_{scenario_num}_CeI.png"
    fig_cei.write_image(filename_cei)
    print(f"✓ {filename_cei}")
    
    # Gráfico IeB
    fig_ieb = create_chart(scenario_num, "IeB")
    filename_ieb = f"cenario_{scenario_num}_IeB.png"
    fig_ieb.write_image(filename_ieb)
    print(f"✓ {filename_ieb}")

print("\n🎉 Todos os 28 gráficos foram gerados com sucesso!")
