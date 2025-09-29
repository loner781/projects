import sqlite3
import os

def view_database():
    """View all data in the bus attendance database"""
    
    # Database path
    db_path = "bus.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file 'bus.db' not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        print("🗄️  BUS ATTENDANCE DATABASE VIEWER")
        print("=" * 50)
        
        # Get table names
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        
        if not tables:
            print("❌ No tables found in database!")
            return
        
        print(f"📋 Found {len(tables)} table(s): {[table[0] for table in tables]}")
        print()
        
        # View each table
        for table in tables:
            table_name = table[0]
            print(f"📊 TABLE: {table_name.upper()}")
            print("-" * 30)
            
            # Get table structure
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"Columns: {', '.join(column_names)}")
            
            # Get all data
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            
            if rows:
                print(f"Rows: {len(rows)}")
                print()
                
                # Print header
                print(" | ".join(f"{col:15}" for col in column_names))
                print("-" * (len(column_names) * 18))
                
                # Print data (limit to 20 rows for readability)
                for i, row in enumerate(rows[:20]):
                    print(" | ".join(f"{str(cell):15}" for cell in row))
                
                if len(rows) > 20:
                    print(f"... and {len(rows) - 20} more rows")
            else:
                print("No data found")
            
            print()
            print("=" * 50)
            print()
        
        conn.close()
        print("✅ Database view completed!")
        
    except Exception as e:
        print(f"❌ Error viewing database: {e}")

if __name__ == "__main__":
    view_database()

