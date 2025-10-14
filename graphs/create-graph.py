# pip install plotly>=5 kaleido
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def format_number(value, decimal_places=0):
    """Formata números com K (mil), M (milhão) e B (bilhão)"""
    if decimal_places == 0:  # Cycles e Instructions
        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:.0f}"
    else:  # IPC e BPC
        return f"{value:.{decimal_places}f}"

# ============================================
# 1. DADOS EMBUTIDOS
# ============================================
DATA = {
    # Test ID: {role: {metric: value}}
    1: {
        "client": {"cycles": 32644650, "instructions": 73901621, "ipc": 2.264186, "bpc": 0.004174},
        "server": {"cycles": 89540747, "instructions": 146150240, "ipc": 1.632213, "bpc": 0.004322}
    },
    2: {
        "client": {"cycles": 46303028, "instructions": 113234505, "ipc": 2.445386, "bpc": 0.003486},
        "server": {"cycles": 110889617, "instructions": 199057853, "ipc": 1.795313, "bpc": 0.004022}
    },
    3: {
        "client": {"cycles": 57021879, "instructions": 151918155, "ipc": 2.664012, "bpc": 0.002658},
        "server": {"cycles": 128495569, "instructions": 265876400, "ipc": 2.069169, "bpc": 0.003358}
    },
    4: {
        "client": {"cycles": 36007279, "instructions": 89048317, "ipc": 2.472653, "bpc": 0.003814},
        "server": {"cycles": 85315996, "instructions": 141632836, "ipc": 1.660072, "bpc": 0.004385}
    },
    5: {
        "client": {"cycles": 488553925, "instructions": 1112218701, "ipc": 2.276572, "bpc": 0.000362},
        "server": {"cycles": 127887482, "instructions": 232273023, "ipc": 1.816511, "bpc": 0.00305}
    },
    6: {
        "client": {"cycles": 512953625, "instructions": 1190213056, "ipc": 2.320366, "bpc": 0.000374},
        "server": {"cycles": 166909509, "instructions": 351993197, "ipc": 2.108846, "bpc": 0.002605}
    },
    7: {
        "client": {"cycles": 491859991, "instructions": 1127340436, "ipc": 2.292018, "bpc": 0.000361},
        "server": {"cycles": 123690268, "instructions": 227782005, "ipc": 1.841544, "bpc": 0.003045}
    },
    8: {
        "client": {"cycles": 36430209, "instructions": 81574252, "ipc": 2.238776, "bpc": 0.004385},
        "server": {"cycles": 95138264, "instructions": 151397734, "ipc": 1.591911, "bpc": 0.004521}
    },
    9: {
        "client": {"cycles": 47460909, "instructions": 116097474, "ipc": 2.445694, "bpc": 0.003495},
        "server": {"cycles": 111370070, "instructions": 200569943, "ipc": 1.801013, "bpc": 0.004015}
    },
    10: {
        "client": {"cycles": 64425472, "instructions": 169544589, "ipc": 2.631675, "bpc": 0.002804},
        "server": {"cycles": 134362965, "instructions": 270697527, "ipc": 2.015047, "bpc": 0.00352}
    },
    11: {
        "client": {"cycles": 36693757, "instructions": 90614678, "ipc": 2.4693, "bpc": 0.004101},
        "server": {"cycles": 89399938, "instructions": 145915997, "ipc": 1.632819, "bpc": 0.004568}
    },
    12: {
        "client": {"cycles": 46359076, "instructions": 110204367, "ipc": 2.377397, "bpc": 0.004319},
        "server": {"cycles": 104283219, "instructions": 203674990, "ipc": 1.952927, "bpc": 0.004074}
    },
    13: {
        "client": {"cycles": 46047281, "instructions": 109594276, "ipc": 2.381352, "bpc": 0.004345},
        "server": {"cycles": 104476959, "instructions": 204038303, "ipc": 1.953216, "bpc": 0.004089}
    },
    14: {
        "client": {"cycles": 75923278, "instructions": 184316832, "ipc": 2.427801, "bpc": 0.002633},
        "server": {"cycles": 133193225, "instructions": 276404268, "ipc": 2.075206, "bpc": 0.003149}
    },
    15: {
        "client": {"cycles": 20616001, "instructions": 28007064, "ipc": 1.36044, "bpc": 0.005099},
        "server": {"cycles": 64220365, "instructions": 82488651, "ipc": 1.285082, "bpc": 0.004718}
    },
    16: {
        "client": {"cycles": 22370157, "instructions": 31626844, "ipc": 1.411886, "bpc": 0.004936},
        "server": {"cycles": 66640944, "instructions": 87456170, "ipc": 1.313218, "bpc": 0.004713}
    },
    17: {
        "client": {"cycles": 50235042, "instructions": 102073733, "ipc": 2.032628, "bpc": 0.002081},
        "server": {"cycles": 93315504, "instructions": 155555636, "ipc": 1.667225, "bpc": 0.003195}
    },
    18: {
        "client": {"cycles": 126918966, "instructions": 294784748, "ipc": 2.322831, "bpc": 0.000878},
        "server": {"cycles": 169594519, "instructions": 348481978, "ipc": 2.054766, "bpc": 0.001803}
    },
    19: {
        "client": {"cycles": 20227424, "instructions": 27299323, "ipc": 1.351757, "bpc": 0.00514},
        "server": {"cycles": 64225105, "instructions": 82876369, "ipc": 1.291688, "bpc": 0.004776}
    },
    20: {
        "client": {"cycles": 21090217, "instructions": 28987127, "ipc": 1.378091, "bpc": 0.005119},
        "server": {"cycles": 65750161, "instructions": 85851696, "ipc": 1.307716, "bpc": 0.004774}
    },
    21: {
        "client": {"cycles": 21664090, "instructions": 30440226, "ipc": 1.409205, "bpc": 0.005073},
        "server": {"cycles": 66878754, "instructions": 88408807, "ipc": 1.323721, "bpc": 0.004778}
    }
}

