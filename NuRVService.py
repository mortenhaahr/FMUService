from rabbitmq import Rabbitmq
import protocol
from pyhocon import ConfigFactory

def on_read(ch, method, properties, body):
    print(body)

def main():
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    config = ConfigFactory.parse_file("simulation.conf")["rabbitmq"]
    

    rabbit = Rabbitmq(**config)

    topic = "incubator.mock.hw.temperature.t1" # Could also be .*
    rabbit.connect_to_server()
    rabbit.subscribe(routing_key=topic, on_message_callback=on_read)
    rabbit.start_consuming()

if __name__ == "__main__":
    main()