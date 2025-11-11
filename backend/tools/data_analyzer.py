"""
Data Analyzer Tool - Comprehensive data analysis, visualization, and insights
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import io
import base64
from datetime import datetime


class DataAnalyzer:
    """Analyze datasets and provide insights"""
    
    def __init__(self):
        self.loaded_datasets = {}  # Cache loaded datasets
        self.viz_dir = Path("uploads/visualizations")
        self.viz_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(
        self,
        file_path: str,
        file_type: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Load data from file
        
        Args:
            file_path: Path to data file
            file_type: 'csv', 'excel', 'json', 'parquet', or 'auto'
            **kwargs: Additional arguments for pandas read functions
        
        Returns:
            Dictionary with loaded data info
        """
        try:
            file_path = Path(file_path)
            
            # If path doesn't exist, try adding 'uploads/' prefix
            if not file_path.exists() and not file_path.is_absolute():
                alt_path = Path("uploads") / file_path
                if alt_path.exists():
                    file_path = alt_path
            
            # Check if file exists
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}. Make sure the file is uploaded and you are using the correct file path.'
                }
            
            # Auto-detect file type
            if file_type == "auto":
                suffix = file_path.suffix.lower()
                type_map = {
                    '.csv': 'csv',
                    '.xlsx': 'excel', '.xls': 'excel',
                    '.json': 'json',
                    '.parquet': 'parquet'
                }
                file_type = type_map.get(suffix, 'csv')
            
            # Load data
            if file_type == 'csv':
                df = pd.read_csv(file_path, **kwargs)
            elif file_type == 'excel':
                df = pd.read_excel(file_path, **kwargs)
            elif file_type == 'json':
                df = pd.read_json(file_path, **kwargs)
            elif file_type == 'parquet':
                df = pd.read_parquet(file_path, **kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_type}'
                }
            
            # Store in cache
            dataset_id = str(file_path)
            self.loaded_datasets[dataset_id] = df
            
            return {
                'success': True,
                'dataset_id': dataset_id,
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to load data: {str(e)}'
            }
    
    def get_basic_stats(self, dataset_id: str) -> Dict[str, Any]:
        """Get basic statistics for dataset"""
        if dataset_id not in self.loaded_datasets:
            return {'success': False, 'error': 'Dataset not loaded'}
        
        try:
            df = self.loaded_datasets[dataset_id]
            
            # Basic info
            info = {
                'success': True,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict()
            }
            
            # Missing values
            missing = df.isnull().sum()
            if missing.sum() > 0:
                info['missing_values'] = missing[missing > 0].to_dict()
                info['missing_percentage'] = (missing[missing > 0] / len(df) * 100).round(2).to_dict()
            else:
                info['missing_values'] = None
            
            # Numeric statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                stats = df[numeric_cols].describe().round(2)
                info['numeric_stats'] = stats.to_dict()
            
            # Categorical info
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(cat_cols) > 0:
                cat_info = {}
                for col in cat_cols[:10]:  # Limit to first 10 categorical columns
                    value_counts = df[col].value_counts()
                    cat_info[col] = {
                        'unique_values': len(value_counts),
                        'top_values': value_counts.head(5).to_dict()
                    }
                info['categorical_info'] = cat_info
            
            # Duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                info['duplicate_rows'] = int(duplicates)
            
            return info
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get statistics: {str(e)}'
            }
    
    def get_correlations(
        self,
        dataset_id: str,
        method: str = "pearson",
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Get correlations between numeric columns"""
        if dataset_id not in self.loaded_datasets:
            return {'success': False, 'error': 'Dataset not loaded'}
        
        try:
            df = self.loaded_datasets[dataset_id]
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.shape[1] < 2:
                return {
                    'success': False,
                    'error': 'Need at least 2 numeric columns for correlation'
                }
            
            # Calculate correlations
            corr_matrix = numeric_df.corr(method=method).round(3)
            
            # Find high correlations
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) >= threshold:
                        high_corr.append({
                            'col1': corr_matrix.columns[i],
                            'col2': corr_matrix.columns[j],
                            'correlation': float(corr_val)
                        })
            
            return {
                'success': True,
                'correlation_matrix': corr_matrix.to_dict(),
                'high_correlations': sorted(high_corr, key=lambda x: abs(x['correlation']), reverse=True)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to calculate correlations: {str(e)}'
            }
    
    def suggest_cleaning(self, dataset_id: str) -> Dict[str, Any]:
        """Suggest data cleaning operations"""
        if dataset_id not in self.loaded_datasets:
            return {'success': False, 'error': 'Dataset not loaded'}
        
        try:
            df = self.loaded_datasets[dataset_id]
            suggestions = []
            
            # Missing values
            missing = df.isnull().sum()
            if missing.sum() > 0:
                for col in missing[missing > 0].index:
                    pct = (missing[col] / len(df)) * 100
                    if pct > 50:
                        suggestions.append({
                            'type': 'missing_values',
                            'column': col,
                            'issue': f'{pct:.1f}% missing values',
                            'suggestion': 'Consider dropping this column or imputing with domain knowledge'
                        })
                    else:
                        suggestions.append({
                            'type': 'missing_values',
                            'column': col,
                            'issue': f'{pct:.1f}% missing values',
                            'suggestion': 'Impute with mean/median for numeric, mode for categorical'
                        })
            
            # Duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                suggestions.append({
                    'type': 'duplicates',
                    'issue': f'{duplicates} duplicate rows found',
                    'suggestion': 'Remove duplicates with df.drop_duplicates()'
                })
            
            # Outliers (numeric columns)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                if outliers > 0:
                    pct = (outliers / len(df)) * 100
                    if pct > 5:
                        suggestions.append({
                            'type': 'outliers',
                            'column': col,
                            'issue': f'{outliers} outliers ({pct:.1f}%)',
                            'suggestion': 'Investigate outliers - may need capping, transformation, or removal'
                        })
            
            # Data types
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Check if it could be datetime
                    try:
                        pd.to_datetime(df[col].head(100), errors='coerce')
                        if df[col].head(100).notna().sum() > 50:
                            suggestions.append({
                                'type': 'data_type',
                                'column': col,
                                'issue': 'Column appears to be datetime but stored as object',
                                'suggestion': f"Convert to datetime: df['{col}'] = pd.to_datetime(df['{col}'])"
                            })
                    except:
                        pass
            
            # Constant columns
            for col in df.columns:
                if df[col].nunique() == 1:
                    suggestions.append({
                        'type': 'constant_column',
                        'column': col,
                        'issue': 'Column has only one unique value',
                        'suggestion': 'Consider dropping this column as it provides no information'
                    })
            
            return {
                'success': True,
                'suggestions': suggestions,
                'total_issues': len(suggestions)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate suggestions: {str(e)}'
            }
    
    def generate_visualization(
        self,
        dataset_id: str,
        chart_type: str,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate visualization"""
        if dataset_id not in self.loaded_datasets:
            return {'success': False, 'error': 'Dataset not loaded'}
        
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            df = self.loaded_datasets[dataset_id]
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'histogram':
                if not x_col:
                    return {'success': False, 'error': 'x_col required for histogram'}
                plt.hist(df[x_col].dropna(), bins=kwargs.get('bins', 30), edgecolor='black')
                plt.xlabel(x_col)
                plt.ylabel('Frequency')
                plt.title(f'Distribution of {x_col}')
            
            elif chart_type == 'scatter':
                if not x_col or not y_col:
                    return {'success': False, 'error': 'x_col and y_col required for scatter'}
                plt.scatter(df[x_col], df[y_col], alpha=0.6)
                plt.xlabel(x_col)
                plt.ylabel(y_col)
                plt.title(f'{y_col} vs {x_col}')
            
            elif chart_type == 'boxplot':
                if not x_col:
                    return {'success': False, 'error': 'x_col required for boxplot'}
                df.boxplot(column=x_col)
                plt.ylabel(x_col)
                plt.title(f'Box Plot of {x_col}')
            
            elif chart_type == 'correlation_heatmap':
                numeric_df = df.select_dtypes(include=[np.number])
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', center=0)
                plt.title('Correlation Heatmap')
            
            elif chart_type == 'bar':
                if not x_col:
                    return {'success': False, 'error': 'x_col required for bar chart'}
                value_counts = df[x_col].value_counts().head(10)
                plt.bar(range(len(value_counts)), value_counts.values)
                plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')
                plt.xlabel(x_col)
                plt.ylabel('Count')
                plt.title(f'Top 10 {x_col} Values')
            
            else:
                return {'success': False, 'error': f'Unsupported chart type: {chart_type}'}
            
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{chart_type}_{timestamp}.png"
            filepath = self.viz_dir / filename
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            # Get relative path
            try:
                relative_path = str(filepath.relative_to(Path.cwd()))
            except ValueError:
                # If filepath is already relative
                relative_path = str(filepath)
            
            return {
                'success': True,
                'chart_type': chart_type,
                'filepath': str(filepath),
                'relative_path': relative_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate visualization: {str(e)}'
            }
    
    def query_data(
        self,
        dataset_id: str,
        query: str,
        query_type: str = "pandas"
    ) -> Dict[str, Any]:
        """Query data using pandas or SQL-like syntax"""
        if dataset_id not in self.loaded_datasets:
            return {'success': False, 'error': 'Dataset not loaded'}
        
        try:
            df = self.loaded_datasets[dataset_id]
            
            if query_type == "pandas":
                # Execute pandas query
                result = df.query(query)
            elif query_type == "sql":
                # Use pandasql for SQL queries
                try:
                    from pandasql import sqldf
                    result = sqldf(query, {'df': df})
                except ImportError:
                    return {
                        'success': False,
                        'error': 'pandasql not installed. Use pandas query instead.'
                    }
            else:
                return {'success': False, 'error': f'Unknown query type: {query_type}'}
            
            # Return results
            return {
                'success': True,
                'rows_returned': len(result),
                'columns': result.columns.tolist(),
                'data': result.head(100).to_dict('records'),  # Limit to 100 rows
                'preview': result.head(10).to_string()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Query failed: {str(e)}'
            }
    
    def generate_pandas_code(
        self,
        operation: str,
        dataset_id: str,
        **params
    ) -> Dict[str, Any]:
        """Generate pandas code for common operations"""
        if dataset_id not in self.loaded_datasets:
            return {'success': False, 'error': 'Dataset not loaded'}
        
        try:
            df = self.loaded_datasets[dataset_id]
            code_snippets = []
            
            if operation == "load_data":
                code_snippets.append(f"import pandas as pd")
                code_snippets.append(f"df = pd.read_csv('{params.get('filepath', 'data.csv')}')")
            
            elif operation == "handle_missing":
                col = params.get('column')
                method = params.get('method', 'drop')
                if method == 'drop':
                    code_snippets.append(f"df = df.dropna(subset=['{col}'])")
                elif method == 'mean':
                    code_snippets.append(f"df['{col}'].fillna(df['{col}'].mean(), inplace=True)")
                elif method == 'median':
                    code_snippets.append(f"df['{col}'].fillna(df['{col}'].median(), inplace=True)")
                elif method == 'mode':
                    code_snippets.append(f"df['{col}'].fillna(df['{col}'].mode()[0], inplace=True)")
            
            elif operation == "remove_outliers":
                col = params.get('column')
                code_snippets.append(f"Q1 = df['{col}'].quantile(0.25)")
                code_snippets.append(f"Q3 = df['{col}'].quantile(0.75)")
                code_snippets.append(f"IQR = Q3 - Q1")
                code_snippets.append(f"df = df[(df['{col}'] >= Q1 - 1.5*IQR) & (df['{col}'] <= Q3 + 1.5*IQR)]")
            
            elif operation == "group_aggregate":
                group_col = params.get('group_by')
                agg_col = params.get('agg_column')
                agg_func = params.get('agg_function', 'mean')
                code_snippets.append(f"df.groupby('{group_col}')['{agg_col}'].{agg_func}()")
            
            elif operation == "pivot":
                index = params.get('index')
                columns = params.get('columns')
                values = params.get('values')
                code_snippets.append(f"df.pivot_table(index='{index}', columns='{columns}', values='{values}')")
            
            elif operation == "merge":
                code_snippets.append(f"df1.merge(df2, on='{params.get('on', 'id')}', how='{params.get('how', 'inner')}')")
            
            else:
                return {'success': False, 'error': f'Unknown operation: {operation}'}
            
            return {
                'success': True,
                'operation': operation,
                'code': '\n'.join(code_snippets)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Code generation failed: {str(e)}'
            }


# Global instance
data_analyzer = DataAnalyzer()

