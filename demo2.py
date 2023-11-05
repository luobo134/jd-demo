import os
import re
import pandas as pd
import sqlite3

# 指定目录路径和配置文件路径
directory = 'C:\Users\Administrator\Downloads\item'  # 指定目录路径
column_mapping_file = 'column_mapping.propties'  # 配置文件名

# 正则表达式模式，用于匹配 store_code 是否满足 "JD_数字" 的格式
store_code_pattern = r'^JD_\d+$'


def process_csv(file_path):
    # 读取配置文件中的列映射关系
    column_mapping = {}
    with open(column_mapping_file, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            column_mapping[key] = value

    # 读取csv文件内容
    df = pd.read_csv(file_path)

    # 校验 store_code：检查是否满足 "JD_数字" 的格式
    file_name = os.path.basename(file_path)
    store_code = re.findall(r'JD_(\d+)', file_name)
    if not store_code or not re.match(store_code_pattern, store_code[0]):
        raise ValueError(f"Invalid store code in file name: {file_name}")

    # 校验列是否存在，并打印缺少的列名
    missing_columns = set(column_mapping.keys()) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in CSV file: {', '.join(missing_columns)}")

    # 将每一行转换为insert语句，并插入数据库
    conn = sqlite3.connect('database.db')  # 连接数据库
    cursor = conn.cursor()

    for _, row in df.iterrows():
        insert_values = []
        for col_name, db_col_name in column_mapping.items():
            if col_name == 'store_code':
                insert_values.append(store_code[0])  # 将 store_code 加入插入值中
            else:
                insert_values.append(str(row[col_name]))

        values_str = ', '.join(insert_values)
        query = f"INSERT INTO items ({', '.join(column_mapping.values())}) VALUES ({values_str})"
        cursor.execute(query)

    conn.commit()
    conn.close()

    # 处理成功的csv文件重命名
    new_file_path = os.path.splitext(file_path)[0] + '.COMPLETED'
    os.rename(file_path, new_file_path)


def process_directory(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            file_path = os.path.join(directory, file_name)

            try:
                process_csv(file_path)
                print(f"Processed CSV file: {file_name}")
            except Exception as e:
                new_file_path = os.path.join(directory, file_name.split('.')[0] + '.FAILED')
                os.rename(file_path, new_file_path)
                print(f"Failed to process CSV file: {file_name}. Error: {str(e)}")


# 主程序入口
if __name__ == '__main__':
    process_directory(directory)