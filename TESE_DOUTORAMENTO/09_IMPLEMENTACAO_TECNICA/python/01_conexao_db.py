"""
Módulo de Conexão com PostgreSQL + TimescaleDB
Classe para gerir conexões com a base de dados da tese
"""

import os
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor, execute_values
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Classe para gerir conexões com PostgreSQL + TimescaleDB
    
    Uso:
        db = DatabaseConnection()
        df = db.query_to_dataframe("SELECT * FROM atletas")
        db.close()
    """
    
    def __init__(self, 
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 database: Optional[str] = None,
                 user: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Inicializar conexão com a base de dados
        
        Args:
            host: Endereço do servidor (default: variável ambiente DB_HOST)
            port: Porta (default: 5432)
            database: Nome da base de dados (default: futebol_tese)
            user: Username (default: postgres)
            password: Password (default: variável ambiente DB_PASSWORD)
        """
        # Carregar variáveis de ambiente
        try:
            load_dotenv(encoding="utf-8")
        except UnicodeDecodeError:
            load_dotenv(encoding="utf-16")
        
        # Configurações de conexão
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'futebol_tese')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
        
        # Connection pool (para melhor performance)
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"✅ Conexão estabelecida com {self.database} em {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar: {e}")
            raise
    
    def get_connection(self):
        """Obter conexão do pool"""
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Devolver conexão ao pool"""
        self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> None:
        """
        Executar query sem retorno de dados (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query
            params: Parâmetros da query (opcional)
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                logger.info(f"✅ Query executada: {query[:100]}...")
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao executar query: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def query_to_dataframe(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """
        Executar query e retornar DataFrame pandas
        
        Args:
            query: SQL query SELECT
            params: Parâmetros da query (opcional)
            
        Returns:
            DataFrame com resultados
        """
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(query, conn, params=params)
            logger.info(f"✅ Query retornou {len(df)} linhas")
            return df
        except Exception as e:
            logger.error(f"❌ Erro na query: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def query_to_dict(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executar query e retornar lista de dicionários
        
        Args:
            query: SQL query SELECT
            params: Parâmetros da query
            
        Returns:
            Lista de dicionários (cada linha é um dict)
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.info(f"✅ Query retornou {len(results)} linhas")
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"❌ Erro na query: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def insert_dataframe(self, df: pd.DataFrame, table: str, batch_size: int = 1000) -> None:
        """
        Inserir DataFrame em tabela (método COPY - muito rápido)
        
        Args:
            df: DataFrame a inserir
            table: Nome da tabela
            batch_size: Tamanho do batch (para grandes volumes)
        """
        conn = self.get_connection()
        try:
            # Converter DataFrame para tuples
            columns = df.columns.tolist()
            values = [tuple(row) for row in df.values]
            
            # Criar query de INSERT
            query = f"""
                INSERT INTO {table} ({', '.join(columns)}) 
                VALUES %s
            """
            
            with conn.cursor() as cursor:
                execute_values(cursor, query, values, page_size=batch_size)
                conn.commit()
                
            logger.info(f"✅ {len(df)} linhas inseridas em {table}")
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao inserir dados: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def verificar_timescaledb(self) -> bool:
        """
        Verificar se TimescaleDB está ativo
        
        Returns:
            True se TimescaleDB está instalado
        """
        query = "SELECT * FROM pg_extension WHERE extname = 'timescaledb'"
        result = self.query_to_dict(query)
        
        if result:
            logger.info("✅ TimescaleDB está ativo")
            return True
        else:
            logger.warning("⚠️ TimescaleDB não encontrado")
            return False
    
    def listar_hypertables(self) -> pd.DataFrame:
        """
        Listar todas as hypertables
        
        Returns:
            DataFrame com informação das hypertables
        """
        query = """
            SELECT 
                hypertable_schema,
                hypertable_name,
                num_dimensions,
                num_chunks,
                compression_enabled
            FROM timescaledb_information.hypertables
        """
        return self.query_to_dataframe(query)
    
    def estatisticas_tabela(self, table: str) -> Dict[str, Any]:
        """
        Obter estatísticas de uma tabela
        
        Args:
            table: Nome da tabela
            
        Returns:
            Dicionário com estatísticas
        """
        # Contar linhas
        count_query = f"SELECT COUNT(*) as total FROM {table}"
        count = self.query_to_dict(count_query)[0]['total']
        
        # Tamanho
        size_query = f"SELECT pg_size_pretty(pg_total_relation_size('{table}')) as size"
        size = self.query_to_dict(size_query)[0]['size']
        
        return {
            'tabela': table,
            'num_linhas': count,
            'tamanho': size
        }
    
    def close(self):
        """Fechar todas as conexões"""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()
            logger.info("🔒 Conexões fechadas")


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def testar_conexao():
    """Testar conexão com a base de dados"""
    try:
        db = DatabaseConnection()
        
        # Verificar TimescaleDB
        if db.verificar_timescaledb():
            print("✅ TimescaleDB está operacional")
        
        # Listar hypertables
        hypertables = db.listar_hypertables()
        if not hypertables.empty:
            print("\n📊 Hypertables criadas:")
            print(hypertables.to_string(index=False))
        else:
            print("⚠️ Nenhuma hypertable encontrada")
        
        # Listar tabelas
        tabelas = db.query_to_dataframe("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        print("\n📋 Tabelas disponíveis:")
        for table in tabelas['table_name']:
            stats = db.estatisticas_tabela(table)
            print(f"  - {table}: {stats['num_linhas']} linhas, {stats['tamanho']}")
        
        db.close()
        print("\n✅ Teste de conexão bem-sucedido!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste de conexão: {e}")
        return False


if __name__ == "__main__":
    # Executar teste ao executar este ficheiro
    print("🧪 Testando conexão com base de dados...\n")
    testar_conexao()
