# src/utils/visualization.py
import plotly.express as px

def create_allocation_pie(recommendations):
    labels = [rec["coin"] for rec in recommendations]
    sizes = [rec["allocation_percentage"] for rec in recommendations]
    fig = px.pie(values=sizes, names=labels, title="Investment Allocation")
    return fig
