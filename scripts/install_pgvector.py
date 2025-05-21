#!/usr/bin/env python3
"""
Script to install pgvector extension from compiled source
"""

import os
import logging
import shutil
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Install pgvector extension files and create extension in database"""
    try:
        # PostgreSQL info
        db_user = "postgres"
        db_password = "4010"
        db_name = "ai_assistant"
        
        # PostgreSQL paths - adjust as needed for your installation
        pg_path = "F:/PostgreSQL"
        pg_lib_dir = os.path.join(pg_path, "lib")
        pg_ext_dir = os.path.join(pg_path, "share/extension")
        
        # pgvector source paths
        pgvector_src = "F:/pgvector-source"
        pgvector_dll = os.path.join(pgvector_src, "vector.dll")
        pgvector_control = os.path.join(pgvector_src, "vector.control")
        pgvector_sql_dir = os.path.join(pgvector_src, "sql")
        
        # Ensure directories exist
        os.makedirs(pg_ext_dir, exist_ok=True)
        
        # Copy DLL to lib directory
        logger.info(f"Copying vector.dll to {pg_lib_dir}")
        if os.path.exists(pgvector_dll):
            shutil.copy2(pgvector_dll, pg_lib_dir)
            logger.info("DLL copied successfully")
        else:
            logger.error(f"DLL not found at {pgvector_dll}")
            return False
        
        # Copy control file to extension directory
        logger.info(f"Copying vector.control to {pg_ext_dir}")
        if os.path.exists(pgvector_control):
            shutil.copy2(pgvector_control, pg_ext_dir)
            logger.info("Control file copied successfully")
        else:
            logger.error(f"Control file not found at {pgvector_control}")
            return False
        
        # Copy SQL files to extension directory
        logger.info(f"Copying SQL files to {pg_ext_dir}")
        latest_version_sql = None
        latest_version = "0.0.0"
        
        # Find the latest version SQL file
        for sql_file in os.listdir(pgvector_sql_dir):
            if sql_file.startswith("vector--") and sql_file.endswith(".sql") and not "--" in sql_file[8:]:
                version = sql_file[8:-4]
                if version > latest_version:
                    latest_version = version
                    latest_version_sql = sql_file
        
        if latest_version_sql:
            logger.info(f"Found latest version: {latest_version_sql}")
            
            # Copy the latest version SQL file
            src_path = os.path.join(pgvector_sql_dir, latest_version_sql)
            dst_path = os.path.join(pg_ext_dir, latest_version_sql)
            shutil.copy2(src_path, dst_path)
            logger.info(f"Copied {latest_version_sql}")
            
            # Copy all upgrade SQL files
            for sql_file in os.listdir(pgvector_sql_dir):
                if sql_file.startswith("vector--") and sql_file.endswith(".sql"):
                    src_path = os.path.join(pgvector_sql_dir, sql_file)
                    dst_path = os.path.join(pg_ext_dir, sql_file)
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"Copied {sql_file}")
        else:
            logger.error("No version SQL files found")
            return False
        
        # Try to create the extension in the database
        logger.info("Creating pgvector extension in database")
        try:
            conn = psycopg2.connect(
                user=db_user,
                password=db_password,
                host="localhost",
                database=db_name
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            logger.info("pgvector extension created successfully in database")
            
            # Test the extension
            cursor.execute("SELECT '[1,2,3]'::vector")
            result = cursor.fetchone()
            if result:
                logger.info("pgvector extension is working correctly!")
            
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error creating extension in database: {e}")
            logger.error("Installation was completed, but you may need to restart PostgreSQL")
            return False
        
        logger.info("\npgvector extension installed successfully!")
        logger.info("You might need to restart the PostgreSQL server for the changes to take effect.")
        
    except Exception as e:
        logger.error(f"Error installing pgvector: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)