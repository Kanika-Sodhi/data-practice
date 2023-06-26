import os
import isodate
import shutil
from pyspark.sql.functions import col, to_timestamp, to_date
from pyspark.sql.types import IntegerType, LongType, StringType


def get_minutes(str_time):
    if str_time == '':
        str_time = str_time.replace('', 'PT')
    # parsing pt format type time with the help of iso date
    minutes = round((isodate.parse_duration(str_time).total_seconds()) / 60)
    return minutes


def is_not_empty(path):
    # Checking if the directory is empty or not
    if os.listdir(path):
        return True
    else:
        return False


def move_file_other_folder(source_dir, target_dir):
    # listing directory file
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        # move file from source to destination area
        shutil.move(os.path.join(source_dir, file_name), target_dir)


# df is source dataframe and dftype is dataype info dataframe
def cast_columns(df, dftype, table):
    dftype = dftype.where(dftype.tablename == table).collect()
    for row in dftype:
        if row["dtype"] == 'int':
            df = df.withColumn(row["fields"], col(row["fields"]).cast(IntegerType()))
        if 'bigint' in row["dtype"]:
            df = df.withColumn(row["fields"], col(row["fields"]).cast(LongType()))
        if 'varchar' in row["dtype"] or 'longtext' in row["dtype"] or 'nvarchar' in row["dtype"] or \
                'string' in row["dtype"]:
            df = df.withColumn(row["fields"], col(row["fields"]).cast(StringType()))
        if row["dtype"] == 'datetime':
            df = df.withColumn(row["fields"], to_timestamp(row["fields"], "dd-MM-yyyy HH:mm"))
        if row["dtype"] == 'date':
            df = df.withColumn(row["fields"], to_date(row["fields"], "yyyy-MM-dd"))
    return df


def create_column_list(df):
    col_list = []
    # creating column list
    for i in df.columns:
        col_list.append(i)
    return col_list


def write_csv(path, df):
    # Write CSV file with column header (column names)
    df.write.csv(path)
