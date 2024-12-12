import os
import sqlite3
import pandas as pd

# 定义函数，将单个 Excel 文件导入 SQLite 数据库
def import_excel_to_sqlite(excel_file, table_name, conn):
    """
    导入单个 Excel 文件到 SQLite 数据库
    :param excel_file: Excel 文件路径
    :param table_name: SQLite 中的表名
    :param conn: SQLite 数据库连接对象
    """
    try:
        # 使用 pandas 读取 Excel 文件
        df = pd.read_excel(excel_file, engine="openpyxl")

        # 将数据写入 SQLite 数据库
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"导入成功: {excel_file} -> 表 {table_name}")
    except Exception as e:
        print(f"导入失败: {excel_file} -> 表 {table_name}, 错误: {e}")

# 主程序逻辑
def batch_import_xlsx_to_sqlite(folder_path, database_path):
    """
    批量导入文件夹中的 Excel 文件到 SQLite 数据库
    :param folder_path: 包含 Excel 文件的文件夹路径
    :param database_path: SQLite 数据库文件路径
    """
    # 连接 SQLite 数据库（如果不存在会创建新的数据库文件）
    conn = sqlite3.connect(database_path)

    # 遍历文件夹中的所有 .xlsx 文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".xlsx"):
            # 文件路径
            file_path = os.path.join(folder_path, file_name)

            # 使用文件名作为表名（去掉扩展名）
            table_name = os.path.splitext(file_name)[0].replace(" ", "").replace("(", "_").replace(")", "").replace("-", "_").replace("，", "_")

            # 导入 Excel 到 SQLite
            import_excel_to_sqlite(file_path, table_name, conn)

    # 关闭数据库连接
    conn.close()

# 使用示例
if __name__ == "__main__":
    # 定义 Excel 文件夹路径和 SQLite 数据库路径
    folder_path = "./data"  # 替换为你的文件夹路径
    database_path = "./data.db"  # 替换为你的数据库路径

    # 批量导入
    batch_import_xlsx_to_sqlite(folder_path, database_path)