# ============================================
# 2. DESCRIÇÕES COMPLETAS (para legenda)
# ============================================
TEST_DESCRIPTIONS = {
    1: "RSA 2048 (Clássico)",
    2: "RSA 3072 (Clássico)",
    3: "RSA 4096 (Clássico)",
    4: "Ed25519 (Clássico)",
    5: "RSA 2048 (Híbrido SNTRUP)",
    6: "RSA 4096 (Híbrido SNTRUP)",
    7: "Ed25519 (Híbrido SNTRUP)",
    8: "RSA 2048 (Híbrido MLKEM)",
    9: "RSA 3072 (Híbrido MLKEM)",
    10: "RSA 4096 (Híbrido MLKEM)",
    11: "Ed25519 (Híbrido MLKEM)",
    12: "RSA 3072 + FALCON 512",
    13: "RSA 3072 + ML-DSA 44",
    14: "RSA 3072 + SPHINCS 2128",
    15: "FALCON 512 (PQC)",
    16: "FALCON 1024 (PQC)",
    17: "SPHINCS 2128 (PQC)",
    18: "SPHINCS 2256 (PQC)",
    19: "ML-DSA 44 (PQC)",
    20: "ML-DSA 65 (PQC)",
    21: "ML-DSA 87 (PQC)"
}

