# SQLmap Agent

This agent uses `sqlmap` to perform SQL injection attacks on the vulnerable application.

## Setup

1.  Install the required Python libraries:
    ```
    pip install -r requirements.txt
    ```

2.  Make sure you have `sqlmap` installed and in your PATH.

## Usage

To run the agent, execute the `agent.py` script:

```
python agent.py
```

The agent will:

1.  Read the `openapi.yaml` file from the `vulnerable-app` directory.
2.  Identify potential SQL injection targets.
3.  Construct and execute `sqlmap` commands.
4.  Save the output of the attacks in the `attack-logs` directory.
