from typing import Any, List
from datetime import datetime
import json
import re
import pandas as pd
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.deps import get_current_active_user, get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.DataSource])
def read_data_sources(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all data sources.
    """
    data_sources = (
        db.query(models.DataSource)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return data_sources


@router.post("/", response_model=schemas.DataSource)
def create_data_source(
    *,
    db: Session = Depends(get_db),
    data_source_in: schemas.DataSourceCreate,
) -> Any:
    """
    Create new data source.
    """
    # Pour l'instant, utiliser le projet ID 1 par défaut
    project_id = data_source_in.project_id or 1
    
    # Vérifier si le projet existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        # Créer un projet par défaut si il n'existe pas
        default_project = models.Project(
            name="Projet Principal",
            description="Projet principal",
            owner_id=1,  # Utilisateur par défaut
            is_active=True
        )
        db.add(default_project)
        db.commit()
        db.refresh(default_project)
        project_id = default_project.id
    
    db_data_source = models.DataSource(**data_source_in.dict())
    db.add(db_data_source)
    db.commit()
    db.refresh(db_data_source)
    return db_data_source


@router.get("/{data_source_id}", response_model=schemas.DataSource)
def read_data_source(
    *,
    db: Session = Depends(get_db),
    data_source_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get data source by ID.
    """
    data_source = (
        db.query(models.DataSource)
        .join(models.Project)
        .filter(
            models.DataSource.id == data_source_id,
            models.Project.owner_id == current_user.id
        )
        .first()
    )
    
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return data_source


@router.put("/{data_source_id}", response_model=schemas.DataSource)
def update_data_source(
    *,
    db: Session = Depends(get_db),
    data_source_id: int,
    data_source_in: schemas.DataSourceUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update data source.
    """
    data_source = (
        db.query(models.DataSource)
        .join(models.Project)
        .filter(
            models.DataSource.id == data_source_id,
            models.Project.owner_id == current_user.id
        )
        .first()
    )
    
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    update_data = data_source_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(data_source, field, value)
    
    db.commit()
    db.refresh(data_source)
    return data_source


@router.delete("/{data_source_id}")
def delete_data_source(
    *,
    db: Session = Depends(get_db),
    data_source_id: int,
) -> Any:
    """
    Delete data source and all its associated data.
    """
    data_source = db.query(models.DataSource).filter(models.DataSource.id == data_source_id).first()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Delete all associated DataFrame data first
    db.query(models.DataFrameData).filter(models.DataFrameData.data_source_id == data_source_id).delete()

    # Delete the data source
    db.delete(data_source)
    db.commit()

    return {"message": "Data source and associated data deleted successfully"}


@router.post("/{data_source_id}/sync")
async def sync_data_source(
    *,
    db: Session = Depends(get_db),
    data_source_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Sync data source with external system.
    """
    from app.services.data_sync import create_sync_service
    
    data_source = db.query(models.DataSource).filter(models.DataSource.id == data_source_id).first()
    
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Utiliser le service de synchronisation réel
    sync_service = create_sync_service(db)
    
    try:
        sync_result = await sync_service.sync_data_source(data_source_id)
        
        if sync_result["success"]:
            return {
                "message": sync_result["message"],
                "last_sync": sync_result["last_sync"],
                "status": "connected",
                "rows_updated": sync_result["rows_updated"],
                "data_source_type": sync_result["data_source_type"],
                "schema_info": sync_result["schema_info"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur de synchronisation: {sync_result['message']}"
            )
            
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de la synchronisation: {str(e)}"
        )


# Alternative endpoint for demo/test without authentication
@router.post("/{data_source_id}/sync-demo")
async def sync_data_source_demo(
    *,
    db: Session = Depends(get_db),
    data_source_id: int,
) -> Any:
    """
    Sync data source with external system - Demo version without authentication.
    """
    from app.services.data_sync import create_sync_service
    
    data_source = db.query(models.DataSource).filter(models.DataSource.id == data_source_id).first()
    
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Utiliser le service de synchronisation réel
    sync_service = create_sync_service(db)
    
    try:
        sync_result = await sync_service.sync_data_source(data_source_id)
        
        if sync_result["success"]:
            return {
                "message": sync_result["message"],
                "last_sync": sync_result["last_sync"],
                "status": "connected",
                "rows_updated": sync_result["rows_updated"],
                "data_source_type": sync_result["data_source_type"],
                "schema_info": sync_result["schema_info"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur de synchronisation: {sync_result['message']}"
            )
            
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de la synchronisation: {str(e)}"
        )

@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
) -> Any:
    """
    Analyze a file to detect encoding, delimiter, and basic structure.
    """
    try:
        print(f"🔍 Analyzing file: {file.filename}, size: {file.size}")

        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.txt', '.sql']
        file_extension = '.' + file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type {file_extension} not supported")

        # Read file content
        content = await file.read()

        if file_extension == '.csv':
            # Try different encodings for CSV files
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            detected_encoding = None
            detected_delimiter = None
            columns = 0
            rows = 0

            for encoding in encodings_to_try:
                try:
                    text_content = content.decode(encoding)
                    # Try to detect delimiter automatically
                    sample = text_content[:1024]  # First 1KB for detection

                    # Common delimiters to try
                    delimiters = [',', ';', '\t', '|']
                    for delim in delimiters:
                        if delim in sample:
                            try:
                                test_df = pd.read_csv(io.StringIO(text_content), sep=delim, nrows=5)
                                if len(test_df.columns) > 1:  # Must have multiple columns
                                    detected_delimiter = delim
                                    detected_encoding = encoding
                                    columns = len(test_df.columns)
                                    # Count total rows (approximate)
                                    rows = text_content.count('\n') + 1
                                    break
                            except Exception as e:
                                print(f"⚠️  CSV test failed with delimiter '{delim}': {e}")
                                continue

                    if detected_delimiter:
                        break

                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"⚠️  CSV analysis failed with encoding {encoding}: {e}")
                    continue

            if not detected_encoding:
                raise HTTPException(status_code=400, detail="Unable to analyze CSV file encoding")

            return {
                "encoding": detected_encoding,
                "delimiter": detected_delimiter,
                "columns": columns,
                "rows": rows,
                "file_type": file_extension[1:]
            }
        
        elif file_extension == '.sql':
            # Analyze SQL dump file
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            detected_encoding = None
            tables_count = 0
            total_rows_estimate = 0
            
            for encoding in encodings_to_try:
                try:
                    text_content = content.decode(encoding)
                    
                    # Count CREATE TABLE statements
                    create_table_matches = len(re.findall(r'CREATE TABLE\s+`?\w+`?\s*\(', text_content, re.IGNORECASE))
                    
                    # Count INSERT statements
                    insert_matches = len(re.findall(r'INSERT INTO\s+`?\w+`?\s*\(', text_content, re.IGNORECASE))
                    
                    if create_table_matches > 0:
                        detected_encoding = encoding
                        tables_count = create_table_matches
                        total_rows_estimate = insert_matches
                        break
                        
                except UnicodeDecodeError:
                    continue
            
            if not detected_encoding:
                raise HTTPException(status_code=400, detail="Unable to analyze SQL dump file encoding")

            return {
                "encoding": detected_encoding,
                "delimiter": None,
                "columns": 0,
                "rows": total_rows_estimate,
                "tables": tables_count,
                "file_type": "sql"
            }

        elif file_extension == '.txt':
            # Analyze TXT files
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            detected_encoding = None
            detected_delimiter = None
            columns = 0
            rows = 0

            for encoding in encodings_to_try:
                try:
                    text_content = content.decode(encoding)
                    sample = text_content[:1024]  # First 1KB for detection

                    # Common delimiters to try
                    delimiters = [',', ';', '\t', '|', ' ']
                    for delim in delimiters:
                        if delim in sample:
                            try:
                                test_df = pd.read_csv(io.StringIO(text_content), sep=delim, nrows=5)
                                if len(test_df.columns) > 1:  # Must have multiple columns
                                    detected_delimiter = delim
                                    detected_encoding = encoding
                                    columns = len(test_df.columns)
                                    rows = text_content.count('\n') + 1
                                    break
                            except:
                                continue

                    if detected_delimiter:
                        break

                except UnicodeDecodeError:
                    continue

            if not detected_encoding:
                detected_encoding = 'utf-8'  # Default fallback

            return {
                "encoding": detected_encoding,
                "delimiter": detected_delimiter,
                "columns": columns,
                "rows": rows,
                "file_type": file_extension[1:]
            }
        else:
            # For other file types, basic analysis
            return {
                "encoding": "utf-8",
                "delimiter": None,
                "columns": 0,
                "rows": 0,
                "file_type": file_extension[1:]
            }

    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


