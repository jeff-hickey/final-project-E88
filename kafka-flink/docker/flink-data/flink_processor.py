from datetime import datetime
from json import dumps

from nltk.sentiment import SentimentIntensityAnalyzer
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, DataTypes
from pyflink.table.udf import udf

# Converting between datastream and table api in pyflink
# https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/data_stream_api/

"""
A User Defined Function (UDF) used to calculate the sentiment of a tweet. This function is applied in the 
processing pipeline on the incoming data stream.
"""


@udf(input_types=[DataTypes.STRING()], result_type=DataTypes.STRING())
def summary(tweet):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(tweet)
    sentiment['created_on'] = datetime.now()
    print(sentiment)
    return dumps(sentiment, indent=4, sort_keys=True, default=str)


def main():
    # Create the streaming environment
    env = StreamExecutionEnvironment.get_execution_environment()

    settings = EnvironmentSettings.new_instance() \
        .in_streaming_mode() \
        .use_blink_planner() \
        .build()

    # create table environment
    tbl_env = StreamTableEnvironment.create(stream_execution_environment=env,
                                            environment_settings=settings)
    tbl_env.register_function('summary', summary)
    # add kafka connector dependency
    kafka_jar = "file:///opt/flink/lib/flink-connector-kafka_2.12-1.14.0.jar"

    tbl_env.get_config() \
        .get_configuration() \
        .set_string("pipeline.jars", kafka_jar)

    #######################################################################
    # Create Kafka Source Table with DDL
    #######################################################################

    src_ddl = """
        CREATE TABLE logs (
            tweet VARCHAR,
            proctime AS PROCTIME()
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'sentiment_input',
            'properties.bootstrap.servers' = 'broker1:29092',
            'properties.group.id' = 'logs',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    """

    tbl_env.execute_sql(src_ddl)

    # create and initiate loading of source Table
    tbl = tbl_env.from_path('logs')

    print('\nSource Schema')
    tbl.print_schema()

    #####################################################################
    # Define Tumbling Window Aggregate Calculation (Seller Sales Per Minute)
    #####################################################################

    sql = """
        SELECT
          summary(tweet),
          TUMBLE_END(proctime, INTERVAL '5' SECONDS) AS window_end,
          count(*) as cnt
        FROM logs
        GROUP BY
          TUMBLE(proctime, INTERVAL '5' SECONDS),
          tweet
    """
    logs_tbl = tbl_env.sql_query(sql)

    print('\nProcess Sink Schema')
    logs_tbl.print_schema()

    ###############################################################
    # Create Kafka Sink Table
    ###############################################################
    sink_ddl = """
        CREATE TABLE logs_uaos (
            tweet VARCHAR,
            window_end TIMESTAMP(3),
            cnt BIGINT
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'sentiment_output',
            'properties.bootstrap.servers' = 'broker1:29092',
            'format' = 'json'
        )
    """
    tbl_env.execute_sql(sink_ddl)

    # write time windowed aggregations to sink table
    logs_tbl.execute_insert('logs_uaos').wait()

    tbl_env.execute('windowed-logs')


if __name__ == '__main__':
    main()
