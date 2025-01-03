# src/report_generator.py
# import pandas as pd
# import numpy as np
# from typing import Dict, List
# import logging
# from pathlib import Path
# import json

# logger = logging.getLogger(__name__)

# class ReportGenerator:
#     def __init__(self, output_dir: str):
#         self.output_dir = Path(output_dir)
#         self.output_dir.mkdir(parents=True, exist_ok=True)
        
#     def generate_summary_csv(self, results: List[Dict]):
#         df = pd.DataFrame(results)
#         output_path = self.output_dir / 'summary_statistics.csv'
#         df.to_csv(output_path, index=False)
        
#     def generate_detailed_report(self, results: List[Dict], config: Dict):
#         converted_results = self._convert_to_serializable(results)
#         report = {
#             'overall_statistics': self._calculate_overall_stats(converted_results),
#             'per_sample_breakdown': converted_results,
#             'configuration': config,
#             'methods_description': self._get_methods_description()
#         }
        
#         output_path = self.output_dir / 'detailed_report.json'
#         with open(output_path, 'w') as f:
#             json.dump(report, f, indent=2)
            
#     def _convert_to_serializable(self, data):
#         if isinstance(data, (np.int64, np.int32)):
#             return int(data)
#         elif isinstance(data, (np.float64, np.float32)):
#             return float(data)
#         elif isinstance(data, dict):
#             return {k: self._convert_to_serializable(v) for k, v in data.items()}
#         elif isinstance(data, list):
#             return [self._convert_to_serializable(item) for item in data]
#         return data
            
#     def _calculate_overall_stats(self, results: List[Dict]) -> Dict:
#         df = pd.DataFrame(results)
#         stats = {
#             'total_samples': len(results),
#             'total_reads': int(df['total_reads'].sum()),
#             'average_primer_dimer_rate': float(df['primer_dimer_percentage'].mean()),
#             'average_valid_rate': float((df['valid_amplicon_count'] / df['total_reads']).mean() * 100)
#         }
#         return stats

#     def _get_methods_description(self) -> str:
#         return """Analysis performed using Amplicon Analyzer:
# - Primer dimer detection: Sequences below threshold checked for primer matches
# - Off-target detection: Sequences outside expected length range
# - Quality filtering: Reads below quality threshold removed"""


