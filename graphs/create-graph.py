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
# 1.1 CALCULAR MÁXIMOS GLOBAIS (IGNORANDO SNTRUP)
# ============================================
SNTRUP_IDS = [5, 6, 7]

_all_cycles = []
_all_instructions = []
_all_ipc = []
_all_bpc = []

# Varre todos os dados, MAS PULA SNTRUP
for t_id in DATA:
    if t_id in SNTRUP_IDS:
        continue  # Ignora SNTRUP no cálculo da escala global
        
    for role in ["client", "server"]:
        _all_cycles.append(DATA[t_id][role]["cycles"])
        _all_instructions.append(DATA[t_id][role]["instructions"])
        _all_ipc.append(DATA[t_id][role]["ipc"])
        _all_bpc.append(DATA[t_id][role]["bpc"])

# Define máximos com margem de segurança
GLOBAL_MAX_CYCLES = max(_all_cycles) * 1.15
GLOBAL_MAX_INSTRUCTIONS = max(_all_instructions) * 1.15
GLOBAL_MAX_IPC = max(_all_ipc) * 1.15
GLOBAL_MAX_BPC = max(_all_bpc) * 1.15

print(f"Escala Global Fixa (sem SNTRUP): Cycles={GLOBAL_MAX_CYCLES:.1e}, Instr={GLOBAL_MAX_INSTRUCTIONS:.1e}")

# ============================================
# 2. DESCRIÇÕES COMPLETAS
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
    
    # Verificar se este gráfico contém SNTRUP
    has_sntrup = any(t_id in SNTRUP_IDS for t_id in tests)
    
    # Se tiver SNTRUP, usa escala automática (None). 
    # Se não, usa a escala global calculada anteriormente.
    if chart_type == "CeI":
        metric_left = "cycles"
        metric_right = "instructions"
        y1_label, y2_label = "Cycles", "Instructions"
        decimal_places = 0
        
        if has_sntrup:
            y1_range = None # Automático
            y2_range = None # Automático
        else:
            y1_range = [0, GLOBAL_MAX_CYCLES]
            y2_range = [0, GLOBAL_MAX_INSTRUCTIONS]
            
    else:  # IeB
        metric_left = "ipc"
        metric_right = "bpc"
        y1_label, y2_label = "IPC", "BPC"
        decimal_places = 4
        
        if has_sntrup:
            y1_range = None
            y2_range = None
        else:
            y1_range = [0, GLOBAL_MAX_IPC]
            y2_range = [0, GLOBAL_MAX_BPC]
    
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
    
    # Cores
    group_palette = px.colors.qualitative.Safe
    group_colors = {gd["group"]: group_palette[i % len(group_palette)] for i, gd in enumerate(groups_data)}
    
    # Posicionamento
    GROUP_SPACING = 1.2
    group_centers = {gd["group"]: i * GROUP_SPACING for i, gd in enumerate(groups_data)}
    
    num_bars = len(tests)
    if num_bars == 2:
        offsets = [-0.18, 0.18]; bar_width = 0.28
    elif num_bars == 3:
        offsets = [-0.24, 0.0, 0.24]; bar_width = 0.22
    elif num_bars == 4:
        offsets = [-0.30, -0.10, 0.10, 0.30]; bar_width = 0.18
    elif num_bars == 6:
        offsets = [-0.40, -0.24, -0.08, 0.08, 0.24, 0.40]; bar_width = 0.14
    else:
        offsets = [-0.30, -0.10, 0.10, 0.30]; bar_width = 0.18
    
    first_group = groups_data[0]["group"]
    last_group = groups_data[-1]["group"]
    leftmost = group_centers[first_group] + min(offsets)
    rightmost = group_centers[last_group] + max(offsets)
    PAD = 0.15
    xmin, xmax = leftmost - PAD, rightmost + PAD
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    x_tickvals, x_ticktext = [], []
    
    # Backgrounds
    c1 = group_centers[groups_data[0]["group"]]
    c2 = group_centers[groups_data[1]["group"]]
    c3 = group_centers[groups_data[2]["group"]]
    c4 = group_centers[groups_data[3]["group"]]
    
    b1_left = c1 + min(offsets) - bar_width/2 - 0.08
    b1_right = (c2 + c3) / 2
    fig.add_shape(type="rect", xref="x", yref="paper", x0=b1_left, x1=b1_right, y0=0, y1=1,
                  fillcolor="rgba(173, 216, 230, 0.15)", line=dict(width=0), layer="below")
    
    b2_left = (c2 + c3) / 2
    b2_right = c4 + max(offsets) + bar_width/2 + 0.08
    fig.add_shape(type="rect", xref="x", yref="paper", x0=b2_left, x1=b2_right, y0=0, y1=1,
                  fillcolor="rgba(144, 238, 144, 0.15)", line=dict(width=0), layer="below")
    
    legend_added = set()
    
    for gi, gd in enumerate(groups_data):
        gname = gd["group"]
        cx = group_centers[gname]
        use_right = (gd["axis"] == "right")
        gcolor = group_colors[gname]
        
        for idx, (test_id, value) in enumerate(gd["bars"]):
            x_pos = cx + offsets[idx % len(offsets)]
            x_tickvals.append(x_pos)
            x_ticktext.append(f"({test_id})")
            
            text_val = format_number(value, decimal_places)
            legend_name = f"<b>({test_id}) {TEST_DESCRIPTIONS[test_id]}</b>"
            
            fig.add_trace(
                go.Bar(
                    x=[x_pos], y=[value], width=[bar_width],
                    name=legend_name, legendgroup=f"test{test_id}", showlegend=False,
                    marker=dict(color=gcolor, line=dict(width=0)),
                    text=[text_val], textposition="outside", cliponaxis=False,
                    textfont=dict(size=font_bar_label),
                    hovertemplate=f"<b>Teste ({test_id})</b><br>{TEST_DESCRIPTIONS[test_id]}<br>Grupo: {gname}<br>Valor: %{{y}}<extra></extra>",
                ),
                secondary_y=use_right
            )
            
            if test_id not in legend_added:
                legend_added.add(test_id)
                fig.add_trace(
                    go.Scatter(
                        x=[None], y=[None], mode='markers',
                        marker=dict(size=0, color='rgba(0,0,0,0)'),
                        showlegend=True, name=legend_name, legendgroup=f"test{test_id}", hoverinfo='skip'
                    ),
                    secondary_y=False
                )
            
            # Linha tracejada
            if use_right:
                fig.add_shape(type="line", xref="x", yref="y2", x0=x_pos, x1=xmax, y0=value, y1=value,
                              line=dict(dash="dot", width=2, color=gcolor))
            else:
                fig.add_shape(type="line", xref="x", yref="y", x0=xmin, x1=x_pos, y0=value, y1=value,
                              line=dict(dash="dot", width=2, color=gcolor))
    
    # Divisórias
    for i in range(1, len(groups_data)):
        p = group_centers[groups_data[i-1]["group"]]
        c = group_centers[groups_data[i]["group"]]
        div_x = (p + c) / 2
        line_style = dict(color="rgba(0,0,0,0.45)", width=2, dash="dash") if i == 2 else dict(color="rgba(0,0,0,0.3)", width=0, dash="dash")
        fig.add_shape(type="line", xref="x", yref="paper", x0=div_x, x1=div_x, y0=0, y1=1, line=line_style)
    
    # Layout
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.5, xanchor="center", font=dict(size=font_title)),
        template="plotly_white", bargap=0.06,
        margin=dict(l=70, r=70, t=90, b=180),
        plot_bgcolor="rgba(250,250,252,1)", paper_bgcolor="white",
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.12, yanchor="top",
                    font=dict(size=font_legend, weight='bold'), bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="rgba(0,0,0,0.5)", borderwidth=1.5, itemwidth=30),
        width=width, height=height
    )
    
    fig.update_xaxes(range=[xmin, xmax], tickvals=x_tickvals, ticktext=x_ticktext,
                     tickfont=dict(size=font_axis_tick), showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)")
    
    for gd in groups_data:
        fig.add_annotation(x=group_centers[gd["group"]], xref="x", y=0, yref="paper", text=f"<b>{gd['group']}</b>",
                           showarrow=False, yshift=-60, font=dict(size=font_group_label, color="rgba(0,0,0,0.75)"))
    
    # Eixos Y (Lógica do Range)
    fig.update_yaxes(title_text=f"<b>{y1_label}</b>", secondary_y=False, range=y1_range,
                     title_font=dict(size=font_axis_title), showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
                     tickfont=dict(size=font_axis_tick))
    
    fig.update_yaxes(title_text=f"<b>{y2_label}</b>", secondary_y=True, range=y2_range,
                     title_font=dict(size=font_axis_title), showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
                     tickfont=dict(size=font_axis_tick))
    
    return fig

