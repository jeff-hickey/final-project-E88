### Step 1 - Run Kafka and Flink from the Docker compose image.

Open permissions for the directory and run the docker container
- $ sudo chmod -R 777 flink-data
- $ docker-compose-v1 up -d

Check services are running:
- docker ps --format "{{.ID}} {{.Names}} {{.State}} {{.Ports}} {{.Status}}"

### Step 2 - Create input and output Kafka topics

- $ docker exec broker1 kafka-topics --create --topic sentiment_input --bootstrap-server localhost:9092
- $ docker exec broker1 kafka-topics --create --topic sentiment_output --bootstrap-server localhost:9092
- $ docker exec -it broker1 /bin/kafka-console-producer.sh --bootstrap-server broker1:29092 --topic sentiment_input

### Step 3 - Validate the kafka topics are working correctly

- $ docker exec -it jobmanager bash
- $ docker exec broker1 kafka-console-producer --topic sentiment_input --bootstrap-server localhost:9092

### Step 4 - Start up the Flink stream processor.
- Install nltk (https://www.nltk.org/install.html)
   $ pip install --user -U nltk 
- Test the instal by running $ python then type $ import nltk 
- If you get an error related to sqlite, copy this file:
   $ cp /flink-data/panlex_lite.py ~/.local/lib/python3.7/site-packages/nltk/corpus/reader/ 
- Start the flink processor:
   $ docker exec -it jobmanager bash $ cd /flink-data $ python flink_processor.py

### Step 5 - Run the Kafka Consumer

- $ python3.9 sentiment_consumer.py

### Step 6 - Start the website

- $ cd /final-project-E88/ $ flask --app application run

### Step 7 - Connect to the Twitter Stream.

- $ python3.9 twitter_producer.py

### Step 4 - Submit the Kafka twitter producer from the flink_data directory

- $ docker exec -it jobmanager bash $ ./bin/flink run --detached -py /flink-data/twitter.py