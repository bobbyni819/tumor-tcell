"""
Citation Format Template
=======================

Template for citation formatting and reference management in biological parameter definitions.
Based on citation patterns from tumor-tcell repository.

This template provides:
- Standardized citation formats for different source types
- Reference management utilities
- Parameter-citation linking
- Bibliography generation

Usage:
    from citation_format import CitationManager, ParameterCitation
    
    citation_manager = CitationManager()
    citation = citation_manager.create_citation('journal', {...})
    parameter_citation = ParameterCitation('growth_rate', 0.6, citation)
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Citation:
    """Data class for storing citation information"""
    citation_type: str  # 'journal', 'book', 'conference', 'database', 'website'
    authors: List[str]
    title: str
    year: int
    journal: Optional[str] = None
    volume: Optional[Union[str, int]] = None
    issue: Optional[Union[str, int]] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    url: Optional[str] = None
    publisher: Optional[str] = None
    book_title: Optional[str] = None
    conference: Optional[str] = None
    database: Optional[str] = None
    access_date: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ParameterCitation:
    """Link between parameter and its citation"""
    parameter_name: str
    parameter_value: Any
    citation: Citation
    context: Optional[str] = None
    confidence: Optional[str] = None  # 'high', 'medium', 'low'
    extraction_method: Optional[str] = None  # 'direct', 'calculated', 'estimated'


class CitationManager:
    """
    Manager for creating, storing, and formatting citations based on tumor-tcell patterns.
    
    Supports multiple citation formats and provides utilities for parameter documentation.
    """
    
    def __init__(self):
        self.citations: Dict[str, Citation] = {}
        self.parameter_citations: Dict[str, List[ParameterCitation]] = {}
        self.citation_formats = self._define_citation_formats()
    
    def _define_citation_formats(self) -> Dict[str, str]:
        """Define format templates for different citation styles"""
        return {
            'tumor_tcell_style': {
                'journal': "{authors} ({year}). {title}. {journal}, {volume}({issue}), {pages}.",
                'book': "{authors} ({year}). {title}. {publisher}.",
                'conference': "{authors} ({year}). {title}. In {conference}.",
                'database': "{database} ({year}). {title}. Retrieved {access_date} from {url}.",
                'website': "{authors} ({year}). {title}. Retrieved {access_date} from {url}."
            },
            'apa_style': {
                'journal': "{authors} ({year}). {title}. {journal}, {volume}({issue}), {pages}. doi:{doi}",
                'book': "{authors} ({year}). {title}. {publisher}.",
                'website': "{authors} ({year}). {title}. Retrieved {access_date}, from {url}"
            },
            'vancouver_style': {
                'journal': "{authors}. {title}. {journal}. {year};{volume}({issue}):{pages}.",
                'book': "{authors}. {title}. {publisher}; {year}."
            }
        }
    
    def create_citation(self, citation_type: str, citation_data: Dict[str, Any]) -> Citation:
        """
        Create a citation from provided data.
        
        Args:
            citation_type: Type of citation ('journal', 'book', etc.)
            citation_data: Dictionary containing citation information
        
        Returns:
            Citation object
        """
        return Citation(
            citation_type=citation_type,
            authors=citation_data.get('authors', []),
            title=citation_data.get('title', ''),
            year=citation_data.get('year', datetime.now().year),
            journal=citation_data.get('journal'),
            volume=citation_data.get('volume'),
            issue=citation_data.get('issue'),
            pages=citation_data.get('pages'),
            doi=citation_data.get('doi'),
            pmid=citation_data.get('pmid'),
            url=citation_data.get('url'),
            publisher=citation_data.get('publisher'),
            book_title=citation_data.get('book_title'),
            conference=citation_data.get('conference'),
            database=citation_data.get('database'),
            access_date=citation_data.get('access_date'),
            notes=citation_data.get('notes')
        )
    
    def add_citation(self, citation_id: str, citation: Citation):
        """Add a citation to the manager"""
        self.citations[citation_id] = citation
    
    def add_parameter_citation(self, parameter_name: str, value: Any, citation: Citation,
                             context: str = None, confidence: str = None,
                             extraction_method: str = None):
        """
        Link a parameter to its citation.
        
        Args:
            parameter_name: Name of the parameter
            value: Parameter value
            citation: Citation object
            context: Biological context for the parameter
            confidence: Confidence level in the parameter value
            extraction_method: How the parameter was derived from the source
        """
        param_citation = ParameterCitation(
            parameter_name=parameter_name,
            parameter_value=value,
            citation=citation,
            context=context,
            confidence=confidence,
            extraction_method=extraction_method
        )
        
        if parameter_name not in self.parameter_citations:
            self.parameter_citations[parameter_name] = []
        
        self.parameter_citations[parameter_name].append(param_citation)
    
    def format_citation(self, citation: Citation, style: str = 'tumor_tcell_style') -> str:
        """
        Format a citation according to the specified style.
        
        Args:
            citation: Citation to format
            style: Citation style to use
        
        Returns:
            Formatted citation string
        """
        if style not in self.citation_formats:
            raise ValueError(f"Unknown citation style: {style}")
        
        format_templates = self.citation_formats[style]
        
        if citation.citation_type not in format_templates:
            raise ValueError(f"No template for citation type: {citation.citation_type}")
        
        template = format_templates[citation.citation_type]
        
        # Prepare formatting data
        format_data = {
            'authors': self._format_authors(citation.authors),
            'title': citation.title,
            'year': citation.year,
            'journal': citation.journal or '',
            'volume': citation.volume or '',
            'issue': citation.issue or '',
            'pages': citation.pages or '',
            'doi': citation.doi or '',
            'pmid': citation.pmid or '',
            'url': citation.url or '',
            'publisher': citation.publisher or '',
            'book_title': citation.book_title or '',
            'conference': citation.conference or '',
            'database': citation.database or '',
            'access_date': citation.access_date or ''
        }
        
        # Format the citation
        try:
            formatted = template.format(**format_data)
            # Clean up any empty parentheses or extra spaces
            formatted = self._clean_formatted_citation(formatted)
            return formatted
        except KeyError as e:
            raise ValueError(f"Missing required field for citation formatting: {e}")
    
    def _format_authors(self, authors: List[str]) -> str:
        """Format author list according to convention"""
        if not authors:
            return "Unknown"
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        elif len(authors) <= 6:
            return ", ".join(authors[:-1]) + f", and {authors[-1]}"
        else:
            # For many authors, use et al.
            return f"{authors[0]} et al."
    
    def _clean_formatted_citation(self, citation: str) -> str:
        """Clean up formatted citation by removing empty elements"""
        # Remove empty parentheses
        citation = citation.replace('()', '')
        citation = citation.replace('( )', '')
        
        # Remove extra spaces and punctuation
        citation = ' '.join(citation.split())
        citation = citation.replace(' ,', ',')
        citation = citation.replace(' .', '.')
        citation = citation.replace('..', '.')
        
        return citation
    
    def get_parameter_citations(self, parameter_name: str) -> List[ParameterCitation]:
        """Get all citations for a specific parameter"""
        return self.parameter_citations.get(parameter_name, [])
    
    def generate_bibliography(self, style: str = 'tumor_tcell_style') -> List[str]:
        """Generate a bibliography of all citations"""
        bibliography = []
        
        for citation_id, citation in self.citations.items():
            formatted = self.format_citation(citation, style)
            bibliography.append(formatted)
        
        return sorted(bibliography)  # Sort alphabetically
    
    def generate_parameter_documentation(self, parameter_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for a parameter including all citations.
        
        Args:
            parameter_name: Name of the parameter to document
        
        Returns:
            Dictionary containing parameter documentation
        """
        param_citations = self.get_parameter_citations(parameter_name)
        
        if not param_citations:
            return {'parameter': parameter_name, 'citations': [], 'documentation': None}
        
        documentation = {
            'parameter': parameter_name,
            'values': [],
            'citations': [],
            'contexts': [],
            'confidence_levels': [],
            'extraction_methods': []
        }
        
        for param_cite in param_citations:
            documentation['values'].append(param_cite.parameter_value)
            documentation['citations'].append(
                self.format_citation(param_cite.citation)
            )
            documentation['contexts'].append(param_cite.context)
            documentation['confidence_levels'].append(param_cite.confidence)
            documentation['extraction_methods'].append(param_cite.extraction_method)
        
        return documentation
    
    def export_citations(self, format_type: str = 'json') -> str:
        """Export citations in specified format"""
        if format_type == 'json':
            export_data = {
                'citations': {
                    citation_id: {
                        'type': citation.citation_type,
                        'authors': citation.authors,
                        'title': citation.title,
                        'year': citation.year,
                        'journal': citation.journal,
                        'volume': citation.volume,
                        'issue': citation.issue,
                        'pages': citation.pages,
                        'doi': citation.doi,
                        'pmid': citation.pmid,
                        'url': citation.url,
                        'publisher': citation.publisher,
                        'notes': citation.notes
                    }
                    for citation_id, citation in self.citations.items()
                },
                'parameter_citations': {
                    param_name: [
                        {
                            'value': pc.parameter_value,
                            'context': pc.context,
                            'confidence': pc.confidence,
                            'extraction_method': pc.extraction_method,
                            'citation_id': next(
                                (cid for cid, c in self.citations.items() if c == pc.citation),
                                None
                            )
                        }
                        for pc in param_citations
                    ]
                    for param_name, param_citations in self.parameter_citations.items()
                }
            }
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")


