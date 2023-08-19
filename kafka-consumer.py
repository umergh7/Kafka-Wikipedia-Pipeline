from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import pymongo
import argparse
from pymongo import MongoClient
import json


def create_kafka_consumer(topic: str, bootstrap_server: str, offset: str):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[bootstrap_server],
            auto_offset_reset=offset,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    except NoBrokersAvailable as err:
        print(f'No broker found {err}')
        raise

    if consumer.bootstrap_connected():
        print('Kafka consumer connected!')
        return consumer
    else:
        print('Failed to establish connection!')
        exit(1)


def create_mongodb_connection(host: str, username: str, password: str):
    try:
        client = MongoClient(
            host,
            27017,
            username=username,
            password=password,
            serverSelectionTimeoutMS=5)
        
        x = client.server_info()  # force connection on a request
        print(x)
        db = client.wiki
        print("Connected successfully!")
        return db

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(f"Could not connect to MongoDB with following error {err}")


def parse_command_line_arguments():

    parser = argparse.ArgumentParser(
        description='Kafka Consumer Script Arguments')

    parser.add_argument('--bootstrap_server', default='localhost:9092',
                        help='Kafka bootstrap broker(s) (host[:port])', type=str)
    parser.add_argument('--topic_name', default='wikipedia-events',
                        help='Kafka topic name', type=str)
    parser.add_argument('--offset', default='earliest',
                        help='From where to start sonsuming messages', type=str)
    parser.add_argument('--mongodb_server', default='localhost',
                        help='MongoDB server', type=str)
    parser.add_argument('--mongodb_username', default='root',
                        help='MongoDB username to auth', type=str)
    parser.add_argument('--mongodb_password', default='password',
                        help='MongoDB password to auth', type=str)

    return parser.parse_args()


args = parse_command_line_arguments()

consumer = create_kafka_consumer(args.topic_name, args.bootstrap_server, args.offset)

connection = create_mongodb_connection(args.mongodb_server, args.mongodb_username, args.mongodb_password)

for msg in consumer:
    record = msg.value
    recored_sent = connection.coba_info.insert_one(record)
    print("The following data is inserted in MongoDB database", record)
