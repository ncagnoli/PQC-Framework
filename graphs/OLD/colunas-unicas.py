# pip install plotly>=5
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------------------------------
# Dados
# --------------------------------------------
bars = [
    {"name": "Alpha", "value": 42,  "axis": "left"},
    {"name": "Beta",  "value": 58,  "axis": "left"},
    {"name": "Gamma", "value": 190, "axis": "right"},
    {"name": "Delta", "value": 240, "axis": "right"},
]

palette = ["#6366F1", "#22C55E", "#F59E0B", "#EC4899"]

# Usaremos posições numéricas no eixo X para facilitar as linhas até a borda do gráfico
cats = [b["name"] for b in bars]
xpos = {name: i for i, name in enumerate(cats)}
n = len(cats)

# Margens para o range do X, garantindo que as linhas encostem nos eixos
xmin = -0.6
xmax = (n - 1) + 0.6

# --------------------------------------------
# Figura com dois eixos Y
# --------------------------------------------
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Barras
for i, b in enumerate(bars):
    is_right = (b["axis"] == "right")
    fig.add_trace(
        go.Bar(
            x=[xpos[b["name"]]],
            y=[b["value"]],
            name=b["name"],
            marker=dict(color=palette[i], line=dict(width=0)),
            text=[f"{b['value']}"],
            textposition="outside",
            hovertemplate="<b>%{text}</b><extra></extra>",
        ),
        secondary_y=is_right
    )

# --------------------------------------------
# Linhas tracejadas do topo da barra até o eixo Y equivalente
# Esquerda: da barra até xmin
# Direita:  da barra até xmax
# --------------------------------------------
shapes = []
for i, b in enumerate(bars):
    xi = xpos[b["name"]]
    yv = b["value"]
    if b["axis"] == "left":
        shapes.append(dict(
            type="line",
            xref="x", yref="y",
            x0=xmin, x1=xi,
            y0=yv,  y1=yv,
            line=dict(dash="dash", width=2, color=palette[i])
        ))
    else:
        shapes.append(dict(
            type="line",
            xref="x", yref="y2",
            x0=xi,  x1=xmax,
            y0=yv,  y1=yv,
            line=dict(dash="dash", width=2, color=palette[i])
        ))

fig.update_layout(shapes=shapes)

# --------------------------------------------
# Aparência moderna
# --------------------------------------------
fig.update_layout(
    title=dict(
        text="Barras com dois eixos Y e linhas tracejadas até o eixo correspondente",
        x=0.5,
        xanchor="center",
        font=dict(size=22, family="Inter, Segoe UI, Roboto, Arial")
    ),
    template="plotly_white",
    bargap=0.35,
    margin=dict(l=40, r=40, t=70, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="rgba(250,250,252,1)",
    paper_bgcolor="white"
)

# Eixo X com rótulos das categorias
fig.update_xaxes(
    range=[xmin, xmax],
    tickvals=list(range(n)),
    ticktext=cats,
    showline=True,
    linewidth=1,
    linecolor="rgba(0,0,0,0.25)",
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

# Opcional: salvar como HTML interativo
# fig.write_html("barras_duplo_eixo_linhas_ate_eixo.html", include_plotlyjs="cdn", full_html=True)

