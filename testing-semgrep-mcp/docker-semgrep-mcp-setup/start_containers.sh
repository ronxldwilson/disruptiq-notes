#!/bin/bash

# Script to start Docker MCP Toolkit containers

echo "Starting Docker MCP Toolkit containers..."

# Start the core Docker MCP server for running temporary containers
docker run -d --name docker-mcp-toolkit -p 3000:3000 mcp/docker

# Start GitHub MCP server for repository operations
docker run -d --name github-mcp -p 3001:3001 mcp/github-official

# Start Stripe MCP server (example for payments/business logic)
docker run -d --name stripe-mcp -p 3002:3002 mcp/stripe

# Start MongoDB MCP server (example for database operations)
docker run -d --name mongodb-mcp -p 3003:3003 mcp/mongodb

echo "Docker MCP Toolkit containers started successfully!"
echo ""
echo "Running containers:"
docker ps --filter "name=mcp"
echo ""
echo "To stop containers: docker stop docker-mcp-toolkit github-mcp stripe-mcp mongodb-mcp"
echo "To remove containers: docker rm docker-mcp-toolkit github-mcp stripe-mcp mongodb-mcp"