# ============================================
# 4. GERAR GRÁFICOS
# ============================================

scenarios = [
    (1, [1, 2, 3, 4], "Cenário 1 - Algoritmos Clássicos"),
    (2, [2, 9], "Cenário 2 - Clássico com KEX PQC Simples"),
    (3, [3, 4, 10, 11], "Cenário 3 - Clássico com KEX PQC Multiplo"),
    (4, [5, 6, 7, 8, 10, 11], "Cenário 4 - Comparativo SNTRUP vs ML-KEM", 1800, 900),
    (5, [9, 12, 15], "Cenário 5 - Composicão RSA, RSA+Falcon, Falcon"),
    (6, [9, 14, 17], "Cenário 6 - Composicão RSA, RSA+SPHINCS, SPHINCS"),
    (7, [9, 13, 19], "Cenário 7 - Composicão RSA, RSA+ML-DSA, ML-DSA"),
    (8, [1, 15], "Cenário 8 - Alto Desempenho"),
    (9, [15, 19], "Cenário 9 - PQC Chaves Menores"),
    (10, [17, 20], "Cenário 10 - PQC Chaves Intermediárias"),
    (11, [16, 18, 21], "Cenário 11 - PQC Chaves Maiores"),
    (12, [15, 16], "Cenário 12 - Falcon diferentes tamanhos"),
    (13, [17, 18], "Cenário 13 - SPHINCS diferentes tamanhos"),
    (14, [19, 20, 21], "Cenário 14 - ML-DSA diferentes tamanhos"),
]

for s in scenarios:
    s_num, tests, title = s[0], s[1], s[2]
    w, h = (s[3], s[4]) if len(s) > 3 else (1200, 800)
    
    print(f"Gerando Cenário {s_num}...")
    
    fig = create_chart(s_num, tests, title, "CeI", width=w, height=h)
    fig.write_image(f"cenario_{s_num}_CeI.png")
    
    fig = create_chart(s_num, tests, title, "IeB", width=w, height=h)
    fig.write_image(f"cenario_{s_num}_IeB.png")

print("Concluído!")
