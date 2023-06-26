# dir for template schema
template_path = '../../template/'
# dir for transformed data schema
transformed_path = '../../transformed_data/'
# todo
recipe_DQnotnull = ".where((json_data.cookTime.isNotNull()) & \
                           (json_data.prepTime.isNotNull()) &\
                           (json_data.ingredients.isNotNull()) &\
                        (json_data.datePublished.isNotNull()))"
# filtering ingredient
filter_ingredient = 'beef'
# ingeste file path
ingest_write_path = "../../data/injest_data/injest"
# test ngeste file path
test_ingest_write_path = "../../data/test_injest_data/"
# reading ingested data
ingest_read_path = "../../data/injest_data/injest/*.parquet"
# reading test ingested data
test_ingest_read_path = '../../data/test_ingest_data/*.parquet'
# directory path
recipes_folder = "../../data/input/"
# raw data path
recipes_raw_data = "*.json"
# ['../../data/input/recipes-000.json', '../../data/input/recipes-001.json','../../data/input/recipes-002.json']

# file name of recipe schema
recipe_temp_file_name = 'recipe_table_template.csv'
recipe_schema = 'recipeschema.csv'
# load data into target area
persist_path = '../../persist'
# load incremental data
incremental_path = '../../transformed_data/incremental_data/'
# name of table
tablename = 'recipes'

###########################################################
'''select_params.txt:
select transformed_with_dq.ingredients,
       transformed_with_dq.description,
       transformed_with_dq.image,
       transformed_with_dq.cookTime_mins,
       transformed_with_dq.prepTime_mins
with open('select_params.txt', 'r') as file:
    select_statement = file.read().replace('\n', '')
transformed_with_dq_new = transformed_with_dq.selectExpr(select_statement)'''
