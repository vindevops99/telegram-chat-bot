# db.py - Database Management Module
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
import logging
from config import Config

logger = logging.getLogger(__name__)

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager để quản lý database connection an toàn
    
    Sử dụng:
        with get_db() as conn:
            c = conn.cursor()
            c.execute(...)
    """
    conn = sqlite3.connect(Config.DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise e
    finally:
        conn.close()

def init_db():
    """Khởi tạo database với các bảng cần thiết"""
    with get_db() as conn:
        c = conn.cursor()
        
        # Bảng sales (doanh thu)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                amount INTEGER NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bảng expenses (chi phí)
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tạo index để tăng tốc query
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_created_at 
            ON sales(created_at)
        """)
        
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_expenses_created_at 
            ON expenses(created_at)
        """)
        
        logger.info("✅ Database initialized successfully")

def get_stats() -> Optional[Dict[str, Any]]:
    """Lấy thống kê tổng quan từ database"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            
            # Đếm số bản ghi
            c.execute("SELECT COUNT(*) FROM sales")
            total_sales = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM expenses")
            total_expenses = c.fetchone()[0]
            
            # Tổng tiền
            c.execute("SELECT COALESCE(SUM(amount), 0) FROM sales")
            sum_sales = c.fetchone()[0]
            
            c.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
            sum_expenses = c.fetchone()[0]
            
            return {
                "total_sales_count": total_sales,
                "total_expenses_count": total_expenses,
                "total_sales_amount": sum_sales,
                "total_expenses_amount": sum_expenses,
                "profit": sum_sales - sum_expenses
            }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return None

if __name__ == "__main__":
    # Test database
    logging.basicConfig(level=logging.INFO)
    init_db()
    stats = get_stats()
    if stats:
        print("\n📊 Database Statistics:")
        print(f"  Sales: {stats['total_sales_count']} bills, {stats['total_sales_amount']:,}đ")
        print(f"  Expenses: {stats['total_expenses_count']} items, {stats['total_expenses_amount']:,}đ")
        print(f"  Profit: {stats['profit']:,}đ")
