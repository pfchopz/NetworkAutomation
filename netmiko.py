import netmiko
import time
import threading
import queue

# Start time of program
startTimeGlobal = time.perf_counter()

# Global variables for multi threading
NUM_THREADS = 4
PRINT_LOCK = threading.Lock()

# Main function for executing code
def main():
    # Inventory of all device variables which differ between devices
    device_list = [
        {
            'deviceName': 'edge-rtr-01',
            'deviceType': 'cisco_ios',
            'devicePort': '1000'
        },
        {
            'deviceName': 'edge-rtr-02',
            'deviceType': 'cisco_ios',
            'devicePort': '1002'
        },
        {
            'deviceName': 'core-sw-01',
            'deviceType': 'cisco_ios',
            'devicePort': '1004'
        },
        {
            'deviceName': 'acc-sw-01',
            'deviceType': 'cisco_ios',
            'devicePort': '1008'
        },
        {
            'deviceName': 'acc-sw-02',
            'deviceType': 'cisco_ios',
            'devicePort': '1010'
        },
        {
            'deviceName': 'acc-sw-03',
            'deviceType': 'cisco_ios',
            'devicePort': '1012'
        },
        {
            'deviceName': 'core-fw-01',
            'deviceType': 'cisco_asa',
            'devicePort': '1014'
        }
    ]

    # Generate total thread count based on number of devices in device_list
    #global NUM_THREADS
    #NUM_THREADS = len(device_list)

    # Create queue for job list
    device_queue = queue.Queue(maxsize=0)

    # Add each device from device_list into the queue
    for device in device_list:
        device_queue.put(device)

    # Save config for each device levering multiple threads
    run_mt(mt_function=saveConfig, q=device_queue, totalDevices=len(device_list))

# Function to see what thread a print statement comes from
def mt_print(msg):
    with PRINT_LOCK:
        print(msg)

# Code that actually instantiates threading
def run_mt(mt_function, q, totalDevices):
    num_threads = min(NUM_THREADS, totalDevices)

    for i in range(num_threads):
        thread_name = f'Thread-{i}'
        worker = threading.Thread(name=thread_name, target=mt_function, args=(q,))
        worker.start()

    q.join()

# Function to save config from list of devices above
def saveConfig(q):
    while True:
        # Get the name of the thread this function runs on
        thread_name = threading.current_thread().getName()

        # Catch for when the queue is empty
        if q.empty():
            # mt_print(f'{thread_name}: Closing as there is no job left in the queue')
            return

        # Gather variables from queue
        device_details = q.get()
        deviceName = device_details['deviceName']
        deviceType = device_details['deviceType']
        devicePort = device_details['devicePort']

        # Calculate elapsed time so far
        elapsed = time.perf_counter() - startTimeGlobal

        # Print device name and start time when initiating connection
        mt_print(f'{thread_name}: Starting connection: {deviceName}    Time Elapsed: {elapsed:0.2f}')

        # Create dictionary for netmiko module to reference
        iosv_router = {
            'meta': {
                'device_name': deviceName
            },
            'netmiko': {
                'device_type': deviceType,
                'host': '10.3.196.13',
                'username': 'netadmin',
                'password': 'qwe123$!',
                'port': devicePort
            }
        }

        # Connect via SSH to currently iterated device
        try:
            device_connection = netmiko.ConnectHandler(**iosv_router['netmiko'])
        except Exception as e:
            mt_print(f'Error occured when connecting to device {deviceName}: {e}\n')

        # Get the 'show run' from the current iterated device
        try:
            running_config = device_connection.send_command('show run')
        except Exception as e:
            mt_print(f'Error occured when sending command to device {deviceName}: {e}\n')

        # Write running config to output file in local directory
        try:
            with open(f'{iosv_router["meta"]["device_name"]}-running_config.txt', "w") as file:
                file.write(running_config)
        except Exception as e:
            mt_print(f'Error occured when writing config to file for {deviceName}: {e}\n')

        q.task_done()

# Execute main() if this file is executed
if __name__ == "__main__":
    # Execute main function
    main()

    # Print total run time of program
    elapsedFinal = time.perf_counter() - startTimeGlobal
    print(f'Program completed in {elapsedFinal:0.2f} seconds.')
