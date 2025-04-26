# Academic Paper Visualizations

## Overview

This feature enhances the academic research capabilities of Sentino AI by adding interactive visualizations for academic papers. These visualizations help users understand relationships between papers, track research progression over time, and explore author collaborations.

## Features

### 1. Citation Network Visualization

The citation network visualization displays relationships between papers based on their citations. Papers are represented as nodes in a network graph, with directional edges showing citation relationships.

- **Nodes**: Research papers with titles and publication years
- **Edges**: Citations between papers
- **Color coding**: Based on the number of connections (citations and references)
- **Hover information**: Displays paper title, publication year, and citation statistics

### 2. Research Timeline Visualization

The timeline visualization presents papers chronologically, allowing users to track the progression of research on a particular topic over time.

- **Time axis**: Shows the publication years
- **Paper points**: Positioned along the timeline
- **Hover information**: Shows full paper title, authors, and publication date
- **Labels**: Abbreviated paper titles appear directly on the timeline

### 3. Author Collaboration Network

The author collaboration visualization shows connections between authors who have co-authored papers together.

- **Nodes**: Individual authors
- **Edges**: Co-authorship relationships
- **Node size/color**: Represents the number of papers by that author
- **Edge thickness**: Represents the number of co-authored papers
- **Hover information**: Shows author name, paper count, and paper titles

## Technical Implementation

The visualizations are implemented using:

1. **Plotly.js**: For creating interactive charts and network diagrams
2. **NetworkX**: For graph data structure and analysis (server-side)
3. **Flask endpoints**: For generating visualization data
4. **MongoDB**: For storing paper metadata

## Usage

1. Perform an academic search by entering a research question
2. After results load, scroll down to the "Research Visualizations" section
3. Use the tabs to switch between different visualization types
4. Hover over elements to see detailed information
5. Use the Export button to download the current visualization as an image

## Notes

- The citation data is partially simulated since arXiv's API doesn't directly provide citation information
- For optimal visualizations, we recommend searching for topics with at least 5-7 papers
- The visualizations are responsive and work on mobile devices, though desktop viewing is recommended for complex networks

## Future Enhancements

Planned improvements for the visualization system include:

1. Integration with Semantic Scholar or Google Scholar for more accurate citation data
2. Topic clustering visualization to show research themes
3. Filtering options based on publication date, citation count, or author
4. Citation prediction using machine learning to suggest potential missing connections
5. User bookmarking of specific visualizations

## Technical Requirements

The visualization features require the following packages (added to requirements.txt):
- plotly==5.22.0
- networkx==3.2.1
- scholarly==1.7.11
- pandas==2.1.1
- scikit-learn==1.4.0 