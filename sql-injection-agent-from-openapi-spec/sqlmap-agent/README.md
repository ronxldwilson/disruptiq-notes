# SQLmap Agent

This agent uses `sqlmap` to perform SQL injection attacks on the vulnerable application.

## How it Works

The agent works by:

1.  **Parsing the OpenAPI Specification:** The agent reads the `openapi.yaml` file from the `vulnerable-app` directory to identify the API endpoints.

2.  **Identifying Potential Targets:** It then identifies potential SQL injection targets by looking for endpoints that accept parameters in the query string or request body.

3.  **Constructing `sqlmap` Commands:** For each potential target, the agent constructs a `sqlmap` command with the appropriate URL, parameters, and options.

4.  **Executing `sqlmap`:** The agent executes the `sqlmap` commands using Python's `subprocess` module.

5.  **Saving the Results:** The output of each `sqlmap` command is saved to a log file in the `attack-logs` directory for later analysis.

## Setup

1.  **Install Dependencies:** Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure `sqlmap` Path:** The agent is configured to use a local `sqlmap` installation. You need to update the `SQLMAP_PATH` constant in the `agent.py` file to point to your `sqlmap.py` script.

    By default, it is set to:
    ```python
    SQLMAP_PATH = 'F:\disruptiq-notes\sqlmap-dev\sqlmap.py'
    ```

## Usage

To run the agent, execute the `agent.py` script from within the `sqlmap-agent` directory:

```bash
cd sqlmap-agent
python agent.py
```

The agent will then start the attack process, and you will see the `sqlmap` commands being executed in the console. The results will be saved in the `attack-logs` directory.

## Customization

You can customize the agent's behavior by modifying the `agent.py` script:

*   **Targeting Logic:** You can change the `is_potential_target` function to modify how the agent identifies potential targets. For example, you could add more sophisticated logic to analyze the endpoint's description or other properties.

*   **`sqlmap` Options:** You can modify the `construct_sqlmap_command` function to change the `sqlmap` options used in the attacks. For example, you could change the `level` and `risk` parameters, or add other options as needed.