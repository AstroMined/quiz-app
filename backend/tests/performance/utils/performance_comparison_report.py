"""
Performance comparison report generator.

This module provides utilities for generating comprehensive performance
comparison reports between baseline and current performance measurements.
"""

import json
import argparse
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, Any, List, Tuple
from datetime import datetime


class PerformanceComparisonReport:
    """Generate comprehensive performance comparison reports."""
    
    def __init__(self, baseline_file: Path, current_file: Path):
        """Initialize with baseline and current performance data files."""
        self.baseline_file = baseline_file
        self.current_file = current_file
        self.baseline_data = self._load_json_file(baseline_file)
        self.current_data = self._load_json_file(current_file)
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON data from file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Performance data file not found: {file_path}")
        
        with open(file_path) as f:
            return json.load(f)
    
    def generate_comparison_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive comparison analysis."""
        comparison_data = {
            "comparison_metadata": {
                "timestamp": datetime.now().isoformat(),
                "baseline_file": str(self.baseline_file),
                "current_file": str(self.current_file),
                "baseline_timestamp": self.baseline_data.get("baseline_metadata", {}).get("timestamp"),
                "current_timestamp": self.current_data.get("comparison_metadata", {}).get("timestamp"),
            },
            "operation_comparisons": {},
            "summary_statistics": {}
        }
        
        operations = self.baseline_data["operations"].keys()
        
        for operation in operations:
            if operation in self.current_data["operations"]:
                comparison_data["operation_comparisons"][operation] = self._compare_operation(
                    operation,
                    self.baseline_data["operations"][operation],
                    self.current_data["operations"][operation]
                )
        
        comparison_data["summary_statistics"] = self._calculate_summary_statistics(
            comparison_data["operation_comparisons"]
        )
        
        return comparison_data
    
    def _compare_operation(self, operation: str, baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Compare performance metrics for a single operation."""
        baseline_duration = baseline["duration_stats"]["mean"]
        current_duration = current["duration_stats"]["mean"]
        baseline_queries = baseline["query_stats"]["mean"]
        current_queries = current["query_stats"]["mean"]
        
        # Calculate improvements
        duration_improvement = ((baseline_duration - current_duration) / baseline_duration) * 100
        query_reduction = ((baseline_queries - current_queries) / baseline_queries) * 100
        
        return {
            "operation": operation,
            "baseline_metrics": {
                "duration_ms": baseline_duration,
                "queries": baseline_queries,
                "iterations": baseline.get("iterations", 50)
            },
            "current_metrics": {
                "duration_ms": current_duration,
                "queries": current_queries,
                "iterations": current.get("iterations", 50)
            },
            "improvements": {
                "duration_improvement_percent": duration_improvement,
                "query_reduction_percent": query_reduction,
                "speedup_factor": baseline_duration / current_duration if current_duration > 0 else float('inf'),
                "queries_saved": baseline_queries - current_queries
            },
            "statistical_data": {
                "baseline_duration_std": baseline["duration_stats"]["std_dev"],
                "current_duration_std": current["duration_stats"]["std_dev"],
                "baseline_duration_range": (baseline["duration_stats"]["min"], baseline["duration_stats"]["max"]),
                "current_duration_range": (current["duration_stats"]["min"], current["duration_stats"]["max"])
            }
        }
    
    def _calculate_summary_statistics(self, operation_comparisons: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall summary statistics."""
        all_duration_improvements = [
            op["improvements"]["duration_improvement_percent"]
            for op in operation_comparisons.values()
        ]
        
        all_query_reductions = [
            op["improvements"]["query_reduction_percent"]
            for op in operation_comparisons.values()
        ]
        
        total_baseline_queries = sum(
            op["baseline_metrics"]["queries"]
            for op in operation_comparisons.values()
        )
        
        total_current_queries = sum(
            op["current_metrics"]["queries"]
            for op in operation_comparisons.values()
        )
        
        return {
            "overall_duration_improvement": {
                "mean": mean(all_duration_improvements),
                "std_dev": stdev(all_duration_improvements) if len(all_duration_improvements) > 1 else 0,
                "min": min(all_duration_improvements),
                "max": max(all_duration_improvements)
            },
            "overall_query_reduction": {
                "mean": mean(all_query_reductions),
                "std_dev": stdev(all_query_reductions) if len(all_query_reductions) > 1 else 0,
                "min": min(all_query_reductions),
                "max": max(all_query_reductions)
            },
            "total_database_load_reduction": {
                "baseline_total_queries": total_baseline_queries,
                "current_total_queries": total_current_queries,
                "total_queries_saved": total_baseline_queries - total_current_queries,
                "total_reduction_percent": ((total_baseline_queries - total_current_queries) / total_baseline_queries) * 100
            },
            "performance_targets_assessment": self._assess_performance_targets(operation_comparisons)
        }
    
    def _assess_performance_targets(self, operation_comparisons: Dict[str, Any]) -> Dict[str, Any]:
        """Assess performance against expected targets."""
        # Define expected targets
        single_fk_operations = ["user_creation", "question_creation", "group_creation"]
        multiple_fk_operations = ["user_response_creation", "leaderboard_creation"]
        
        # Single FK operations targets
        single_fk_query_reductions = [
            operation_comparisons[op]["improvements"]["query_reduction_percent"]
            for op in single_fk_operations if op in operation_comparisons
        ]
        single_fk_duration_improvements = [
            operation_comparisons[op]["improvements"]["duration_improvement_percent"]
            for op in single_fk_operations if op in operation_comparisons
        ]
        
        # Multiple FK operations targets
        multiple_fk_query_reductions = [
            operation_comparisons[op]["improvements"]["query_reduction_percent"]
            for op in multiple_fk_operations if op in operation_comparisons
        ]
        multiple_fk_duration_improvements = [
            operation_comparisons[op]["improvements"]["duration_improvement_percent"]
            for op in multiple_fk_operations if op in operation_comparisons
        ]
        
        return {
            "single_fk_operations": {
                "query_reduction_target": 50.0,
                "query_reduction_actual": min(single_fk_query_reductions) if single_fk_query_reductions else 0,
                "query_reduction_met": min(single_fk_query_reductions) >= 50.0 if single_fk_query_reductions else False,
                "duration_improvement_target": 45.0,
                "duration_improvement_actual": min(single_fk_duration_improvements) if single_fk_duration_improvements else 0,
                "duration_improvement_met": min(single_fk_duration_improvements) >= 45.0 if single_fk_duration_improvements else False
            },
            "multiple_fk_operations": {
                "query_reduction_target": 55.0,
                "query_reduction_actual": min(multiple_fk_query_reductions) if multiple_fk_query_reductions else 0,
                "query_reduction_met": min(multiple_fk_query_reductions) >= 55.0 if multiple_fk_query_reductions else False,
                "duration_improvement_target": 56.0,
                "duration_improvement_actual": min(multiple_fk_duration_improvements) if multiple_fk_duration_improvements else 0,
                "duration_improvement_met": min(multiple_fk_duration_improvements) >= 56.0 if multiple_fk_duration_improvements else False
            },
            "overall_targets": {
                "average_query_reduction_target": 53.0,
                "average_query_reduction_actual": mean([op["improvements"]["query_reduction_percent"] for op in operation_comparisons.values()]),
                "average_query_reduction_met": mean([op["improvements"]["query_reduction_percent"] for op in operation_comparisons.values()]) >= 53.0,
                "average_duration_improvement_target": 51.0,
                "average_duration_improvement_actual": mean([op["improvements"]["duration_improvement_percent"] for op in operation_comparisons.values()]),
                "average_duration_improvement_met": mean([op["improvements"]["duration_improvement_percent"] for op in operation_comparisons.values()]) >= 51.0
            }
        }
    
    def generate_formatted_report(self) -> str:
        """Generate formatted text report."""
        comparison_data = self.generate_comparison_analysis()
        
        report = []
        report.append("=" * 80)
        report.append("VALIDATION SERVICE REMOVAL PERFORMANCE IMPACT REPORT")
        report.append("=" * 80)
        
        # Metadata
        report.append(f"\nReport Generated: {comparison_data['comparison_metadata']['timestamp']}")
        report.append(f"Baseline Data: {comparison_data['comparison_metadata']['baseline_timestamp']}")
        report.append(f"Current Data: {comparison_data['comparison_metadata']['current_timestamp']}")
        
        # Operation-by-operation comparison
        report.append(f"\n{'='*80}")
        report.append("OPERATION-BY-OPERATION COMPARISON")
        report.append(f"{'='*80}")
        
        report.append(f"{'Operation':<25} {'Baseline':<15} {'Current':<15} {'Improvement':<15} {'Queries':<15}")
        report.append("-" * 85)
        
        for operation, data in comparison_data["operation_comparisons"].items():
            baseline_ms = data["baseline_metrics"]["duration_ms"]
            current_ms = data["current_metrics"]["duration_ms"]
            improvement = data["improvements"]["duration_improvement_percent"]
            baseline_q = data["baseline_metrics"]["queries"]
            current_q = data["current_metrics"]["queries"]
            
            report.append(f"{operation.replace('_', ' ').title():<25} "
                         f"{baseline_ms:<15.2f} "
                         f"{current_ms:<15.2f} "
                         f"{improvement:<15.1f}% "
                         f"{baseline_q}→{current_q} ({data['improvements']['query_reduction_percent']:.1f}%)")
        
        # Summary statistics
        summary = comparison_data["summary_statistics"]
        report.append(f"\n{'='*80}")
        report.append("PERFORMANCE SUMMARY")
        report.append(f"{'='*80}")
        
        report.append(f"Average Duration Improvement: {summary['overall_duration_improvement']['mean']:.1f}%")
        report.append(f"Average Query Reduction: {summary['overall_query_reduction']['mean']:.1f}%")
        report.append(f"Total Database Load Reduction: {summary['total_database_load_reduction']['total_reduction_percent']:.1f}%")
        report.append(f"Total Queries Saved: {summary['total_database_load_reduction']['total_queries_saved']}")
        
        # Performance targets assessment
        targets = summary["performance_targets_assessment"]
        report.append(f"\n{'='*80}")
        report.append("PERFORMANCE TARGETS ASSESSMENT")
        report.append(f"{'='*80}")
        
        # Single FK operations
        single_fk = targets["single_fk_operations"]
        report.append(f"\nSingle FK Operations:")
        report.append(f"  Query Reduction: {single_fk['query_reduction_actual']:.1f}% (Target: ≥{single_fk['query_reduction_target']:.1f}%) {'✅' if single_fk['query_reduction_met'] else '❌'}")
        report.append(f"  Duration Improvement: {single_fk['duration_improvement_actual']:.1f}% (Target: ≥{single_fk['duration_improvement_target']:.1f}%) {'✅' if single_fk['duration_improvement_met'] else '❌'}")
        
        # Multiple FK operations
        multiple_fk = targets["multiple_fk_operations"]
        report.append(f"\nMultiple FK Operations:")
        report.append(f"  Query Reduction: {multiple_fk['query_reduction_actual']:.1f}% (Target: ≥{multiple_fk['query_reduction_target']:.1f}%) {'✅' if multiple_fk['query_reduction_met'] else '❌'}")
        report.append(f"  Duration Improvement: {multiple_fk['duration_improvement_actual']:.1f}% (Target: ≥{multiple_fk['duration_improvement_target']:.1f}%) {'✅' if multiple_fk['duration_improvement_met'] else '❌'}")
        
        # Overall targets
        overall = targets["overall_targets"]
        report.append(f"\nOverall Performance:")
        report.append(f"  Average Query Reduction: {overall['average_query_reduction_actual']:.1f}% (Target: ≥{overall['average_query_reduction_target']:.1f}%) {'✅' if overall['average_query_reduction_met'] else '❌'}")
        report.append(f"  Average Duration Improvement: {overall['average_duration_improvement_actual']:.1f}% (Target: ≥{overall['average_duration_improvement_target']:.1f}%) {'✅' if overall['average_duration_improvement_met'] else '❌'}")
        
        # Conclusion
        all_targets_met = all([
            single_fk['query_reduction_met'],
            single_fk['duration_improvement_met'],
            multiple_fk['query_reduction_met'],
            multiple_fk['duration_improvement_met'],
            overall['average_query_reduction_met'],
            overall['average_duration_improvement_met']
        ])
        
        report.append(f"\n{'='*80}")
        if all_targets_met:
            report.append("✅ VALIDATION SERVICE REMOVAL SUCCESSFUL")
            report.append("✅ ALL PERFORMANCE TARGETS MET OR EXCEEDED")
        else:
            report.append("⚠️ VALIDATION SERVICE REMOVAL PERFORMANCE REVIEW NEEDED")
            report.append("⚠️ SOME PERFORMANCE TARGETS NOT MET")
        report.append(f"{'='*80}")
        
        return "\n".join(report)
    
    def save_report(self, output_file: Path, format: str = "both"):
        """Save report to file(s)."""
        if format in ["json", "both"]:
            comparison_data = self.generate_comparison_analysis()
            json_file = output_file.with_suffix(".json")
            with open(json_file, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            print(f"JSON report saved to: {json_file}")
        
        if format in ["text", "both"]:
            formatted_report = self.generate_formatted_report()
            text_file = output_file.with_suffix(".txt")
            with open(text_file, 'w') as f:
                f.write(formatted_report)
            print(f"Text report saved to: {text_file}")
    
    def print_report(self):
        """Print formatted report to console."""
        print(self.generate_formatted_report())


def main():
    """Command-line interface for generating performance comparison reports."""
    parser = argparse.ArgumentParser(
        description="Generate performance comparison report for validation service removal"
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to baseline performance data JSON file"
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Path to current performance data JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (without extension)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text", "both"],
        default="both",
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print report to console"
    )
    
    args = parser.parse_args()
    
    # Create report generator
    report_generator = PerformanceComparisonReport(args.baseline, args.current)
    
    # Print to console if requested
    if args.print:
        report_generator.print_report()
    
    # Save to file if output specified
    if args.output:
        report_generator.save_report(args.output, args.format)


if __name__ == "__main__":
    main()