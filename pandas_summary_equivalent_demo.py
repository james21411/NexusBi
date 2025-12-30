"""
Démonstration : Équivalent de la fonction summary() de R en Python avec pandas

Ce script montre comment obtenir les mêmes statistiques descriptives que R summary() 
en utilisant pandas describe() et d'autres fonctions pandas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Créer un dataset d'exemple similaire aux données de l'interface
np.random.seed(42)
data = {
    'revenue': np.random.normal(19250, 4250, 100),
    'sales': np.random.normal(5170, 1350, 100),
    'costs': np.random.normal(2906, 420, 100),
    'department': np.random.choice(['Sales', 'Marketing', 'Support', 'R&D'], 100),
    'status': np.random.choice(['Active', 'Pending', 'Completed'], 100),
    'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
}

df = pd.DataFrame(data)

print("=== ÉQUIVALENT DE R summary() EN PYTHON PANDAS ===\n")

print("1. STATISTIQUES DESCRIPTIVES COMPLÈTES (équivalent R summary())")
print("=" * 60)

# pandas describe() est l'équivalent direct de R summary()
numeric_summary = df.describe()
print("Statistiques pour les variables numériques:")
print(numeric_summary.round(2))

print("\n" + "=" * 60)
print("2. STATISTIQUES POUR LES VARIABLES CATÉGORIELLES")
print("=" * 60)

# Pour les variables catégorielles, on utilise value_counts()
categorical_columns = ['department', 'status', 'region']

for col in categorical_columns:
    print(f"\nRépartition de {col}:")
    value_counts = df[col].value_counts()
    percentages = df[col].value_counts(normalize=True) * 100
    
    for category, count in value_counts.items():
        percentage = percentages[category]
        print(f"  {category}: {count} ({percentage:.1f}%)")

print("\n" + "=" * 60)
print("3. ANALYSE COMPARATIVE : PANDAS vs R SUMMARY()")
print("=" * 60)

print("""
R summary() pour variables numériques donne :
- Min, 1st Qu, Median, Mean, 3rd Qu, Max

Pandas describe() donne :
- Count, Mean, Std, Min, 25%, 50%, 75%, Max

Ces deux fonctions sont équivalentes mais avec des noms différents :
""")

# Créer un tableau de correspondance
comparison_df = pd.DataFrame({
    'R summary()': ['Min', '1st Qu (Q1)', 'Median', 'Mean', '3rd Qu (Q3)', 'Max'],
    'Pandas describe()': ['min', '25% (Q1)', '50% (median)', 'mean', '75% (Q3)', 'max'],
    'Description': [
        'Valeur minimale',
        'Premier quartile (25e percentile)',
        'Médiane (50e percentile)',
        'Moyenne arithmétique',
        'Troisième quartile (75e percentile)',
        'Valeur maximale'
    ]
})

print(comparison_df.to_string(index=False))

print("\n" + "=" * 60)
print("4. FONCTIONS PANDAS ÉQUIVALENTES AUX STATISTIQUES R")
print("=" * 60)

print("""
Fonctions Pandas équivalentes aux fonctions R :
- summary()        → df.describe()
- mean()           → df.mean()
- median()         → df.median()
- sd()             → df.std()
- var()            → df.var()
- min()            → df.min()
- max()            → df.max()
- quantile()       → df.quantile()
- head()           → df.head()
- tail()           → df.tail()
- str()            → df.dtypes
- nrow()           → len(df)
- ncol()           → len(df.columns)
""")

print("\n5. EXEMPLES PRATIQUES")
print("=" * 30)

print("\nExemples d'utilisation des fonctions équivalentes :")

# Exemples pratiques
print(f"✓ Nombre de lignes: {len(df)} (équivalent R: nrow(df))")
print(f"✓ Nombre de colonnes: {len(df.columns)} (équivalent R: ncol(df))")
print(f"✓ Moyenne des revenus: {df['revenue'].mean():.2f} (équivalent R: mean(df$revenue))")
print(f"✓ Médiane des ventes: {df['sales'].median():.2f} (équivalent R: median(df$sales))")
print(f"✓ Écart-type des coûts: {df['costs'].std():.2f} (équivalent R: sd(df$costs))")
print(f"✓ Premier quartile revenus: {df['revenue'].quantile(0.25):.2f} (équivalent R: quantile(df$revenue, 0.25))")
print(f"✓ 95e percentile: {df['revenue'].quantile(0.95):.2f}")

print("\n6. INFORMATION SUR LES TYPES DE DONNÉES")
print("=" * 45)

print("Types de données dans le DataFrame:")
print(df.dtypes)

print("\n7. VALEURS MANQUANTES")
print("=" * 25)

missing_values = df.isnull().sum()
if missing_values.sum() == 0:
    print("✓ Aucune valeur manquante détectée")
else:
    print("Valeurs manquantes par colonne:")
    print(missing_values[missing_values > 0])

print("\n" + "=" * 60)
print("8. STATISTIQUES AVANCÉES")
print("=" * 60)

# Corrélations
print("\nMatrice de corrélation:")
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlation_matrix = df[numeric_cols].corr()
print(correlation_matrix.round(3))

# Skewness et Kurtosis
from scipy import stats
print("\nAsymétrie (Skewness) et Aplatissement (Kurtosis):")
for col in numeric_cols:
    skewness = stats.skew(df[col])
    kurtosis = stats.kurtosis(df[col])
    print(f"{col}: Skewness = {skewness:.3f}, Kurtosis = {kurtosis:.3f}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)

print("""
Pandas describe() est l'équivalent direct de R summary() et fournit
toutes les statistiques descriptives essentielles pour l'analyse de données.

Avantages de pandas describe():
✓ Plus flexible et extensible
✓ Meilleure intégration avec d'autres bibliothèques Python
✓ Support natif pour les données manquantes
✓ Performances optimisées pour les gros datasets

Dans l'interface NexusBi, nous utilisons exactement ces fonctions pandas
pour générer les statistiques descriptives que vous voyez.
""")

print("\nFin de la démonstration.")