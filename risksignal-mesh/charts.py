import plotly.io as pio
import plotly.graph_objects as go

UBS_RED = "#E60000"
UBS_NAVY = "#001F3F"
UBS_GRAY = "#D9D9D9"
UBS_LIGHT_GRAY = "#F5F5F5"
UBS_GRID = "#E5E7EB"
UBS_TEXT = "#1A1A1A"
UBS_MUTED = "#6B7280"

UBS_COLORWAY = [
    UBS_NAVY,
    UBS_GRAY,
    UBS_RED,
    UBS_MUTED,
]

UBS_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(
            family="Arial",
            size=13,
            color=UBS_TEXT,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        colorway=UBS_COLORWAY,
        margin=dict(l=20, r=20, t=45, b=30),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor=UBS_GRID,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=UBS_GRID,
            zeroline=False,
            linecolor=UBS_GRID,
        ),
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0,
        ),
    )
)


def apply_global_chart_theme():
    pio.templates["ubs"] = UBS_TEMPLATE
    pio.templates.default = "ubs"


def clean_fig(fig, showlegend=False):
    fig.update_layout(
        template="ubs",
        showlegend=showlegend,
    )
    return fig


def executive_bar(fig):
    fig = clean_fig(fig)
    fig.update_traces(
        marker_color=UBS_NAVY
    )
    return fig


def executive_horizontal_bar(fig):
    fig = clean_fig(fig)
    fig.update_traces(
        marker_color=UBS_NAVY
    )
    fig.update_yaxes(showgrid=False)
    return fig


def material_donut(fig):
    fig = clean_fig(fig, True)

    fig.update_traces(
        marker=dict(
            colors=[
                UBS_RED,
                UBS_GRAY
            ]
        ),
        hole=0.62
    )

    return fig