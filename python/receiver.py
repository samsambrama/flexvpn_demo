from typing import Iterable
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

import random
import time

def get_router_uptime(_: CallbackOptions) -> Iterable[Observation]:
    yield Observation(random.randint(0, 100000), {
            "customerid": "90000001",
            "ipaddress": "10.252.32.1",
            "hostname": "r1111-0001",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(0, 100000), {
            "customerid": "90000001",
            "ipaddress": "10.252.32.2",
            "hostname": "r1111-0002",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(0, 100000), {
            "customerid": "90000002",
            "ipaddress": "10.252.32.3",
            "hostname": "r1111-0003",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(0, 100000), {
            "customerid": "90000003",
            "ipaddress": "10.252.32.4",
            "hostname": "r1111-0004",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })

def get_router_pingtime(_: CallbackOptions) -> Iterable[Observation]:
    yield Observation(random.randint(30, 105), {
            "customerid": "90000001",
            "ipaddress": "10.252.32.1",
            "hostname": "r1111-0001",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(30, 105), {
            "customerid": "90000001",
            "ipaddress": "10.252.32.2",
            "hostname": "r1111-0002",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(30, 105), {
            "customerid": "90000002",
            "ipaddress": "10.252.32.3",
            "hostname": "r1111-0003",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(30, 105), {
            "customerid": "90000003",
            "ipaddress": "10.252.32.4",
            "hostname": "r1111-0004",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })

def get_router_devicememory(_: CallbackOptions) -> Iterable[Observation]:
    yield Observation(random.randint(1000, 10000), {
            "customerid": "90000001",
            "ipaddress": "10.252.32.1",
            "hostname": "r1111-0001",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(1000, 10000), {
            "customerid": "90000001",
            "ipaddress": "10.252.32.2",
            "hostname": "r1111-0002",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(1000, 10000), {
            "customerid": "90000002",
            "ipaddress": "10.252.32.3",
            "hostname": "r1111-0003",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
    yield Observation(random.randint(1000, 10000), {
            "customerid": "90000003",
            "ipaddress": "10.252.32.4",
            "hostname": "r1111-0004",
            "version": "16.0.03b",
            "image": "cisco ios 16.0.03b",
            "serialnumber": "85e5cca8-a9eb-4345-8068-d9fedc7393b0",
            "devicemodel": "C1111-4P"
        })
        
def main():
    resource = Resource(attributes={
        SERVICE_NAME: "router-monitoring"
    })


    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint="http://otelcollector:4317", insecure=True),
        export_interval_millis=1000
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])


    # Sets the global default meter provider
    metrics.set_meter_provider(provider)


    # Creates a meter from the global meter provider
    meter = metrics.get_meter("router.monitoring")

    meter.create_observable_gauge(
        "router.uptime",
        callbacks=[get_router_uptime],
        description="retrieve the router uptime",
        unit="1"
    )
    meter.create_observable_gauge(
        "router.pingtime",
        callbacks=[get_router_pingtime],
        description="retrieve the router pingtime",
        unit="1"
    )
    meter.create_observable_gauge(
        "router.devicememory",
        callbacks=[get_router_devicememory],
        description="retrieve the router devicememory",
        unit="1"
    )

    try:
        while True:
            # Update the metric instruments using the direct calling convention
            time.sleep(1)


    except KeyboardInterrupt:
        print("shutdown")


if __name__ == "__main__":
    main()
