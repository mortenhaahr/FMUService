from rabbitmq import Rabbitmq
from pyhocon import ConfigFactory
from fmuinterface import FMUInterface
import logging

f = FMUInterface(fileName="m2.fmu", startTime=0)

x2 = 100


def on_read(ch, method, properties, body):
    global x2
    val = int(body)
    inputs = {"Integer": {"x1": val, "x2": x2}}
    f.setInputs(inputs)
    f.callback_doStep(0, 1)
    print(f"Inputs: {inputs}. Outputs: {f.getValues()}")
    x2 += 10


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
