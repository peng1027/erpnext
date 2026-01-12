#!/usr/bin/env python3
"""
檢查數據庫表結構
"""

import sqlite3
from pathlib import Path

def check_table_schema(db_path):
    """檢查數據庫表結構"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 獲取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("數據庫表結構檢查")
    print("="*50)
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 表: {table_name}")
        print("-" * 30)
        
        # 獲取表結構
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            cid, name, type_, notnull, default, pk = col
            nullable = "NOT NULL" if notnull else "NULL"
            primary = "PRIMARY KEY" if pk else ""
            default_val = f"DEFAULT {default}" if default else ""
            
            print(f"  {name:<25} {type_:<15} {nullable:<10} {primary:<15} {default_val}")
    
    conn.close()

def main():
    db_path = Path(__file__).parent / "test_construction_inspection.db"
    
    if not db_path.exists():
        print(f"❌ 數據庫文件不存在: {db_path}")
        return
    
    check_table_schema(db_path)

if __name__ == "__main__":
    main()