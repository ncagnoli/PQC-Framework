# pip install plotly>=5
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------------------------------
# Dados: grupo e eixo de cada barra
# --------------------------------------------
bars = [
    {"name": "Alpha", "value": 42,  "axis": "left",  "group": "G1"},
    {"name": "Gamma", "value": 190, "axis": "right", "group": "G1"},
    {"name": "Beta",  "value": 58,  "axis": "left",  "group": "G2"},
    {"name": "Delta", "value": 240, "axis": "right", "group": "G2"},
]

palette = {"Alpha":"#6366F1","Gamma":"#F59E0B","Beta":"#22C55E","Delta":"#EC4899"}

# --------------------------------------------
# Posicionamento: dois clusters em X
# G1 no centro 0, G2 no centro 1
# Offset interno deixa as duas barras coladas
# --------------------------------------------
group_center = {"G1": 0.0, "G2": 1.0}
# offsets internos dentro de cada grupo
offset_by_axis = {"left": -0.18, "right": +0.18}
bar_width = 0.34  # ajuste fino de quão coladas ficam

# Limites do eixo X para que as linhas alcancem os eixos
xmin, xmax = -0.6, 1.6

# --------------------------------------------
# Figura com dois eixos Y
# --------------------------------------------
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Barras
for b in bars:
    x_pos = group_center[b["group"]] + offset_by_axis[b["axis"]]
    fig.add_trace(
        go.Bar(
            x=[x_pos],
            y=[b["value"]],
            width=[bar_width],
            name=b["name"],
            marker=dict(color=palette[b["name"]], line=dict(width=0)),
            text=[f"{b['value']}"],
            textposition="outside",
            hovertemplate="<b>%{customdata[0]}</b><br>Grupo: %{customdata[1]}<br>Valor: %{y}<extra></extra>",
            customdata=[[b["name"], b["group"]]],
        ),
        secondary_y=(b["axis"] == "right")
    )

# --------------------------------------------
# Linhas tracejadas do topo da barra até o eixo Y correspondente
# --------------------------------------------
shapes = []
for b in bars:
    xi = group_center[b["group"]] + offset_by_axis[b["axis"]]
    yv = b["value"]
    color = palette[b["name"]]
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

# --------------------------------------------
# Aparência moderna
# --------------------------------------------
fig.update_layout(
    title=dict(
        text="Barras agrupadas por G1 e G2, dois eixos Y e linhas tracejadas até o eixo",
        x=0.5, xanchor="center",
        font=dict(size=22, family="Inter, Segoe UI, Roboto, Arial")
    ),
    template="plotly_white",
    bargap=0.05,
    margin=dict(l=40, r=40, t=70, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="rgba(250,250,252,1)",
    paper_bgcolor="white"
)

# Eixo X: mostra apenas os rótulos dos grupos
fig.update_xaxes(
    range=[xmin, xmax],
    tickvals=[group_center["G1"], group_center["G2"]],
    ticktext=["G1", "G2"],
    showline=True, linewidth=1, linecolor="rgba(0,0,0,0.25)",
    tickfont=dict(size=12)
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

# Para salvar em HTML interativo:
# fig.write_html("barras_grupos_duplo_eixo.html", include_plotlyjs="cdn", full_html=True)

