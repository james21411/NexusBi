import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from typing import Dict, Any, Optional
import io
import base64


class ChartGenerator:
    """Service for generating interactive charts and visualizations"""

    def __init__(self):
        # Set matplotlib backend to non-interactive for server environment
        plt.switch_backend('Agg')

        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_palette("husl")

    def generate_plotly_chart(self, df: pd.DataFrame, chart_type: str,
                            x_column: str = None, y_column: str = None,
                            title: str = "Chart", **kwargs) -> Dict[str, Any]:
        """
        Generate interactive Plotly chart
        Returns chart data as JSON-serializable dict
        """
        try:
            if chart_type == "scatter":
                fig = px.scatter(df, x=x_column, y=y_column, title=title, **kwargs)

            elif chart_type == "line":
                fig = px.line(df, x=x_column, y=y_column, title=title, **kwargs)

            elif chart_type == "bar":
                fig = px.bar(df, x=x_column, y=y_column, title=title, **kwargs)

            elif chart_type == "histogram":
                fig = px.histogram(df, x=x_column, title=title, **kwargs)

            elif chart_type == "box":
                fig = px.box(df, x=x_column, y=y_column, title=title, **kwargs)

            elif chart_type == "heatmap":
                # Correlation heatmap
                numeric_df = df.select_dtypes(include=[np.number])
                corr_matrix = numeric_df.corr()
                fig = px.imshow(corr_matrix, title=title, **kwargs)

            elif chart_type == "pie":
                if y_column and x_column:
                    fig = px.pie(df, values=y_column, names=x_column, title=title, **kwargs)
                else:
                    # Count plot
                    value_counts = df[x_column].value_counts()
                    fig = px.pie(values=value_counts.values, names=value_counts.index, title=title, **kwargs)

            else:
                # Default to scatter plot
                fig = px.scatter(df, x=x_column, y=y_column, title=title, **kwargs)

            # Convert to JSON-serializable format
            chart_data = json.loads(json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder))
            return {
                "success": True,
                "chart_data": chart_data,
                "chart_type": chart_type
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate chart: {str(e)}",
                "chart_type": chart_type
            }

    def generate_matplotlib_chart(self, df: pd.DataFrame, chart_type: str,
                                x_column: str = None, y_column: str = None,
                                title: str = "Chart") -> Dict[str, Any]:
        """
        Generate matplotlib chart and return as base64 encoded image
        """
        try:
            plt.figure(figsize=(10, 6))

            if chart_type == "scatter":
                plt.scatter(df[x_column], df[y_column])
                plt.xlabel(x_column)
                plt.ylabel(y_column)

            elif chart_type == "line":
                plt.plot(df[x_column], df[y_column])
                plt.xlabel(x_column)
                plt.ylabel(y_column)

            elif chart_type == "bar":
                plt.bar(df[x_column], df[y_column])
                plt.xlabel(x_column)
                plt.ylabel(y_column)

            elif chart_type == "histogram":
                plt.hist(df[x_column], bins=30, alpha=0.7)
                plt.xlabel(x_column)
                plt.ylabel("Frequency")

            elif chart_type == "box":
                sns.boxplot(data=df, x=x_column, y=y_column)
                plt.xlabel(x_column)
                plt.ylabel(y_column)

            elif chart_type == "heatmap":
                numeric_df = df.select_dtypes(include=[np.number])
                corr_matrix = numeric_df.corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
                plt.title(title)

            plt.title(title)
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

            return {
                "success": True,
                "image_base64": image_base64,
                "chart_type": chart_type,
                "format": "png"
            }

        except Exception as e:
            plt.close()
            return {
                "success": False,
                "error": f"Failed to generate matplotlib chart: {str(e)}",
                "chart_type": chart_type
            }

    def generate_seaborn_chart(self, df: pd.DataFrame, chart_type: str,
                             x_column: str = None, y_column: str = None,
                             title: str = "Chart") -> Dict[str, Any]:
        """
        Generate seaborn chart and return as base64 encoded image
        """
        try:
            plt.figure(figsize=(12, 8))

            if chart_type == "scatter":
                sns.scatterplot(data=df, x=x_column, y=y_column)
            elif chart_type == "line":
                sns.lineplot(data=df, x=x_column, y=y_column)
            elif chart_type == "bar":
                sns.barplot(data=df, x=x_column, y=y_column)
            elif chart_type == "box":
                sns.boxplot(data=df, x=x_column, y=y_column)
            elif chart_type == "violin":
                sns.violinplot(data=df, x=x_column, y=y_column)
            elif chart_type == "histogram":
                sns.histplot(data=df, x=x_column, bins=30)
            elif chart_type == "pairplot":
                # For pairplot, we create a separate figure
                plt.close()
                g = sns.pairplot(df.select_dtypes(include=[np.number]))
                g.fig.suptitle(title, y=1.02)
                buffer = io.BytesIO()
                g.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close(g.fig)
                return {
                    "success": True,
                    "image_base64": image_base64,
                    "chart_type": chart_type,
                    "format": "png"
                }
            elif chart_type == "heatmap":
                numeric_df = df.select_dtypes(include=[np.number])
                corr_matrix = numeric_df.corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, square=True)

            plt.title(title)
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

            return {
                "success": True,
                "image_base64": image_base64,
                "chart_type": chart_type,
                "format": "png"
            }

        except Exception as e:
            plt.close()
            return {
                "success": False,
                "error": f"Failed to generate seaborn chart: {str(e)}",
                "chart_type": chart_type
            }

    def generate_chart_from_query(self, df: pd.DataFrame, query: str,
                                chart_library: str = "plotly") -> Dict[str, Any]:
        """
        Generate chart based on natural language query
        This would be enhanced with AI to interpret queries
        """
        # Simple keyword-based chart type detection
        query_lower = query.lower()

        if "scatter" in query_lower or "points" in query_lower:
            chart_type = "scatter"
        elif "line" in query_lower or "trend" in query_lower:
            chart_type = "line"
        elif "bar" in query_lower or "bars" in query_lower:
            chart_type = "bar"
        elif "histogram" in query_lower or "distribution" in query_lower:
            chart_type = "histogram"
        elif "box" in query_lower or "boxplot" in query_lower:
            chart_type = "box"
        elif "correlation" in query_lower or "heatmap" in query_lower:
            chart_type = "heatmap"
        elif "pie" in query_lower or "proportion" in query_lower:
            chart_type = "pie"
        else:
            chart_type = "bar"  # default

        # Auto-detect numeric columns for x/y axes
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_columns) >= 2:
            x_column = numeric_columns[0]
            y_column = numeric_columns[1]
        elif len(numeric_columns) == 1:
            x_column = numeric_columns[0]
            y_column = None
        else:
            # Use first two columns if no numeric
            x_column = df.columns[0] if len(df.columns) > 0 else None
            y_column = df.columns[1] if len(df.columns) > 1 else None

        if chart_library == "plotly":
            return self.generate_plotly_chart(df, chart_type, x_column, y_column, title=query)
        elif chart_library == "matplotlib":
            return self.generate_matplotlib_chart(df, chart_type, x_column, y_column, title=query)
        elif chart_library == "seaborn":
            return self.generate_seaborn_chart(df, chart_type, x_column, y_column, title=query)
        else:
            return self.generate_plotly_chart(df, chart_type, x_column, y_column, title=query)


# Global instance
chart_generator = ChartGenerator()