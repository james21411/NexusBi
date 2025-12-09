import pandas as pd
import numpy as np
from app.services.data_analysis import DataAnalyzer
from app.services.data_visualization import DataVisualizer

# Create test data with various quality issues
def create_test_data():
    """Create a test dataset with missing values, outliers, and duplicates"""
    np.random.seed(42)

    data = {
        'id': range(1, 101),
        'age': np.random.normal(40, 15, 100).astype(int),
        'income': np.random.normal(50000, 20000, 100).astype(int),
        'category': np.random.choice(['A', 'B', 'C', 'D'], 100),
        'score': np.random.uniform(0, 100, 100).round(2)
    }

    df = pd.DataFrame(data)

    # Add missing values
    df.loc[df.sample(15).index, 'age'] = np.nan
    df.loc[df.sample(10).index, 'income'] = np.nan
    df.loc[df.sample(5).index, 'category'] = np.nan

    # Add outliers
    df.loc[95:99, 'income'] = df.loc[95:99, 'income'] * 10  # Make some incomes very high
    df.loc[85:89, 'age'] = df.loc[85:89, 'age'] + 100  # Make some ages very high

    # Add duplicates
    duplicate_rows = df.sample(5).copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    return df

def test_data_analysis():
    """Test the data analysis functionality"""
    print("Creating test data...")
    df = create_test_data()

    print(f"Test data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print()

    # Test DataAnalyzer
    print("Testing DataAnalyzer...")
    analyzer = DataAnalyzer(df)
    analysis_results = analyzer.analyze_data_quality()

    print("Analysis Results:")
    print(f"Missing values: {analysis_results['missing_values']['total_missing']} ({analysis_results['missing_values']['total_percentage']}%)")
    print(f"Outliers detected: {len(analysis_results['outliers'])} columns")
    print(f"Duplicates: {analysis_results['duplicates']['count']} ({analysis_results['duplicates']['percentage']}%)")
    print()

    # Test code generation
    print("Testing code generation...")
    cleaning_code = analyzer.generate_missing_value_treatment_code('median')
    print("Generated cleaning code (first 200 chars):")
    print(cleaning_code[:200] + "...")
    print()

    comprehensive_code = analyzer.generate_comprehensive_cleaning_code()
    print("Generated comprehensive code (first 200 chars):")
    print(comprehensive_code[:200] + "...")
    print()

    # Test visualization suggestions
    visualization_suggestions = analyzer.suggest_visualizations()
    print(f"Visualization suggestions: {len(visualization_suggestions)}")
    for suggestion in visualization_suggestions:
        print(f"- {suggestion['type']}: {suggestion['description']}")
    print()

    # Test DataVisualizer
    print("Testing DataVisualizer...")
    visualizer = DataVisualizer(df, analysis_results)

    # Test missing values visualization code
    missing_code = visualizer.generate_visualization_code('missing_values')
    print("Missing values visualization code (first 150 chars):")
    print(missing_code[:150] + "...")
    print()

    # Test outlier visualization code
    outlier_code = visualizer.generate_visualization_code('outliers')
    print("Outlier visualization code (first 150 chars):")
    print(outlier_code[:150] + "...")
    print()

    # Test visualization suggestions
    viz_suggestions = visualizer.generate_visualization_suggestions()
    print(f"Extended visualization suggestions: {len(viz_suggestions)}")
    for suggestion in viz_suggestions:
        print(f"- {suggestion['type']}: {suggestion['description']}")
    print()

    print("All tests completed successfully!")

if __name__ == "__main__":
    test_data_analysis()