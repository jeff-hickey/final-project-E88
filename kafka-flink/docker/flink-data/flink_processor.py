from datetime import datetime

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from nltk.sentiment import SentimentIntensityAnalyzer


def summary(tweet):
    # sia = SentimentIntensityAnalyzer()
    # sentiment = sia.polarity_scores(tweet)
    # sentiment['created_on'] = datetime.now()
    # return sentiment
    pass


def main():
    # Create streaming environment
    env = StreamExecutionEnvironment.get_execution_environment()

    settings = EnvironmentSettings.new_instance() \
        .in_streaming_mode() \
        .use_blink_planner() \
        .build()

    # create table environment
    tbl_env = StreamTableEnvironment.create(stream_execution_environment=env,
                                            environment_settings=settings)

    # add kafka connector dependency
    # kafka_jar = os.path.join(os.path.abspath(os.path.dirname(__file__)),
    #                         'flink-sql-connector-kafka_2.11-1.13.0.jar')
    kafka_jar = "file:///opt/flink/lib/flink-connector-kafka_2.12-1.14.0.jar"

    tbl_env.get_config() \
        .get_configuration() \
        .set_string("pipeline.jars", kafka_jar)
    # .set_string("pipeline.jars", "file://{}".format(kafka_jar))

    #######################################################################
    # Create Kafka Source Table with DDL
    #######################################################################

    src_ddl = """
        CREATE TABLE sentiment (
            tweet VARCHAR,
            tweet_id VARCHAR,
            lang VARCHAR,
            proctime AS PROCTIME()
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'sentiment_input',
            'properties.bootstrap.servers' = 'broker1:29092',
            'properties.group.id' = 'sentiment',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    """

    tbl_env.execute_sql(src_ddl)

    # create and initiate loading of source Table
    tbl = tbl_env.from_path('sentiment')

    print('\nSource Schema')
    tbl.print_schema()

    #####################################################################
    # Define Tumbling Window Aggregate Calculation
    #####################################################################
    #   SUM(1) * 0.85 AS cnt
    #   count(*) as cnt

    sql = """
        SELECT
          tweet, tweet_id, lang,
          TUMBLE_END(proctime, INTERVAL '5' SECONDS) AS window_end
        FROM sentiment
        GROUP BY
          TUMBLE(proctime, INTERVAL '5' SECONDS),
          tweet, tweet_id, lang
    """
    sentiment_tbl = tbl_env.sql_query(sql)

    print('\nProcess Sink Schema')
    sentiment_tbl.print_schema()

    ###############################################################
    # Create Kafka Sink Table
    ###############################################################
    sink_ddl = """
        CREATE TABLE sentiment_summary (
            tweet VARCHAR,
            tweet_id VARCHAR,
            lang VARCHAR,
            window_end TIMESTAMP(3)
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'sentiment_output',
            'properties.bootstrap.servers' = 'broker1:29092',
            'format' = 'json'
        )
    """
    tbl_env.execute_sql(sink_ddl)

    # write time windowed aggregations to sink table
    print(sentiment_tbl)
    sentiment_tbl.execute_insert('sentiment_summary').wait()

    tbl_env.execute('windowed-sentiment')


if __name__ == '__main__':
    main()
