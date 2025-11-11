"""
Data Analyzer Tool Integration for LLM Function Calling
"""
from typing import Dict, Any, Optional, List
import json

from backend.tools.data_analyzer import data_analyzer


def analyze_dataset(
    file_path: str,
    analysis_type: str = "basic_stats",
    **kwargs
) -> str:
    """
    Analyze a dataset (CSV, Excel, JSON) and provide insights
    
    Args:
        file_path: Path to the data file (relative to uploads/ or absolute)
        analysis_type: Type of analysis ('basic_stats', 'correlations', 'cleaning_suggestions', 'query')
        **kwargs: Additional parameters based on analysis_type
    
    Returns:
        JSON string with analysis results
    """
    try:
        # Load data if not already loaded
        load_result = data_analyzer.load_data(file_path)
        
        if not load_result['success']:
            return json.dumps(load_result)
        
        dataset_id = load_result['dataset_id']
        
        # Perform requested analysis
        if analysis_type == "basic_stats":
            result = data_analyzer.get_basic_stats(dataset_id)
            result['data_shape'] = load_result['shape']
            result['columns'] = load_result['columns']
        
        elif analysis_type == "correlations":
            threshold = kwargs.get('threshold', 0.5)
            method = kwargs.get('method', 'pearson')
            result = data_analyzer.get_correlations(dataset_id, method, threshold)
        
        elif analysis_type == "cleaning_suggestions":
            result = data_analyzer.suggest_cleaning(dataset_id)
        
        elif analysis_type == "query":
            query = kwargs.get('query')
            if not query:
                return json.dumps({
                    'success': False,
                    'error': 'query parameter required for query analysis'
                })
            query_type = kwargs.get('query_type', 'pandas')
            result = data_analyzer.query_data(dataset_id, query, query_type)
        
        else:
            return json.dumps({
                'success': False,
                'error': f'Unknown analysis type: {analysis_type}'
            })
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        })


def create_visualization(
    file_path: str,
    chart_type: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    **kwargs
) -> str:
    """
    Create visualizations from dataset
    
    Args:
        file_path: Path to the data file
        chart_type: Type of chart ('histogram', 'scatter', 'boxplot', 'correlation_heatmap', 'bar')
        x_column: Column name for X-axis
        y_column: Column name for Y-axis (for scatter plots)
        **kwargs: Additional chart parameters
    
    Returns:
        JSON string with visualization path
    """
    try:
        # Load data
        load_result = data_analyzer.load_data(file_path)
        
        if not load_result['success']:
            return json.dumps(load_result)
        
        dataset_id = load_result['dataset_id']
        
        # Generate visualization
        result = data_analyzer.generate_visualization(
            dataset_id=dataset_id,
            chart_type=chart_type,
            x_col=x_column,
            y_col=y_column,
            **kwargs
        )
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f'Visualization failed: {str(e)}'
        })


def generate_code(
    operation: str,
    file_path: Optional[str] = None,
    **params
) -> str:
    """
    Generate pandas code for data operations
    
    Args:
        operation: Operation type ('load_data', 'handle_missing', 'remove_outliers', 'group_aggregate', 'pivot', 'merge')
        file_path: Path to dataset (if needed)
        **params: Parameters for the operation
    
    Returns:
        JSON string with generated code
    """
    try:
        if file_path:
            load_result = data_analyzer.load_data(file_path)
            if not load_result['success']:
                return json.dumps(load_result)
            dataset_id = load_result['dataset_id']
        else:
            dataset_id = "default"
        
        result = data_analyzer.generate_pandas_code(operation, dataset_id, **params)
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f'Code generation failed: {str(e)}'
        })


# Tool definitions for LLM function calling
DATA_ANALYZER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_dataset",
            "description": "Analyze CSV, Excel, or JSON datasets. Get statistics, correlations, missing values, data quality issues, and insights. Use this when user uploads data files or asks about data analysis. IMPORTANT: Use the 'File path for analysis' from the attached files context as the file_path parameter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the data file. Use the 'File path for analysis' from the attached files context (e.g., '1/2025/11/data.csv' or 'uploads/1/2025/11/data.csv')"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["basic_stats", "correlations", "cleaning_suggestions", "query"],
                        "description": "Type of analysis: basic_stats (descriptive stats), correlations (relationships), cleaning_suggestions (data quality), query (filter/aggregate data)",
                        "default": "basic_stats"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Correlation threshold (for correlations analysis, default: 0.5)",
                        "default": 0.5
                    },
                    "method": {
                        "type": "string",
                        "enum": ["pearson", "spearman", "kendall"],
                        "description": "Correlation method (default: pearson)",
                        "default": "pearson"
                    },
                    "query": {
                        "type": "string",
                        "description": "Pandas query string (for query analysis, e.g., 'age > 25 and salary < 50000')"
                    },
                    "query_type": {
                        "type": "string",
                        "enum": ["pandas", "sql"],
                        "description": "Query language (default: pandas)",
                        "default": "pandas"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_visualization",
            "description": "Create charts and visualizations from datasets (histograms, scatter plots, box plots, correlation heatmaps, bar charts). Use when user asks to visualize data or create charts. IMPORTANT: Use the 'File path for analysis' from the attached files context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the data file"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["histogram", "scatter", "boxplot", "correlation_heatmap", "bar"],
                        "description": "Type of chart to create"
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Column name for X-axis"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Column name for Y-axis (required for scatter plots)"
                    },
                    "bins": {
                        "type": "integer",
                        "description": "Number of bins for histogram (default: 30)",
                        "default": 30
                    }
                },
                "required": ["file_path", "chart_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_pandas_code",
            "description": "Generate pandas code for data operations (loading, cleaning, aggregating, pivoting, merging). Use when user asks how to do something in pandas or wants code examples.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["load_data", "handle_missing", "remove_outliers", "group_aggregate", "pivot", "merge"],
                        "description": "Type of operation to generate code for"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to dataset (optional, for context)"
                    },
                    "column": {
                        "type": "string",
                        "description": "Column name (for operations on specific columns)"
                    },
                    "method": {
                        "type": "string",
                        "description": "Method for operation (e.g., 'mean', 'median', 'mode' for handle_missing)"
                    },
                    "group_by": {
                        "type": "string",
                        "description": "Column to group by (for group_aggregate)"
                    },
                    "agg_column": {
                        "type": "string",
                        "description": "Column to aggregate (for group_aggregate)"
                    },
                    "agg_function": {
                        "type": "string",
                        "description": "Aggregation function like 'mean', 'sum', 'count' (for group_aggregate)"
                    }
                },
                "required": ["operation"]
            }
        }
    }
]


def get_data_analyzer_tools(enabled: bool = True) -> Optional[List[Dict]]:
    """Get data analyzer tools if enabled"""
    return DATA_ANALYZER_TOOLS if enabled else None


def execute_data_analyzer_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Execute a data analyzer tool by name"""
    if tool_name == "analyze_dataset":
        return analyze_dataset(**tool_input)
    elif tool_name == "create_visualization":
        return create_visualization(**tool_input)
    elif tool_name == "generate_pandas_code":
        return generate_code(**tool_input)
    else:
        return json.dumps({
            'success': False,
            'error': f'Unknown tool: {tool_name}'
        })

