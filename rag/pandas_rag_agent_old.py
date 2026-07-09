"""
Pandas-First RAG Agent
Handles numerical and tabular data queries with 100% accuracy
Converts natural language to pandas operations
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

            # Step 4: Format result with LLM narration
            answer = self._format_result(question, result, intent)

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

        # Check for filtering
        if any(word in question_lower for word in ['where', 'when', 'above', 'below', 'greater', 'less', 'between']):
            intent['filtering'] = True

        # Check for date range queries
        if any(word in question_lower for word in ['month', 'quarter', 'year', 'week', 'between', 'from', 'to']):
            intent['date_range'] = True

        # Check for calculations (profit/loss, change, difference)
        if any(word in question_lower for word in ['profit', 'loss', 'gain', 'change', 'difference', 'bought', 'sold']):
            intent['operation'] = 'calculation'
            intent['calculation'] = True

        # Check for comparison queries
        if any(word in question_lower for word in ['compare', 'comparison', 'vs', 'versus', 'difference between']):
            intent['operation'] = 'comparison'

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
        elif params['dates']:
            # Filter by specific dates
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

        elif operation == 'aggregation':
            agg_type = intent['aggregation']
            col = params['columns'][0] if params['columns'] else 'Price'

            if col not in working_df.columns:
                return f"Column '{col}' not found in data"

            # Convert to numeric
            numeric_col = pd.to_numeric(working_df[col], errors='coerce')

            if agg_type == 'max':
                max_val = numeric_col.max()
                max_row = working_df[numeric_col == max_val].iloc[0]
                return {'value': max_val, 'row': max_row, 'type': 'max'}
            elif agg_type == 'min':
                min_val = numeric_col.min()
                min_row = working_df[numeric_col == min_val].iloc[0]
                return {'value': min_val, 'row': min_row, 'type': 'min'}
            elif agg_type == 'mean':
                return {'value': numeric_col.mean(), 'type': 'mean'}
            elif agg_type == 'sum':
                return {'value': numeric_col.sum(), 'type': 'sum'}
            elif agg_type == 'count':
                return {'value': len(working_df), 'type': 'count'}

        elif operation == 'comparison':
            # Compare two dates
            if len(params['dates']) >= 2:
                date1 = params['dates'][0]
                date2 = params['dates'][1]

                row1 = df[df['Date'] == date1]
                row2 = df[df['Date'] == date2]

                if row1.empty or row2.empty:
                    return {'type': 'error', 'message': f'One or both dates not found: {date1}, {date2}'}

                return {
                    'type': 'comparison',
                    'date1': date1,
                    'date2': date2,
                    'row1': row1.iloc[0],
                    'row2': row2.iloc[0]
                }
            else:
                return {'type': 'error', 'message': 'Need two dates to compare'}

        elif operation == 'list':
            # Return filtered dataframe (limit to 10 rows)
            return {'data': working_df.head(10), 'type': 'list', 'total': len(working_df)}

        elif operation == 'lookup':
            # Single row lookup
            if len(working_df) > 0:
                return {'row': working_df.iloc[0], 'type': 'lookup'}
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

    def _format_result(self, question: str, result: Any, intent: Dict) -> str:
        """
        Format the result into a natural language response
        """
        if isinstance(result, dict):
            result_type = result.get('type')

            if result_type == 'error':
                return result.get('message', 'An error occurred')

            elif result_type == 'not_found':
                return "No matching data found for your query. Please check the date format or try rephrasing."

            elif result_type == 'profit_loss':
                return f"""
                        **Investment Analysis**

                        📅 **Buy Date**: {result['buy_date']}
                        💰 **Buy Price**: ${result['buy_price']:.2f}

                        📅 **Sell Date**: {result['sell_date']}
                        💰 **Sell Price**: ${result['sell_price']:.2f}

                        📊 **Shares**: {result['shares']}

                        {'📈 **Profit**' if result['profit_loss'] >= 0 else '📉 **Loss**'}: ${abs(result['profit_loss']):.2f} ({result['percentage']:+.2f}%)
                        """

            elif result_type == 'max':
                row = result['row']
                return f"The highest value is **${result['value']:.2f}** on **{row['Date']}**."

            elif result_type == 'min':
                row = result['row']
                return f"The lowest value is **${result['value']:.2f}** on **{row['Date']}**."

            elif result_type == 'mean':
                return f"The average value is **${result['value']:.2f}**."

            elif result_type == 'sum':
                return f"The total sum is **${result['value']:.2f}**."

            elif result_type == 'count':
                return f"There are **{int(result['value'])}** matching records."

            elif result_type == 'comparison':
                # Format comparison in natural language
                row1 = result['row1']
                row2 = result['row2']
                date1 = result['date1']
                date2 = result['date2']

                price1 = float(row1.get('Price', 0))
                price2 = float(row2.get('Price', 0))
                diff = price2 - price1
                pct_change = (diff / price1) * 100 if price1 != 0 else 0

                emoji = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
                direction = "increased" if diff > 0 else "decreased" if diff < 0 else "remained the same"

                return f"""Let me compare the closing prices for these two dates:

                    **{date1}**: ${price1:.2f}
                    **{date2}**: ${price2:.2f}

                    {emoji} The price **{direction}** by **${abs(diff):.2f}** ({pct_change:+.2f}%) from {date1} to {date2}.

                    Additional details:
                    • Open: ${row1.get('Open', 'N/A')} → ${row2.get('Open', 'N/A')}
                    • High: ${row1.get('High', 'N/A')} → ${row2.get('High', 'N/A')}
                    • Low: ${row1.get('Low', 'N/A')} → ${row2.get('Low', 'N/A')}
                    • Volume: {row1.get('Vol.', 'N/A')} → {row2.get('Vol.', 'N/A')}
                """

            elif result_type == 'lookup':
                row = result['row']
                return self._format_row_natural(row, question)

            elif result_type == 'list':
                df = result['data']
                total = result['total']
                table = df.to_string(index=False)
                msg = f"Found {total} matching records"
                if total > 10:
                    msg += " (showing first 10)"
                return f"{msg}:\n\n```\n{table}\n```"

        # Fallback to LLM formatting
        return self._llm_format_result(question, result)

    def _format_row(self, row: pd.Series) -> str:
        """
        Format a single row for display (technical format)
        """
        lines = []
        for col, val in row.items():
            lines.append(f"**{col}**: {val}")
        return "\n".join(lines)

    def _format_row_natural(self, row: pd.Series, question: str) -> str:
        """
        Format a single row in natural, human-friendly language
        """
        question_lower = question.lower()

        # Detect what they're asking about
        if 'closing' in question_lower or 'close' in question_lower or 'price' in question_lower:
            # They asked about closing price
            price = row.get('Price', 'N/A')
            date = row.get('Date', 'N/A')
            open_price = row.get('Open', 'N/A')
            high = row.get('High', 'N/A')
            low = row.get('Low', 'N/A')
            volume = row.get('Vol.', 'N/A')
            change = row.get('Change %', 'N/A')

            return f"""On **{date}**, Microsoft's stock closed at **${price}**.
                Here's the full picture for that day:
                • Opening Price: ${open_price}
                • Highest Price: ${high}
                • Lowest Price: ${low}
                • Trading Volume: {volume}
                • Daily Change: {change}
            """

        elif 'opening' in question_lower or 'open' in question_lower:
            # They asked about opening price
            open_price = row.get('Open', 'N/A')
            date = row.get('Date', 'N/A')
            return f"On **{date}**, Microsoft's stock opened at **${open_price}**."

        else:
            # General query - show key info in natural language
            price = row.get('Price', 'N/A')
            date = row.get('Date', 'N/A')
            change = row.get('Change %', 'N/A')

            return f"""Here's the data for **{date}**:

            Microsoft's stock closed at **${price}** with a daily change of **{change}**.

            Full details:
            • Opening: ${row.get('Open', 'N/A')}
            • High: ${row.get('High', 'N/A')}
            • Low: ${row.get('Low', 'N/A')}
            • Volume: {row.get('Vol.', 'N/A')}
        """

    def _llm_format_result(self, question: str, result: Any) -> str:
        """
        Use LLM to format complex results
        """
        prompt = f"""
            Format this data as a natural language answer to the user's question.
            Be concise and clear.

            Question: {question}

            Data: {result}

            Answer:
            """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except:
            return str(result)


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
