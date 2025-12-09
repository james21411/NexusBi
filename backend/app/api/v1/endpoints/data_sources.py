from typing import Any, List
from datetime import datetime
import json
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
    
    # TODO: Implement actual sync logic based on data source type
    # For now, just update the timestamp
    data_source.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Data source synced successfully",
        "last_sync": data_source.updated_at.isoformat(),
        "status": "connected"
    }


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
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.txt']
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
                            except:
                                continue

                    if detected_delimiter:
                        break

                except UnicodeDecodeError:
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
    """
    try:
        print(f"📁 Upload started: {file.filename}, size: {file.size}")

        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.txt']
        file_extension = '.' + file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type {file_extension} not supported")

        print(f"📄 File type validated: {file_extension}")

        # Read file content
        content = await file.read()
        print(f"📖 File content read: {len(content)} bytes")

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

        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(io.BytesIO(content))
        elif file_extension == '.json':
            df = pd.read_json(io.BytesIO(content))
        elif file_extension == '.txt':
            # Try to detect delimiter
            text_content = content.decode('utf-8')
            df = pd.read_csv(io.StringIO(text_content), sep=None, engine='python')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        print(f"📊 DataFrame created: {len(df)} rows, {len(df.columns)} columns")

        # Create schema info
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

        # Create data source
        data_source_name = name or file.filename.rsplit('.', 1)[0]
        db_data_source = models.DataSource(
            name=data_source_name,
            type=file_extension[1:],  # Remove the dot
            project_id=project_id,
            file_path=file.filename,
            schema_info=json.dumps(schema_info),
            is_active=True
        )

        db.add(db_data_source)
        db.commit()
        db.refresh(db_data_source)

        print(f"✅ Data source created: ID {db_data_source.id}")

        # Store DataFrame data
        print(f"💾 Storing {len(df)} DataFrame rows...")
        for idx, row in df.iterrows():
            row_dict = {col: str(val) for col, val in row.items()}
            db_row = models.DataFrameData(
                data_source_id=db_data_source.id,
                row_data=json.dumps(row_dict),
                row_index=idx
            )
            db.add(db_row)

        db.commit()
        print("✅ DataFrame data stored successfully")

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
        "total_rows": len(rows),
        "skip": skip,
        "limit": limit
    }