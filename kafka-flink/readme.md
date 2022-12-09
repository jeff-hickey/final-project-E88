# Step 1 - Run Kafka and Flink from the Docker compose image. 
### Open permissions for the directory and run the docker container
- $ sudo chmod -R 777 flink-data
- $ docker-compose-v1 up -d

Check services are running:
docker ps --format "{{.ID}} {{.Names}} {{.State}} {{.Ports}} {{.Status}}"

# Step 2 - Create input and output Kafka topics
- $ docker exec broker1 kafka-topics --create --topic sentiment_input --bootstrap-server localhost:9092
- $ docker exec broker1 kafka-topics --create --topic sentiment_output  --bootstrap-server localhost:9092
- $ docker exec  -it broker1 /bin/kafka-console-producer.sh --bootstrap-server broker1:29092 --topic sentiment_input
# Step 3 - Validate the kafka topics are working correctly
- $ docker exec -it jobmanager bash
- $ docker exec broker1 kafka-console-producer --topic sentiment_input --bootstrap-server localhost:9092

## Start up the environment
1. Start the flink processor:
$ docker exec -it jobmanager bash
$ cd /flink-data
$ python flink_processor.py
$ You may need to install this componenet for nltk to run
pip install db-sqlite3

3. Start the kafka consumer
$ python3.9 sentiment_consumer.py

4. Send messages into the system
$ python3.9 twitter_producer.py



### Listen for messages.
$ docker exec broker1 kafka-console-consumer --topic p2_output --bootstrap-server localhost:9092

# Step 4 - Submit the Kafka twitter producer from the flink_data directory
$ docker exec -it jobmanager bash
$ ./bin/flink run --detached -py /flink-data/twitter.py