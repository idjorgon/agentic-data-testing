"""
Data utilities for loading and processing test data
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Union
import pandas as pd


def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2):
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        file_path: Path to save file
        indent: JSON indentation
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)


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