# ============================================
# 3. FUNÇÃO PRINCIPAL
# ============================================
def create_chart(scenario_num, tests, title, chart_type="CeI", 
                 font_title=32, font_axis_title=26, font_axis_tick=18, 
                 font_bar_label=16, font_group_label=22, font_legend=16,
                 width=1200, height=800):
    """
    Cria gráfico personalizado
    
    Args:
        scenario_num: número do cenário (para nome do arquivo)
        tests: lista de test IDs (ex: [1, 2, 3, 4])
        title: título do gráfico
        chart_type: "CeI" ou "IeB"
        font_*: tamanhos de fonte ajustáveis
        width, height: dimensões da imagem
    """
    
    # Definir métricas e labels
    if chart_type == "CeI":
        metric_left = "cycles"
        metric_right = "instructions"
        y1_label, y2_label = "Cycles", "Instructions"
        decimal_places = 0
        show_text = True  # Mostrar valores nas barras
    else:  # IeB
        metric_left = "ipc"
        metric_right = "bpc"
        y1_label, y2_label = "IPC", "BPC"
        decimal_places = 4
        show_text = True  # Mostrar valores nas barras
    
    # Construir dados do gráfico
    groups_data = []
    for metric, axis in [(metric_left, "left"), (metric_right, "right")]:
        for role in ["client", "server"]:
            if metric == "cycles":
                group_name = f"Clients Cycles" if role == "client" else "Servers Cycles"
            elif metric == "instructions":
                group_name = f"Clients Instructions" if role == "client" else "Servers Instructions"
            elif metric == "ipc":
                group_name = f"Clients IPC" if role == "client" else "Servers IPC"
            else:  # bpc
                group_name = f"Clients BPC" if role == "client" else "Servers BPC"
            
            bars = []
            for test_id in tests:
                value = DATA[test_id][role][metric]
                bars.append((test_id, value))
            groups_data.append({"group": group_name, "bars": bars, "axis": axis})
    
    # Cores suaves (paleta Safe do Plotly)
    group_palette = px.colors.qualitative.Safe
    group_colors = {gd["group"]: group_palette[i % len(group_palette)] for i, gd in enumerate(groups_data)}
    
    # Posicionamento com ESPAÇAMENTO MAIOR entre grupos
    GROUP_SPACING = 1.2  # Aumentado de 0.8 para 1.2
    group_centers = {gd["group"]: i * GROUP_SPACING for i, gd in enumerate(groups_data)}
    
    # Calcular offsets baseado no número de barras
    num_bars = len(tests)
    if num_bars == 2:
        offsets = [-0.18, 0.18]
        bar_width = 0.28
    elif num_bars == 3:
        offsets = [-0.24, 0.0, 0.24]
        bar_width = 0.22
    elif num_bars == 4:
        offsets = [-0.30, -0.10, 0.10, 0.30]
        bar_width = 0.18
    elif num_bars == 6:
        offsets = [-0.40, -0.24, -0.08, 0.08, 0.24, 0.40]
        bar_width = 0.14
    else:
        offsets = [-0.30, -0.10, 0.10, 0.30]
        bar_width = 0.18
    
    first_group = groups_data[0]["group"]
    last_group = groups_data[-1]["group"]
    leftmost = group_centers[first_group] + min(offsets)
    rightmost = group_centers[last_group] + max(offsets)
    PAD = 0.15
    xmin, xmax = leftmost - PAD, rightmost + PAD
    
    # Criar figura
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    x_tickvals, x_ticktext = [], []
    
    # Adicionar backgrounds coloridos - DOIS BLOCOS GRANDES
    # Bloco 1 (Azul): Client Cycles + Server Cycles (eixo esquerdo)
    # Bloco 2 (Verde): Client Instructions/IPC + Server Instructions/BPC (eixo direito)
    
    # Identificar quais grupos usam eixo esquerdo (índices 0 e 1)
    # e quais usam eixo direito (índices 2 e 3)
    
    # Calcular limites do primeiro bloco - EIXO ESQUERDO (grupos 0 e 1)
    first_group_center = group_centers[groups_data[0]["group"]]
    second_group_center = group_centers[groups_data[1]["group"]]
    third_group_center = group_centers[groups_data[2]["group"]]
    
    # Bloco azul vai do início até o meio entre grupo 1 e 2
    block1_left = first_group_center + min(offsets) - bar_width/2 - 0.08
    block1_right = (second_group_center + third_group_center) / 2  # Até o meio
    
    fig.add_shape(
        type="rect",
        xref="x", yref="paper",
        x0=block1_left, x1=block1_right,
        y0=0, y1=1,
        fillcolor="rgba(173, 216, 230, 0.15)",  # Azul claro
        line=dict(width=0),
        layer="below"
    )
    
    # Calcular limites do segundo bloco - EIXO DIREITO (grupos 2 e 3)
    fourth_group_center = group_centers[groups_data[3]["group"]]
    
    # Bloco verde vai do meio até o final
    block2_left = (second_group_center + third_group_center) / 2  # Do meio
    block2_right = fourth_group_center + max(offsets) + bar_width/2 + 0.08
    
    fig.add_shape(
        type="rect",
        xref="x", yref="paper",
        x0=block2_left, x1=block2_right,
        y0=0, y1=1,
        fillcolor="rgba(144, 238, 144, 0.15)",  # Verde claro
        line=dict(width=0),
        layer="below"
    )
    
    # Adicionar barras
    legend_added = set()  # Controle para adicionar legenda apenas uma vez
    
    for gi, gd in enumerate(groups_data):
        gname = gd["group"]
        cx = group_centers[gname]
        use_right = (gd["axis"] == "right")
        gcolor = group_colors[gname]
        
        for idx, (test_id, value) in enumerate(gd["bars"]):
            x_pos = cx + offsets[idx % len(offsets)]
            x_tickvals.append(x_pos)
            x_ticktext.append(f"({test_id})")  # Usando parênteses
            
            # Formatar valor usando a função
            text_val = format_number(value, decimal_places)
            
            # Nome completo para legenda
            legend_name = f"<b>({test_id}) {TEST_DESCRIPTIONS[test_id]}</b>"
            
            # Adicionar barra (sem mostrar na legenda)
            fig.add_trace(
                go.Bar(
                    x=[x_pos], y=[value], width=[bar_width],
                    name=legend_name,
                    legendgroup=f"test{test_id}",
                    showlegend=False,  # Não mostrar barras na legenda
                    marker=dict(
                        color=gcolor,
                        line=dict(width=0)
                    ),
                    text=[text_val], 
                    textposition="outside", 
                    cliponaxis=False,
                    textfont=dict(size=font_bar_label),
                    hovertemplate=f"<b>Teste ({test_id})</b><br>{TEST_DESCRIPTIONS[test_id]}<br>Grupo: {gname}<br>Valor: %{{y}}<extra></extra>",
                ),
                secondary_y=use_right
            )
            
            # Adicionar entrada de legenda apenas texto (primeira vez)
            if test_id not in legend_added:
                legend_added.add(test_id)
                fig.add_trace(
                    go.Scatter(
                        x=[None], y=[None],
                        mode='markers',
                        marker=dict(size=0, color='rgba(0,0,0,0)'),  # Marcador invisível
                        showlegend=True,
                        name=legend_name,
                        legendgroup=f"test{test_id}",
                        hoverinfo='skip'
                    ),
                    secondary_y=False
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
    
    # Adicionar linhas divisórias verticais entre grandes grupos
    for i in range(1, len(groups_data)):
        prev_center = group_centers[groups_data[i-1]["group"]]
        curr_center = group_centers[groups_data[i]["group"]]
        division_x = (prev_center + curr_center) / 2
        
        # Linha central (entre blocos azul e verde) - mais escura
        if i == 2:  # Linha central entre grupo 1 e 2 (entre eixo esquerdo e direito)
            fig.add_shape(
                type="line",
                xref="x", yref="paper",
                x0=division_x, x1=division_x,
                y0=0, y1=1,
                line=dict(color="rgba(0,0,0,0.45)", width=2, dash="dash")  # Mais escura e grossa
            )
        else:
            # Outras linhas divisórias (normais)
            fig.add_shape(
                type="line",
                xref="x", yref="paper",
                x0=division_x, x1=division_x,
                y0=0, y1=1,
                line=dict(color="rgba(0,0,0,0.3)", width=0, dash="dash")
            )
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",  # Negrito no título
            x=0.5, xanchor="center",
            font=dict(size=font_title, family="Inter, Segoe UI, Roboto, Arial")
        ),
        template="plotly_white",
        bargap=0.06,
        margin=dict(l=70, r=70, t=90, b=180),  # Reduzido de 340 para 180
        plot_bgcolor="rgba(250,250,252,1)",
        paper_bgcolor="white",
        legend=dict(
            orientation="h",  # Horizontal
            x=0.5, xanchor="center",
            y=-0.12, yanchor="top",  # Ajustado de -0.20 para -0.12
            font=dict(size=font_legend, weight='bold'),  # Negrito
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.5)",  # Borda mais escura (era 0.1)
            borderwidth=1.5,  # Borda um pouco mais grossa
            itemsizing='constant',
            tracegroupgap=10,
            itemwidth=30,
            itemclick=False,  # Desabilita clique
            itemdoubleclick=False  # Desabilita duplo clique
        ),
        showlegend=True,
        uniformtext_minsize=9,
        uniformtext_mode="hide",
        width=width,
        height=height
    )
    
    # Eixo X
    fig.update_xaxes(
        range=[xmin, xmax],
        tickvals=x_tickvals,
        ticktext=x_ticktext,
        tickfont=dict(size=font_axis_tick),
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
            yshift=-60,  # Ajustado para -60
            font=dict(size=font_group_label, color="rgba(0,0,0,0.75)"),
            align="center"
        )
    
    # Eixos Y
    fig.update_yaxes(
        title_text=f"<b>{y1_label}</b>",  # Negrito
        secondary_y=False,
        title_font=dict(size=font_axis_title),
        title_standoff=12,
        zeroline=False,
        gridcolor="rgba(0,0,0,0.08)",
        showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
        tickfont=dict(size=font_axis_tick)
    )
    fig.update_yaxes(
        title_text=f"<b>{y2_label}</b>",  # Negrito
        secondary_y=True,
        title_font=dict(size=font_axis_title),
        title_standoff=12,
        zeroline=False,
        showgrid=True,
        showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
        tickfont=dict(size=font_axis_tick)
    )
    
    return fig