# src/report_generator.py
import pandas as pd
import numpy as np
from typing import Dict, List
import logging
from pathlib import Path
import json
from .visualizer import Visualizer  # Add this import

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.visualizer = Visualizer(str(self.output_dir / 'plots'))
        
    def generate_summary_csv(self, results: List[Dict]):
        """Generate summary CSV with multi-sample support."""
        df = pd.DataFrame(results)
        output_path = self.output_dir / 'summary_statistics.csv'
        df.to_csv(output_path, index=False)
        
        # Generate per-sample CSVs
        for result in results:
            sample_id = result['sample_id']
            sample_df = pd.DataFrame([result])
            sample_path = self.output_dir / f"{sample_id}_statistics.csv"
            sample_df.to_csv(sample_path, index=False)
            
    def generate_detailed_report(self, results: List[Dict], config: Dict):
        """Generate detailed report with multi-sample support."""
        converted_results = self._convert_to_serializable(results)
        
        # Calculate per-sample statistics
        sample_stats = {}
        for result in converted_results:
            sample_id = result['sample_id']
            sample_stats[sample_id] = {
                'total_reads': result['total_reads'],
                'primer_dimer_rate': result['primer_dimer_percentage'],
                'valid_rate': (result['valid_amplicon_count'] / result['total_reads']) * 100
            }
        
        report = {
            'overall_statistics': self._calculate_overall_stats(converted_results),
            'per_sample_statistics': sample_stats,
            'per_sample_breakdown': converted_results,
            'configuration': config,
            'methods_description': self._get_methods_description()
        }
        
        output_path = self.output_dir / 'detailed_report.json'
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
    # def generate_html_report(self, results: List[Dict], config: Dict):
    #     """Generate an HTML report with embedded visualizations."""
    #     template = """
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #         <title>Amplicon Analysis Report</title>
    #         <style>
    #             body { font-family: Arial, sans-serif; margin: 20px; }
    #             .section { margin-bottom: 30px; }
    #             .plot { margin: 20px 0; }
    #             table { border-collapse: collapse; width: 100%; }
    #             th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    #             th { background-color: #f2f2f2; }
    #         </style>
    #     </head>
    #     <body>
    #         <h1>Amplicon Analysis Report</h1>
            
    #         <div class="section">
    #             <h2>Summary Statistics</h2>
    #             {summary_table}
    #         </div>
            
    #         <div class="section">
    #             <h2>Visualizations</h2>
    #             <div class="plot">
    #                 <h3>Length Distributions</h3>
    #                 <img src="plots/length_distributions_grid.png" alt="Length Distributions">
    #             </div>
                
    #             <div class="plot">
    #                 <h3>Primer Dimer Comparison</h3>
    #                 <img src="plots/primer_dimer_comparison.png" alt="Primer Dimer Comparison">
    #             </div>
                
    #             <div class="plot">
    #                 <h3>Quality Metrics Heatmap</h3>
    #                 <img src="plots/metrics_heatmap.png" alt="Quality Metrics Heatmap">
    #             </div>
                
    #             <div class="plot">
    #                 <h3>Summary Dashboard</h3>
    #                 <img src="plots/summary_dashboard.png" alt="Summary Dashboard">
    #             </div>
    #         </div>
            
    #         <div class="section">
    #             <h2>Configuration</h2>
    #             {config_table}
    #         </div>
    #     </body>
    #     </html>
    #     """
        
    #     # Create summary table
    #     df = pd.DataFrame(results)
    #     summary_table = df.to_html(classes='summary-table')
        
    #     # Create config table
    #     config_df = pd.DataFrame([config]).T
    #     config_df.columns = ['Value']
    #     config_table = config_df.to_html(classes='config-table')
        
    #     # Generate HTML
    #     html_content = template.format(
    #         summary_table=summary_table,
    #         config_table=config_table
    #     )
        
    #     # Save HTML report
    #     with open(self.output_dir / 'report.html', 'w') as f:
    #         f.write(html_content)

    def generate_html_report(self, results: List[Dict], config: Dict):
        """Generate an HTML report with embedded visualizations."""
        template = """<!DOCTYPE html>
<html>
<head>
    <title>Amplicon Analysis Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .plot {
            margin: 20px 0;
            padding: 15px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        h1, h2, h3 {
            color: #333;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 10px auto;
        }
    </style>
</head>
<body>
    <h1>Amplicon Analysis Report</h1>
    
    <div class="section">
        <h2>Summary Statistics</h2>
        {summary_table}
    </div>
    
    <div class="section">
        <h2>Visualizations</h2>
        <div class="plot">
            <h3>Length Distributions</h3>
            <img src="plots/length_distributions_grid.png" alt="Length Distributions">
        </div>
        
        <div class="plot">
            <h3>Primer Dimer Comparison</h3>
            <img src="plots/primer_dimer_comparison.png" alt="Primer Dimer Comparison">
        </div>
        
        <div class="plot">
            <h3>Quality Metrics Heatmap</h3>
            <img src="plots/metrics_heatmap.png" alt="Quality Metrics Heatmap">
        </div>
        
        <div class="plot">
            <h3>Summary Dashboard</h3>
            <img src="plots/summary_dashboard.png" alt="Summary Dashboard">
        </div>
    </div>
    
    <div class="section">
        <h2>Configuration</h2>
        {config_table}
    </div>
</body>
</html>"""
        
        try:
            # Create summary table
            df = pd.DataFrame(results)
            summary_table = df.to_html(classes='summary-table', border=1)
            
            # Create config table
            config_df = pd.DataFrame([config]).T
            config_df.columns = ['Value']
            config_table = config_df.to_html(classes='config-table', border=1)
            
            # Generate HTML
            html_content = template.format(
                summary_table=summary_table,
                config_table=config_table
            )
            
            # Save HTML report
            with open(self.output_dir / 'report.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            raise    
            
    def _convert_to_serializable(self, data):
        if isinstance(data, (np.int64, np.int32)):
            return int(data)
        elif isinstance(data, (np.float64, np.float32)):
            return float(data)
        elif isinstance(data, dict):
            return {k: self._convert_to_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_serializable(item) for item in data]
        return data
            
    def _calculate_overall_stats(self, results: List[Dict]) -> Dict:
        df = pd.DataFrame(results)
        stats = {
            'total_samples': len(results),
            'total_reads': int(df['total_reads'].sum()),
            'average_primer_dimer_rate': float(df['primer_dimer_percentage'].mean()),
            'average_valid_rate': float((df['valid_amplicon_count'] / df['total_reads']).mean() * 100)
        }
        return stats

    def _get_methods_description(self) -> str:
        return """Analysis performed using Amplicon Analyzer:
- Primer dimer detection: Sequences below threshold checked for primer matches
- Off-target detection: Sequences outside expected length range
- Quality filtering: Reads below quality threshold removed"""