@router.post("/upload", response_model=schemas.DataSource)
async def upload_data_source(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    name: str = None,
    project_id: int = 1,
) -> Any:
    """
    Upload a file and create a data source with DataFrame data.
    Automatically saves the file to UPLOAD_DIR and stores the full path.
    """
    try:
        print(f"📁 Upload started: {file.filename}, size: {file.size}")

        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.txt', '.sql']
        file_extension = '.' + file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type {file_extension} not supported")

        print(f"📄 File type validated: {file_extension}")

        # Read file content
        content = await file.read()
        print(f"📖 File content read: {len(content)} bytes")
        
        # Save file permanently to UPLOAD_DIR and store full path
        from app.core.config import settings
        import os
        import uuid
        
        # Create UPLOAD_DIR if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{file.filename}"
        full_file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        
        # Save the file permanently
        with open(full_file_path, 'wb') as f:
            f.write(content)
        
        print(f"💾 File saved permanently: {full_file_path}")
        print(f"📍 Full path stored in database: {full_file_path}")

        # Process file with pandas based on type
        if file_extension == '.csv':
            # Try different encodings for CSV files
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            detected_encoding = None
            detected_delimiter = None

            for encoding in encodings_to_try:
                try:
                    text_content = content.decode(encoding)
                    # Try to detect delimiter automatically
                    sample = text_content[:1024]  # First 1KB for detection
                    detected_delimiter = None

                    # Common delimiters to try
                    delimiters = [',', ';', '\t', '|']
                    for delim in delimiters:
                        if delim in sample:
                            try:
                                test_df = pd.read_csv(io.StringIO(text_content), sep=delim, nrows=5)
                                if len(test_df.columns) > 1:  # Must have multiple columns
                                    detected_delimiter = delim
                                    break
                            except:
                                continue

                    # If no delimiter detected, try pandas auto-detection
                    if detected_delimiter is None:
                        df = pd.read_csv(io.StringIO(text_content), sep=None, engine='python')
                    else:
                        df = pd.read_csv(io.StringIO(text_content), sep=detected_delimiter)

                    detected_encoding = encoding
                    print(f"✅ CSV processed successfully - Encoding: {encoding}, Delimiter: '{detected_delimiter or 'auto'}', Shape: {df.shape}")
                    break

                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"⚠️  Failed with {encoding}: {e}")
                    continue

            if df is None:
                raise HTTPException(status_code=400, detail="Unable to process CSV file. Supported encodings: UTF-8, Latin-1, CP1252, ISO-8859-1")

            # Store processing info in schema
            processing_info = {
                "detected_encoding": detected_encoding,
                "detected_delimiter": detected_delimiter,
                "processing_method": "pandas_csv"
            }
            
            # Validate CSV structure - but be more tolerant
            try:
                # Read a larger sample to check for structural issues
                sample_df = pd.read_csv(io.StringIO(text_content), sep=detected_delimiter or ',', nrows=100, on_bad_lines='skip')
                expected_cols = len(sample_df.columns)
                
                # Check for rows with different column counts - but don't fail
                lines = text_content.split('\n')
                problematic_lines = []
                for i, line in enumerate(lines[:200]):  # Check first 200 lines
                    if line.strip():
                        col_count = len(line.split(detected_delimiter or ','))
                        if col_count != expected_cols:
                            problematic_lines.append(f"Line {i+1}: expected {expected_cols} fields, got {col_count}")
                
                if problematic_lines:
                    print(f"⚠️  CSV structure issues detected: {len(problematic_lines)} problematic lines (tolerated)")
                    # Add warning to processing info but don't fail
                    processing_info["structure_warnings"] = problematic_lines[:5]  # Keep first 5 warnings
                    processing_info["tolerated_structure_issues"] = True
                    
            except Exception as e:
                print(f"⚠️  CSV structure validation failed: {e} (continuing anyway)")
                # Don't fail - just log the issue

        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(io.BytesIO(content))
            processing_info = {
                "detected_encoding": "utf-8",
                "detected_delimiter": None,
                "processing_method": "pandas_excel"
            }
        elif file_extension == '.json':
            df = pd.read_json(io.BytesIO(content))
            processing_info = {
                "detected_encoding": "utf-8",
                "detected_delimiter": None,
                "processing_method": "pandas_json"
            }
        elif file_extension == '.txt':
            # Try different encodings for TXT files
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            detected_encoding = None
            detected_delimiter = None

            for encoding in encodings_to_try:
                try:
                    text_content = content.decode(encoding)
                    
                    # Try different delimiters
                    delimiters = [',', ';', '\t', '|', ' ']
                    detected_delimiter = None
                    
                    for delim in delimiters:
                        if delim in text_content[:1000]:  # Check first 1000 chars
                            try:
                                test_df = pd.read_csv(io.StringIO(text_content), sep=delim, nrows=5)
                                if len(test_df.columns) > 1:  # Must have multiple columns
                                    detected_delimiter = delim
                                    break
                            except:
                                continue
                    
                    # If no delimiter detected, try pandas auto-detection
                    try:
                        if detected_delimiter is None:
                            df = pd.read_csv(io.StringIO(text_content), sep=None, engine='python', on_bad_lines='skip')
                        else:
                            df = pd.read_csv(io.StringIO(text_content), sep=detected_delimiter, on_bad_lines='skip')
                    except Exception as parse_error:
                        print(f"⚠️  TXT parsing failed with detected delimiter: {parse_error}")
                        # Try fallback: read as single column
                        lines = text_content.split('\n')
                        df = pd.DataFrame({'content': lines})
                        detected_delimiter = None
                        print(f"✅ TXT fallback processed as single column - Shape: {df.shape}")

                    detected_encoding = encoding
                    print(f"✅ TXT processed successfully - Encoding: {encoding}, Delimiter: '{detected_delimiter or 'auto'}', Shape: {df.shape}")
                    break

                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"⚠️  Failed TXT processing with {encoding}: {e}")
                    continue

            if df is None:
                # Fallback: try to read as simple text file
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    lines = text_content.split('\n')
                    # Create simple DataFrame with single column
                    df = pd.DataFrame({'content': lines})
                    detected_encoding = 'utf-8'
                    print(f"✅ TXT fallback processed as single column - Shape: {df.shape}")
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Unable to process TXT file: {str(e)}")

            # Store processing info for TXT
            processing_info = {
                "detected_encoding": detected_encoding,
                "detected_delimiter": detected_delimiter,
                "processing_method": "pandas_txt"
            }
        elif file_extension == '.sql':
            # Process SQL dump file using the strategy
            try:
                from app.services.data_sources.factory import DataSourceFactory
                
                # Save file temporarily for analysis
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sql') as tmp_file:
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                
                try:
                    # Try different encodings
                    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    detected_encoding = None
                    
                    for encoding in encodings_to_try:
                        try:
                            # Test if we can read the file with this encoding
                            with open(tmp_file_path, 'r', encoding=encoding) as f:
                                sample = f.read(1024)  # Read first 1KB
                            
                            # Check if it contains SQL statements
                            if 'CREATE TABLE' in sample.upper() or 'INSERT INTO' in sample.upper():
                                detected_encoding = encoding
                                break
                        except UnicodeDecodeError:
                            continue
                    
                    if not detected_encoding:
                        detected_encoding = 'utf-8'  # Default fallback
                    
                    # Use SQL dump strategy to analyze the file
                    factory = DataSourceFactory()
                    strategy = factory.get_source('sql_dump', {
                        'file_path': tmp_file_path,
                        'encoding': detected_encoding
                    })
                    
                    strategy.connect()
                    
                    try:
                        # Get schema information
                        schema = strategy.get_schema()
                        tables_count = len(schema.get('tables', []))
                        
                        # Get all data from all tables - NO LIMIT for complete data storage
                        all_table_data = strategy.get_all_table_data()  # Get ALL data, not just preview
                        
                        # Combine all tables into a single DataFrame
                        if all_table_data:
                            all_dataframes = []
                            for table_name, table_df in all_table_data.items():
                                # Add table name column to identify source
                                table_df_with_source = table_df.copy()
                                table_df_with_source.insert(0, '_source_table', table_name)
                                all_dataframes.append(table_df_with_source)
                            
                            combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
                        else:
                            combined_df = pd.DataFrame()
                        
                        # Store processing info in schema
                        processing_info = {
                            "detected_encoding": detected_encoding,
                            "tables_count": tables_count,
                            "processing_method": "sql_dump_parser",
                            "total_data_rows": len(combined_df),  # Store actual rows count
                            "tables_processed": list(all_table_data.keys()) if all_table_data else []
                        }
                        
                        print(f"✅ SQL dump processed successfully - Encoding: {detected_encoding}, Tables: {tables_count}, Total rows: {len(combined_df)}")
                        
                        # Use combined_df instead of df for further processing
                        df = combined_df
                        
                    finally:
                        strategy.disconnect()
                        
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
                        
            except Exception as e:
                print(f"⚠️  SQL dump processing failed: {e}")
                # Create empty DataFrame as fallback
                df = pd.DataFrame()
                processing_info = {
                    "detected_encoding": "utf-8",
                    "tables_count": 0,
                    "processing_method": "sql_dump_fallback",
                    "error": str(e),
                    "fallback": True
                }
                print(f"⚠️  SQL dump processing failed, using fallback: {e}")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
        
        # Ensure processing_info is always defined
        if 'processing_info' not in locals():
            processing_info = {
                "detected_encoding": "utf-8",
                "detected_delimiter": None,
                "processing_method": "unknown",
                "fallback": True
            }

        print(f"📊 DataFrame created: {len(df)} rows, {len(df.columns)} columns")

        # Create schema info based on file type
        if file_extension == '.sql':
            # For SQL dumps, create a more complex schema with table information
            try:
                # Get the strategy again to access schema information
                factory = DataSourceFactory()
                strategy = factory.get_source('sql_dump', {
                    'file_path': file.filename,  # Use original filename
                    'encoding': processing_info.get('detected_encoding', 'utf-8')
                })
                
                # Create a temporary file to analyze
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sql') as tmp_file:
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                
                try:
                    strategy_temp = factory.get_source('sql_dump', {
                        'file_path': tmp_file_path,
                        'encoding': processing_info.get('detected_encoding', 'utf-8')
                    })
                    
                    strategy_temp.connect()
                    try:
                        schema = strategy_temp.get_schema()
                        schema_info = {
                            "tables": schema.get('tables', []),
                            "total_tables": len(schema.get('tables', [])),
                            "total_rows": sum(table.get('row_count', 0) for table in schema.get('tables', [])),
                            "row_count": len(df),  # Add row_count for frontend compatibility
                            "sample_data_columns": [{"name": col, "type": str(df[col].dtype)} for col in df.columns],
                            "sample_data_row_count": len(df),
                            "sample_data_column_count": len(df.columns),
                            "processing_info": processing_info
                        }
                    finally:
                        strategy_temp.disconnect()
                        
                finally:
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
                        
            except Exception as e:
                print(f"⚠️  Failed to get detailed SQL schema: {e}")
                # Fallback schema for SQL files
                schema_info = {
                    "tables": [],
                    "total_tables": 0,
                    "total_rows": 0,
                    "row_count": len(df),  # Add row_count for frontend compatibility
                    "sample_data_columns": [{"name": col, "type": str(df[col].dtype)} for col in df.columns],
                    "sample_data_row_count": len(df),
                    "sample_data_column_count": len(df.columns),
                    "processing_info": processing_info
                }
        else:
            # For other file types, create standard schema
            schema_info = {
                "columns": [{"name": col, "type": str(df[col].dtype)} for col in df.columns],
                "row_count": len(df),
                "column_count": len(df.columns),
                "processing_info": processing_info
            }

        print(f"📋 Schema info created: {schema_info}")

        # Vérifier si le projet existe
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            print("🏗️  Creating default project...")

            # Vérifier s'il y a des utilisateurs
            user_count = db.query(models.User).count()
            if user_count == 0:
                print("👤 Creating default user...")

                # Créer un utilisateur par défaut
                from app.core.security import get_password_hash
                try:
                    default_user = models.User(
                        email="admin@nexusbi.com",
                        hashed_password=get_password_hash("admin"),
                        full_name="Administrateur NexusBi",
                        is_active=True,
                        is_superuser=True
                    )
                    db.add(default_user)
                    db.commit()
                    db.refresh(default_user)
                    owner_id = default_user.id
                except Exception as e:
                    print(f"⚠️  Password hash failed: {e}, using fallback")
                    # Fallback sans hash
                    default_user = models.User(
                        email="admin@nexusbi.com",
                        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfLkIwXH0qQhEy",
                        full_name="Administrateur NexusBi",
                        is_active=True,
                        is_superuser=True
                    )
                    db.add(default_user)
                    db.commit()
                    db.refresh(default_user)
                    owner_id = default_user.id
            else:
                # Utiliser le premier utilisateur existant
                first_user = db.query(models.User).first()
                owner_id = first_user.id

            # Créer un projet par défaut
            default_project = models.Project(
                name="Projet Principal",
                description="Projet principal",
                owner_id=owner_id,
                is_active=True
            )
            db.add(default_project)
            db.commit()
            db.refresh(default_project)
            project_id = default_project.id

        print(f"✅ Project ready: ID {project_id}")

        # Create data source with full file path
        data_source_name = name or file.filename.rsplit('.', 1)[0]
        db_data_source = models.DataSource(
            name=data_source_name,
            type=file_extension[1:],  # Remove the dot
            project_id=project_id,
            file_path=full_file_path,  # Store full absolute path
            schema_info=json.dumps(schema_info),
            is_active=True
        )

        db.add(db_data_source)
        db.commit()
        db.refresh(db_data_source)

        print(f"✅ Data source created: ID {db_data_source.id}")

        # Detect large data columns (images base64, etc.)
        def detect_large_data_columns(dataframe):
            """Détecte les colonnes avec des données volumineuses"""
            large_columns = {}
            LARGE_DATA_THRESHOLD = 10 * 1024  # 10KB
            
            for col in dataframe.columns:
                large_values = 0
                total_values = 0
                
                for val in dataframe[col].dropna():
                    total_values += 1
                    val_str = str(val)
                    # Détecter base64 (commence par常见的base64 patterns)
                    if (len(val_str) > LARGE_DATA_THRESHOLD or
                        val_str.startswith('data:image/') or
                        val_str.startswith('iVBOR') or  # PNG base64
                        val_str.startswith('/9j/') or   # JPEG base64
                        (len(val_str) > 100 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in val_str[:100]))):
                        large_values += 1
                    
                    # Vérifier seulement les premières valeurs pour la performance
                    if total_values >= 10:
                        break
                
                # Si plus de 50% des valeurs échantillonnées sont volumineuses, marquer la colonne
                if total_values > 0 and large_values / total_values > 0.5:
                    large_columns[col] = True
            
            return large_columns

        def sanitize_large_data(value, is_large_column):
            """Remplace les données volumineuses par des labels"""
            if is_large_column:
                if not value or value == 'nan' or value == 'None':
                    return "[Données vides]"
                else:
                    return f"[Données volumineuses - {len(value)} caractères]"
            return value

        # Store DataFrame data
        print(f"💾 Storing {len(df)} DataFrame rows...")
        
        # Détecter les colonnes avec des données volumineuses
        large_columns = detect_large_data_columns(df)
        if large_columns:
            print(f"🔍 Détecté colonnes avec données volumineuses: {list(large_columns.keys())}")
        
        for idx, row in df.iterrows():
            row_dict = {}
            for col, val in row.items():
                val_str = str(val) if val is not None else ""
                # Sanitize si c'est une colonne avec des données volumineuses
                sanitized_val = sanitize_large_data(val_str, large_columns.get(col, False))
                row_dict[col] = sanitized_val
            
            db_row = models.DataFrameData(
                data_source_id=db_data_source.id,
                row_data=json.dumps(row_dict),
                row_index=idx
            )
            db.add(db_row)

        db.commit()
        print("✅ DataFrame data stored successfully")
        if large_columns:
            print(f"📊 {len(large_columns)} colonnes avec données volumineuses处理ées")

        return db_data_source

    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/{data_source_id}/data")
def get_data_source_data(
    *,
    db: Session = Depends(get_db),
    data_source_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get data rows for a data source.
    """
    # Check if data source exists
    data_source = db.query(models.DataSource).filter(models.DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Get total count of rows for this data source
    total_count = db.query(models.DataFrameData).filter(models.DataFrameData.data_source_id == data_source_id).count()

    # Get data rows
    data_rows = (
        db.query(models.DataFrameData)
        .filter(models.DataFrameData.data_source_id == data_source_id)
        .order_by(models.DataFrameData.row_index)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Parse row data
    rows = []
    for row in data_rows:
        rows.append(json.loads(row.row_data))

    return {
        "data_source_id": data_source_id,
        "rows": rows,
        "total_rows": total_count,  # Use real total count, not just returned rows
        "skip": skip,
        "limit": limit
    }