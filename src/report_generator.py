"""
HTML report generation for meetings using Jinja2 templates.
"""
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Optional
from .models import Meeting


class ReportGenerator:
    """Handles HTML report generation for meetings."""
    
    def __init__(self, template_dir: str = "templates"):
        """Initialize the report generator with template directory."""
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
        
        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    def generate_html_report(self, meeting: Meeting) -> Optional[str]:
        """
        Generate HTML report for a meeting.
        
        Args:
            meeting: The Meeting object to generate report for
            
        Returns:
            str: HTML content as string, or None if generation failed
        """
        try:
            template = self.jinja_env.get_template('meeting_report.html')
            html_content = template.render(meeting=meeting)
            
            print(f"Successfully generated HTML report for meeting {meeting.id}")
            return html_content
            
        except Exception as e:
            print(f"Error generating HTML report for meeting {meeting.id}: {e}")
            return None
    
    def save_html_report(self, meeting: Meeting, output_dir: str = "reports") -> Optional[str]:
        """
        Generate and save HTML report to local file.
        
        Args:
            meeting: The Meeting object to generate report for
            output_dir: Directory to save the report
            
        Returns:
            str: Path to saved file, or None if failed
        """
        try:
            # Generate HTML content
            html_content = self.generate_html_report(meeting)
            if not html_content:
                return None
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Save to file
            report_file = output_path / f"{meeting.id}_report.html"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML report saved to: {report_file}")
            return str(report_file)
            
        except Exception as e:
            print(f"Error saving HTML report for meeting {meeting.id}: {e}")
            return None
    
    def get_template_path(self) -> Path:
        """Get the path to the template directory."""
        return self.template_dir
    
    def template_exists(self) -> bool:
        """Check if the meeting report template exists."""
        template_file = self.template_dir / "meeting_report.html"
        return template_file.exists()