# ============================================
# 4. GERAR TODOS OS CENÁRIOS
# ============================================

# CENÁRIO 1
fig = create_chart(1, [1, 2, 3, 4], "Cenário 1 - Algoritmos Clássicos", "CeI")
fig.write_image("cenario_1_CeI.png")
fig = create_chart(1, [1, 2, 3, 4], "Cenário 1 - Algoritmos Clássicos", "IeB")
fig.write_image("cenario_1_IeB.png")
print("✓ Cenário 1")

# CENÁRIO 2
fig = create_chart(2, [2, 9], "Cenário 2 - Clássico com KEX PQC Simples", "CeI")
fig.write_image("cenario_2_CeI.png")
fig = create_chart(2, [2, 9], "Cenário 2 - Clássico com KEX PQC Simples", "IeB")
fig.write_image("cenario_2_IeB.png")
print("✓ Cenário 2")

# CENÁRIO 3
fig = create_chart(3, [3, 4, 10, 11], "Cenário 3 - Clássico com KEX PQC Multiplo", "CeI")
fig.write_image("cenario_3_CeI.png")
fig = create_chart(3, [3, 4, 10, 11], "Cenário 3 - Clássico com KEX PQC Multiplo", "IeB")
fig.write_image("cenario_3_IeB.png")
print("✓ Cenário 3")

