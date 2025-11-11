"""
Quick test script for Data Analyzer Tool
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Create test data
print("📊 Creating test dataset...")
np.random.seed(42)
data = {
    'name': [f'Person_{i}' for i in range(100)],
    'age': np.random.randint(18, 65, 100),
    'salary': np.random.randint(30000, 120000, 100),
    'department': np.random.choice(['IT', 'HR', 'Sales', 'Marketing'], 100),
    'experience': np.random.randint(0, 20, 100)
}
df = pd.DataFrame(data)

# Add some missing values
df.loc[5:10, 'salary'] = np.nan

# Save test file
test_dir = Path("uploads/test_data")
test_dir.mkdir(parents=True, exist_ok=True)
test_file = test_dir / "employee_data.csv"
df.to_csv(test_file, index=False)
print(f"✓ Created test file: {test_file}")
print(f"  Shape: {df.shape}")
print(f"  Columns: {df.columns.tolist()}")

# Test the data analyzer
print("\n" + "="*60)
print("Testing Data Analyzer")
print("="*60)

from backend.tools.data_analyzer_integration import (
    analyze_dataset,
    create_visualization,
    generate_code
)
import json

# Test 1: Basic stats
print("\n1️⃣ Testing basic statistics...")
result = analyze_dataset(str(test_file), "basic_stats")
result_dict = json.loads(result)
if result_dict['success']:
    print("✓ Basic stats successful!")
    print(f"  Rows: {result_dict['rows']}")
    print(f"  Columns: {result_dict['columns']}")
    if result_dict.get('missing_values'):
        print(f"  Missing values: {result_dict['missing_values']}")
else:
    print(f"✗ Failed: {result_dict.get('error')}")

# Test 2: Correlations
print("\n2️⃣ Testing correlations...")
result = analyze_dataset(str(test_file), "correlations", threshold=0.3)
result_dict = json.loads(result)
if result_dict['success']:
    print("✓ Correlations successful!")
    if result_dict['high_correlations']:
        print(f"  Found {len(result_dict['high_correlations'])} high correlations")
        for corr in result_dict['high_correlations'][:3]:
            print(f"    {corr['col1']} <-> {corr['col2']}: {corr['correlation']:.3f}")
else:
    print(f"✗ Failed: {result_dict.get('error')}")

# Test 3: Cleaning suggestions
print("\n3️⃣ Testing cleaning suggestions...")
result = analyze_dataset(str(test_file), "cleaning_suggestions")
result_dict = json.loads(result)
if result_dict['success']:
    print("✓ Cleaning suggestions successful!")
    print(f"  Total issues found: {result_dict['total_issues']}")
    for suggestion in result_dict['suggestions'][:3]:
        print(f"    {suggestion['type']}: {suggestion['issue']}")
else:
    print(f"✗ Failed: {result_dict.get('error')}")

# Test 4: Visualization
print("\n4️⃣ Testing visualization...")
result = create_visualization(str(test_file), "histogram", x_column="age")
result_dict = json.loads(result)
if result_dict['success']:
    print("✓ Visualization successful!")
    print(f"  Chart saved: {result_dict['relative_path']}")
else:
    print(f"✗ Failed: {result_dict.get('error')}")

# Test 5: Code generation
print("\n5️⃣ Testing code generation...")
result = generate_code(
    operation="handle_missing",
    file_path=str(test_file),
    column="salary",
    method="mean"
)
result_dict = json.loads(result)
if result_dict['success']:
    print("✓ Code generation successful!")
    print("  Generated code:")
    for line in result_dict['code'].split('\n'):
        print(f"    {line}")
else:
    print(f"✗ Failed: {result_dict.get('error')}")

print("\n" + "="*60)
print("✅ All tests completed!")
print("="*60)

