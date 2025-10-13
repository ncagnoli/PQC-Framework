# pip install plotly>=5
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# --------------------------------------------------
# 4 grupos, 4 barras em cada grupo
# Em cada grupo: duas barras no eixo esquerdo e duas no direito
# --------------------------------------------------
groups_data = [
    {"group": "(1) RSA 2048",
     "bars": [("(1)C", 32644650, "left"), ("(1)S", 89540747, "left"),
              ("(1)C", 73901621, "right"), ("(1)S", 146150240, "right")]},
    {"group": "(2) RSA 3072",
     "bars": [("(2)C", 46303028, "left"), ("(2)S", 110889617, "left"),
              ("(2)C", 113234505, "right"), ("(2)S", 199057853, "right")]},
    {"group": "(3) RSA 4096",
     "bars": [("(3)C", 57021879, "left"), ("(3)S", 128495569, "left"),
              ("(3)C", 151918155, "right"), ("(3)S", 265876400, "right")]},
    {"group": "(4)Ed25519",
     "bars": [("(4)C", 36007279, "left"), ("(4)S", 85315996, "left"),
              ("(4)C", 89048317, "right"), ("(4)S", 141632836, "right")]},
]

# Paleta de cores por nome
palette16 = [
    "#6366F1","#22C55E","#F59E0B","#EC4899",
    "#0EA5E9","#E11D48","#8B5CF6","#84CC16",
    "#14B8A6","#FB923C","#06B6D4","#DB2777",
    "#4F46E5","#FACC15","#EF4444","#10B981",
]
# Mapeia cor por nome de barra
all_names = []
for gd in groups_data:
    for name, _, _ in gd["bars"]:
        if name not in all_names:
            all_names.append(name)
color_by_name = {name: palette16[i % len(palette16)] for i, name in enumerate(all_names)}

# --------------------------------------------------
# Posicionamento
# Cada grupo no centro 0..3
# Dentro do grupo usamos 4 offsets para colar as barras:
# duas do eixo esquerdo à esquerda e duas do eixo direito à direita
# --------------------------------------------------
group_centers = {gd["group"]: i for i, gd in enumerate(groups_data)}
offsets_left  = [-0.27, -0.09]
offsets_right = [ +0.09, +0.27]
bar_width = 0.16

xmin, xmax = -0.8, len(groups_data) - 1 + 0.8

fig = make_subplots(specs=[[{"secondary_y": True}]])

x_tickvals, x_ticktext = [], []
shapes = []

# --------------------------------------------------
# Adiciona barras e cria as linhas tracejadas até o eixo correspondente
# --------------------------------------------------
for gd in groups_data:
    gname = gd["group"]
    cx = group_centers[gname]

    # separe barras por eixo para aplicar offsets estáveis
    left_bars  = [(n, v, a) for (n, v, a) in gd["bars"] if a == "left"]
    right_bars = [(n, v, a) for (n, v, a) in gd["bars"] if a == "right"]

    # garante 2 por eixo, mas funciona mesmo se variar
    for (idx, (n, v, a)) in enumerate(left_bars):
        x_pos = cx + offsets_left[min(idx, len(offsets_left)-1)]
        x_tickvals.append(x_pos)
        x_ticktext.append(n)

        fig.add_trace(
            go.Bar(
                x=[x_pos], y=[v], width=[bar_width],
                name=n, legendgroup="left",
                marker=dict(color=color_by_name[n], line=dict(width=0)),
                text=[f"{v}"], textposition="outside",
                hovertemplate="<b>%{customdata[0]}</b><br>Grupo: %{customdata[1]}<br>Valor: %{y}<extra></extra>",
                customdata=[[n, gname]],
                showlegend=True,
            ),
            secondary_y=False
        )
        # linha tracejada do topo até o eixo esquerdo
        shapes.append(dict(
            type="line", xref="x", yref="y",
            x0=xmin, x1=x_pos, y0=v, y1=v,
            line=dict(dash="dash", width=2, color=color_by_name[n])
        ))

    for (idx, (n, v, a)) in enumerate(right_bars):
        x_pos = cx + offsets_right[min(idx, len(offsets_right)-1)]
        x_tickvals.append(x_pos)
        x_ticktext.append(n)

        fig.add_trace(
            go.Bar(
                x=[x_pos], y=[v], width=[bar_width],
                name=n, legendgroup="right",
                marker=dict(color=color_by_name[n], line=dict(width=0)),
                text=[f"{v}"], textposition="outside",
                hovertemplate="<b>%{customdata[0]}</b><br>Grupo: %{customdata[1]}<br>Valor: %{y}<extra></extra>",
                customdata=[[n, gname]],
                showlegend=True,
            ),
            secondary_y=True
        )
        # linha tracejada do topo até o eixo direito
        shapes.append(dict(
            type="line", xref="x", yref="y2",
            x0=x_pos, x1=xmax, y0=v, y1=v,
            line=dict(dash="dash", width=2, color=color_by_name[n])
        ))

# linhas como itens de legenda auxiliares
fig.add_trace(
    go.Scatter(x=[None], y=[None], mode="lines",
               line=dict(dash="dash", width=2),
               name="Linha topo (Y esquerdo)"),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=[None], y=[None], mode="lines",
               line=dict(dash="dash", width=2),
               name="Linha topo (Y direito)"),
    secondary_y=True
)

fig.update_layout(shapes=shapes)

# --------------------------------------------------
# Layout e estilo
# --------------------------------------------------
fig.update_layout(
    title=dict(
        text="4 grupos, 4 barras por grupo, dois eixos Y e linhas até o eixo correspondente",
        x=0.5, xanchor="center",
        font=dict(size=22, family="Inter, Segoe UI, Roboto, Arial")
    ),
    template="plotly_white",
    bargap=0.05,
    margin=dict(l=50, r=50, t=100, b=180),
    plot_bgcolor="rgba(250,250,252,1)",
    paper_bgcolor="white",
    legend=dict(
        orientation="h",
        x=0.5, xanchor="center",
        y=-0.25, yanchor="top",
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        bgcolor="rgba(255,255,255,0.9)"
    )
)

# Eixo X com nomes das barras
fig.update_xaxes(
    range=[xmin, xmax],
    tickvals=x_tickvals,
    ticktext=x_ticktext,
    tickangle=-45,
    tickfont=dict(size=10),
    automargin=True,
    showline=True, linewidth=1, linecolor="rgba(0,0,0,0.25)"
)

# Rótulos dos grupos centralizados na base
for gd in groups_data:
    cx = group_centers[gd["group"]]
    fig.add_annotation(
        x=cx, xref="x",
        y=0, yref="paper",
        text=f"<b>{gd['group']}</b>",
        showarrow=False,
        yshift=-50,
        font=dict(size=12, color="rgba(0,0,0,0.75)"),
        align="center"
    )

# Eixos Y
fig.update_yaxes(
    title_text="Cycles",
    secondary_y=False,
    zeroline=False,
    gridcolor="rgba(0,0,0,0.08)",
    tickfont=dict(size=12)
)
fig.update_yaxes(
    title_text="Instructions",
    secondary_y=True,
    zeroline=False,
    showgrid=False,
    tickfont=dict(size=12)
)

fig.show()
