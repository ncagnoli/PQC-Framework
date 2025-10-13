# pip install plotly>=5
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import textwrap

def wrap_label(txt, width=10):
    # quebra em múltiplas linhas para evitar sobreposição
    return "<br>".join(textwrap.fill(txt, width=width, break_long_words=False).split("\n"))

# --------------------------------------------
# Dados de exemplo
# G1 e G2 usam eixo esquerdo; G3 e G4 usam eixo direito
# Troque nomes e valores conforme sua necessidade
# --------------------------------------------
groups_data = [
    {"group": "Client cycles", "bars": [("RSA 2048", 32644650), ("RSA 3072", 46303028), ("RSA 4096", 57021879), ("Ed25519", 36007279)]},
    {"group": "Server cycles", "bars": [("RSA 2048", 89540747), ("RSA 3072", 110889617), ("RSA 4096", 128495569), ("Ed25519", 85315996)]},
    {"group": "Client instructions", "bars": [("RSA 2048", 73901621), ("RSA 3072", 113234505), ("RSA 4096", 151918155), ("Ed25519", 89048317)]},
    {"group": "Server instructions", "bars": [("RSA 2048", 146150240), ("RSA 3072", 199057853), ("RSA 4096", 265876400), ("Ed25519", 141632836)]},
]

# Paleta por grupo (suave e legível)
group_palette = px.colors.qualitative.Safe  # 10 cores seguras
group_colors = {gd["group"]: group_palette[i % len(group_palette)] for i, gd in enumerate(groups_data)}

# Posicionamento
GROUP_SPACING = 0.8 
group_centers = {gd["group"]: i * GROUP_SPACING for i, gd in enumerate(groups_data)}

offsets_4 = [-0.27, -0.09, 0.09, 0.27]
bar_width = 0.16

# Bordas esquerda e direita mais justas
first_group = groups_data[0]["group"]
last_group  = groups_data[-1]["group"]

leftmost  = group_centers[first_group] + min(offsets_4)   # barra mais à esquerda
rightmost = group_centers[last_group]  + max(offsets_4)   # barra mais à direita

PAD = 0.1  # ajuste fino das bordas, experimente 0.04 a 0.10
xmin, xmax = leftmost - PAD, rightmost + PAD




fig = make_subplots(specs=[[{"secondary_y": True}]])

x_tickvals, x_ticktext = [], []

# Barras e linhas até o eixo correspondente
for gi, gd in enumerate(groups_data):
    gname = gd["group"]
    cx = group_centers[gname]
    use_right = gi >= 2  # G1,G2 -> esquerda ; G3,G4 -> direita
    gcolor = group_colors[gname]

    for idx, (name, value) in enumerate(gd["bars"]):
        x_pos = cx + offsets_4[idx % len(offsets_4)]
        x_tickvals.append(x_pos)
        x_ticktext.append(wrap_label(name, width=10))

        fig.add_trace(
            go.Bar(
                x=[x_pos], y=[value], width=[bar_width],
                name=gname,                    # legenda por grupo, não por barra
                legendgroup=gname,
                showlegend=(idx == 0),         # só a 1ª barra do grupo aparece na legenda
                marker=dict(color=gcolor, line=dict(width=0)),
                text=[f"{value}"], textposition="outside", cliponaxis=False,
                hovertemplate="<b>%{customdata[0]}</b><br>Grupo: %{customdata[1]}<br>Valor: %{y}<extra></extra>",
                customdata=[[name, gname]],
            ),
            secondary_y=use_right
        )

        # linha tracejada do topo até o eixo correspondente
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

# Layout e estilo
fig.update_layout(
    title=dict(
        text="Cenário 1 - Cycles e Instructions",
        x=0.5, xanchor="center",
        font=dict(size=32, family="Inter, Segoe UI, Roboto, Arial")
    ),
    template="plotly_white",
    bargap=0.06,
    margin=dict(l=70, r=70, t=90, b=260),
    plot_bgcolor="rgba(250,250,252,1)",
    paper_bgcolor="white",
    # legenda embaixo ocupando a largura do gráfico
    legend=dict(
        orientation="h",
        x=0.5, xanchor="center",   # centraliza na base
        y=-0.2, yanchor="top",    # coloca abaixo do gráfico
        font=dict(size=22),
        tracegroupgap=16,
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="rgba(0,0,0,0.1)", borderwidth=1
    ),
    uniformtext_minsize=9,
    uniformtext_mode="hide"
)

# Eixo X, com rótulos quebrados e inclinados
fig.update_xaxes(
    range=[xmin, xmax],
    tickvals=x_tickvals,
    ticktext=x_ticktext,
    #tickangle=-30,
    tickfont=dict(size=16),
    automargin=True,
    showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)"
)

# Rótulos dos grupos centralizados na base
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

# Eixos Y com linhas visíveis
fig.update_yaxes(
    title_text="Cycles",
    secondary_y=False,
    title_font=dict(size=26),   # <<< aumenta aqui
    title_standoff=12,          # <<< opcional, afasta do eixo
    zeroline=False,
    gridcolor="rgba(0,0,0,0.08)",
    showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
    tickfont=dict(size=18)
)
fig.update_yaxes(
    title_text="Instructions",
    secondary_y=True,
    title_font=dict(size=26),   # <<< aumenta aqui
    title_standoff=12,          # <<< opcional, afasta do eixo
    zeroline=False,
    showgrid=True,
    showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
    tickfont=dict(size=18)
)

fig.update_layout(showlegend=False)
fig.show()


