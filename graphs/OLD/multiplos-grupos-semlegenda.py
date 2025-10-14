# pip install plotly>=5
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------------------------------------
# EXEMPLO: 8 grupos, 2 barras por grupo
#   - left: eixo Y esquerdo (valores menores)
#   - right: eixo Y direito (valores maiores)
# Substitua nomes/valores conforme seu caso.
# --------------------------------------------------
groups_data = [
    {"group": "G1", "left": ("Alpha", 42),   "right": ("Gamma", 190)},
    {"group": "G2", "left": ("Beta", 58),    "right": ("Delta", 240)},
    {"group": "G3", "left": ("Epsilon", 35), "right": ("Zeta", 120)},
    {"group": "G4", "left": ("Eta", 66),     "right": ("Theta", 210)},
    {"group": "G5", "left": ("Iota", 52),    "right": ("Kappa", 175)},
    {"group": "G6", "left": ("Lambda", 47),  "right": ("Mu", 205)},
    {"group": "G7", "left": ("Nu", 31),      "right": ("Xi", 160)},
    {"group": "G8", "left": ("Omicron", 73), "right": ("Pi", 230)},
]

# Constrói lista plana de barras
bars = []
for gd in groups_data:
    g = gd["group"]
    lname, lval = gd["left"]
    rname, rval = gd["right"]
    bars.append({"name": lname, "value": lval, "axis": "left",  "group": g})
    bars.append({"name": rname, "value": rval, "axis": "right", "group": g})

# Paleta moderna (16 cores)
palette16 = [
    "#6366F1","#22C55E","#F59E0B","#EC4899",
    "#0EA5E9","#E11D48","#8B5CF6","#84CC16",
    "#14B8A6","#FB923C","#06B6D4","#DB2777",
    "#4F46E5","#FACC15","#EF4444","#10B981",
]
# Mapeia cor por nome da barra
unique_names = [b["name"] for b in bars]
unique_names = list(dict.fromkeys(unique_names))
color_by_name = {name: palette16[i % len(palette16)] for i, name in enumerate(unique_names)}

# --------------------------------------------------
# Posicionamento: 8 clusters em X (centros 0..7)
# Dentro de cada grupo, duas barras coladas via offset
# --------------------------------------------------
group_centers = {gd["group"]: i for i, gd in enumerate(groups_data)}
offset_by_axis = {"left": -0.18, "right": +0.18}
bar_width = 0.34

xmin, xmax = -0.7, len(groups_data)-1 + 0.7  # deixa espaço para as linhas até os eixos

# --------------------------------------------------
# Figura com dois eixos Y
# --------------------------------------------------
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Barras (uma trace por barra para manter eixos separados)
x_tickvals = []
x_ticktext = []
for b in bars:
    x_pos = group_centers[b["group"]] + offset_by_axis[b["axis"]]
    x_tickvals.append(x_pos)
    x_ticktext.append(b["name"])

    fig.add_trace(
        go.Bar(
            x=[x_pos],
            y=[b["value"]],
            width=[bar_width],
            name=b["name"],  # pode ficar pesado no legend com 16 itens
            marker=dict(color=color_by_name[b["name"]], line=dict(width=0)),
            text=[f"{b['value']}"],
            textposition="outside",
            hovertemplate="<b>%{customdata[0]}</b><br>Grupo: %{customdata[1]}<br>Valor: %{y}<extra></extra>",
            customdata=[[b["name"], b["group"]]],
            showlegend=False,  # deixe True se quiser legenda para cada barra
        ),
        secondary_y=(b["axis"] == "right")
    )

# --------------------------------------------------
# Linhas tracejadas do topo da barra até o eixo Y correspondente
# Esquerda: da barra até xmin; Direita: da barra até xmax
# --------------------------------------------------
shapes = []
for b in bars:
    xi = group_centers[b["group"]] + offset_by_axis[b["axis"]]
    yv = b["value"]
    color = color_by_name[b["name"]]
    if b["axis"] == "left":
        shapes.append(dict(
            type="line", xref="x", yref="y",
            x0=xmin, x1=xi, y0=yv, y1=yv,
            line=dict(dash="dash", width=2, color=color)
        ))
    else:
        shapes.append(dict(
            type="line", xref="x", yref="y2",
            x0=xi, x1=xmax, y0=yv, y1=yv,
            line=dict(dash="dash", width=2, color=color)
        ))
fig.update_layout(shapes=shapes)

# --------------------------------------------------
# Aparência
# --------------------------------------------------
fig.update_layout(
    title=dict(
        text="8 grupos com 2 barras coladas, dois eixos Y e linhas até o eixo correspondente",
        x=0.5, xanchor="center",
        font=dict(size=22, family="Inter, Segoe UI, Roboto, Arial")
    ),
    template="plotly_white",
    bargap=0.05,
    margin=dict(l=50, r=50, t=70, b=100),  # b maior para caber rótulos duplos
    plot_bgcolor="rgba(250,250,252,1)",
    paper_bgcolor="white",
)

# Eixo X: rótulos nas posições das barras (nomes das barras)
fig.update_xaxes(
    range=[xmin, xmax],
    tickvals=x_tickvals,
    ticktext=x_ticktext,
    tickangle=0,
    showline=True, linewidth=1, linecolor="rgba(0,0,0,0.25)",
    tickfont=dict(size=12)
)

# Adiciona rótulos de GRUPO abaixo dos nomes das barras, centralizados em cada cluster
for gd in groups_data:
    cx = group_centers[gd["group"]]
    fig.add_annotation(
        x=cx, xref="x",
        y=0, yref="paper",  # base do gráfico
        text=f"<b>{gd['group']}</b>",
        showarrow=False,
        yshift=-35,  # empurra para baixo dos ticks das barras
        font=dict(size=12, color="rgba(0,0,0,0.75)"),
        align="center"
    )

# Y esquerdo
fig.update_yaxes(
    title_text="Unidade A",
    secondary_y=False,
    zeroline=False,
    gridcolor="rgba(0,0,0,0.08)",
    tickfont=dict(size=12)
)

# Y direito
fig.update_yaxes(
    title_text="Unidade B",
    secondary_y=True,
    zeroline=False,
    showgrid=False,
    tickfont=dict(size=12)
)

fig.show()

# Opcional: salvar como HTML interativo
# fig.write_html("barras_8_grupos_duplo_eixo.html", include_plotlyjs="cdn", full_html=True)