# CENÁRIO 4 - Aumentado para acomodar 6 barras
fig = create_chart(4, [5, 6, 7, 8, 10, 11], "Cenário 4 - Comparativo SNTRUP vs ML-KEM", "CeI", width=1800, height=900)
fig.write_image("cenario_4_CeI.png")
fig = create_chart(4, [5, 6, 7, 8, 10, 11], "Cenário 4 - Comparativo SNTRUP vs ML-KEM", "IeB", width=1800, height=900)
fig.write_image("cenario_4_IeB.png")
print("✓ Cenário 4")

# CENÁRIO 5
fig = create_chart(5, [9, 12, 15], "Cenário 5 - Composicão RSA, RSA+Falcon, Falcon", "CeI")
fig.write_image("cenario_5_CeI.png")
fig = create_chart(5, [9, 12, 15], "Cenário 5 - Composicão RSA, RSA+Falcon, Falcon", "IeB")
fig.write_image("cenario_5_IeB.png")
print("✓ Cenário 5")

# CENÁRIO 6
fig = create_chart(6, [9, 14, 17], "Cenário 6 - Composicão RSA, RSA+SPHINCS, SPHINCS", "CeI")
fig.write_image("cenario_6_CeI.png")
fig = create_chart(6, [9, 14, 17], "Cenário 6 - Composicão RSA, RSA+SPHINCS, SPHINCS", "IeB")
fig.write_image("cenario_6_IeB.png")
print("✓ Cenário 6")

