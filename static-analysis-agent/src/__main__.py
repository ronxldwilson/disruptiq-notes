"""
Command-line interface for the Static Analysis Agent.
"""

import asyncio
import click
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import sys
import os
from datetime import datetime
import logging

# Configure logging to show info level and above to console
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

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
@click.option('--output-format', '-f', type=click.Choice(['json', 'html', 'markdown', 'summary']), default='json',
              help='Output format for the report')
@click.option('--output-dir', '-d', type=click.Path(), default='output',
              help='Output directory for the report (default: output)')
@click.option('--report-name', '-n', type=str, default='latest',
              help='Name for the report file (default: latest, will be archived if exists)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress console output, only save to file')
def analyze(codebase_path: str, languages: List[str], tools: List[str],
           output_format: str, output_dir: str, report_name: str, quiet: bool):
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

            # Create organized output structure
            reports_dir = os.path.join(output_dir, 'reports')
            archives_dir = os.path.join(output_dir, 'archives')
            os.makedirs(reports_dir, exist_ok=True)
            os.makedirs(archives_dir, exist_ok=True)

            # Archive existing report if it exists
            extension_map = {
                'json': 'json',
                'html': 'html',
                'markdown': 'md',
                'summary': 'txt'
            }
            extension = extension_map.get(output_format, 'txt')
            report_filename = f"{report_name}.{extension}"
            report_path = os.path.join(reports_dir, report_filename)

            if os.path.exists(report_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archive_name = f"{report_name}_{timestamp}.{extension}"
                archive_path = os.path.join(archives_dir, archive_name)
                os.rename(report_path, archive_path)
                if not quiet:
                    click.echo(f"Previous report archived to: {archive_path}")

            # Generate report content based on format
            if output_format == 'json':
                report_content = json.dumps(result, indent=2)
            elif output_format == 'html':
                from .agent.report_generator import ReportGenerator
                generator = ReportGenerator()
                report_content = generator._generate_html_report(result)
            elif output_format == 'markdown':
                report_content = _generate_markdown_report(result)
            elif output_format == 'summary':
                report_content = _generate_summary_report(result)

            # Save the report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            if not quiet:
                click.echo(f"Analysis complete. Report saved to: {report_path}")

                # Show summary on console unless quiet mode
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


@cli.command()
@click.option('--output-dir', '-d', type=click.Path(), default='output',
              help='Output directory to clean (default: output)')
@click.option('--days', type=int, default=7,
              help='Delete reports older than N days (default: 7)')
@click.confirmation_option(prompt='Are you sure you want to delete old reports?')
def clean_reports(output_dir: str, days: int):
    """Clean up old archived reports."""
    import time
    from datetime import datetime, timedelta

    archives_dir = os.path.join(output_dir, 'archives')
    if not os.path.exists(archives_dir):
        click.echo("No archives directory found.")
        return

    cutoff_time = datetime.now() - timedelta(days=days)
    deleted_count = 0

    for filename in os.listdir(archives_dir):
        filepath = os.path.join(archives_dir, filename)
        if os.path.isfile(filepath):
            # Extract timestamp from filename (format: name_YYYYMMDD_HHMMSS.ext)
            try:
                timestamp_str = filename.split('_')[-1].split('.')[0]  # Get YYYYMMDD_HHMMSS part
                file_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                if file_time < cutoff_time:
                    os.remove(filepath)
                    deleted_count += 1
                    click.echo(f"Deleted: {filename}")
            except (ValueError, IndexError):
                # Skip files that don't match the expected format
                continue

    click.echo(f"Cleaned up {deleted_count} old report(s) older than {days} days.")


def _generate_markdown_report(result: Dict[str, Any]) -> str:
    """Generate a markdown report from analysis results."""
    lines = []

    lines.append("# Static Analysis Report\n")
    lines.append(f"**Generated:** {result['report']['timestamp']}\n")

    lines.append("## Summary\n")
    summary = result['report']['summary']
    lines.append(f"- **Languages Analyzed:** {', '.join(result['detected_languages'])}")
    lines.append(f"- **Tools Used:** {', '.join(result['tools_used'])}")
    lines.append(f"- **Total Findings:** {summary['total_findings']}")
    lines.append(f"- **Total Errors:** {summary['total_errors']}")

    severity_breakdown = summary['severity_breakdown']
    if any(count > 0 for count in severity_breakdown.values()):
        lines.append("\n### Severity Breakdown")
        for severity, count in severity_breakdown.items():
            if count > 0:
                lines.append(f"- **{severity.capitalize()}:** {count}")

    # Tool summaries
    lines.append("\n## Tool Results\n")
    for tool_name, tool_summary in result['report']['tool_summaries'].items():
        lines.append(f"### {tool_name}")
        lines.append(f"- Findings: {tool_summary['findings_count']}")
        lines.append(f"- Errors: {tool_summary['errors_count']}")
        if tool_summary['errors']:
            lines.append("**Errors:**")
            for error in tool_summary['errors'][:5]:  # Limit to first 5 errors
                lines.append(f"  - {error}")
        lines.append("")

    # Detailed findings
    if result['report']['findings']:
        lines.append("## Detailed Findings\n")
        for finding in result['report']['findings'][:50]:  # Limit to first 50 findings
            lines.append(f"### {finding['tool'].upper()}: {finding['rule']}")
            lines.append(f"**File:** {finding['file']}:{finding['line']}")
            lines.append(f"**Severity:** {finding['severity'].upper()}")
            lines.append(f"**Message:** {finding['message']}")
            if finding.get('cwe'):
                lines.append(f"**CWE:** {finding['cwe']}")
            lines.append("")

    return "\n".join(lines)


def _generate_summary_report(result: Dict[str, Any]) -> str:
    """Generate a concise summary report."""
    lines = []

    lines.append("STATIC ANALYSIS SUMMARY REPORT")
    lines.append("=" * 40)
    lines.append(f"Generated: {result['report']['timestamp']}")
    lines.append("")

    summary = result['report']['summary']
    lines.append(f"Languages: {', '.join(result['detected_languages'])}")
    lines.append(f"Tools: {', '.join(result['tools_used'])}")
    lines.append(f"Total Findings: {summary['total_findings']}")
    lines.append(f"Total Errors: {summary['total_errors']}")
    lines.append("")

    # Severity breakdown
    severity_breakdown = summary['severity_breakdown']
    if any(count > 0 for count in severity_breakdown.values()):
        lines.append("SEVERITY BREAKDOWN:")
        for severity in ['high', 'medium', 'low']:
            if severity_breakdown.get(severity, 0) > 0:
                lines.append(f"  {severity.upper()}: {severity_breakdown[severity]}")
        lines.append("")

    # Top findings by tool
    lines.append("TOP FINDINGS BY TOOL:")
    for tool_result in result['results']:
        tool_name = tool_result['tool_name']
        findings = tool_result['findings']
        if findings:
            lines.append(f"  {tool_name.upper()}: {len(findings)} findings")
            # Show top 3 findings
            for finding in findings[:3]:
                lines.append(f"    - {finding['rule']}: {finding['message'][:60]}...")
    lines.append("")

    # Errors
    total_errors = sum(len(tool_result['errors']) for tool_result in result['results'])
    if total_errors > 0:
        lines.append("TOOL ERRORS:")
        for tool_result in result['results']:
            if tool_result['errors']:
                lines.append(f"  {tool_result['tool_name'].upper()}: {len(tool_result['errors'])} errors")
        lines.append("")

    lines.append("For detailed results, see the full JSON report.")

    return "\n".join(lines)


if __name__ == '__main__':
    cli()
