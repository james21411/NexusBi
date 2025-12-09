from typing import Dict, Any, List
import pandas as pd
import numpy as np
import json
from datetime import datetime

class DataVisualizer:
    """Service for generating data visualization code and insights"""

    def __init__(self, data: pd.DataFrame, analysis_results: Dict[str, Any]):
        self.data = data
        self.analysis_results = analysis_results

    def generate_visualization_code(self, visualization_type: str = 'missing_values') -> str:
        """Generate Python code for data visualization"""
        if visualization_type == 'missing_values':
            return self._generate_missing_values_visualization()
        elif visualization_type == 'outliers':
            return self._generate_outliers_visualization()
        elif visualization_type == 'distribution':
            return self._generate_distribution_visualization()
        elif visualization_type == 'correlation':
            return self._generate_correlation_visualization()
        else:
            return self._generate_comprehensive_visualization()

    def _generate_missing_values_visualization(self) -> str:
        """Generate code for visualizing missing values"""
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "import missingno as msno",
            "",
            "def visualize_missing_values(df):",
            "    \"\"\"Visualize missing values in the dataset\"\"\"",
            "    plt.figure(figsize=(15, 10))",
            "    ",
            "    # Missing values matrix",
            "    plt.subplot(2, 2, 1)",
            "    msno.matrix(df)",
            "    plt.title('Missing Values Matrix')",
            "    ",
            "    # Missing values bar chart",
            "    plt.subplot(2, 2, 2)",
            "    missing_counts = df.isnull().sum()",
            "    missing_counts = missing_counts[missing_counts > 0]",
            "    if len(missing_counts) > 0:",
            "        missing_counts.plot(kind='bar')",
            "        plt.title('Missing Values by Column')",
            "        plt.ylabel('Count of Missing Values')",
            "    ",
            "    # Missing values heatmap",
            "    plt.subplot(2, 2, 3)",
            "    msno.heatmap(df)",
            "    plt.title('Missing Values Heatmap')",
            "    ",
            "    # Missing values percentage",
            "    plt.subplot(2, 2, 4)",
            "    missing_percent = (df.isnull().sum() / len(df)) * 100",
            "    missing_percent = missing_percent[missing_percent > 0]",
            "    if len(missing_percent) > 0:",
            "        missing_percent.plot(kind='bar', color='orange')",
            "        plt.title('Missing Values Percentage')",
            "        plt.ylabel('Percentage (%)')",
            "    ",
            "    plt.tight_layout()",
            "    plt.show()",
            "    ",
            "    # Print summary",
            "    print('Missing Values Summary:')",
            "    print(df.isnull().sum())",
            "    print(f'\\nTotal missing values: {df.isnull().sum().sum()}')",
            "    print(f'Total percentage: {(df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100:.2f}%')"
        ]

        return "\n".join(code_lines)

    def _generate_outliers_visualization(self) -> str:
        """Generate code for visualizing outliers"""
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "",
            "def visualize_outliers(df):",
            "    \"\"\"Visualize outliers in numeric columns\"\"\"",
            "    numeric_cols = df.select_dtypes(include=[np.number]).columns",
            "    ",
            "    if len(numeric_cols) == 0:",
            "        print('No numeric columns found for outlier visualization')",
            "        return",
            "    ",
            "    # Create boxplots for each numeric column",
            "    plt.figure(figsize=(15, 5 * len(numeric_cols)))",
            "    ",
            "    for i, col in enumerate(numeric_cols, 1):",
            "        plt.subplot(len(numeric_cols), 1, i)",
            "        sns.boxplot(x=df[col])",
            "        plt.title(f'Boxplot of {col} - Outliers Detection')",
            "        ",
            "        # Add IQR bounds",
            "        q1 = df[col].quantile(0.25)",
            "        q3 = df[col].quantile(0.75)",
            "        iqr = q3 - q1",
            "        lower_bound = q1 - 1.5 * iqr",
            "        upper_bound = q3 + 1.5 * iqr",
            "        ",
            "        # Count outliers",
            "        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()",
            "        plt.text(0.95, 0.95, f'Outliers: {outliers}',",
            "                 transform=plt.gca().transAxes,",
            "                 ha='right', va='top',",
            "                 bbox=dict(facecolor='red', alpha=0.5))",
            "    ",
            "    plt.tight_layout()",
            "    plt.show()",
            "    ",
            "    # Print outlier statistics",
            "    print('Outlier Statistics:')",
            "    for col in numeric_cols:",
            "        q1 = df[col].quantile(0.25)",
            "        q3 = df[col].quantile(0.75)",
            "        iqr = q3 - q1",
            "        outliers = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum()",
            "        print(f'{col}: {outliers} outliers ({(outliers/len(df))*100:.2f}%)')"
        ]

        return "\n".join(code_lines)

    def _generate_distribution_visualization(self) -> str:
        """Generate code for visualizing data distributions"""
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "",
            "def visualize_distributions(df):",
            "    \"\"\"Visualize distributions of numeric and categorical data\"\"\"",
            "    numeric_cols = df.select_dtypes(include=[np.number]).columns",
            "    categorical_cols = df.select_dtypes(include=['object']).columns",
            "    ",
            "    plt.figure(figsize=(18, 12))",
            "    ",
            "    # Numeric data distributions",
            "    if len(numeric_cols) > 0:",
            "        for i, col in enumerate(numeric_cols[:4], 1):  # Limit to 4 numeric cols",
            "            plt.subplot(2, 2, i)",
            "            sns.histplot(df[col], kde=True, bins=30)",
            "            plt.title(f'Distribution of {col}')",
            "            plt.xlabel(col)",
            "            plt.ylabel('Frequency')",
            "    ",
            "    plt.tight_layout()",
            "    plt.show()",
            "    ",
            "    # Categorical data distributions",
            "    if len(categorical_cols) > 0:",
            "        plt.figure(figsize=(15, 5))",
            "        for i, col in enumerate(categorical_cols[:3], 1):  # Limit to 3 categorical cols",
            "            plt.subplot(1, 3, i)",
            "            df[col].value_counts().plot(kind='bar')",
            "            plt.title(f'Distribution of {col}')",
            "            plt.xlabel(col)",
            "            plt.ylabel('Count')",
            "            plt.xticks(rotation=45)",
            "        ",
            "        plt.tight_layout()",
            "        plt.show()",
            "    ",
            "    # Print statistics",
            "    print('Numeric Data Statistics:')",
            "    print(df[numeric_cols].describe())",
            "    print('\\nCategorical Data Statistics:')",
            "    for col in categorical_cols:",
            "        print(f'{col}: {df[col].nunique()} unique values')"
        ]

        return "\n".join(code_lines)

    def _generate_correlation_visualization(self) -> str:
        """Generate code for visualizing correlations"""
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "",
            "def visualize_correlations(df):",
            "    \"\"\"Visualize correlations between numeric variables\"\"\"",
            "    numeric_cols = df.select_dtypes(include=[np.number]).columns",
            "    ",
            "    if len(numeric_cols) < 2:",
            "        print('Not enough numeric columns for correlation analysis')",
            "        return",
            "    ",
            "    # Correlation matrix",
            "    plt.figure(figsize=(12, 10))",
            "    corr_matrix = df[numeric_cols].corr()",
            "    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')",
            "    plt.title('Correlation Matrix of Numeric Variables')",
            "    plt.show()",
            "    ",
            "    # Pairplot for top correlated variables",
            "    # Get top correlations",
            "    corr_pairs = []",
            "    for i in range(len(corr_matrix.columns)):",
            "        for j in range(i):",
            "            corr_pairs.append((corr_matrix.iloc[i, j], corr_matrix.columns[i], corr_matrix.columns[j]))",
            "    ",
            "    # Sort by absolute correlation",
            "    corr_pairs.sort(key=lambda x: abs(x[0]), reverse=True)",
            "    ",
            "    # Show top 3 correlations",
            "    top_correlations = corr_pairs[:3]",
            "    ",
            "    if len(top_correlations) > 0:",
            "        plt.figure(figsize=(15, 5))",
            "        for i, (corr, col1, col2) in enumerate(top_correlations, 1):",
            "            plt.subplot(1, 3, i)",
            "            sns.scatterplot(x=df[col1], y=df[col2])",
            "            plt.title(f'{col1} vs {col2}\\nCorrelation: {corr:.2f}')",
            "        ",
            "        plt.tight_layout()",
            "        plt.show()",
            "    ",
            "    # Print correlation summary",
            "    print('Correlation Analysis Summary:')",
            "    for corr, col1, col2 in top_correlations:",
            "        print(f'{col1} ↔ {col2}: {corr:.3f}')"
        ]

        return "\n".join(code_lines)

    def _generate_comprehensive_visualization(self) -> str:
        """Generate comprehensive visualization code"""
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "import missingno as msno",
            "",
            "def comprehensive_data_visualization(df):",
            "    \"\"\"Comprehensive data visualization dashboard\"\"\"",
            "    ",
            "    # 1. Data Overview",
            "    print('=== Data Overview ===')",
            "    print(f'Shape: {df.shape}')",
            "    print(f'Columns: {list(df.columns)}')",
            "    print(f'Data Types:\\n{df.dtypes}')",
            "    print()",
            "    ",
            "    # 2. Missing Values Analysis",
            "    print('=== Missing Values Analysis ===')",
            "    missing_counts = df.isnull().sum()",
            "    missing_percent = (df.isnull().sum() / len(df)) * 100",
            "    missing_df = pd.DataFrame({'Missing Count': missing_counts, 'Percentage': missing_percent})",
            "    missing_df = missing_df[missing_df['Missing Count'] > 0]",
            "    print(missing_df)",
            "    ",
            "    plt.figure(figsize=(15, 8))",
            "    ",
            "    # Missing values matrix",
            "    plt.subplot(2, 3, 1)",
            "    msno.matrix(df)",
            "    plt.title('Missing Values Matrix')",
            "    ",
            "    # Missing values bar chart",
            "    plt.subplot(2, 3, 2)",
            "    if len(missing_df) > 0:",
            "        sns.barplot(x=missing_df.index, y='Missing Count', data=missing_df)",
            "        plt.title('Missing Values by Column')",
            "        plt.xticks(rotation=45)",
            "    ",
            "    # 3. Numeric Data Analysis",
            "    numeric_cols = df.select_dtypes(include=[np.number]).columns",
            "    if len(numeric_cols) > 0:",
            "        plt.subplot(2, 3, 3)",
            "        sns.histplot(df[numeric_cols[0]], kde=True, bins=30)",
            "        plt.title(f'Distribution of {numeric_cols[0]}')",
            "    ",
            "    # 4. Outlier Analysis",
            "    if len(numeric_cols) > 0:",
            "        plt.subplot(2, 3, 4)",
            "        sns.boxplot(x=df[numeric_cols[0]])",
            "        plt.title(f'Boxplot of {numeric_cols[0]}')",
            "    ",
            "    # 5. Correlation Analysis",
            "    if len(numeric_cols) > 1:",
            "        plt.subplot(2, 3, 5)",
            "        corr_matrix = df[numeric_cols].corr()",
            "        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)",
            "        plt.title('Correlation Matrix')",
            "    ",
            "    plt.tight_layout()",
            "    plt.show()",
            "    ",
            "    # 6. Data Quality Summary",
            "    print('=== Data Quality Summary ===')",
            "    print(f'Total missing values: {df.isnull().sum().sum()}')",
            "    print(f'Missing value percentage: {(df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100:.2f}%')",
            "    ",
            "    # Outlier analysis",
            "    for col in numeric_cols:",
            "        q1 = df[col].quantile(0.25)",
            "        q3 = df[col].quantile(0.75)",
            "        iqr = q3 - q1",
            "        outliers = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum()",
            "        print(f'{col} outliers: {outliers} ({(outliers/len(df))*100:.2f}%)')",
            "    ",
            "    # Duplicate analysis",
            "    duplicates = df.duplicated().sum()",
            "    print(f'Duplicate rows: {duplicates} ({(duplicates/len(df))*100:.2f}%)')"
        ]

        return "\n".join(code_lines)

    def generate_visualization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate visualization suggestions based on data analysis"""
        suggestions = []

        # Missing values visualization
        if self.analysis_results['missing_values']['total_missing'] > 0:
            suggestions.append({
                'type': 'missing_values',
                'description': 'Visualize missing values distribution and patterns',
                'recommended_code': 'visualize_missing_values(df)',
                'insight': f"{self.analysis_results['missing_values']['total_missing']} missing values detected"
            })

        # Outliers visualization
        if len(self.analysis_results['outliers']) > 0:
            suggestions.append({
                'type': 'outliers',
                'description': 'Visualize outliers in numeric columns using boxplots',
                'recommended_code': 'visualize_outliers(df)',
                'insight': f"Outliers detected in {len(self.analysis_results['outliers'])} columns"
            })

        # Distribution visualization
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            suggestions.append({
                'type': 'distribution',
                'description': 'Visualize distribution of numeric data',
                'recommended_code': 'visualize_distributions(df)',
                'insight': f"Found {len(numeric_cols)} numeric columns for distribution analysis"
            })

        # Correlation visualization
        if len(numeric_cols) > 1:
            suggestions.append({
                'type': 'correlation',
                'description': 'Visualize correlations between numeric variables',
                'recommended_code': 'visualize_correlations(df)',
                'insight': f"Potential correlations between {len(numeric_cols)} numeric columns"
            })

        return suggestions