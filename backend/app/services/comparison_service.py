"""
Service for paper comparison operations.
"""
from typing import Dict, Any, List
from app.services.paper_service import PaperService


class ComparisonService:
    """Service for structured paper comparisons."""
    
    def __init__(self, paper_service: PaperService):
        """
        Initialize comparison service.
        
        Args:
            paper_service: Paper service instance
        """
        self.paper_service = paper_service
    
    async def generate_comparison_table(
        self,
        paper1_id: str,
        paper2_id: str
    ) -> Dict[str, Any]:
        """
        Generate a structured comparison table.
        
        Args:
            paper1_id: First paper identifier
            paper2_id: Second paper identifier
            
        Returns:
            Structured comparison dictionary
        """
        aspects = ["methodology", "dataset", "results", "limitations"]
        
        comparison = await self.paper_service.compare_papers(
            paper1_id, paper2_id, aspects
        )
        
        # Format as table-like structure
        table = {
            'aspects': {},
            'paper1_name': comparison['paper1_name'],
            'paper2_name': comparison['paper2_name']
        }
        
        for aspect in aspects:
            if aspect in comparison['comparison']:
                aspect_data = comparison['comparison'][aspect]
                table['aspects'][aspect] = {
                    'paper1': aspect_data.get('paper1', 'Not available'),
                    'paper2': aspect_data.get('paper2', 'Not available'),
                    'differences': aspect_data.get('differences', 'Not available'),
                    'raw_text': aspect_data.get('raw_text', '')
                }
        
        return table




