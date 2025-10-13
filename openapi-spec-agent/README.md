# OpenAPI Spec Agent

This agent's purpose is to take a project of any kind, review it and then build out the open api spec file for it.

## Project Structure

The project is structured as follows:

- `src/`: Contains the source code for the agent.
  - `main.py`: The main entry point for the agent.
  - `scanner.py`: Contains the logic for scanning the project directory.
  - `parser.py`: Contains the logic for parsing the source code and extracting API information.
  - `generator.py`: Contains the logic for generating the OpenAPI spec.
- `tests/`: Contains unit tests for the agent.
- `tmp/`: Contains temporary files used by the agent.

## How to Use

To see the agent's capabilities, you can run it on the sample Flask application provided in the `tmp` directory.

1. **Install the dependencies:**

   ```bash
   pip install flask pyyaml
   ```

2. **Run the agent:**

   ```bash
   python src/main.py
   ```

   This will scan the `tmp` directory for the sample Flask application, parse the code to extract the API endpoints, and then generate an OpenAPI spec in YAML format, which will be printed to the console.

## How to Run Tests

To run the tests for the agent, you can use the `unittest` module.

1. **Navigate to the project directory:**

   ```bash
   cd openapi-spec-agent
   ```

2. **Run the tests:**

   ```bash
   python -m unittest discover tests
   ```

   This will discover and run all the tests in the `tests` directory.

## Current Capabilities

The agent can currently:

- Scan a project directory and identify Python files.
- Parse Python files and extract Flask route information (`@app.route(...)`).
- Generate a basic OpenAPI spec in YAML format, including paths and HTTP methods.

## Roadmap

This section outlines the roadmap for making the OpenAPI Spec Agent an S-tier, industry-best software.

### Core Features

- **Support for more languages and frameworks:**
  - JavaScript/TypeScript (with Express, Nest.js, etc.)
  - Java (with Spring Boot, JAX-RS, etc.)
  - C# (with ASP.NET Core)
  - Go (with Gin, etc.)
  - Ruby (with Rails, Sinatra, etc.)
- **Sophisticated code analysis:**
  - Extract request/response models and data schemas.
  - Infer data types from code.
  - Identify authentication and authorization requirements.
  - Support for OpenAPI components (schemas, responses, parameters, etc.).
- **Model-agnostic interface:**
  - Define a clear interface that separates the core logic from the specific AI model being used.
  - Allow users to easily swap out different models (e.g., GPT-3, Claude, etc.).
- **CLI improvements:**
  - Allow users to specify the project directory and the output file for the OpenAPI spec.
  - Add support for different output formats (e.g., JSON, YAML).
  - Add a watch mode that automatically regenerates the spec when the code changes.
- **Error handling and logging:**
  - Add robust error handling and logging to make the agent more reliable.

### Advanced Features

- **AI-powered inference:**
  - Use AI models to infer missing information, such as descriptions, examples, and constraints.
  - Automatically generate human-readable descriptions for endpoints and schemas.
- **Interactive mode:**
  - Add an interactive mode that allows users to review and edit the generated spec before saving it.
- **Integration with other tools:**
  - Integrate with popular API design tools, such as Swagger Hub and Postman.
  - Integrate with CI/CD pipelines to automatically generate and validate the spec.
- **GUI:**
  - Create a graphical user interface (GUI) to make the agent more user-friendly.

### Community and Support

- **Comprehensive documentation:**
  - Create comprehensive documentation that covers all aspects of the agent.
- **Community forum:**
  - Create a community forum where users can ask questions, share ideas, and get help.
- **Extensive test suite:**
  - Build out a comprehensive test suite to ensure the quality and reliability of the agent.
