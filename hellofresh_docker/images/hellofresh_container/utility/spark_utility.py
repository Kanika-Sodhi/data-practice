# custom code which can be used by every class

def reading_json_file(spark, json_file):
    # reading raw json data
    read_json = spark.read.json(json_file)
    return read_json


def reading_csv_file(spark, file, header):
    # reading raw json data
    read_csv = spark.read.csv(file, header=header)
    return read_csv


def reading_parquet_file(spark, file):
    # read parquet data
    read_parquet = spark.read.parquet(file)
    return read_parquet


def write_csv_file(df, path):
    # write DataFrame into csv file
    write_df = df.write.format("csv").mode('overwrite').save(path)
