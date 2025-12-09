from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import json
from datetime import datetime

class DataAnalyzer:
    """Service for analyzing data and generating insights"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.analysis_results = {}

    def analyze_data_quality(self) -> Dict[str, Any]:
        """Analyze data quality and identify issues"""
        results = {
            'missing_values': self._analyze_missing_values(),
            'data_types': self._analyze_data_types(),
            'statistics': self._calculate_statistics(),
            'outliers': self._detect_outliers(),
            'duplicates': self._find_duplicates()
        }
        self.analysis_results = results
        return results

    def _analyze_missing_values(self) -> Dict[str, Any]:
        """Analyze missing values in the dataset"""
        missing_data = {}
        total_missing = 0

        for col in self.data.columns:
            missing_count = self.data[col].isnull().sum()
            missing_percentage = (missing_count / len(self.data)) * 100

            if missing_count > 0:
                missing_data[col] = {
                    'count': int(missing_count),
                    'percentage': round(missing_percentage, 2),
                    'dtype': str(self.data[col].dtype)
                }
                total_missing += missing_count

        return {
            'columns': missing_data,
            'total_missing': total_missing,
            'total_percentage': round((total_missing / (len(self.data) * len(self.data.columns))) * 100, 2)
        }

    def _analyze_data_types(self) -> Dict[str, Any]:
        """Analyze data types and suggest improvements"""
        type_analysis = {}

        for col in self.data.columns:
            dtype = str(self.data[col].dtype)
            sample_values = self.data[col].dropna().unique()[:5]

            # Detect potential type issues
            type_issues = []
            if dtype == 'object':
                # Check if could be datetime
                try:
                    pd.to_datetime(sample_values[:1])
                    type_issues.append('potential_datetime')
                except:
                    pass

                # Check if could be numeric
                try:
                    pd.to_numeric(sample_values[:1])
                    type_issues.append('potential_numeric')
                except:
                    pass

            type_analysis[col] = {
                'current_type': dtype,
                'sample_values': [str(v) for v in sample_values],
                'potential_issues': type_issues
            }

        return type_analysis

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate basic statistics for numeric columns"""
        stats = {}

        for col in self.data.select_dtypes(include=[np.number]).columns:
            stats[col] = {
                'mean': float(self.data[col].mean()),
                'median': float(self.data[col].median()),
                'std': float(self.data[col].std()),
                'min': float(self.data[col].min()),
                'max': float(self.data[col].max()),
                'quartile_25': float(self.data[col].quantile(0.25)),
                'quartile_75': float(self.data[col].quantile(0.75))
            }

        return stats

    def _detect_outliers(self) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        outliers = {}

        for col in self.data.select_dtypes(include=[np.number]).columns:
            q1 = self.data[col].quantile(0.25)
            q3 = self.data[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_count = ((self.data[col] < lower_bound) | (self.data[col] > upper_bound)).sum()
            outlier_percentage = (outlier_count / len(self.data)) * 100

            if outlier_count > 0:
                outliers[col] = {
                    'count': int(outlier_count),
                    'percentage': round(outlier_percentage, 2),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound)
                }

        return outliers

    def _find_duplicates(self) -> Dict[str, Any]:
        """Find duplicate rows in the dataset"""
        duplicate_count = self.data.duplicated().sum()
        duplicate_percentage = (duplicate_count / len(self.data)) * 100

        return {
            'count': int(duplicate_count),
            'percentage': round(duplicate_percentage, 2),
            'has_duplicates': duplicate_count > 0
        }

    def generate_missing_value_treatment_code(self, strategy: str = 'mean') -> str:
        """Generate Python code for handling missing values"""
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "",
            "# Treatment for missing values",
            "df_cleaned = df.copy()",
            "",
            "# Summary before treatment",
            "print('Missing values before treatment:')",
            "print(df.isnull().sum())",
            "print()",
            ""
        ]

        for col, missing_info in self.analysis_results['missing_values']['columns'].items():
            if strategy == 'mean' and self.data[col].dtype in ['float64', 'int64']:
                code_lines.append(f"# Fill missing values in '{col}' with mean")
                code_lines.append(f"df_cleaned['{col}'] = df_cleaned['{col}'].fillna(df_cleaned['{col}'].mean())")
            elif strategy == 'median' and self.data[col].dtype in ['float64', 'int64']:
                code_lines.append(f"# Fill missing values in '{col}' with median")
                code_lines.append(f"df_cleaned['{col}'] = df_cleaned['{col}'].fillna(df_cleaned['{col}'].median())")
            elif strategy == 'mode':
                code_lines.append(f"# Fill missing values in '{col}' with mode")
                code_lines.append(f"df_cleaned['{col}'] = df_cleaned['{col}'].fillna(df_cleaned['{col}'].mode()[0])")
            elif strategy == 'drop':
                code_lines.append(f"# Drop rows with missing values in '{col}'")
                code_lines.append(f"df_cleaned = df_cleaned.dropna(subset=['{col}'])")
            else:
                code_lines.append(f"# Fill missing values in '{col}' with constant value")
                code_lines.append(f"df_cleaned['{col}'] = df_cleaned['{col}'].fillna('MISSING')")

        code_lines.append("")
        code_lines.append("# Summary of missing values after treatment")
        code_lines.append("missing_after = df_cleaned.isnull().sum()")
        code_lines.append("print('Missing values after treatment:')")
        code_lines.append("print(missing_after)")
        code_lines.append("")
        code_lines.append("# Additional data quality checks")
        code_lines.append("print('\\nData types after cleaning:')")
        code_lines.append("print(df_cleaned.dtypes)")
        code_lines.append("")
        code_lines.append("# Basic statistics")
        code_lines.append("print('\\nBasic statistics:')")
        code_lines.append("print(df_cleaned.describe())")

        return "\n".join(code_lines)

    def generate_data_cleaning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive data cleaning report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_shape': {
                'rows': len(self.data),
                'columns': len(self.data.columns)
            },
            'quality_issues': [],
            'recommendations': []
        }

        # Add missing values issues
        if self.analysis_results['missing_values']['total_missing'] > 0:
            report['quality_issues'].append({
                'type': 'missing_values',
                'severity': 'high' if self.analysis_results['missing_values']['total_percentage'] > 10 else 'medium',
                'description': f"{self.analysis_results['missing_values']['total_missing']} missing values ({self.analysis_results['missing_values']['total_percentage']}%)",
                'affected_columns': list(self.analysis_results['missing_values']['columns'].keys())
            })

        # Add outlier issues
        if len(self.analysis_results['outliers']) > 0:
            report['quality_issues'].append({
                'type': 'outliers',
                'severity': 'medium',
                'description': f"Outliers detected in {len(self.analysis_results['outliers'])} numeric columns",
                'affected_columns': list(self.analysis_results['outliers'].keys())
            })

        # Add duplicate issues
        if self.analysis_results['duplicates']['count'] > 0:
            report['quality_issues'].append({
                'type': 'duplicates',
                'severity': 'low' if self.analysis_results['duplicates']['percentage'] < 5 else 'medium',
                'description': f"{self.analysis_results['duplicates']['count']} duplicate rows ({self.analysis_results['duplicates']['percentage']}%)",
                'recommendation': 'Consider removing duplicates using df.drop_duplicates()'
            })

        # Generate recommendations
        if len(report['quality_issues']) > 0:
            report['recommendations'] = [
                "Implement data validation rules during data ingestion",
                "Create automated data cleaning pipelines",
                "Set up data quality monitoring alerts",
                "Document data quality issues and resolutions"
            ]

        return report

    def suggest_visualizations(self) -> List[Dict[str, Any]]:
        """Suggest appropriate visualizations based on data types"""
        suggestions = []

        # Check for numeric columns that could be visualized
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) >= 2:
            suggestions.append({
                'type': 'scatter_plot',
                'description': 'Scatter plot to visualize relationships between numeric variables',
                'recommended_columns': numeric_cols[:2]
            })

        if len(numeric_cols) >= 1:
            suggestions.append({
                'type': 'histogram',
                'description': 'Histogram to show distribution of numeric data',
                'recommended_columns': numeric_cols[:1]
            })

        # Check for categorical columns
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()

        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            suggestions.append({
                'type': 'bar_chart',
                'description': 'Bar chart to compare categories',
                'recommended_columns': {
                    'x': categorical_cols[0],
                    'y': numeric_cols[0]
                }
            })

        return suggestions

    def generate_comprehensive_cleaning_code(self) -> str:
        """Generate comprehensive Python code for data cleaning including multiple treatments"""
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "",
            "# Comprehensive Data Cleaning Pipeline",
            "def clean_data(df):",
            "    \"\"\"Comprehensive data cleaning function\"\"\"",
            "    df_cleaned = df.copy()",
            "    print('=== Data Cleaning Report ===')",
            "    print(f'Original shape: {df.shape}')",
            "    print(f'Columns: {list(df.columns)}')",
            "    print()",
            ""
        ]

        # Add missing values treatment
        if self.analysis_results['missing_values']['total_missing'] > 0:
            code_lines.append("# Missing Values Treatment")
            code_lines.append("print('Missing values before treatment:')")
            code_lines.append("print(df_cleaned.isnull().sum())")
            code_lines.append("print()")

            for col, missing_info in self.analysis_results['missing_values']['columns'].items():
                if self.data[col].dtype in ['float64', 'int64']:
                    code_lines.append(f"# Fill numeric missing values in '{col}' with median")
                    code_lines.append(f"df_cleaned['{col}'] = df_cleaned['{col}'].fillna(df_cleaned['{col}'].median())")
                else:
                    code_lines.append(f"# Fill categorical missing values in '{col}' with mode")
                    code_lines.append(f"df_cleaned['{col}'] = df_cleaned['{col}'].fillna(df_cleaned['{col}'].mode()[0])")

            code_lines.append("")
            code_lines.append("print('Missing values after treatment:')")
            code_lines.append("print(df_cleaned.isnull().sum())")
            code_lines.append("print()")

        # Add outlier treatment
        if len(self.analysis_results['outliers']) > 0:
            code_lines.append("# Outlier Treatment (capping)")
            for col in self.analysis_results['outliers'].keys():
                code_lines.append(f"# Cap outliers in '{col}'")
                code_lines.append(f"q1 = df_cleaned['{col}'].quantile(0.25)")
                code_lines.append(f"q3 = df_cleaned['{col}'].quantile(0.75)")
                code_lines.append(f"iqr = q3 - q1")
                code_lines.append(f"lower_bound = q1 - 1.5 * iqr")
                code_lines.append(f"upper_bound = q3 + 1.5 * iqr")
                code_lines.append(f"df_cleaned['{col}'] = np.where(df_cleaned['{col}'] < lower_bound, lower_bound, df_cleaned['{col}'])")
                code_lines.append(f"df_cleaned['{col}'] = np.where(df_cleaned['{col}'] > upper_bound, upper_bound, df_cleaned['{col}'])")

        # Add duplicate removal
        if self.analysis_results['duplicates']['count'] > 0:
            code_lines.append("")
            code_lines.append("# Remove duplicates")
            code_lines.append("print(f'Removed {df_cleaned.duplicated().sum()} duplicate rows')")
            code_lines.append("df_cleaned = df_cleaned.drop_duplicates()")

        # Add final summary
        code_lines.append("")
        code_lines.append("# Final Data Quality Checks")
        code_lines.append("print('Final data shape:', df_cleaned.shape)")
        code_lines.append("print('Final data types:')")
        code_lines.append("print(df_cleaned.dtypes)")
        code_lines.append("print()")
        code_lines.append("print('Basic statistics:')")
        code_lines.append("print(df_cleaned.describe())")
        code_lines.append("")
        code_lines.append("return df_cleaned")

        # Add visualization code
        code_lines.append("")
        code_lines.append("# Visualization of data quality improvements")
        code_lines.append("def visualize_cleaning_results(original_df, cleaned_df):")
        code_lines.append("    \"\"\"Visualize the impact of data cleaning\"\"\"")
        code_lines.append("    plt.figure(figsize=(15, 10))")
        code_lines.append("")
        code_lines.append("    # Missing values comparison")
        code_lines.append("    plt.subplot(2, 2, 1)")
        code_lines.append("    original_missing = original_df.isnull().sum()")
        code_lines.append("    cleaned_missing = cleaned_df.isnull().sum()")
        code_lines.append("    comparison = pd.DataFrame({'Original': original_missing, 'Cleaned': cleaned_missing})")
        code_lines.append("    comparison.plot(kind='bar', ax=plt.gca())")
        code_lines.append("    plt.title('Missing Values: Before vs After Cleaning')")
        code_lines.append("    plt.ylabel('Count of Missing Values')")
        code_lines.append("")
        code_lines.append("    # Data distribution comparison for numeric columns")
        code_lines.append("    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns")
        code_lines.append("    if len(numeric_cols) > 0:")
        code_lines.append("        plt.subplot(2, 2, 2)")
        code_lines.append("        sns.histplot(cleaned_df[numeric_cols[0]], kde=True, ax=plt.gca())")
        code_lines.append("        plt.title(f'Distribution of {numeric_cols[0]}')")
        code_lines.append("")
        code_lines.append("    plt.tight_layout()")
        code_lines.append("    plt.show()")

        return "\n".join(code_lines)