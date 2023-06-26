from unittest import TestCase, mock
import unittest
# from unittest.mock import ANY, Mock
#
# import pyspark
# from pyspark.sql import SparkSession
#
# from source.main.ingest import Ingest
#
#
# class TestIngest(TestCase):
#     @mock.patch('pyspark.sql.SparkSession', spec=pyspark.sql.SparkSession)
#     def test_schema_validation(self, spark):
#         mock_query = mock.Mock()
#         mock_query.json.return_value = spark.createDataFrame(data=[], schema=[])
#         # spark().read.json(ANY).side_effect = Exception('Test')
#         # ingest_process = Ingest(spark)
#         # ingest_process.schema_validation()
#         with self.assertRaises(Exception):
#             mock_query.json("")

import datetime
from unittest.mock import Mock

# Save a couple of test days
tuesday = datetime.datetime(year=2019, month=1, day=1)
saturday = datetime.datetime(year=2019, month=1, day=5)

# Mock datetime to control today's date
datetime = Mock()

def is_weekday():
    today = datetime.datetime.today()
    # Python's datetime library treats Monday as 0 and Sunday as 6
    return (0 <= today.weekday() < 5)

# Mock .today() to return Tuesday
datetime.datetime.today.return_value = tuesday
# Test Tuesday is a weekday
assert is_weekday()
# Mock .today() to return Saturday
datetime.datetime.today.return_value = saturday
# Test Saturday is not a weekday
assert not is_weekday()
#
# if __name__ == '__main__':
#     unittest.main()
