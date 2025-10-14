# pip install plotly>=5 kaleido
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ============================================
# 1. DADOS EMBUTIDOS
# ============================================
DATA = {
    # Test ID: {role: {metric: value}}
    1: {
        "client": {"cycles": 32644650, "instr": 73901621, "ipc": 2.264186, "bpc": 0.004174},
        "server": {"cycles": 89540747, "instr": 146150240, "ipc": 1.632213, "bpc": 0.004322}
    },
    2: {
        "client": {"cycles": 46303028, "instr": 113234505, "ipc": 2.445386, "bpc": 0.003486},
        "server": {"cycles": 110889617, "instr": 199057853, "ipc": 1.795313, "bpc": 0.004022}
    },
    3: {
        "client": {"cycles": 57021879, "instr": 151918155, "ipc": 2.664012, "bpc": 0.002658},
        "server": {"cycles": 128495569, "instr": 265876400, "ipc": 2.069169, "bpc": 0.003358}
    },
    4: {
        "client": {"cycles": 36007279, "instr": 89048317, "ipc": 2.472653, "bpc": 0.003814},
        "server": {"cycles": 85315996, "instr": 141632836, "ipc": 1.660072, "bpc": 0.004385}
    },
    5: {
        "client": {"cycles": 488553925, "instr": 1112218701, "ipc": 2.276572, "bpc": 0.000362},
        "server": {"cycles": 127887482, "instr": 232273023, "ipc": 1.816511, "bpc": 0.00305}
    },
    6: {
        "client": {"cycles": 512953625, "instr": 1190213056, "ipc": 2.320366, "bpc": 0.000374},
        "server": {"cycles": 166909509, "instr": 351993197, "ipc": 2.108846, "bpc": 0.002605}
    },
    7: {
        "client": {"cycles": 491859991, "instr": 1127340436, "ipc": 2.292018, "bpc": 0.000361},
        "server": {"cycles": 123690268, "instr": 227782005, "ipc": 1.841544, "bpc": 0.003045}
    },
    8: {
        "client": {"cycles": 36430209, "instr": 81574252, "ipc": 2.238776, "bpc": 0.004385},
        "server": {"cycles": 95138264, "instr": 151397734, "ipc": 1.591911, "bpc": 0.004521}
    },
    9: {
        "client": {"cycles": 47460909, "instr": 116097474, "ipc": 2.445694, "bpc": 0.003495},
        "server": {"cycles": 111370070, "instr": 200569943, "ipc": 1.801013, "bpc": 0.004015}
    },
    10: {
        "client": {"cycles": 64425472, "instr": 169544589, "ipc": 2.631675, "bpc": 0.002804},
        "server": {"cycles": 134362965, "instr": 270697527, "ipc": 2.015047, "bpc": 0.00352}
    },
    11: {
        "client": {"cycles": 36693757, "instr": 90614678, "ipc": 2.4693, "bpc": 0.004101},
        "server": {"cycles": 89399938, "instr": 145915997, "ipc": 1.632819, "bpc": 0.004568}
    },
    12: {
        "client": {"cycles": 46359076, "instr": 110204367, "ipc": 2.377397, "bpc": 0.004319},
        "server": {"cycles": 104283219, "instr": 203674990, "ipc": 1.952927, "bpc": 0.004074}
    },
    13: {
        "client": {"cycles": 46047281, "instr": 109594276, "ipc": 2.381352, "bpc": 0.004345},
        "server": {"cycles": 104476959, "instr": 204038303, "ipc": 1.953216, "bpc": 0.004089}
    },
    14: {
        "client": {"cycles": 75923278, "instr": 184316832, "ipc": 2.427801, "bpc": 0.002633},
        "server": {"cycles": 133193225, "instr": 276404268, "ipc": 2.075206, "bpc": 0.003149}
    },
    15: {
        "client": {"cycles": 20616001, "instr": 28007064, "ipc": 1.36044, "bpc": 0.005099},
        "server": {"cycles": 64220365, "instr": 82488651, "ipc": 1.285082, "bpc": 0.004718}
    },
    16: {
        "client": {"cycles": 22370157, "instr": 31626844, "ipc": 1.411886, "bpc": 0.004936},
        "server": {"cycles": 66640944, "instr": 87456170, "ipc": 1.313218, "bpc": 0.004713}
    },
    17: {
        "client": {"cycles": 50235042, "instr": 102073733, "ipc": 2.032628, "bpc": 0.002081},
        "server": {"cycles": 93315504, "instr": 155555636, "ipc": 1.667225, "bpc": 0.003195}
    },
    18: {
        "client": {"cycles": 126918966, "instr": 294784748, "ipc": 2.322831, "bpc": 0.000878},
        "server": {"cycles": 169594519, "instr": 348481978, "ipc": 2.054766, "bpc": 0.001803}
    },
    19: {
        "client": {"cycles": 20227424, "instr": 27299323, "ipc": 1.351757, "bpc": 0.00514},
        "server": {"cycles": 64225105, "instr": 82876369, "ipc": 1.291688, "bpc": 0.004776}
    },
    20: {
        "client": {"cycles": 21090217, "instr": 28987127, "ipc": 1.378091, "bpc": 0.005119},
        "server": {"cycles": 65750161, "instr": 85851696, "ipc": 1.307716, "bpc": 0.004774}
    },
    21: {
        "client": {"cycles": 21664090, "instr": 30440226, "ipc": 1.409205, "bpc": 0.005073},
        "server": {"cycles": 66878754, "instr": 88408807, "ipc": 1.323721, "bpc": 0.004778}
    }
}

