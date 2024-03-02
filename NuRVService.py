from rabbitmq import Rabbitmq
from pyhocon import ConfigFactory
from fmuinterface import FMUInterface
import logging

f = FMUInterface(filename="m2.fmu", start_time=0)


def on_read(ch, method, properties, body):
    l = logging.getLogger("RabbitMQClass")
    val = int(body)
    f.callback_doStep([val, 26], 0, 1)
    print(f.getValues())


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    config = ConfigFactory.parse_file("simulation.conf")["rabbitmq"]

    rabbit = Rabbitmq(**config)

    topic = "incubator.mock.hw.temperature.t1"  # Could also be .*
    rabbit.connect_to_server()
    rabbit.subscribe(routing_key=topic, on_message_callback=on_read)
    rabbit.start_consuming()


if __name__ == "__main__":
    main()
