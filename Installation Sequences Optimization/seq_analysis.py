import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import re
from matplotlib.gridspec import GridSpec
import os

# 导入数据模块
try:
    from simulated_dataset import tags_data_3, data_3, built_values_3
except ImportError:
    print("Warning: Could not import data directly. Will try alternate methods.")
    import importlib.util
    
    # 尝试从当前目录导入
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "simulated_dataset.py")
    
    if os.path.exists(file_path):
        spec = importlib.util.spec_from_file_location("simulated_dataset", file_path)
        simulated_dataset = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(simulated_dataset)
        tags_data_3 = simulated_dataset.tags_data_3
        data_3 = simulated_dataset.data_3
        built_values_3 = simulated_dataset.built_values_3
    else:
        print(f"Error: Could not find {file_path}")


class BendingActiveOptimizer:
    """
    A class to optimize assembly sequences for bending-active structures based on 
    displacement data and built values.
    """
    
    def __init__(self, tags_data, displacement_data, built_values):
        """
        Initialize the optimizer with assembly sequences and displacement data.
        
        Parameters:
        - tags_data: Dictionary mapping sequence IDs to assembly sequences
        - displacement_data: Dictionary mapping sequence IDs to displacement values at each step
        - built_values: Dictionary mapping rods to their ease-of-control scores (higher is better)
        """
        self.tags_data = tags_data
        self.displacement_data = displacement_data
        self.built_values = built_values
        
        # Pre-calculate metrics
        self.max_metrics = self._calculate_max_metrics()
        self.range_metrics = self._calculate_range_metrics()
        self.sum_metrics = self._calculate_sum_metrics()
        self.combined_metrics = self._calculate_combined_metrics()
    
    def _normalize_values(self, values):
        """Normalize values to a 0-1a scale."""
        min_value = min(values.values())
        max_value = max(values.values())
        if max_value == min_value:  # Avoid division by zero
            return {k: 0.5 for k, v in values.items()}
        return {k: (v - min_value) / (max_value - min_value) for k, v in values.items()}
    
    def _calculate_max_metrics(self):
        """Calculate maximum displacement for each sequence."""
        return {sequence: max(displacements) for sequence, displacements in self.displacement_data.items()}
    
    def _calculate_range_metrics(self):
        """Calculate displacement range (max-min) for each sequence."""
        return {sequence: max(displacements) - min(displacements) 
                for sequence, displacements in self.displacement_data.items()}
    
    def _calculate_sum_metrics(self):
        """Calculate average displacement for each sequence."""
        return {sequence: sum(displacements) / len(displacements) 
                for sequence, displacements in self.displacement_data.items()}
    
    def _calculate_combined_metrics(self, max_weight=0.4, range_weight=0.3, sum_weight=0.3):
        """
        Calculate combined metrics using weighted sum of normalized metrics.
        
        Parameters:
        - max_weight: Weight for maximum displacement (default: 0.4)
        - range_weight: Weight for displacement range (default: 0.3)
        - sum_weight: Weight for average displacement (default: 0.3)
        
        Returns:
        - Dictionary of combined metrics for each sequence
        """
        # Normalize individual metrics (lower values are better)
        norm_max = self._normalize_values(self.max_metrics)
        norm_range = self._normalize_values(self.range_metrics)
        norm_sum = self._normalize_values(self.sum_metrics)
        
        # Combine metrics with weights
        combined = {}
        for sequence in self.tags_data.keys():
            combined[sequence] = (
                max_weight * norm_max.get(sequence, 0) +
                range_weight * norm_range.get(sequence, 0) +
                sum_weight * norm_sum.get(sequence, 0)
            )
        
        return combined
    
    def get_top_sequences(self, metric_type='combined', n=25):
        """
        Get the top n sequences based on the specified metric.
        
        Parameters:
        - metric_type: Type of metric to use ('max', 'range', 'sum', 'combined')
        - n: Number of top sequences to return
        
        Returns:
        - List of (sequence_id, metric_value) tuples for top sequences
        """
        if metric_type == 'max':
            metrics = self.max_metrics
        elif metric_type == 'range':
            metrics = self.range_metrics
        elif metric_type == 'sum':
            metrics = self.sum_metrics
        else:  # 'combined' or any other value
            metrics = self.combined_metrics
        
        # Sort sequences by metric value (lower is better)
        sorted_sequences = sorted(metrics.items(), key=lambda x: x[1])
        
        # Return top n sequences
        return sorted_sequences[:n]
    
    def calculate_rod_influence(self, top_sequences, metrics, m=2):
        """
        Calculate influence factors for rods based on top sequences.
        
        Parameters:
        - top_sequences: List of (sequence_id, metric_value) tuples
        - metrics: Dictionary of metric values for each sequence
        - m: Divisor for determining how many tags to consider (default: 2)
        
        Returns:
        - Dictionary of normalized influence factors for each rod
        """
        # Extract all tags from top sequences
        all_tags = []
        for sequence_id, _ in top_sequences:
            all_tags.extend(self.tags_data[sequence_id])
        
        # Take first half of tags (divided by m)
        half_list_length = len(all_tags) // m
        top_tags = all_tags[:half_list_length]
        
        # Calculate influence factors
        influence_factors = defaultdict(float)
        
        for sequence_id, _ in top_sequences:
            # Get tags from the sequence
            sequence_tags = self.tags_data[sequence_id]
            
            # Calculate metric weight (lower metric value is better)
            metric_weight = 1 / metrics[sequence_id]
            
            # Calculate position weight (earlier position is better)
            position_weights = {tag: (len(sequence_tags) - idx) / len(sequence_tags) 
                               for idx, tag in enumerate(sequence_tags)}
            
            # Calculate influence for each tag
            for tag in sequence_tags:
                influence_factors[tag] += metric_weight * position_weights[tag]
        
        # Normalize influence factors
        return self._normalize_values(influence_factors)
    
    def calculate_final_influence(self, max_weight=0.4, range_weight=0.3, built_weight=0.3, n=25):
        """
        Calculate final influence combining multiple metrics and built values.
        
        Parameters:
        - max_weight: Weight for maximum displacement influence (default: 0.4)
        - range_weight: Weight for range displacement influence (default: 0.3)
        - built_weight: Weight for built values (default: 0.3)
        - n: Number of top sequences to consider for each metric
        
        Returns:
        - Dictionary of final influence factors for each rod
        """
        # Get top sequences for each metric
        top_max_sequences = self.get_top_sequences('max', n)
        top_range_sequences = self.get_top_sequences('range', n)
        top_sum_sequences = self.get_top_sequences('sum', n)
        
        # Calculate influence factors for each metric
        max_influence = self.calculate_rod_influence(top_max_sequences, self.max_metrics)
        range_influence = self.calculate_rod_influence(top_range_sequences, self.range_metrics)
        sum_influence = self.calculate_rod_influence(top_sum_sequences, self.sum_metrics)
        
        # Normalize built values (higher is better)
        norm_built_values = self._normalize_values(self.built_values)
        
        # Combine influence factors
        final_influence = {}
        all_rods = set(self.built_values.keys())
        
        for rod in all_rods:
            final_influence[rod] = (
                max_weight * max_influence.get(rod, 0) +
                range_weight * range_influence.get(rod, 0) +
                built_weight * norm_built_values.get(rod, 0)
            )
        
        return final_influence

    def predict_optimal_sequence(self, n_rods=None):
        """
        Predict the optimal assembly sequence based on final influence factors.
        
        Parameters:
        - n_rods: Number of rods to include in the sequence (default: all rods)
        
        Returns:
        - List of rods in optimal assembly order
        """
        # Calculate final influence
        final_influence = self.calculate_final_influence()
        
        # Sort rods by influence (higher is better for early assembly)
        sorted_rods = sorted(final_influence.items(), key=lambda x: x[1], reverse=True)
        
        # Create optimal sequence
        if n_rods is None:
            return [rod for rod, _ in sorted_rods]
        else:
            return [rod for rod, _ in sorted_rods][:n_rods]
    
    def visualize_metrics_comparison(self):
        """
        Visualize comparison of different metrics used for optimization.
        """
        # Create figure
        plt.figure(figsize=(15, 10))
        
        # Scatter plot of max vs. range metrics
        plt.subplot(2, 2, 1)
        plt.scatter(list(self.max_metrics.values()), list(self.range_metrics.values()), alpha=0.6)
        plt.xlabel('Maximum Displacement')
        plt.ylabel('Displacement Range')
        plt.title('Max vs. Range Metrics')
        
        # Scatter plot of max vs. sum metrics
        plt.subplot(2, 2, 2)
        plt.scatter(list(self.max_metrics.values()), list(self.sum_metrics.values()), alpha=0.6)
        plt.xlabel('Maximum Displacement')
        plt.ylabel('Average Displacement')
        plt.title('Max vs. Avg Metrics')
        
        # Scatter plot of range vs. sum metrics
        plt.subplot(2, 2, 3)
        plt.scatter(list(self.range_metrics.values()), list(self.sum_metrics.values()), alpha=0.6)
        plt.xlabel('Displacement Range')
        plt.ylabel('Average Displacement')
        plt.title('Range vs. Avg Metrics')
        
        # Distribution of combined metrics
        plt.subplot(2, 2, 4)
        plt.hist(list(self.combined_metrics.values()), bins=20, alpha=0.7)
        plt.xlabel('Combined Metric Value')
        plt.ylabel('Frequency')
        plt.title('Distribution of Combined Metrics')
        
        plt.tight_layout()
        return plt.gcf()
    
    def visualize_top_sequences(self, metric_type='combined', n=5):
        """
        Visualize displacement curves for top sequences.
        
        Parameters:
        - metric_type: Type of metric to use ('max', 'range', 'sum', 'combined')
        - n: Number of top sequences to visualize
        """
        # Get top sequences
        top_sequences = self.get_top_sequences(metric_type, n)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot displacement curves for top sequences
        for i, (sequence_id, metric_value) in enumerate(top_sequences):
            displacements = self.displacement_data[sequence_id]
            steps = range(1, len(displacements) + 1)
            plt.plot(steps, displacements, marker='o', label=f'{sequence_id} ({metric_value:.4f})')
        
        plt.xlabel('Assembly Step')
        plt.ylabel('Displacement')
        plt.title(f'Top {n} Sequences by {metric_type.capitalize()} Metric')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt.gcf()
    
    def visualize_rod_influence(self, metric_type='combined', n=25):
        """
        Visualize rod influence factors for a specific metric.
        
        Parameters:
        - metric_type: Type of metric to use ('max', 'range', 'sum', 'combined')
        - n: Number of top sequences to consider
        """
        # Get top sequences
        top_sequences = self.get_top_sequences(metric_type, n)
        
        # Get corresponding metrics
        if metric_type == 'max':
            metrics = self.max_metrics
        elif metric_type == 'range':
            metrics = self.range_metrics
        elif metric_type == 'sum':
            metrics = self.sum_metrics
        else:  # 'combined'
            metrics = self.combined_metrics
        
        # Calculate influence factors
        influence = self.calculate_rod_influence(top_sequences, metrics)
        
        # Sort rods for visualization (extract numeric part for sorting)
        def extract_number(rod):
            return int(re.search(r'\d+', rod).group())
        
        sorted_influence = sorted(influence.items(), key=lambda x: extract_number(x[0]))
        rods, values = zip(*sorted_influence)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        plt.bar(rods, values, color='skyblue')
        plt.xlabel('Rod')
        plt.ylabel('Influence Factor')
        plt.title(f'Rod Influence Factors ({metric_type.capitalize()} Metric)')
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', alpha=0.3)
        
        return plt.gcf()
    
    def visualize_final_influence(self):
        """
        Visualize final influence factors for all rods.
        """
        # Calculate final influence
        final_influence = self.calculate_final_influence()
        
        # Sort rods for visualization (extract numeric part for sorting)
        def extract_number(rod):
            return int(re.search(r'\d+', rod).group())
        
        sorted_influence = sorted(final_influence.items(), key=lambda x: extract_number(x[0]))
        rods, values = zip(*sorted_influence)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        plt.bar(rods, values, color='skyblue')
        plt.xlabel('Rod')
        plt.ylabel('Final Influence Factor')
        plt.title('Final Rod Influence Factors (Combined Metrics)')
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', alpha=0.3)
        
        return plt.gcf()
    
    def visualize_optimal_sequence(self):
        """
        Visualize the optimal assembly sequence with rod influence.
        """
        # Get optimal sequence
        optimal_sequence = self.predict_optimal_sequence()
        
        # Get influence values for each rod in the sequence
        final_influence = self.calculate_final_influence()
        influence_values = [final_influence[rod] for rod in optimal_sequence]
        
        # Create figure
        plt.figure(figsize=(15, 8))
        
        # Plot influence values as bar chart
        plt.subplot(2, 1, 1)
        plt.bar(optimal_sequence, influence_values, color='skyblue')
        plt.xlabel('Rod')
        plt.ylabel('Influence Factor')
        plt.title('Optimal Assembly Sequence (Higher Influence First)')
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', alpha=0.3)
        
        # Plot assembly order as a step chart
        plt.subplot(2, 1, 2)
        x = list(range(1, len(optimal_sequence) + 1))
        y = [self.built_values.get(rod, 0) for rod in optimal_sequence]
        
        plt.step(x, y, where='mid', marker='o', linestyle='-', linewidth=2)
        plt.title('Assembly Order vs. Rod Control Value')
        plt.xlabel('Assembly Step')
        plt.ylabel('Rod Control Value')
        plt.grid(True, alpha=0.3)
        
        # Add rod labels
        for i, rod in enumerate(optimal_sequence):
            plt.text(i + 1, y[i], rod, ha='center', va='bottom')
        
        plt.tight_layout()
        return plt.gcf()
    
    def visualize_comprehensive_analysis(self):
        """
        Create a comprehensive visualization dashboard of the analysis.
        """
        # Calculate final influence
        final_influence = self.calculate_final_influence()
        
        # Get optimal sequence
        optimal_sequence = self.predict_optimal_sequence()
        
        # Set up the figure with grid
        fig = plt.figure(figsize=(20, 16))
        gs = GridSpec(3, 2, figure=fig)
        
        # 1. Influence comparison for different metrics
        ax1 = fig.add_subplot(gs[0, 0])
        
        # Get influence factors for different metrics
        top_max = self.get_top_sequences('max', 25)
        top_range = self.get_top_sequences('range', 25)
        top_sum = self.get_top_sequences('sum', 25)
        
        max_influence = self.calculate_rod_influence(top_max, self.max_metrics)
        range_influence = self.calculate_rod_influence(top_range, self.range_metrics)
        sum_influence = self.calculate_rod_influence(top_sum, self.sum_metrics)
        
        # Sort rods consistently for all metrics
        all_rods = list(self.built_values.keys())
        all_rods.sort(key=lambda x: int(re.search(r'\d+', x).group()))
        
        # Plot grouped bar chart for different metrics
        bar_width = 0.2
        x = np.arange(len(all_rods))
        
        ax1.bar(x - bar_width, [max_influence.get(rod, 0) for rod in all_rods], 
                width=bar_width, label='Max', alpha=0.7)
        ax1.bar(x, [range_influence.get(rod, 0) for rod in all_rods], 
                width=bar_width, label='Range', alpha=0.7)
        ax1.bar(x + bar_width, [sum_influence.get(rod, 0) for rod in all_rods], 
                width=bar_width, label='Avg', alpha=0.7)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(all_rods, rotation=45)
        ax1.set_xlabel('Rod')
        ax1.set_ylabel('Influence Factor')
        ax1.set_title('Rod Influence by Different Metrics')
        ax1.legend()
        ax1.grid(True, axis='y', alpha=0.3)
        
        # 2. Final influence and built values
        ax2 = fig.add_subplot(gs[0, 1])
        
        ax2.bar(range(len(all_rods)), [final_influence.get(rod, 0) for rod in all_rods], 
                alpha=0.7, color='skyblue', label='Final Influence')
        ax2.plot(range(len(all_rods)), [self.built_values.get(rod, 0) for rod in all_rods], 
                'ro-', label='Built Value')
        
        ax2.set_xlabel('Rod')
        ax2.set_ylabel('Value')
        ax2.set_title('Final Influence vs. Built Values')
        ax2.legend()
        ax2.set_xticks(range(len(all_rods)))
        ax2.set_xticklabels(all_rods, rotation=45)
        ax2.grid(True, axis='y', alpha=0.3)
        
        # 3. Top sequences displacement curves
        ax3 = fig.add_subplot(gs[1, :])
        
        # Plot displacement curves for top sequences by combined metric
        top_combined = self.get_top_sequences('combined', 5)
        colors = plt.cm.tab10(np.linspace(0, 1, len(top_combined)))
        
        for i, (sequence_id, metric_value) in enumerate(top_combined):
            displacements = self.displacement_data[sequence_id]
            steps = range(1, len(displacements) + 1)
            ax3.plot(steps, displacements, marker='o', label=f'{sequence_id} ({metric_value:.4f})',
                    color=colors[i])
        
        ax3.set_xlabel('Assembly Step')
        ax3.set_ylabel('Displacement')
        ax3.set_title('Top 5 Sequences by Combined Metric')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Optimal sequence visualization
        ax4 = fig.add_subplot(gs[2, 0])
        
        # Get influence values for each rod in the sequence
        influence_values = [final_influence[rod] for rod in optimal_sequence]
        
        # Plot optimal sequence as step chart
        ax4.bar(range(len(optimal_sequence)), influence_values, color='skyblue')
        ax4.set_xlabel('Rod')
        ax4.set_ylabel('Influence Factor')
        ax4.set_title('Optimal Assembly Sequence')
        ax4.set_xticks(range(len(optimal_sequence)))
        ax4.set_xticklabels(optimal_sequence, rotation=45)
        ax4.grid(True, axis='y', alpha=0.3)
        
        # 5. Rod control value in optimal sequence
        ax5 = fig.add_subplot(gs[2, 1])
        
        x = list(range(1, len(optimal_sequence) + 1))
        y = [self.built_values.get(rod, 0) for rod in optimal_sequence]
        
        ax5.step(x, y, where='mid', marker='o', linestyle='-', linewidth=2)
        ax5.set_title('Control Value in Optimal Sequence')
        ax5.set_xlabel('Assembly Step')
        ax5.set_ylabel('Rod Control Value')
        ax5.grid(True, alpha=0.3)
        
        # Add rod labels
        for i, rod in enumerate(optimal_sequence):
            ax5.text(i + 1, y[i], rod, ha='center', va='bottom')
        
        plt.tight_layout()
        return fig

