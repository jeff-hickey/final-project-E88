from json import dumps

from nltk.sentiment import SentimentIntensityAnalyzer
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, DataTypes
from pyflink.table.udf import udf

# Converting between datastream and table api in pyflink
# https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/data_stream_api/


@udf(input_types=[DataTypes.STRING()], result_type=DataTypes.STRING())
def summary(tweet):
    """
    A User Defined Function (UDF) used to calculate the sentiment of a tweet. This function is applied in the
    processing pipeline on the incoming tweete and produces a positive, negative, neutral and compound score.
    """
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(tweet)
    print('flink_processor: ', sentiment)
    return dumps(sentiment, indent=4, sort_keys=True, default=str)


def main():
    """
    This code is adapted from the week 9 lab. Using the PyFlink DataStream and Table APIs, the incoming message is
    received into the src_ddl table, an sql query is used to pull data from that table and perform sentiment
    analysis with a user defined function (UDF) called summary(). A sink table (sink_ddl) is created to receive the
    results of this sql query and process the data to the sentiment_output kafka queue.
    """
    # Create the streaming environment
    env = StreamExecutionEnvironment.get_execution_environment()

    settings = EnvironmentSettings.new_instance() \
        .in_streaming_mode() \
        .use_blink_planner() \
        .build()

    # Create table environment
    tbl_env = StreamTableEnvironment.create(stream_execution_environment=env,
                                            environment_settings=settings)
    tbl_env.register_function('summary', summary)
    # add kafka connector dependency
    kafka_jar = "file:///opt/flink/lib/flink-connector-kafka_2.12-1.14.0.jar"

    tbl_env.get_config() \
        .get_configuration() \
        .set_string("pipeline.jars", kafka_jar)


    # Create Kafka Source Table.
    src_ddl = """
        CREATE TABLE tweets (
            tweet VARCHAR
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

    # Create and initiate loading of source Table
    tbl = tbl_env.from_path('tweets')

    print('\nSource Schema')
    tbl.print_schema()

    # Sentiment Analysis.
    sql = """
        SELECT
          summary(tweet)
        FROM tweets
    """
    tweets_tbl = tbl_env.sql_query(sql)

    print('\nProcess Sink Schema')
    tweets_tbl.print_schema()

    ###############################################################
    # Create Kafka Sink Table
    ###############################################################
    sink_ddl = """
        CREATE TABLE sentiment (
            tweet VARCHAR
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'sentiment_output',
            'properties.bootstrap.servers' = 'broker1:29092',
            'format' = 'json'
        )
    """
    tbl_env.execute_sql(sink_ddl)

    # write time windowed aggregations to sink table
    tweets_tbl.execute_insert('sentiment').wait()
    tbl_env.execute('windowed-sentiment')


if __name__ == '__main__':
    main()
