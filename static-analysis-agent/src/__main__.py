"""
Command-line interface for the Static Analysis Agent.
"""

import asyncio
import click
from pathlib import Path
from typing import Optional, List
import json
import sys
import os
from datetime import datetime

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
@click.option('--output-dir', '-d', type=click.Path(), default='output',
              help='Output directory for the report (default: output)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress console output, only save to file')
def analyze(codebase_path: str, languages: List[str], tools: List[str],
           output_format: str, output_dir: str, quiet: bool):
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

            # Generate output filename based on codebase path
            codebase_name = os.path.basename(os.path.abspath(codebase_path))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis_{codebase_name}_{timestamp}.{output_format}"
            output_file = os.path.join(output_dir, filename)

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Save to file
            if output_format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                from .agent.report_generator import ReportGenerator
                generator = ReportGenerator()
                html_content = generator._generate_html_report(result)
                with open(output_file, 'w') as f:
                    f.write(html_content)

            click.echo(f"Analysis complete. Report saved to: {output_file}")

            # Show summary on console unless quiet mode
            if not quiet:
                click.echo("\nAnalysis Summary:")
                click.echo(f"  Languages detected: {', '.join(result['detected_languages'])}")
                click.echo(f"  Tools used: {', '.join(result['tools_used'])}")
                click.echo(f"  Total findings: {result['report']['summary']['total_findings']}")
                click.echo(f"  Total errors: {result['report']['summary']['total_errors']}")

                severity_breakdown = result['report']['summary']['severity_breakdown']
                if any(count > 0 for count in severity_breakdown.values()):
                    click.echo("  Severity breakdown:")
                    for severity, count in severity_breakdown.items():
                        if count > 0:
                            click.echo(f"    {severity.capitalize()}: {count}")

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

    agent = StaticAnalysisAgent()
    tools = agent.get_available_tools()

    for tool in tools:
        status = "[INSTALLED]" if tool['installed'] else "[NOT INSTALLED]"
        click.echo(f"{status} {tool['name']}: {tool['description']}")
        click.echo(f"    Supports: {', '.join(tool['supported_languages'])}")
        click.echo()


if __name__ == '__main__':
    cli()