class TumorTCellCitations:
    """Predefined citations from tumor-tcell repository for reuse"""
    
    @staticmethod
    def get_common_citations() -> Dict[str, Citation]:
        """Return commonly used citations from tumor-tcell repository"""
        citations = {}
        
        # Growth rate citations
        citations['eden_2011'] = Citation(
            citation_type='journal',
            authors=['Eden, E.', 'et al.'],
            title='Probability of tumor cell division in 24 hours',
            year=2011,
            journal='Cancer Research',
            volume='71',
            issue='8',
            pages='2900-2910',
            notes='Source for PDL1n growth rate parameter (0.6 probability per 24h)'
        )
        
        # T cell citations
        citations['boissonnas_2007'] = Citation(
            citation_type='journal',
            authors=['Boissonnas, A.', 'et al.'],
            title='In vivo imaging of cytotoxic T cell infiltration and elimination of a solid tumor',
            year=2007,
            journal='Journal of Experimental Medicine',
            volume='204',
            issue='2',
            pages='345-356',
            notes='Source for T cell migration velocities (PD1n: 10 μm/min, PD1p: 5 μm/min)'
        )
        
        # Molecular weight citations
        citations['celada_1987'] = Citation(
            citation_type='journal',
            authors=['Celada, A.', 'Gray, P.W.', 'Rinderknecht, E.', 'Schreiber, R.D.'],
            title='Evidence for gamma-interferon-dependent and -independent mechanisms of macrophage activation',
            year=1987,
            journal='Journal of Experimental Medicine',
            volume='165',
            issue='4',
            pages='1267-1289',
            notes='Source for IFN-gamma internalization rate (31/60 per second)'
        )
        
        # Death mechanism citations
        citations['gong_2017'] = Citation(
            citation_type='journal',
            authors=['Gong, J.', 'et al.'],
            title='Development of PD-1 and PD-L1 inhibitors as a form of cancer immunotherapy',
            year=2017,
            journal='OncoTargets and Therapy',
            volume='10',
            pages='2423-2433',
            notes='Source for tumor cell apoptosis rates (0.95 by 5 days, negligible compared to growth/killing)'
        )
        
        # Cytotoxic mechanism citations
        citations['betts_2004'] = Citation(
            citation_type='journal',
            authors=['Betts, M.R.', 'et al.'],
            title='Sensitive and viable identification of antigen-specific CD8+ T cells by a flow cytometric assay for degranulation',
            year=2004,
            journal='Journal of Immunological Methods',
            volume='281',
            issue='1-2',
            pages='65-78',
            notes='Source for cytotoxic packet threshold (128 packets for death)'
        )
        
        # Dendritic cell citations
        citations['morefield_2005'] = Citation(
            citation_type='journal',
            authors=['Morefield, G.L.', 'et al.'],
            title='Role of aluminum-containing adjuvants in antigen internalization by dendritic cells in vitro',
            year=2005,
            journal='Vaccine',
            volume='23',
            issue='13',
            pages='1588-1595',
            notes='Source for dendritic cell diameter (10 μm)'
        )
        
        # Migration citations
        citations['lammermann_2008'] = Citation(
            citation_type='journal',
            authors=['Lammermann, T.', 'et al.'],
            title='Rapid leukocyte migration by integrin-independent flowing and squeezing',
            year=2008,
            journal='Nature',
            volume='453',
            issue='7191',
            pages='51-55',
            notes='Source for dendritic cell migration velocities (inactive: 2-5 μm/min, active: 10-15 μm/min)'
        )
        
        # DAMP citations
        citations['apetoh_2007'] = Citation(
            citation_type='journal',
            authors=['Apetoh, L.', 'et al.'],
            title='Toll-like receptor 4-dependent contribution of the immune system to anticancer chemotherapy and radiotherapy',
            year=2007,
            journal='Nature Medicine',
            volume='13',
            issue='9',
            pages='1050-1059',
            notes='Source for tumor debris amounts (1.4e15 molecules per cell) and HMGB1 molecular weight (29 kDa)'
        )
        
        return citations
    
    @staticmethod
    def create_parameter_citations() -> Dict[str, List[ParameterCitation]]:
        """Create parameter-citation mappings for common tumor-tcell parameters"""
        citations = TumorTCellCitations.get_common_citations()
        param_citations = {}
        
        # Tumor cell parameters
        param_citations['PDL1n_growth'] = [
            ParameterCitation(
                parameter_name='PDL1n_growth',
                parameter_value=0.6,
                citation=citations['eden_2011'],
                context='Probability of tumor cell division in 24 hours for PDL1-negative cells',
                confidence='high',
                extraction_method='direct'
            )
        ]
        
        param_citations['death_apoptosis'] = [
            ParameterCitation(
                parameter_name='death_apoptosis',
                parameter_value=0.5,
                citation=citations['gong_2017'],
                context='Baseline apoptosis rate, negligible compared to growth/killing (0.95 by 5 day)',
                confidence='medium',
                extraction_method='calculated'
            )
        ]
        
        # T cell parameters
        param_citations['PD1n_migration'] = [
            ParameterCitation(
                parameter_name='PD1n_migration',
                parameter_value=10.0,  # μm/min
                citation=citations['boissonnas_2007'],
                context='Migration velocity of non-exhausted T cells',
                confidence='high',
                extraction_method='direct'
            )
        ]
        
        param_citations['Max_IFNg_internalization'] = [
            ParameterCitation(
                parameter_name='Max_IFNg_internalization',
                parameter_value=31/60,  # per second
                citation=citations['celada_1987'],
                context='IFN-gamma internalization rate (1860 molecules/cell/hr converted to per second)',
                confidence='high',
                extraction_method='calculated'
            )
        ]
        
        # Dendritic cell parameters
        param_citations['diameter'] = [
            ParameterCitation(
                parameter_name='diameter',
                parameter_value=10.0,  # μm
                citation=citations['morefield_2005'],
                context='Typical dendritic cell diameter from microscopy measurements',
                confidence='high',
                extraction_method='direct'
            )
        ]
        
        return param_citations