# Example usage
def run_demonstration(tags_data=None, displacement_data=None, built_values=None):
    """
    Run a demonstration of the optimizer with visualizations.
    
    Parameters:
    - tags_data: Dictionary mapping sequence IDs to assembly sequences
    - displacement_data: Dictionary mapping sequence IDs to displacement values at each step
    - built_values: Dictionary mapping rods to their ease-of-control scores
    
    Returns:
    - Optimizer instance
    - Optimal sequence
    """
    # Use provided data or default to S3 data
    if tags_data is None:
        tags_data = tags_data_3
    if displacement_data is None:
        displacement_data = data_3
    if built_values is None:
        built_values = built_values_3
    
    # Initialize optimizer
    optimizer = BendingActiveOptimizer(tags_data, displacement_data, built_values)
    
    # Get and display optimal sequence
    optimal_sequence = optimizer.predict_optimal_sequence()
    print("Optimal Assembly Sequence:")
    for i, rod in enumerate(optimal_sequence):
        print(f"{i+1}. {rod} (Control Value: {built_values.get(rod, 0):.3f})")
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # Comprehensive analysis dashboard
    fig_comprehensive = optimizer.visualize_comprehensive_analysis()
    plt.figure(fig_comprehensive.number)
    plt.savefig("comprehensive_analysis.png", dpi=300, bbox_inches='tight')
    
    # Metrics comparison
    fig_metrics = optimizer.visualize_metrics_comparison()
    plt.figure(fig_metrics.number)
    plt.savefig("metrics_comparison.png", dpi=300, bbox_inches='tight')
    
    # Top sequences
    fig_top_seq = optimizer.visualize_top_sequences(metric_type='combined', n=5)
    plt.figure(fig_top_seq.number)
    plt.savefig("top_sequences_combined.png", dpi=300, bbox_inches='tight')
    
    # Final influence
    fig_influence = optimizer.visualize_final_influence()
    plt.figure(fig_influence.number)
    plt.savefig("final_influence.png", dpi=300, bbox_inches='tight')
    
    # Optimal sequence
    fig_optimal = optimizer.visualize_optimal_sequence()
    plt.figure(fig_optimal.number)
    plt.savefig("optimal_sequence.png", dpi=300, bbox_inches='tight')
    
    print("\nVisualization complete! All figures have been saved.")
    
    # Show plots
    plt.show()
    
    # Return optimizer and optimal sequence
    return optimizer, optimal_sequence

# Run the demonstration if this script is executed directly
if __name__ == "__main__":
    try:
        optimizer, optimal_sequence = run_demonstration()
    except NameError as e:
        print(f"Error: {e}")
        print("Could not run demonstration due to missing data. Please check your data files.")