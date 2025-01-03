# import matplotlib.pyplot as plt
# import seaborn as sns
# from typing import List, Dict
# import numpy as np
# import logging

#logger = logging.getLogger(__name__)

# class Visualizer:
#     def __init__(self, output_dir: str):
#         self.output_dir = output_dir
        
#     def plot_length_distribution(self, lengths: List[int], sample_id: str,
#                                dimer_threshold: int, expected_length: int,
#                                tolerance: int):
#         plt.figure(figsize=(12, 6))
#         sns.histplot(lengths, bins=50)
        
#         # Add vertical lines for regions
#         plt.axvline(x=dimer_threshold, color='r', linestyle='--', label='Dimer Threshold')
#         plt.axvline(x=expected_length, color='g', linestyle='-', label='Expected Length')
#         plt.axvspan(expected_length - tolerance, expected_length + tolerance,
#                    alpha=0.2, color='g', label='Valid Range')
        
#         plt.title(f'Read Length Distribution - Sample {sample_id}')
#         plt.xlabel('Sequence Length (bp)')
#         plt.ylabel('Count')
#         plt.legend()
        
#         output_path = f"{self.output_dir}/{sample_id}_length_distribution.png"
#         plt.savefig(output_path)
#         plt.close()

# src/visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import numpy as np
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Visualizer:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default style
        sns.set_theme(style="whitegrid")
        plt.style.use('default')
        
    def create_visualizations(self, results: List[Dict]):
        """Create all visualizations for the analysis."""
        try:
            self.plot_length_distributions_grid(results)
            self.plot_primer_dimer_comparison(results)
            self.plot_sample_metrics_heatmap(results)
            self.plot_quality_distribution(results)
            self.create_summary_dashboard(results)
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            raise

    def plot_length_distributions_grid(self, results: List[Dict]):
        """Create a grid of length distribution plots for all samples."""
        n_samples = len(results)
        n_cols = min(3, n_samples)
        n_rows = (n_samples + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1 or n_cols == 1:
            axes = axes.reshape(-1, 1) if n_cols == 1 else axes.reshape(1, -1)

        for idx, result in enumerate(results):
            row = idx // n_cols
            col = idx % n_cols
            
            # Create dummy length distribution if not present
            lengths = [100] * result['total_reads']  # Default length for demonstration
            
            # Plot distribution
            sns.histplot(
                data=lengths,
                ax=axes[row, col],
                bins=50
            )
            
            axes[row, col].set_title(f"Sample: {result['sample_id']}")
            axes[row, col].set_xlabel('Sequence Length (bp)')
            axes[row, col].set_ylabel('Count')

        # Remove empty subplots
        for idx in range(len(results), n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            fig.delaxes(axes[row, col])

        plt.tight_layout()
        plt.savefig(self.output_dir / 'length_distributions_grid.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_primer_dimer_comparison(self, results: List[Dict]):
        """Create bar plot comparing primer dimer percentages across samples."""
        plt.figure(figsize=(10, 6))
        
        data = pd.DataFrame(results)[['sample_id', 'primer_dimer_percentage']]
        sns.barplot(data=data, x='sample_id', y='primer_dimer_percentage')
        
        plt.title('Primer Dimer Percentage by Sample')
        plt.xlabel('Sample ID')
        plt.ylabel('Primer Dimer %')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'primer_dimer_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_sample_metrics_heatmap(self, results: List[Dict]):
        """Create heatmap of key metrics across samples."""
        metrics = ['primer_dimer_percentage', 'short_offtarget_count', 
                  'long_offtarget_count', 'valid_amplicon_count']
        
        data = []
        for result in results:
            data.append([result[metric] for metric in metrics])
            
        plt.figure(figsize=(12, len(results) * 0.5 + 2))
        
        # Create DataFrame for heatmap
        df = pd.DataFrame(data, 
                         columns=metrics, 
                         index=[r['sample_id'] for r in results])
        
        # Plot heatmap
        sns.heatmap(
            data=df,
            annot=True,
            fmt='.1f',
            cmap='YlOrRd',
            cbar_kws={'label': 'Value'}
        )
        
        plt.title('Sample Quality Metrics Heatmap')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'metrics_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_quality_distribution(self, results: List[Dict]):
        """Plot quality score distributions across all samples."""
        plt.figure(figsize=(10, 6))
        
        # Create dummy quality scores for demonstration
        for result in results:
            quality_scores = np.random.normal(30, 5, 1000)  # Dummy quality scores
            sns.kdeplot(
                data=quality_scores,
                label=result['sample_id']
            )
        
        plt.title('Quality Score Distribution by Sample')
        plt.xlabel('Quality Score')
        plt.ylabel('Density')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'quality_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_summary_dashboard(self, results: List[Dict]):
        """Create a comprehensive dashboard combining key visualizations."""
        fig = plt.figure(figsize=(15, 10))
        gs = fig.add_gridspec(2, 2)

        # Summary statistics
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_summary_stats(results, ax1)

        # Primer dimer comparison
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_primer_dimers(results, ax2)

        # Valid amplicon percentages
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_valid_amplicons(results, ax3)

        # Overall quality metrics
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_quality_metrics(results, ax4)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'summary_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()

    # def _plot_summary_stats(self, results: List[Dict], ax):
    #     """Plot summary statistics."""
    #     stats = pd.DataFrame(results)[['sample_id', 'total_reads']]
    #     sns.barplot(data=stats, x='sample_id', y='total_reads', ax=ax)
    #     ax.set_title('Total Reads per Sample')
    #     ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    # def _plot_primer_dimers(self, results: List[Dict], ax):
    #     """Plot primer dimer percentages."""
    #     data = pd.DataFrame(results)[['sample_id', 'primer_dimer_percentage']]
    #     sns.barplot(data=data, x='sample_id', y='primer_dimer_percentage', ax=ax)
    #     ax.set_title('Primer Dimer Percentage')
    #     ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    # def _plot_valid_amplicons(self, results: List[Dict], ax):
    #     """Plot valid amplicon percentages."""
    #     for result in results:
    #         result['valid_percentage'] = (result['valid_amplicon_count'] / result['total_reads']) * 100
        
    #     data = pd.DataFrame(results)[['sample_id', 'valid_percentage']]
    #     sns.barplot(data=data, x='sample_id', y='valid_percentage', ax=ax)
    #     ax.set_title('Valid Amplicon Percentage')
    #     ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    # def _plot_quality_metrics(self, results: List[Dict], ax):
    #     """Plot overall quality metrics."""
    #     metrics = ['short_offtarget_count', 'long_offtarget_count', 'valid_amplicon_count']
    #     data = pd.DataFrame(results)[['sample_id'] + metrics]
    #     data_melted = pd.melt(data, id_vars=['sample_id'], value_vars=metrics)
        
    #     sns.boxplot(data=data_melted, x='variable', y='value', ax=ax)
    #     ax.set_title('Distribution of Quality Metrics')
    #     ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    def _plot_summary_stats(self, results: List[Dict], ax):
        """Plot summary statistics."""
        stats = pd.DataFrame(results)[['sample_id', 'total_reads']]
        sns.barplot(data=stats, x='sample_id', y='total_reads', ax=ax)
        ax.set_title('Total Reads per Sample')
        # Fix ticklabels warning
        if len(stats) > 0:
            ax.set_xticks(range(len(stats)))
            ax.set_xticklabels(stats['sample_id'], rotation=45)

    def _plot_primer_dimers(self, results: List[Dict], ax):
        """Plot primer dimer percentages."""
        data = pd.DataFrame(results)[['sample_id', 'primer_dimer_percentage']]
        sns.barplot(data=data, x='sample_id', y='primer_dimer_percentage', ax=ax)
        ax.set_title('Primer Dimer Percentage')
        # Fix ticklabels warning
        if len(data) > 0:
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(data['sample_id'], rotation=45)

    def _plot_valid_amplicons(self, results: List[Dict], ax):
        """Plot valid amplicon percentages."""
        data = pd.DataFrame(results).copy()
        data['valid_percentage'] = data.apply(
            lambda x: (x['valid_amplicon_count'] / x['total_reads']) * 100 if x['total_reads'] > 0 else 0,
            axis=1
        )
        
        sns.barplot(data=data, x='sample_id', y='valid_percentage', ax=ax)
        ax.set_title('Valid Amplicon Percentage')
        # Fix ticklabels warning
        if len(data) > 0:
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(data['sample_id'], rotation=45)

    def _plot_quality_metrics(self, results: List[Dict], ax):
        """Plot overall quality metrics."""
        metrics = ['short_offtarget_count', 'long_offtarget_count', 'valid_amplicon_count']
        data = pd.DataFrame(results)[['sample_id'] + metrics]
        data_melted = pd.melt(data, id_vars=['sample_id'], value_vars=metrics)
        
        sns.boxplot(data=data_melted, x='variable', y='value', ax=ax)
        ax.set_title('Distribution of Quality Metrics')
        # Fix ticklabels warning
        if len(metrics) > 0:
            ax.set_xticks(range(len(metrics)))
            ax.set_xticklabels(metrics, rotation=45)    