# Utility functions
def create_journal_citation(authors: List[str], title: str, journal: str, year: int,
                          volume: str = None, issue: str = None, pages: str = None,
                          doi: str = None, pmid: str = None) -> Citation:
    """Convenience function to create journal citation"""
    return Citation(
        citation_type='journal',
        authors=authors,
        title=title,
        journal=journal,
        year=year,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        pmid=pmid
    )


def create_book_citation(authors: List[str], title: str, publisher: str, year: int,
                        pages: str = None) -> Citation:
    """Convenience function to create book citation"""
    return Citation(
        citation_type='book',
        authors=authors,
        title=title,
        publisher=publisher,
        year=year,
        pages=pages
    )


# Example usage and testing
if __name__ == '__main__':
    # Create citation manager
    citation_manager = CitationManager()
    
    # Add some common citations
    common_citations = TumorTCellCitations.get_common_citations()
    for citation_id, citation in common_citations.items():
        citation_manager.add_citation(citation_id, citation)
    
    # Add parameter citations
    param_citations = TumorTCellCitations.create_parameter_citations()
    for param_name, citations_list in param_citations.items():
        for param_cite in citations_list:
            citation_manager.add_parameter_citation(
                param_cite.parameter_name,
                param_cite.parameter_value,
                param_cite.citation,
                param_cite.context,
                param_cite.confidence,
                param_cite.extraction_method
            )
    
    # Example: Format a citation
    eden_citation = common_citations['eden_2011']
    formatted_citation = citation_manager.format_citation(eden_citation)
    print(f"Formatted citation: {formatted_citation}")
    
    # Example: Generate parameter documentation
    growth_docs = citation_manager.generate_parameter_documentation('PDL1n_growth')
    print(f"Growth parameter documentation: {growth_docs}")
    
    # Example: Generate bibliography
    bibliography = citation_manager.generate_bibliography()
    print(f"Bibliography ({len(bibliography)} entries):")
    for i, citation in enumerate(bibliography[:3], 1):  # Show first 3
        print(f"{i}. {citation}")
    
    print("Citation format template created successfully!")