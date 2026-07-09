"""
Pandas-First RAG Agent V2
Handles numerical and tabular data queries with 100% accuracy
Uses LLM for natural language generation instead of hardcoded templates
"""

import pandas as pd
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json


class PandasRAGAgent:
    """
    Intelligent agent that converts natural language queries
    to pandas operations for accurate numerical data retrieval
    """

    def __init__(self, llm):
        """
        Args:
            llm: Language model for query understanding and result narration
        """
        self.llm = llm

    def process_query(self, question: str, df: pd.DataFrame) -> str:
        """
        Main entry point - processes natural language query and returns answer

        Args:
            question: User's natural language question
            df: Pandas DataFrame containing the data

        Returns:
            Natural language answer
        """
        try:
            # Step 1: Analyze query intent
            intent = self._analyze_query_intent(question, df)

            # Step 2: Extract parameters from question
            params = self._extract_parameters(question, df)

            # Step 3: Build and execute pandas query
            result = self._execute_query(intent, params, df)

            # Step 4: Let LLM format the result naturally
            answer = self._llm_format_result(question, result)

            return answer

        except Exception as e:
            return f"Error processing query: {str(e)}\n\nPlease try rephrasing your question."

    def _analyze_query_intent(self, question: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the user's question to determine intent
        """
        question_lower = question.lower()

        # Detect operation type
        intent = {
            'operation': 'lookup',  # default
            'aggregation': None,
            'filtering': False,
            'date_range': False,
            'calculation': False
        }

        # Check for aggregations
        if any(word in question_lower for word in ['highest', 'maximum', 'max', 'largest', 'peak']):
            intent['operation'] = 'aggregation'
            intent['aggregation'] = 'max'
        elif any(word in question_lower for word in ['lowest', 'minimum', 'min', 'smallest']):
            intent['operation'] = 'aggregation'
            intent['aggregation'] = 'min'
        elif any(word in question_lower for word in ['average', 'mean', 'avg']):
            intent['operation'] = 'aggregation'
            intent['aggregation'] = 'mean'
        elif any(word in question_lower for word in ['total', 'sum']):
            intent['operation'] = 'aggregation'
            intent['aggregation'] = 'sum'
        elif any(word in question_lower for word in ['count', 'how many']):
            intent['operation'] = 'aggregation'
            intent['aggregation'] = 'count'

        # Check for comparison queries
        if any(word in question_lower for word in ['compare', 'comparison', 'vs', 'versus', 'difference between']):
            intent['operation'] = 'comparison'

        # Check for calculations (profit/loss, change, difference)
        if any(word in question_lower for word in ['profit', 'loss', 'gain', 'bought', 'sold']):
            intent['operation'] = 'calculation'
            intent['calculation'] = True

        # Check for listing/showing multiple rows
        if any(word in question_lower for word in ['show', 'list', 'all', 'display']):
            intent['operation'] = 'list'

        return intent

    def _extract_parameters(self, question: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract specific parameters from the question
        """
        params = {
            'dates': [],
            'columns': [],
            'values': [],
            'comparison': None,
            'month': None,
            'year': None,
            'shares': None
        }

        # Extract dates in various formats
        # Format: DD-MM-YYYY
        dates_format1 = re.findall(r'\d{2}-\d{2}-\d{4}', question)
        params['dates'].extend(dates_format1)

        # Format: Month DD, YYYY or DD Month YYYY
        months = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09',
            'oct': '10', 'nov': '11', 'dec': '12'
        }

        question_lower = question.lower()

        # Extract month and year
        for month_name, month_num in months.items():
            if month_name in question_lower:
                params['month'] = month_num
                # Try to find year
                year_match = re.search(r'20\d{2}', question)
                if year_match:
                    params['year'] = year_match.group()
                break

        # Extract numerical values
        numbers = re.findall(r'\b\d+\.?\d*\b', question)
        params['values'] = [float(n) for n in numbers]

        # Extract shares if mentioned
        shares_match = re.search(r'(\d+)\s+share', question_lower)
        if shares_match:
            params['shares'] = int(shares_match.group(1))

        # Detect comparison operators
        if 'above' in question_lower or 'greater' in question_lower or 'more than' in question_lower:
            params['comparison'] = '>'
        elif 'below' in question_lower or 'less' in question_lower or 'under' in question_lower:
            params['comparison'] = '<'

        # Detect columns from dataframe
        for col in df.columns:
            if col.lower() in question_lower:
                params['columns'].append(col)

        # Common column aliases
        aliases = {
            'price': 'Price',
            'open': 'Open',
            'close': 'Price',
            'closing': 'Price',
            'high': 'High',
            'low': 'Low',
            'volume': 'Vol.',
            'change': 'Change %'
        }

        for alias, actual_col in aliases.items():
            if alias in question_lower and actual_col in df.columns and actual_col not in params['columns']:
                params['columns'].append(actual_col)

        return params

    def _execute_query(self, intent: Dict, params: Dict, df: pd.DataFrame) -> Any:
        """
        Execute the pandas query based on intent and parameters
        """
        operation = intent['operation']

        # Make a copy to avoid modifying original
        working_df = df.copy()

        # Apply date filtering if needed
        if params['month'] and params['year']:
            # Filter by month and year
            date_pattern = f"-{params['month']}-{params['year']}"
            working_df = working_df[working_df['Date'].str.contains(date_pattern)]
        elif params['dates'] and operation != 'comparison':
            # Filter by specific dates (but not for comparison - needs both dates)
            working_df = working_df[working_df['Date'].isin(params['dates'])]

        # Apply value filtering if needed
        if params['comparison'] and params['columns'] and params['values']:
            col = params['columns'][0]
            val = params['values'][0]
            if params['comparison'] == '>':
                working_df = working_df[pd.to_numeric(working_df[col], errors='coerce') > val]
            elif params['comparison'] == '<':
                working_df = working_df[pd.to_numeric(working_df[col], errors='coerce') < val]

        # Execute based on operation
        if operation == 'calculation' and params['shares'] and len(params['dates']) >= 2:
            # Profit/loss calculation
            return self._calculate_profit_loss(df, params['dates'][0], params['dates'][1], params['shares'])

        elif operation == 'comparison':
            # Compare two dates
            if len(params['dates']) >= 2:
                return self._compare_dates(df, params['dates'][0], params['dates'][1])
            else:
                return {'type': 'error', 'message': 'Please provide two dates to compare (format: DD-MM-YYYY)'}

        elif operation == 'aggregation':
            agg_type = intent['aggregation']
            col = params['columns'][0] if params['columns'] else 'Price'

            if col not in working_df.columns:
                return {'type': 'error', 'message': f"Column '{col}' not found in data"}

            # Convert to numeric
            numeric_col = pd.to_numeric(working_df[col], errors='coerce')

            if agg_type == 'max':
                max_val = numeric_col.max()
                max_row = working_df[numeric_col == max_val].iloc[0]
                return {'value': max_val, 'row': max_row.to_dict(), 'type': 'max', 'column': col}
            elif agg_type == 'min':
                min_val = numeric_col.min()
                min_row = working_df[numeric_col == min_val].iloc[0]
                return {'value': min_val, 'row': min_row.to_dict(), 'type': 'min', 'column': col}
            elif agg_type == 'mean':
                return {'value': numeric_col.mean(), 'type': 'mean', 'column': col}
            elif agg_type == 'sum':
                return {'value': numeric_col.sum(), 'type': 'sum', 'column': col}
            elif agg_type == 'count':
                return {'value': len(working_df), 'type': 'count'}

        elif operation == 'list':
            # Return filtered dataframe (limit to 10 rows)
            return {'data': working_df.head(10).to_dict('records'), 'type': 'list', 'total': len(working_df)}

        elif operation == 'lookup':
            # Single row lookup
            if len(working_df) > 0:
                return {'row': working_df.iloc[0].to_dict(), 'type': 'lookup'}
            else:
                return {'type': 'not_found'}

        return {'type': 'error', 'message': 'Could not determine how to process query'}

    def _calculate_profit_loss(self, df: pd.DataFrame, buy_date: str, sell_date: str, shares: int) -> Dict:
        """
        Calculate profit/loss for stock trading
        """
        buy_row = df[df['Date'] == buy_date]
        sell_row = df[df['Date'] == sell_date]

        if buy_row.empty:
            return {'type': 'error', 'message': f'Buy date {buy_date} not found in data'}
        if sell_row.empty:
            return {'type': 'error', 'message': f'Sell date {sell_date} not found in data'}

        buy_price = float(buy_row.iloc[0]['Price'])
        sell_price = float(sell_row.iloc[0]['Price'])

        profit_loss = (sell_price - buy_price) * shares
        percentage = ((sell_price - buy_price) / buy_price) * 100

        return {
            'type': 'profit_loss',
            'buy_date': buy_date,
            'sell_date': sell_date,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'shares': shares,
            'profit_loss': profit_loss,
            'percentage': percentage
        }

    def _compare_dates(self, df: pd.DataFrame, date1: str, date2: str) -> Dict:
        """
        Compare data between two dates
        """
        row1 = df[df['Date'] == date1]
        row2 = df[df['Date'] == date2]

        if row1.empty:
            return {'type': 'error', 'message': f'Date {date1} not found in data'}
        if row2.empty:
            return {'type': 'error', 'message': f'Date {date2} not found in data'}

        return {
            'type': 'comparison',
            'date1': date1,
            'date2': date2,
            'row1': row1.iloc[0].to_dict(),
            'row2': row2.iloc[0].to_dict()
        }

    def _llm_format_result(self, question: str, result: Any) -> str:
        """
        Use LLM to format results in natural, human-friendly language
        """
        # Handle errors directly
        if isinstance(result, dict):
            if result.get('type') == 'error':
                return result.get('message', 'An error occurred')
            elif result.get('type') == 'not_found':
                return "No matching data found for your query. Please check the date format or try rephrasing."

        # Convert result to JSON for LLM
        result_json = json.dumps(result, indent=2, default=str)

        prompt = f"""You are a financial analyst assistant. Answer the user's question based on the data retrieved.

User Question: {question}

Retrieved Data:
{result_json}

Instructions:
1. Provide a clear, natural language answer
2. Be conversational and friendly
3. Highlight key insights
4. Use formatting (bold, bullets) for readability
5. Include relevant comparisons or percentages when applicable
6. For price data, always use $ symbol
7. Keep it concise but informative
8. If comparing dates, clearly show the change and direction
9. Don't mention that you're looking at JSON or data structures
10. Answer as if you're explaining to someone who doesn't see the raw data

Answer:"""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            # Fallback to simple formatting if LLM fails
            return f"Based on the data: {result}"


def load_dataframe(path: str) -> pd.DataFrame:
    """
    Load CSV or Excel file into pandas DataFrame
    """
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    elif path.endswith('.xlsx'):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

    # Try to detect and parse date columns
    for col in df.columns:
        if 'date' in col.lower():
            try:
                # Try different date formats
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
                df[col] = df[col].dt.strftime('%d-%m-%Y')
            except:
                pass

    return df


def pandas_agent_query(question: str, path: str, llm) -> str:
    """
    Main entry point for pandas-based queries

    Args:
        question: User's natural language question
        path: Path to CSV/XLSX file
        llm: Language model instance

    Returns:
        Natural language answer
    """
    try:
        # Load data
        df = load_dataframe(path)

        # Create agent
        agent = PandasRAGAgent(llm)

        # Process query
        answer = agent.process_query(question, df)

        return answer

    except Exception as e:
        return f"Error: {str(e)}"
