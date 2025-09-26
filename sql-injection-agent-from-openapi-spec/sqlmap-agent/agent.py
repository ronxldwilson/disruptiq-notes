import os
import subprocess
import yaml

# Constants
OPENAPI_FILE = '../vulnerable-app/openapi.yaml'
LOGS_DIR = 'attack-logs'

def main():
    """Main function for the SQLmap agent."""
    # Create the logs directory if it doesn't exist
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    # Read the OpenAPI specification
    with open(OPENAPI_FILE, 'r') as f:
        openapi_spec = yaml.safe_load(f)

    # Get the server URL
    server_url = openapi_spec['servers'][0]['url']

    # Iterate over the paths in the OpenAPI specification
    for path, path_item in openapi_spec['paths'].items():
        for method, operation in path_item.items():
            # Check if the endpoint is a potential target for SQL injection
            if is_potential_target(operation):
                # Construct the sqlmap command
                sqlmap_command = construct_sqlmap_command(server_url, path, method, operation)

                # Print the command to the user
                print(f"[+] Executing command: {sqlmap_command}")

                # Execute the command and save the output
                execute_and_save_output(sqlmap_command, operation['summary'])

def is_potential_target(operation):
    """Checks if an operation is a potential target for SQL injection."""
    # For now, we'll consider any endpoint with parameters as a potential target
    return 'parameters' in operation

def construct_sqlmap_command(server_url, path, method, operation):
    """Constructs the sqlmap command for a given operation."""
    # Base command
    command = ['sqlmap', '-u', f'{server_url}{path}']

    # Add parameters
    if 'parameters' in operation:
        for param in operation['parameters']:
            if param['in'] == 'query':
                command.extend(['--data', f'{param["name"]}=test'])

    # Add request body for POST requests
    if method == 'post' and 'requestBody' in operation:
        content_type = list(operation['requestBody']['content'].keys())[0]
        if content_type == 'application/x-www-form-urlencoded':
            properties = operation['requestBody']['content'][content_type]['schema']['properties']
            data = '&'.join([f'{prop}=test' for prop in properties])
            command.extend(['--data', data])

    # Add other sqlmap options
    command.extend(['--batch', '--level=5', '--risk=3'])

    return ' '.join(command)

def execute_and_save_output(command, summary):
    """Executes a command and saves the output to a file."""
    log_file = os.path.join(LOGS_DIR, f'{summary.replace(" ", "_")}.log')
    with open(log_file, 'w') as f:
        process = subprocess.Popen(command, shell=True, stdout=f, stderr=subprocess.STDOUT)
        process.wait()

if __name__ == '__main__':
    main()
