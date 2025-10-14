# pip install plotly>=5
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import textwrap
import re

# ---------------- Helpers ----------------
def wrap_label(txt, width=12):
    # quebra em múltiplas linhas para evitar sobreposição
    return "<br>".join(textwrap.fill(txt, width=width, break_long_words=False).split("\n"))

def parse_color_to_rgb(color_str: str):
    """
    Aceita "#RRGGBB", "#RGB", "rgb(r,g,b)" ou "rgba(r,g,b,a)".
    Retorna tupla (r, g, b) com ints 0..255.
    """
    s = color_str.strip()
    if s.startswith("#"):
        hx = s[1:]
        if len(hx) == 3:
            hx = "".join(c*2 for c in hx)
        if len(hx) != 6:
            raise ValueError(f"Hex inválido: {color_str}")
        r = int(hx[0:2], 16)
        g = int(hx[2:4], 16)
        b = int(hx[4:6], 16)
        return (r, g, b)
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", s)
    if m:
        return tuple(int(x) for x in m.groups())
    raise ValueError(f"Formato de cor não suportado: {color_str}")

def lighten(color_str: str, amount: float):
    """
    Clareia cor misturando com branco.
    amount em [0,1], 0 = cor original; 0.4 ~ 40% mais clara.
    Retorna "rgb(r,g,b)".
    """
    r, g, b = parse_color_to_rgb(color_str)
    r2 = int(round((1 - amount) * r + amount * 255))
    g2 = int(round((1 - amount) * g + amount * 255))
    b2 = int(round((1 - amount) * b + amount * 255))
    return f"rgb({r2},{g2},{b2})"

# ---------------- Dados de exemplo ----------------
# G1 e G2 usam eixo esquerdo; G3 e G4 usam eixo direito
groups_data = [
    {"group": "G1", "bars": [("Alpha cliente", 42), ("Beta servidor", 58), ("Gamma total", 63), ("Delta pico", 37)]},
    {"group": "G2", "bars": [("Epsilon cliente", 51), ("Zeta servidor", 47), ("Eta total", 72), ("Theta pico", 66)]},
    {"group": "G3", "bars": [("Iota cliente", 180), ("Kappa servidor", 210), ("Lambda total", 155), ("Mu pico", 190)]},
    {"group": "G4", "bars": [("Nu cliente", 230), ("Xi servidor", 205), ("Omicron total", 245), ("Pi pico", 215)]},
]

# Cores base por grupo
base_palette = px.colors.qualitative.Safe  # retorna "rgb(r,g,b)"
base_by_group = {gd["group"]: base_palette[i % len(base_palette)] for i, gd in enumerate(groups_data)}

# Degradê de 4 tons por grupo (0 é base, depois clareando)
gradient_steps = [0.00, 0.12, 0.24, 0.36]
shades_by_group = {
    g["group"]: [lighten(base_by_group[g["group"]], a) for a in gradient_steps]
    for g in groups_data
}

# ---------------- Posicionamento ----------------
group_centers = {gd["group"]: i for i, gd in enumerate(groups_data)}  # 0..3
offsets_4 = [-0.27, -0.09, 0.09, 0.27]  # 4 barras coladas por grupo
bar_width = 0.16
xmin, xmax = -0.8, len(groups_data) - 1 + 0.8

fig = make_subplots(specs=[[{"secondary_y": True}]])

x_tickvals, x_ticktext = [], []

# ---------------- Barras + linhas até o eixo ----------------
for gi, gd in enumerate(groups_data):
    gname = gd["group"]
    cx = group_centers[gname]
    use_right = gi >= 2  # G1,G2 -> esquerda ; G3,G4 -> direita
    group_shades = shades_by_group[gname]  # 4 tons para as 4 barras

    for idx, (name, value) in enumerate(gd["bars"]):
        x_pos = cx + offsets_4[idx % len(offsets_4)]
        color = group_shades[idx % len(group_shades)]

        x_tickvals.append(x_pos)
        x_ticktext.append(wrap_label(name, width=12))

        fig.add_trace(
            go.Bar(
                x=[x_pos], y=[value], width=[bar_width],
                name=gname,                    # legenda por grupo
                legendgroup=gname,
                showlegend=(idx == 0),         # só a 1a barra do grupo aparece na legenda
                marker=dict(color=color, line=dict(width=0)),
                text=[f"{value}"],
                textposition="outside",
                cliponaxis=False,
                hovertemplate="<b>%{customdata[0]}</b><br>Grupo: %{customdata[1]}<br>Valor: %{y}<extra></extra>",
                customdata=[[name, gname]],
            ),
            secondary_y=use_right
        )

        # linha tracejada do topo até o eixo correspondente, na mesma cor da barra
        if use_right:
            fig.add_shape(
                type="line", xref="x", yref="y2",
                x0=x_pos, x1=xmax, y0=value, y1=value,
                line=dict(dash="dash", width=2, color=color)
            )
        else:
            fig.add_shape(
                type="line", xref="x", yref="y",
                x0=xmin, x1=x_pos, y0=value, y1=value,
                line=dict(dash="dash", width=2, color=color)
            )

# ---------------- Layout e estilo ----------------
fig.update_layout(
    title=dict(
        text="4 grupos com degradê interno por grupo, G1 e G2 no Y esquerdo, G3 e G4 no Y direito",
        x=0.5, xanchor="center",
        font=dict(size=22, family="Inter, Segoe UI, Roboto, Arial")
    ),
    template="plotly_white",
    bargap=0.06,
    margin=dict(l=70, r=70, t=90, b=260),
    plot_bgcolor="rgba(250,250,252,1)",
    paper_bgcolor="white",
    legend=dict(
        orientation="h",
        x=0, xanchor="left",
        y=-0.28, yanchor="top",
        entrywidthmode="fraction",  # reparte em frações da largura
        entrywidth=0.25,            # 4 colunas, um por grupo
        tracegroupgap=12,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="rgba(0,0,0,0.1)", borderwidth=1
    ),
    uniformtext_minsize=9,
    uniformtext_mode="hide"
)

# Eixo X com rótulos quebrados e inclinados, e linha do eixo visível
fig.update_xaxes(
    range=[xmin, xmax],
    tickvals=x_tickvals,
    ticktext=x_ticktext,
    tickangle=-38,
    tickfont=dict(size=10),
    automargin=True,
    showline=True, linewidth=1.4, linecolor="rgba(0,0,0,0.6)"
)

# Rótulos dos grupos na base
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

# fig.write_html("barras_4grupos_degrade_por_grupo.html", include_plotlyjs="cdn", full_html=True)

