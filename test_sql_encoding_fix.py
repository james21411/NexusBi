#!/usr/bin/env python3
"""
Test script to verify SQL dump encoding fix for UTF-16 files
"""
import sys
import os

# Add backend to path
sys.path.append('backend')

from app.services.data_sources.sql_dump_strategy import SQLDumpStrategy

def test_sql_encoding():
    """Test SQL dump with encoding detection"""
    
    # Path to the SQL file
    sql_file_path = "../../../fichiers/tes.sql"
    
    if not os.path.exists(sql_file_path):
        print(f"❌ SQL file not found: {sql_file_path}")
        return False
    
    try:
        # Create strategy instance
        config = {'file_path': sql_file_path}
        strategy = SQLDumpStrategy(config)
        
        print(f"🔍 Testing SQL dump parsing...")
        print(f"📁 File path: {sql_file_path}")
        
        # Connect and parse
        strategy.connect()
        
        # Get schema info
        schema = strategy.get_schema()
        
        print(f"\n📊 Parsing Results:")
        print(f"   Encoding used: {strategy.encoding}")
        print(f"   Number of tables: {len(schema.get('tables', []))}")
        
        # Get all table data
        all_data = strategy.get_all_table_data()
        
        print(f"\n📋 Table Data:")
        total_rows = 0
        for table_name, df in all_data.items():
            row_count = len(df)
            total_rows += row_count
            print(f"   {table_name}: {row_count} rows")
            
            if row_count > 0:
                print(f"      Columns: {list(df.columns)}")
                print(f"      Sample data (first 2 rows):")
                print(df.head(2).to_string(index=False))
                print()
        
        print(f"✅ Total rows across all tables: {total_rows}")
        
        if total_rows > 0:
            print(f"🎉 SUCCESS: SQL dump encoding fix works!")
            return True
        else:
            print(f"❌ FAILED: No data parsed from SQL dump")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing SQL dump encoding detection and parsing...")
    success = test_sql_encoding()
    
    if success:
        print("\n✨ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1)