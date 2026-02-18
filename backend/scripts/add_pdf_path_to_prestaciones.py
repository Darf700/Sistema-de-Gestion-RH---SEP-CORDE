"""Agrega columna pdf_path a la tabla prestaciones."""
import sqlite3
import sys

DB_PATH = "./data/empleados.db"


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(prestaciones)")
    columns = [row[1] for row in cursor.fetchall()]

    if "pdf_path" in columns:
        print("La columna pdf_path ya existe en prestaciones. No se requiere migracion.")
        conn.close()
        return

    cursor.execute("ALTER TABLE prestaciones ADD COLUMN pdf_path TEXT")
    conn.commit()
    print("Columna pdf_path agregada exitosamente a prestaciones.")
    conn.close()


if __name__ == "__main__":
    migrate()