# CENÁRIO 7
fig = create_chart(7, [9, 13, 19], "Cenário 7 - Composicão RSA, RSA+ML-DSA, ML-DSA", "CeI")
fig.write_image("cenario_7_CeI.png")
fig = create_chart(7, [9, 13, 19], "Cenário 7 - Composicão RSA, RSA+ML-DSA, ML-DSA", "IeB")
fig.write_image("cenario_7_IeB.png")
print("✓ Cenário 7")

# CENÁRIO 8
fig = create_chart(8, [1, 15], "Cenário 8 - Alto Desempenho", "CeI")
fig.write_image("cenario_8_CeI.png")
fig = create_chart(8, [1, 15], "Cenário 8 - Alto Desempenho", "IeB")
fig.write_image("cenario_8_IeB.png")
print("✓ Cenário 8")

# CENÁRIO 9
fig = create_chart(9, [15, 19], "Cenário 9 - PQC Chaves Menores", "CeI")
fig.write_image("cenario_9_CeI.png")
fig = create_chart(9, [15, 19], "Cenário 9 - PQC Chaves Menores", "IeB")
fig.write_image("cenario_9_IeB.png")
print("✓ Cenário 9")

# CENÁRIO 10
fig = create_chart(10, [17, 20], "Cenário 10 - PQC Chaves Intermediárias", "CeI")
fig.write_image("cenario_10_CeI.png")
fig = create_chart(10, [17, 20], "Cenário 10 - PQC Chaves Intermediárias", "IeB")
fig.write_image("cenario_10_IeB.png")
print("✓ Cenário 10")

# CENÁRIO 11
fig = create_chart(11, [16, 18, 21], "Cenário 11 - PQC Chaves Maiores", "CeI")
fig.write_image("cenario_11_CeI.png")
fig = create_chart(11, [16, 18, 21], "Cenário 11 - PQC Chaves Maiores", "IeB")
fig.write_image("cenario_11_IeB.png")
print("✓ Cenário 11")

# CENÁRIO 12
fig = create_chart(12, [15, 16], "Cenário 12 - Falcon diferentes tamanhos", "CeI")
fig.write_image("cenario_12_CeI.png")
fig = create_chart(12, [15, 16], "Cenário 12 - Falcon diferentes tamanhos", "IeB")
fig.write_image("cenario_12_IeB.png")
print("✓ Cenário 12")

# CENÁRIO 13
fig = create_chart(13, [17, 18], "Cenário 13 - SPHINCS diferentes tamanhos", "CeI")
fig.write_image("cenario_13_CeI.png")
fig = create_chart(13, [17, 18], "Cenário 13 - SPHINCS diferentes tamanhos", "IeB")
fig.write_image("cenario_13_IeB.png")
print("✓ Cenário 13")

# CENÁRIO 14
fig = create_chart(14, [19, 20, 21], "Cenário 14 - ML-DSA diferentes tamanhos", "CeI")
fig.write_image("cenario_14_CeI.png")
fig = create_chart(14, [19, 20, 21], "Cenário 14 - ML-DSA diferentes tamanhos", "IeB")
fig.write_image("cenario_14_IeB.png")
print("✓ Cenário 14")

print("Todos os 28 gráficos gerados!")
