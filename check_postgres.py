#!/usr/bin/env python3
"""Check PostgreSQL installation and status"""

import subprocess
import os
import sys

def check_postgres_service():
    """Check if PostgreSQL is installed as a Windows service"""
    print("Checking PostgreSQL services...")
    
    try:
        # List all services with 'postgres' in the name
        result = subprocess.run(
            ["sc", "query", "state=", "all"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        postgres_services = []
        lines = result.stdout.split('\n')
        
        for i, line in enumerate(lines):
            if 'SERVICE_NAME:' in line and 'postgres' in line.lower():
                service_name = line.split('SERVICE_NAME:')[1].strip()
                postgres_services.append(service_name)
        
        if postgres_services:
            print(f"\nFound PostgreSQL services: {postgres_services}")
            
            # Check status of each service
            for service in postgres_services:
                result = subprocess.run(
                    ["sc", "query", service],
                    capture_output=True,
                    text=True
                )
                
                if "RUNNING" in result.stdout:
                    print(f"✓ {service} is RUNNING")
                else:
                    print(f"✗ {service} is NOT running")
                    print(f"  To start: net start {service}")
        else:
            print("No PostgreSQL services found!")
            print("\nPostgreSQL might not be installed or installed differently.")
            
    except Exception as e:
        print(f"Error checking services: {e}")

def check_postgres_executable():
    """Check if psql is available in PATH"""
    print("\nChecking PostgreSQL executable...")
    
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ PostgreSQL found: {result.stdout.strip()}")
        else:
            print("✗ psql not found in PATH")
            
    except FileNotFoundError:
        print("✗ psql executable not found in PATH")
        print("\nCommon PostgreSQL installation paths:")
        print("  C:\\Program Files\\PostgreSQL\\17\\bin")
        print("  C:\\Program Files\\PostgreSQL\\16\\bin")
        print("  C:\\Program Files\\PostgreSQL\\15\\bin")

def check_postgres_port():
    """Check if PostgreSQL port 5432 is listening"""
    print("\nChecking PostgreSQL port...")
    
    try:
        result = subprocess.run(
            ["netstat", "-an"],
            capture_output=True,
            text=True
        )
        
        if ":5432" in result.stdout and "LISTENING" in result.stdout:
            print("✓ Port 5432 is listening (PostgreSQL likely running)")
        else:
            print("✗ Port 5432 is not listening")
            
    except Exception as e:
        print(f"Error checking port: {e}")

def test_connection():
    """Try to connect to PostgreSQL"""
    print("\nTesting PostgreSQL connection...")
    
    try:
        import psycopg2
        
        # Try default connection
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            connect_timeout=3
        )
        conn.close()
        print("✓ Successfully connected to PostgreSQL!")
        
    except ImportError:
        print("✗ psycopg2 not installed - can't test connection")
        print("  Install with: pip install psycopg2-binary")
        
    except Exception as e:
        print(f"✗ Could not connect to PostgreSQL: {e}")
        print("\nPossible solutions:")
        print("1. Start PostgreSQL service")
        print("2. Check PostgreSQL is installed")
        print("3. Verify credentials (default: postgres/postgres)")

if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Status Check")
    print("=" * 60)
    
    check_postgres_service()
    check_postgres_executable()
    check_postgres_port()
    test_connection()
    
    print("\n" + "=" * 60)