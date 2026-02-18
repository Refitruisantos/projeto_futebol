import os
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
python_dir = parent_dir / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

import importlib.util

module_path = python_dir / "01_conexao_db.py"
spec = importlib.util.spec_from_file_location("conexao_db", module_path)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load DB module: {module_path}")

conexao_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conexao_db)

DatabaseConnection = conexao_db.DatabaseConnection


def get_db():
    db = DatabaseConnection()
    try:
        yield db
    finally:
        db.close()
