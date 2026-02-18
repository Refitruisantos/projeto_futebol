import os
import sys


def main() -> int:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    python_dir = os.path.join(base_dir, "python")

    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)

    # Import dinâmico (o ficheiro começa por dígitos e não pode ser importado como módulo normal)
    import importlib.util

    module_path = os.path.join(python_dir, "01_conexao_db.py")
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Ficheiro não encontrado: {module_path}")

    spec = importlib.util.spec_from_file_location("conexao_db", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar módulo: {module_path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    testar_conexao = getattr(mod, "testar_conexao")

    ok = bool(testar_conexao())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
