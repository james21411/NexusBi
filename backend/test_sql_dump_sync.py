#!/usr/bin/env python3
"""
Test script for SQL dump synchronization
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.db.session import SessionLocal
from app.services.data_sync import create_sync_service
from app.models.project import DataSource


def create_test_sql_dump_source():
    """Create a test SQL dump data source"""
    db = SessionLocal()
    
    try:
        # Delete existing test source if it exists
        existing = db.query(DataSource).filter(DataSource.name == "Test SQL Dump").first()
        if existing:
            db.delete(existing)
            db.commit()
        
        # Create a new test source
        test_source = DataSource(
            name="Test SQL Dump",
            type="sql",
            file_path="/tmp/test_sql_dump.sql",
            connection_string=None,
            is_active=True,
            schema_info='{"processing_info": {"detected_encoding": "utf-8"}}'
        )
        
        db.add(test_source)
        db.commit()
        db.refresh(test_source)
        
        print(f"✅ Created test SQL dump source with ID: {test_source.id}")
        return test_source.id
        
    except Exception as e:
        print(f"❌ Error creating test source: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()


async def test_sync(sql_source_id: int):
    """Test the synchronization"""
    db = SessionLocal()
    
    try:
        # Create sync service
        sync_service = create_sync_service(db)
        
        # Run synchronization
        result = await sync_service.sync_data_source(sql_source_id)
        
        print("\n📊 Sync Result:")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Rows updated: {result.get('rows_updated', 'N/A')}")
        print(f"Data source type: {result.get('data_source_type', 'N/A')}")
        
        if result['success']:
            schema_info = result.get('schema_info', {})
            print(f"\n📋 Schema Info:")
            print(f"Total tables: {schema_info.get('total_tables', 'N/A')}")
            print(f"Total rows: {schema_info.get('total_rows', 'N/A')}")
            print(f"Processing info: {schema_info.get('processing_info', {})}")
            
            # Check data in database
            from app.models.project import DataFrameData
            data_records = db.query(DataFrameData).filter(DataFrameData.data_source_id == sql_source_id).all()
            print(f"\n💾 Database records: {len(data_records)}")
            
            # Show sample data
            if data_records:
                print("Sample records:")
                for i, record in enumerate(data_records[:5]):  # Show first 5
                    import json
                    row_data = json.loads(record.row_data)
                    print(f"  Row {i+1}: {row_data}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during sync: {str(e)}")
    finally:
        db.close()


async def main():
    """Main test function"""
    print("🧪 Testing SQL dump synchronization...")
    
    # Create test source
    source_id = create_test_sql_dump_source()
    if not source_id:
        return
    
    # Test synchronization
    await test_sync(source_id)


if __name__ == "__main__":
    asyncio.run(main())