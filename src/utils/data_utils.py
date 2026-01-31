"""
Data utilities for loading and processing test data
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any, Union, Optional
import pandas as pd


# Security: Define allowed base directories for file operations
ALLOWED_BASE_DIRS = [
    Path.cwd(),  # Current working directory
    Path.home() / "Documents",
    Path("/tmp"),
]

# Maximum file size to prevent DoS (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


def _validate_file_path(file_path: Union[str, Path], 
                        operation: str = "read",
                        allowed_dirs: Optional[List[Path]] = None) -> Path:
    """
    Validate file path for security
    
    Args:
        file_path: Path to validate
        operation: 'read' or 'write'
        allowed_dirs: Override default allowed directories
        
    Returns:
        Validated resolved Path object
        
    Raises:
        ValueError: If path is invalid or unsafe
        FileNotFoundError: If file doesn't exist (for read operations)
    """
    try:
        # Convert to Path and resolve to absolute path
        path = Path(file_path).resolve()
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid file path: {file_path}") from e
    
    # Check for path traversal attempts
    if ".." in str(file_path):
        raise ValueError(f"Path traversal detected in: {file_path}")
    
    # Validate against allowed directories
    base_dirs = allowed_dirs if allowed_dirs else ALLOWED_BASE_DIRS
    
    # For project files, also allow project root and subdirectories
    project_root = Path(__file__).parent.parent.parent
    if project_root not in base_dirs:
        base_dirs = base_dirs + [project_root]
    
    is_allowed = False
    for allowed_dir in base_dirs:
        try:
            allowed_dir_resolved = allowed_dir.resolve()
            if path.is_relative_to(allowed_dir_resolved):
                is_allowed = True
                break
        except (ValueError, AttributeError):
            # is_relative_to not available in Python < 3.9
            try:
                path.relative_to(allowed_dir.resolve())
                is_allowed = True
                break
            except ValueError:
                continue
    
    if not is_allowed:
        raise ValueError(
            f"Access denied: {file_path} is outside allowed directories. "
            f"Allowed: {[str(d) for d in base_dirs]}"
        )
    
    # For read operations, ensure file exists and is a file
    if operation == "read":
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        # Check file size to prevent DoS
        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE} bytes)"
            )
    
    # For write operations, ensure parent directory exists or can be created
    if operation == "write":
        if not path.parent.exists():
            # Validate parent directory is also allowed
            parent_allowed = False
            for allowed_dir in base_dirs:
                try:
                    if path.parent.is_relative_to(allowed_dir.resolve()):
                        parent_allowed = True
                        break
                except (ValueError, AttributeError):
                    try:
                        path.parent.relative_to(allowed_dir.resolve())
                        parent_allowed = True
                        break
                    except ValueError:
                        continue
            
            if not parent_allowed:
                raise ValueError(f"Cannot create directory outside allowed paths: {path.parent}")
    
    return path


def load_json(file_path: Union[str, Path], 
              allowed_dirs: Optional[List[Path]] = None) -> Dict[str, Any]:
    """
    Safely load JSON file with path validation
    
    Args:
        file_path: Path to JSON file
        allowed_dirs: Optional list of allowed base directories
        
    Returns:
        Parsed JSON data
        
    Raises:
        ValueError: If path is invalid or unsafe
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    validated_path = _validate_file_path(file_path, operation="read", allowed_dirs=allowed_dirs)
    
    try:
        with open(validated_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in file {file_path}: {e.msg}",
            e.doc,
            e.pos
        )


def save_json(data: Dict[str, Any], 
              file_path: Union[str, Path], 
              indent: int = 2,
              allowed_dirs: Optional[List[Path]] = None):
    """
    Safely save data to JSON file with path validation
    
    Args:
        data: Data to save
        file_path: Path to save file
        indent: JSON indentation
        allowed_dirs: Optional list of allowed base directories
        
    Raises:
        ValueError: If path is invalid or unsafe
        TypeError: If data is not JSON serializable
    """
    validated_path = _validate_file_path(file_path, operation="write", allowed_dirs=allowed_dirs)
    
    # Create parent directory if it doesn't exist
    validated_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(validated_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str)
    except TypeError as e:
        raise TypeError(f"Data is not JSON serializable: {e}")


def load_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Load CSV file as list of dictionaries
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of records
    """
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data


def save_csv(data: List[Dict[str, Any]], file_path: Union[str, Path]):
    """
    Save data to CSV file
    
    Args:
        data: List of dictionaries
        file_path: Path to save file
    """
    if not data:
        return
    
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = list(data[0].keys())
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_dataframe(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load data file into pandas DataFrame
    
    Supports CSV, JSON, and Parquet formats
    
    Args:
        file_path: Path to data file
        
    Returns:
        pandas DataFrame
    """
    file_path = Path(file_path)
    
    if file_path.suffix == '.csv':
        return pd.read_csv(file_path)
    elif file_path.suffix == '.json':
        return pd.read_json(file_path)
    elif file_path.suffix == '.parquet':
        return pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def save_dataframe(df: pd.DataFrame, file_path: Union[str, Path]):
    """
    Save pandas DataFrame to file
    
    Args:
        df: DataFrame to save
        file_path: Path to save file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if file_path.suffix == '.csv':
        df.to_csv(file_path, index=False)
    elif file_path.suffix == '.json':
        df.to_json(file_path, orient='records', indent=2)
    elif file_path.suffix == '.parquet':
        df.to_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def infer_schema_from_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Infer JSON schema from sample data
    
    Args:
        data: List of data records
        
    Returns:
        Inferred JSON schema
    """
    if not data:
        return {"type": "object", "properties": {}}
    
    # Use pandas to infer types
    df = pd.DataFrame(data)
    
    properties = {}
    required = []
    
    for column in df.columns:
        # Determine type
        dtype = df[column].dtype
        
        if dtype == 'object':
            field_type = "string"
        elif dtype == 'int64':
            field_type = "integer"
        elif dtype == 'float64':
            field_type = "number"
        elif dtype == 'bool':
            field_type = "boolean"
        else:
            field_type = "string"
        
        properties[column] = {"type": field_type}
        
        # Check if required (no nulls)
        if df[column].notna().all():
            required.append(column)
        
        # Add numeric constraints if applicable
        if field_type in ["integer", "number"]:
            properties[column]["minimum"] = int(df[column].min()) if field_type == "integer" else float(df[column].min())
            properties[column]["maximum"] = int(df[column].max()) if field_type == "integer" else float(df[column].max())
    
    schema = {
        "type": "object",
        "properties": properties
    }
    
    if required:
        schema["required"] = required
    
    return schema