# ============================================
# 2. NOMES DAS BARRAS (personalizáveis)
# ============================================
BAR_NAMES = {
    1: "RSA 2048",
    2: "RSA 3072",
    3: "RSA 4096",
    4: "Ed25519",
    5: "RSA 2048",
    6: "RSA 4096",
    7: "Ed25519",
    8: "RSA 2048",
    9: "RSA 3072",
    10: "RSA 4096",
    11: "Ed25519",
    12: "RSA 3072<br>+<br>FALCON 512",
    13: "RSA 3072<br>+<br>ML-DSA 44",
    14: "RSA 3072<br>+<br>SPHINCS 2128",
    15: "FALCON 512",
    16: "FALCON 1024",
    17: "SPHINCS 2128",
    18: "SPHINCS 2256",
    19: "ML-DSA 44",
    20: "ML-DSA 65",
    21: "ML-DSA 87"
}

# ============================================
# 3. FUNÇÃO PRINCIPAL
# ============================================
def create_chart(scenario_num, tests, title, chart_type="CeI", 
                 font_title=32, font_axis_title=26, font_axis_tick=18, 
                 font_bar_label=16, font_group_label=22):
    """
    Cria gráfico personalizado
    
    Args:
        scenario_num: número do cenário (para nome do arquivo)
        tests: lista de test IDs (ex: [1, 2, 3, 4])
        title: título do gráfico
        chart_type: "CeI" ou "IeB"
        font_*: tamanhos de fonte ajustáveis
    """
    
    # Definir métricas e labels
    if chart_type == "CeI":
        metric_left = "cycles"
        metric_right = "instr"
        y1_label, y2_label = "Cycles", "Instructions"
        decimal_places = 0  # sem decimais para números grandes
    else:  # IeB
        metric_left = "ipc"
        metric_right = "bpc"
        y1_label, y2_label = "IPC", "BPC"
        decimal_places = 4
    
    # Construir dados do gráfico
    groups_data = []
    for metric, axis in [(metric_left, "left"), (metric_right, "right")]:
        for role in ["client", "server"]:
            group_name = f"{role.capitalize()} {metric_left if axis == 'left' else metric_right}"
            bars = []
            for test_id in tests:
                value = DATA[test_id][role][metric]
                name = BAR_NAMES[test_id]
                bars.append((name, value))
            groups_data.append({"group": group_name, "bars": bars, "axis": axis})
    
    # Cores e posicionamento
    group_palette = px.colors.qualitative.Safe
    group_colors = {gd["group"]: group_palette[i % len(group_palette)] for i, gd in enumerate(groups_data)}
    
    GROUP_SPACING = 0.8
    group_centers = {gd["group"]: i * GROUP_SPACING for i, gd in enumerate(groups_data)}
    
    # Calcular offsets baseado no número de barras
    num_bars = len(tests)
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
            x_ticktext.append(name)
            
            # Formatar valor
            if decimal_places == 0:
                text_val = f"{value:,.0f}"
            else:
                text_val = f"{value:.{decimal_places}f}"
            
            fig.add_trace(
                go.Bar(
                    x=[x_pos], y=[value], width=[bar_width],
                    name=gname,
                    legendgroup=gname,
                    showlegend=(idx == 0),
                    marker=dict(color=gcolor, line=dict(width=0)),
                    text=[text_val], 
                    textposition="outside", 
                    cliponaxis=False,
                    textfont=dict(size=font_bar_label),
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
            text=title,
            x=0.5, xanchor="center",
            font=dict(size=font_title, family="Inter, Segoe UI, Roboto, Arial")
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
            yshift=-70,
            font=dict(size=font_group_label, color="rgba(0,0,0,0.75)"),
            align="center"
        )
    
    # Eixos Y
    fig.update_yaxes(
        title_text=y1_label,
        secondary_y=False,
        title_font=dict(size=font_axis_title),
        title_standoff=12,
        zeroline=False,
        gridcolor="rgba(0,0,0,0.08)",
        showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
        tickfont=dict(size=font_axis_tick)
    )
    fig.update_yaxes(
        title_text=y2_label,
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
fig = create_chart(2, [2, 9], "Cenário 2 - Clássico vs KEX PQC", "CeI")
fig.write_image("cenario_2_CeI.png")
fig = create_chart(2, [2, 9], "Cenário 2 - Clássico vs KEX PQC", "IeB")
fig.write_image("cenario_2_IeB.png")
print("✓ Cenário 2")

# CENÁRIO 3
fig = create_chart(3, [3, 4, 10, 11], "Cenário 3 - Clássico vs KEX PQC", "CeI")
fig.write_image("cenario_3_CeI.png")
fig = create_chart(3, [3, 4, 10, 11], "Cenário 3 - Clássico vs KEX PQC", "IeB")
fig.write_image("cenario_3_IeB.png")
print("✓ Cenário 3")

# CENÁRIO 4
fig = create_chart(4, [5, 6, 7, 8, 10, 11], "Cenário 4 - Clássicos com KEX PQC", "CeI")
fig.write_image("cenario_4_CeI.png")
fig = create_chart(4, [5, 6, 7, 8, 10, 11], "Cenário 4 - Clássicos com KEX PQC", "IeB")
fig.write_image("cenario_4_IeB.png")
print("✓ Cenário 4")

# CENÁRIO 5
fig = create_chart(5, [9, 12, 15], "Cenário 5 - RSA+FALCON", "CeI")
fig.write_image("cenario_5_CeI.png")
fig = create_chart(5, [9, 12, 15], "Cenário 5 - RSA+FALCON", "IeB")
fig.write_image("cenario_5_IeB.png")
print("✓ Cenário 5")

# CENÁRIO 6
fig = create_chart(6, [9, 14, 17], "Cenário 6 - RSA+SPHINCS", "CeI")
fig.write_image("cenario_6_CeI.png")
fig = create_chart(6, [9, 14, 17], "Cenário 6 - RSA+SPHINCS", "IeB")
fig.write_image("cenario_6_IeB.png")
print("✓ Cenário 6")

# CENÁRIO 7
fig = create_chart(7, [9, 13, 19], "Cenário 7 - RSA+ML-DSA", "CeI")
fig.write_image("cenario_7_CeI.png")
fig = create_chart(7, [9, 13, 19], "Cenário 7 - RSA+ML-DSA", "IeB")
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
fig = create_chart(10, [17, 20], "Cenário 10 - PQC Chaves Maiores", "CeI")
fig.write_image("cenario_10_CeI.png")
fig = create_chart(10, [17, 20], "Cenário 10 - PQC Chaves Maiores", "IeB")
fig.write_image("cenario_10_IeB.png")
print("✓ Cenário 10")

# CENÁRIO 11
fig = create_chart(11, [16, 18, 21], "Cenário 11 - PQC Chaves Grandes", "CeI")
fig.write_image("cenario_11_CeI.png")
fig = create_chart(11, [16, 18, 21], "Cenário 11 - PQC Chaves Grandes", "IeB")
fig.write_image("cenario_11_IeB.png")
print("✓ Cenário 11")

# CENÁRIO 12
fig = create_chart(12, [15, 16], "Cenário 12 - FALCON Tamanhos", "CeI")
fig.write_image("cenario_12_CeI.png")
fig = create_chart(12, [15, 16], "Cenário 12 - FALCON Tamanhos", "IeB")
fig.write_image("cenario_12_IeB.png")
print("✓ Cenário 12")

# CENÁRIO 13
fig = create_chart(13, [17, 18], "Cenário 13 - SPHINCS Tamanhos", "CeI")
fig.write_image("cenario_13_CeI.png")
fig = create_chart(13, [17, 18], "Cenário 13 - SPHINCS Tamanhos", "IeB")
fig.write_image("cenario_13_IeB.png")
print("✓ Cenário 13")

# CENÁRIO 14
fig = create_chart(14, [19, 20, 21], "Cenário 14 - ML-DSA Tamanhos", "CeI")
fig.write_image("cenario_14_CeI.png")
fig = create_chart(14, [19, 20, 21], "Cenário 14 - ML-DSA Tamanhos", "IeB")
fig.write_image("cenario_14_IeB.png")
print("✓ Cenário 14")

print("\n🎉 Todos os 28 gráficos gerados!")
