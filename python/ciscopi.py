import time
import requests
from requests.exceptions import RequestException
from typing import Iterable
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import urllib3
import re
 
# Disable warnings from urllib3
urllib3.disable_warnings()
 
# Define Cisco PI credentials
username = "SDO-API-User"
password = "!kPghislklj5"
base_url = "https://10.68.228.175/webacs/api/v4/"
 
# Define the endpoint to fetch the list of devices
devices_endpoint = "data/Devices.json"
 
# Define a list of endpoints for CPU and memory utilization
endpoints = [
    "op/statisticsService/device/cpuUtilTrend.json",
    "op/statisticsService/device/memoryUtilTrend.json"
]
 
def fetch_devices():
    try:
        url = base_url + devices_endpoint
        response = requests.get(url, auth=(username, password), verify=False)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        data = response.json()
        device_ids = [entity["@url"].split("/")[-1] for entity in data.get("queryResponse", {}).get("entityId", [])]
        return device_ids
    except RequestException as e:
        print(f"Failed to fetch list of devices: {e}")
        return []
 
def fetch_device_information(device_id):
    try:
        device_url = f"{base_url}data/Devices/{device_id}.json"
        response = requests.get(device_url, auth=(username, password), verify=False)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        device_data = response.json().get("queryResponse", {}).get("entity", [])[0].get("devicesDTO", {})
        device_ip = device_data.get("ipAddress")
        device_info = {
            "device_id": device_id,
            "collection_status": device_data.get("collectionStatus"),
            "collection_time": device_data.get("collectionTime"),
            "serial_number": device_data.get("manufacturerPartNrs", {}).get("manufacturerPartNr", [{}])[0].get("serialNumber"),
            "part_number": device_data.get("manufacturerPartNrs", {}).get("manufacturerPartNr", [{}])[0].get("partNumber"),
            "ip_address": device_ip,
            "software_version": device_data.get("softwareVersion"),
            "device_name": device_data.get("deviceName"),  # Add deviceName field
            "location": device_data.get("location"),
            "reachability": device_data.get("reachability")
        }
        return device_info
    except RequestException as e:
        print(f"Failed to fetch device information from {device_url}: {e}")
        return None
 
def fetch_utilization(device_ip):
    utilization_data = {}
    try:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}?ipAddress={device_ip}&range=1"
            print(f"Fetching utilization data from {url}")
            response = requests.get(url, auth=(username, password), verify=False)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            data = response.json()
            if data and 'mgmtResponse' in data:
                statistic_entry = data.get("mgmtResponse", {}).get("statisticsDTO", [])
                if statistic_entry:
                    entry_value = statistic_entry[0].get("childStatistics", {}).get("childStatistic", [])[0].get("statisticEntries", {}).get("statisticEntry", [])[0].get("entryValue")
                    utilization_data[endpoint.split('/')[-1].split('.')[0]] = entry_value
                else:
                    print(f"No data returned for {endpoint} endpoint.")
            else:
                print(f"No valid response received for {endpoint} endpoint.")
        print(f"Utilization data fetched: {utilization_data}")
        return utilization_data
    except RequestException as e:
        print(f"Failed to fetch utilization data for device with IP {device_ip}: {e}")
        return {}
        
def fetch_uptime(device_id):
    try:
        uptime_url = f"{base_url}data/InventoryDetails/{device_id}.json"
        response = requests.get(uptime_url, auth=(username, password), verify=False)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        uptime_data = response.json().get("queryResponse", {}).get("entity", [])[0].get("inventoryDetailsDTO", {}).get("summary", {}).get("upTime")
        if uptime_data:
            return int(uptime_data)  # Remove the multiplication by 1000
        else:
            return None
    except RequestException as e:
        print(f"Failed to fetch uptime for device {device_id}: {e}")
        return None
 
def format_uptime(uptime):
    seconds = uptime // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"
    
def main():
    # Fetch and print device details
    devices = fetch_devices()
    all_device_ids = set(devices)  # Track all device IDs
 
    # Initialize OpenTelemetry
    resource = Resource(attributes={
        SERVICE_NAME: "router-monitoring"
    })
 
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint="http://otelcollector:4317", insecure=True),
        export_interval_millis=5000
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])
 
    # Sets the global default meter provider
    metrics.set_meter_provider(provider)
 
    # Get the meter outside the loop
    meter = metrics.get_meter(__name__)
 
    # Create metrics outside the loop
    memory_utilization_metric = meter.create_gauge(
        name="router_memory_utilization",
        description="Memory Utilization of routers",
        unit="percent"
    )
 
    cpu_utilization_metric = meter.create_gauge(
        name="router_cpu_utilization",
        description="CPU Utilization of routers",
        unit="percent"
    )
 
    uptime_metric = meter.create_gauge(
        name="router_uptime",
        description="Uptime of routers",
        unit="milliseconds",
    )
 
    reachability_metric = meter.create_gauge(
        name="router_reachability",
        description="Reachability of routers",
        unit="binary",
    )
 
    try:
        while True:
            for device_id in all_device_ids:  # Iterate over all device IDs
                device_info = fetch_device_information(device_id)
                if device_info:
                    device_ip = device_info["ip_address"]
                    # Fetch utilization data
                    utilization_data = fetch_utilization(device_ip)
                    if utilization_data:
                        memory_utilization_str = utilization_data.get('memoryUtilTrend', 'CDBNODATA')
                        cpu_utilization_str = utilization_data.get('cpuUtilTrend', 'CDBNODATA')
 
                        # Extract numeric value from memory utilization string
                        memory_utilization_match = re.search(r'\b(\d+)\b', memory_utilization_str)
                        memory_utilization = int(memory_utilization_match.group(1)) if memory_utilization_match else 0  # Set to 0 if no data
 
                        # Extract numeric value from CPU utilization string
                        cpu_utilization_str = cpu_utilization_str.split(':')[-1]
                        cpu_utilization = int(cpu_utilization_str) if cpu_utilization_str.isdigit() else 0  # Set to 0 if no data
 
                        # Get uptime data
                        uptime = fetch_uptime(device_id)
                        formatted_uptime = format_uptime(uptime)
 
                        # Add device details as labels
                        labels = {
                            "device_id": device_info["device_id"],
                            "device_name": device_info["device_name"],  # Added device name here
                            "part_number": device_info["part_number"],
                            "location": device_info["location"],
                            "reachability": device_info["reachability"],
                            "serial_number": device_info["serial_number"],
                            "ip_address": device_info["ip_address"],
                            "software_version": device_info["software_version"]
                        }
 
                        # Update metric values
                        memory_utilization_metric.set(memory_utilization, labels)
                        cpu_utilization_metric.set(cpu_utilization, labels)
                        uptime_metric.set(uptime, labels)
                        reachability_metric.set(1, labels)  # Set reachability to 1 for reachable devices
                        
                        # Print formatted uptime
                        print(f"Uptime for device {device_id}: {formatted_uptime}")
 
                    else:
                        # If no utilization data is available, set metrics to 0
                        reachability_metric.set(0, labels)  # Set reachability to 0 for unreachable devices
                else:
                    print(f"Failed to fetch device information for device ID: {device_id}")
 
            time.sleep(60)  # Adjust sleep time
 
    except KeyboardInterrupt:
        print("shutdown")
 
 
if __name__ == "__main__":
    main()