## Upload taxi_zone (locations) csv to MinIO manually
- upload https://raw.githubusercontent.com/erkansirin78/datasets/00583d127f0cc780bc85c9a033d9e895b10bc4a3/nyc_taxi_yellow_trip_raw/taxi_zone_lookup.csv bronze bucket

#### Run spark docker container
```commandline
docker run --rm --name spark -p 8888:8888 -p 4040:4040 veribilimiokulu/pyspark:3.5.3_python-3.12_java17 sleep infinity
```

#### Run Jupyter lab
```commandline
docker exec -it spark jupyter lab --ip 0.0.0.0 --port 8888 --allow-root
```
- Use load_dims_development.ipynb for exploring data, understanding data models and initial development.

![](data_model_drawio.png)

---

- Tables to create
```commandline
FactTrip


TripID
PickupDateTimeID
DropOffDateTimeID
PULocationID
DOLocationID
RateCodeID
PaymentTypeID
PassengerCount
TripDistance
FareAmount
TipAmount
TollsAmount
AirportAmount
TotalAmount
Extra
MTATax
CongestionSurcharge
```
## Spark App for loading dimension tables
```commandline

```

## requirements.txt
- activate local virtualenv
```commandline
 source .venv_ingest/bin/activate
```
```commandline
pandas
python-dotenv
pyspark==3.5.3
```
- Install requirements to local environment
```commandline

```
## Dockerfile
```commandline
look from file
```

## Build image
```commandline
pwd 

<project_root_dir>/05_data_transformation/load_facts


docker build -t spark-load_facts:1.0 .
```
- tag image 
```commandline
docker tag  spark-load_facts:1.0 ghcr.io/akincismet/spark-load_facts:1.0
```

## load_facts_sparkApplication.yaml
```yaml
look from file itself
```

## Test on kubernetes cluster(dev cluster)
- start spark application (submit)
```bash
 kubectl apply -f load_facts_sparkApplication.yaml
```
- watch driver and executor pods
```commandline
 kubectl get pod -w
```
- watch driver logs (another terminal)
```commandline
 kubectl logs -f load-facts-driver
```

## Test
- To run the unit tests for the load_dimensions Spark application, use the following commands from the 05_data_transformation/load_dimensions directory:
```commandline
# Activate your virtual environment if not already active
 source ../../.venv_ingest/bin/activate

python -m pip install pyspark==3.5.3 pandas


# Run the tests with the correct PYTHONPATH
PYTHONPATH=. pytest src/tests/test_spark_load_facts.py -v
```
- expected output
```commandline
src/tests/test_unit_spark_load_dimensions.py::TestUnitTests::test_get_spark_session PASSED                                                                                                      [ 12%]
src/tests/test_unit_spark_load_dimensions.py::TestUnitTests::test_get_spark_session_default_name PASSED                                                                                         [ 25%]
src/tests/test_unit_spark_load_dimensions.py::TestUnitTests::test_create_nessie_database PASSED                                                                                                 [ 37%]
src/tests/test_unit_spark_load_dimensions.py::TestUnitTests::test_create_nessie_database_default_name PASSED                                                                                    [ 50%]
src/tests/test_unit_spark_load_dimensions.py::TestDimPaymentUnit::test_write_dimpayment_data_structure PASSED                                                                                   [ 62%]
src/tests/test_unit_spark_load_dimensions.py::TestDimRateCodeUnit::test_write_dimratecode_data_structure PASSED                                                                                 [ 75%]
src/tests/test_unit_spark_load_dimensions.py::TestDimLocationUnit::test_write_dimlocation_csv_reading SKIPPED (Spark DataFrame write chain mocking issue - requires Iceberg dependencies fo...) [ 87%]
src/tests/test_unit_spark_load_dimensions.py::TestDimTimeUnit::test_write_dimtime_sql_generation PASSED                                                                                         [100%]

==================================================================================== 7 passed, 1 skipped in 14.31s ====================================================================================
```

## Airflow
- Create spark_on_k8s directory in airflow dags dir
- Copy load_facts_sparkApplication.yaml here

### Create Airflow dag python module
- in airflow/dags load_dimensions_dag.py

### Create role and rolebinding
- Airflow SparkKubernetesOperator should be able to create and manage SparkApplication resources via the Spark Operator.
```commandline
kubectl apply -f spark_role.yaml
kubectl apply -f spark_rolebinding.yaml
```