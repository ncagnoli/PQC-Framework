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
    {"group": "G1", "bars": [("Alpha cliente", 42), ("Beta servidor", 58), ("Gamma total", 63), ("Delta pico", 37)]},
    {"group": "G2", "bars": [("Epsilon cliente", 51), ("Zeta servidor", 47), ("Eta total", 72), ("Theta pico", 66)]},
    {"group": "G3", "bars": [("Iota cliente", 180), ("Kappa servidor", 210), ("Lambda total", 155), ("Mu pico", 190)]},
    {"group": "G4", "bars": [("Nu cliente", 230), ("Xi servidor", 205), ("Omicron total", 245), ("Pi pico", 215)]},
]

# Paleta por grupo (suave e legível)
group_palette = px.colors.qualitative.Safe  # 10 cores seguras
group_colors = {gd["group"]: group_palette[i % len(group_palette)] for i, gd in enumerate(groups_data)}

# Posicionamento
group_centers = {gd["group"]: i for i, gd in enumerate(groups_data)}  # 0..3
offsets_4 = [-0.27, -0.09, 0.09, 0.27]
bar_width = 0.16
xmin, xmax = -0.8, len(groups_data) - 1 + 0.8

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
                line=dict(dash="dash", width=2, color=gcolor)
            )
        else:
            fig.add_shape(
                type="line", xref="x", yref="y",
                x0=xmin, x1=x_pos, y0=value, y1=value,
                line=dict(dash="dash", width=2, color=gcolor)
            )

# Layout e estilo
fig.update_layout(
    title=dict(
        text="4 grupos, 4 barras por grupo — G1 e G2 no Y esquerdo, G3 e G4 no Y direito",
        x=0.5, xanchor="center",
        font=dict(size=22, family="Inter, Segoe UI, Roboto, Arial")
    ),
    template="plotly_white",
    bargap=0.06,
    margin=dict(l=70, r=70, t=90, b=260),
    plot_bgcolor="rgba(250,250,252,1)",
    paper_bgcolor="white",
    # legenda embaixo ocupando a largura do gráfico
    legend=dict(
        orientation="h",
        x=0, xanchor="left",
        y=-0.28, yanchor="top",
        entrywidthmode="fraction",  # reparte em frações da largura
        entrywidth=0.25,            # 4 colunas alinhadas
        tracegroupgap=12,
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
    tickangle=-40,
    tickfont=dict(size=10),
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
        yshift=-60,
        font=dict(size=12, color="rgba(0,0,0,0.75)"),
        align="center"
    )

# Eixos Y com linhas visíveis
fig.update_yaxes(
    title_text="Escala esquerda",
    secondary_y=False,
    zeroline=False,
    gridcolor="rgba(0,0,0,0.08)",
    showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
    tickfont=dict(size=12)
)
fig.update_yaxes(
    title_text="Escala direita",
    secondary_y=True,
    zeroline=False,
    showgrid=False,
    showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)",
    tickfont=dict(size=12)
)

fig.show()

# fig.write_html("barras_4grupos_duas_escalas_legenda_baixo.html", include_plotlyjs="cdn", full_html=True)

