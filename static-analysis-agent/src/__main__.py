"""
Command-line interface for the Static Analysis Agent.
"""

import asyncio
import click
from pathlib import Path
from typing import Optional, List
import json
import sys

from .agent.core import StaticAnalysisAgent


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Static Analysis Agent - Automated code analysis using multiple tools."""
    pass


@cli.command()
@click.argument('codebase_path', type=click.Path(exists=True))
@click.option('--languages', '-l', multiple=True, help='Specify programming languages to analyze')
@click.option('--tools', '-t', multiple=True, help='Specify tools to use')
@click.option('--output-format', '-f', type=click.Choice(['json', 'html']), default='json',
              help='Output format for the report')
@click.option('--output-file', '-o', type=click.Path(), help='Output file path for the report')
def analyze(codebase_path: str, languages: List[str], tools: List[str],
           output_format: str, output_file: Optional[str]):
    """Analyze a codebase using static analysis tools."""

    # Convert empty lists to None
    languages = list(languages) if languages else None
    tools = list(tools) if tools else None

    async def run_analysis():
        agent = StaticAnalysisAgent()
        try:
            result = await agent.analyze_codebase(codebase_path, languages, tools)

            if not result['success']:
                click.echo(f"Analysis failed: {result.get('error', 'Unknown error')}", err=True)
                return

            # Output to console
            if output_format == 'json':
                click.echo(json.dumps(result, indent=2))
            else:
                # For HTML, we need to generate it
                from .agent.report_generator import ReportGenerator
                generator = ReportGenerator()
                html_content = generator._generate_html_report(result)
                click.echo(html_content)

            # Save to file if specified
            if output_file:
                if output_format == 'json':
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                else:
                    from .agent.report_generator import ReportGenerator
                    generator = ReportGenerator()
                    html_content = generator._generate_html_report(result)
                    with open(output_file, 'w') as f:
                        f.write(html_content)
                click.echo(f"Report saved to {output_file}")

        except Exception as e:
            click.echo(f"Error during analysis: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_analysis())


@cli.command()
@click.option('--tool', '-t', multiple=True, help='Specific tools to install')
def install_tools(tool: List[str]):
    """Install static analysis tools."""

    tools = list(tool) if tool else None

    async def run_install():
        agent = StaticAnalysisAgent()
        try:
            result = await agent.install_tools(tools)
            for item in result['results']:
                if 'success' in item:
                    status = "✓" if item['success'] else "✗"
                    click.echo(f"{status} {item['tool']}")
                else:
                    click.echo(item)
        except Exception as e:
            click.echo(f"Error installing tools: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_install())


@cli.command()
def list_tools():
    """List available static analysis tools."""

    async def run_list():
        agent = StaticAnalysisAgent()
        tools = await agent.get_available_tools()

        for tool in tools:
            status = "[INSTALLED]" if tool['installed'] else "[NOT INSTALLED]"
            click.echo(f"{status} {tool['name']}: {tool['description']}")
            click.echo(f"    Supports: {', '.join(tool['supported_languages'])}")
            click.echo()

    asyncio.run(run_list())


if __name__ == '__main__':
    cli()
