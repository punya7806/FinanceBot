"""
Dynamic Pandas Agent
Generates and executes pandas code dynamically based on user queries
No hardcoded logic - fully flexible and LLM-powered
"""

import pandas as pd
import re
from typing import Dict, Any, Optional
import json
import traceback


class DynamicPandasAgent:
    """
    Agent that dynamically generates pandas code for any query
    """

    def __init__(self, llm):
        """
        Args:
            llm: Language model for code generation and narration
        """
        self.llm = llm

    def process_query(self, question: str, df: pd.DataFrame, debug: bool = True, max_retries: int = 3) -> str:
        """
        Main entry point - dynamically generates and executes pandas code with retry mechanism

        Args:
            question: User's natural language question
            df: Pandas DataFrame containing the data
            debug: If True, includes generated code in error messages
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Natural language answer
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"\n🔄 Retry attempt {attempt + 1}/{max_retries}...")

                # Step 1: LLM generates pandas code (with error feedback on retries)
                if attempt == 0:
                    pandas_code = self._generate_pandas_code(question, df)
                else:
                    # On retry, provide error feedback to help LLM fix the issue
                    pandas_code = self._generate_pandas_code_with_error_feedback(
                        question, df, last_error
                    )

                if debug:
                    print(f"\n{'='*60}")
                    print(f"GENERATED CODE (Attempt {attempt + 1}):")
                    print(f"{'='*60}")
                    print(pandas_code)
                    print(f"{'='*60}\n")

                # Step 2: Execute code safely
                result = self._execute_code_safely(pandas_code, df)

                if debug:
                    print(f"\n{'='*60}")
                    print(f"EXECUTION RESULT:")
                    print(f"{'='*60}")
                    print(result)
                    print(f"{'='*60}\n")

                # Step 3: LLM formats result naturally
                answer = self._format_result_with_llm(question, pandas_code, result)

                # Success! Return the answer
                if attempt > 0:
                    print(f"✅ Success on attempt {attempt + 1}!\n")

                return answer

            except Exception as e:
                last_error = str(e)

                if debug:
                    print(f"\n❌ Attempt {attempt + 1} failed: {last_error}\n")

                # If this was the last attempt, give up
                if attempt == max_retries - 1:
                    print(f"⚠️ All {max_retries} attempts failed.\n")
                    return (
                        f"I apologize, but I'm having trouble processing your question. "
                        f"Please try rephrasing it or ask a different question."
                    )

                # Otherwise, continue to next retry
                continue

        # Fallback (should never reach here)
        return "I apologize, but I encountered an unexpected error. Please try again."

    def _generate_pandas_code(self, question: str, df: pd.DataFrame) -> str:
        """
        Use LLM to generate pandas code based on the question
        """
        # Get DataFrame info
        df_info = self._get_dataframe_info(df)

        prompt = f"""You are a pandas expert. Generate Python code to answer the user's question.

**IMPORTANT:** The user has ALREADY uploaded data. The DataFrame 'df' contains ALL the data you need.
Do NOT ask for more information - just write code to analyze the existing DataFrame.

**DataFrame Info:**
{df_info}

**Sample Data (first 3 rows):**
{df.head(3).to_string()}

**User Question:**
{question}

**CRITICAL INSTRUCTIONS:**
1. Write ONLY executable pandas code - no explanations, no comments
2. The DataFrame is available as 'df'
3. Store the final result in a variable called 'result'
4. For comparisons: ALWAYS fetch ALL dates mentioned in the question
5. Use .isin() for multiple values, not individual checks
6. IMPORTANT - to_dict usage:
   - Use .to_dict() on Series (single row: df.loc[idx])
   - Use .to_dict('records') on DataFrames (multiple rows: df[df['Date'].isin(dates)])
7. For "which is higher/lower" questions: Return ALL data so LLM can compare
8. Handle missing data with .empty checks, not try/except
9. Do NOT use print() or display() statements
10. DO NOT include markdown code blocks - just raw Python code
11. IMPORTANT - Position-based indexing:
   - Use .iloc[0] for first row, .iloc[-1] for last row (position-based)
   - Use .loc[index] only when you have an actual index value
   - NEVER use .loc[-1] - it looks for index labeled -1, not last row!
12. ALWAYS convert string columns to appropriate types (float, int) before calculations
13. CRITICAL - Date string handling:
   - Date strings like '18-06-2026' should ALWAYS be kept as STRINGS in quotes
   - NEVER parse date components as integers (avoid leading zero errors)
   - Use exact string matching: df[df['Date'] == '18-06-2026']
   - For multiple dates use .isin(): df[df['Date'].isin(['18-06-2026', '17-06-2026'])]

**IMPORTANT FOR COMPARISON QUERIES:**
- "Which date had higher X?" → Return data for BOTH dates
- "Compare X and Y" → Return data for BOTH
- "X or Y?" → Return data for BOTH
Let the LLM do the comparison in natural language, not in code!

**IMPORTANT FOR AGGREGATION QUERIES:**
- "What is the total X?" → Use .sum() and return a number in a dict
- "What is the average X?" → Use .mean() and return a number in a dict
- "What is the median X?" → Use .median() and return a number in a dict
- For volume columns with "M" suffix, parse it first: .str.replace('M', '').astype(float)
- Return format: result = dict(metric_name=value, unit='millions')
DO NOT try to fetch all rows for aggregation queries!

**IMPORTANT FOR RANKING/SORTING QUERIES:**
- "Top N biggest X" → Use .nlargest(N, column) on the DATAFRAME (not on a Series!)
- "Top N smallest X" → Use .nsmallest(N, column) on the DATAFRAME (not on a Series!)
- "Rank by X" → Use .sort_values(column, ascending=False)
- For percentage columns with "%" suffix, parse it first: .str.replace('%', '').astype(float)
- For volume columns with "M" suffix, parse it first: .str.replace('M', '').astype(float)
- CRITICAL: Call .nlargest() on the DataFrame, NOT on a single column Series!
- Return format: .to_dict('records') with multiple rows including Date column
- ALWAYS process the ENTIRE dataset, not just a few rows!

**Example Patterns:**

Get single date data (KEEP DATES AS STRINGS):
```python
# Single date - use exact string match
target_date = '18-06-2026'
row = df[df['Date'] == target_date]
if not row.empty:
    result = row.iloc[0].to_dict()
else:
    result = dict(error='Date not found')
```

Compare 2 dates OR check which is higher (ALWAYS return ALL dates for comparison):
```python
dates = ['12-06-2026', '18-06-2026']
filtered = df[df['Date'].isin(dates)]
result = filtered[['Date', 'Price']].to_dict('records')
```

IMPORTANT: For "which is higher/lower" questions, return ALL data points so the LLM can compare and explain!

Compare multiple dates:
```python
dates = ['15-06-2026', '16-06-2026', '17-06-2026', '18-06-2026']
result = df[df['Date'].isin(dates)][['Date', 'Price', 'Change %']].to_dict('records')
```

Get max/highest in entire dataset (single row result):
```python
max_idx = df['Price'].astype(float).idxmax()
result = df.loc[max_idx].to_dict()  # .to_dict() for Series, NOT .to_dict('records')!
```

Get max in a specific month (single row result):
```python
filtered = df[df['Date'].str.contains('-06-2026')]
max_idx = filtered['Price'].astype(float).idxmax()
result = filtered.loc[max_idx].to_dict()  # .to_dict() for Series!
```

IMPORTANT: Use .to_dict() when returning a SINGLE ROW, use .to_dict('records') when returning MULTIPLE ROWS!

Calculate sum/total (returns a single number in a dict):
```python
df_copy = df.copy()
df_copy['Vol_Numeric'] = df_copy['Vol.'].astype(str).str.replace('M', '', regex=False).astype(float)
total_vol = df_copy['Vol_Numeric'].sum()
result = dict(total_volume=total_vol, unit='millions')
```

Calculate average (returns a single number in a dict):
```python
avg_val = df['Price'].astype(float).mean()
result = dict(average_price=round(avg_val, 2))
```

Calculate median (returns a single number in a dict):
```python
med_val = df['Price'].astype(float).median()
result = dict(median_price=round(med_val, 2))
```

Calculate percentage change from first to last row:
```python
first_price = float(df.iloc[0]['Price'])
last_price = float(df.iloc[-1]['Price'])
pct_change = ((last_price - first_price) / first_price) * 100
result = dict(first_price=first_price, last_price=last_price, percentage_change=round(pct_change, 2))
```

Get top N rows sorted by a column (e.g., top 10 biggest gains):
```python
df_sorted = df.copy()
df_sorted['Change_Numeric'] = df_sorted['Change %'].astype(str).str.replace('%', '').astype(float)
top_10 = df_sorted.nlargest(10, 'Change_Numeric')
result = top_10[['Date', 'Price', 'Change %']].to_dict('records')
```

Get top N by volume (need to parse "M" suffix):
```python
df_sorted = df.copy()
df_sorted['Vol_Numeric'] = df_sorted['Vol.'].astype(str).str.replace('M', '', regex=False).astype(float)
top_10 = df_sorted.nlargest(10, 'Vol_Numeric')
result = top_10[['Date', 'Vol.', 'Price']].to_dict('records')
```

Get bottom N rows sorted by a column (e.g., top 10 biggest losses):
```python
df_sorted = df.copy()
df_sorted['Change_Numeric'] = df_sorted['Change %'].astype(str).str.replace('%', '').astype(float)
top_10_losses = df_sorted.nsmallest(10, 'Change_Numeric')
result = top_10_losses[['Date', 'Price', 'Change %']].to_dict('records')
```

IMPORTANT: For ranking queries, use .nlargest() or .nsmallest() on the DATAFRAME (not on a Series).
Always include the Date column in the result so context is provided!

Calculate profit/loss:
```python
buy_row = df[df['Date'] == '01-05-2026']
sell_row = df[df['Date'] == '01-06-2026']
if not buy_row.empty and not sell_row.empty:
    buy_price = float(buy_row.iloc[0]['Price'])
    sell_price = float(sell_row.iloc[0]['Price'])
    shares = 100
    profit = (sell_price - buy_price) * shares
    result = dict(buy=buy_price, sell=sell_price, profit=profit, shares=shares)
else:
    result = dict(error='Date not found')
```

**Now generate code for the user's question:**
"""

        try:
            response = self.llm.invoke(prompt)
            code = response.content.strip()

            # Clean up code (remove markdown, explanations)
            code = self._clean_code(code)

            return code

        except Exception as e:
            raise Exception(f"Failed to generate pandas code: {str(e)}")

    def _generate_pandas_code_with_error_feedback(
        self, question: str, df: pd.DataFrame, error: str
    ) -> str:
        """
        Generate pandas code with feedback from previous error
        This helps the LLM fix mistakes on retry
        """
        # Get DataFrame info
        df_info = self._get_dataframe_info(df)

        prompt = f"""You are a pandas expert. Your previous code attempt failed. Generate CORRECTED Python code.

**PREVIOUS ERROR:**
{error}

**DataFrame Info:**
{df_info}

**Sample Data (first 3 rows):**
{df.head(3).to_string()}

**User Question:**
{question}

**CRITICAL - Learn from the error:**
- If error mentions "leading zeros": Keep date strings as strings, don't parse components
- If error mentions "to_dict": Check if using Series (use .to_dict()) or DataFrame (use .to_dict('records'))
- If error mentions "index": Use .iloc for position-based, .loc for label-based
- If error mentions "astype": Ensure column exists and data is valid
- If error mentions "idxmax" or "idxmin": Make sure you converted to numeric first

**INSTRUCTIONS:**
1. Write ONLY executable pandas code - no explanations
2. Store result in variable 'result'
3. Handle the error that occurred previously
4. Date strings must stay as strings: '18-06-2026' not 18, 06, 2026
5. Use .iloc[0] for first row, .iloc[-1] for last row
6. Use .to_dict() for Series, .to_dict('records') for DataFrame
7. Convert string columns to numeric before math operations
8. DO NOT include markdown code blocks

**Generate the CORRECTED code:**
"""

        try:
            response = self.llm.invoke(prompt)
            code = response.content.strip()
            code = self._clean_code(code)
            return code
        except Exception as e:
            raise Exception(f"Failed to generate corrected code: {str(e)}")

    def _clean_code(self, code: str) -> str:
        """
        Clean LLM-generated code
        """
        # Remove markdown code blocks
        code = re.sub(r'^```python\s*\n', '', code)
        code = re.sub(r'^```\s*\n', '', code)
        code = re.sub(r'\n```\s*$', '', code)

        # Remove any leading/trailing whitespace
        code = code.strip()

        return code

    def _execute_code_safely(self, code: str, df: pd.DataFrame) -> Any:
        """
        Execute generated pandas code in a safe environment
        """
        # Create safe execution environment
        safe_globals = {
            'df': df,
            'pd': pd,
            'result': None,
            # Allow common Python functions
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
        }

        safe_locals = {}

        try:
            # Execute the code
            exec(code, safe_globals, safe_locals)

            # Get result
            result = safe_locals.get('result', safe_globals.get('result'))

            if result is None:
                raise Exception("Code did not produce a 'result' variable")

            return result

        except Exception as e:
            error_msg = f"Execution error: {str(e)}\n\nGenerated code:\n{code}"
            raise Exception(error_msg)

    def _format_result_with_llm(self, question: str, code: str, result: Any) -> str:
        """
        Use LLM to format the result in natural language
        """
        # Convert result to JSON for LLM
        try:
            result_json = json.dumps(result, indent=2, default=str)
        except:
            result_json = str(result)

        prompt = f"""You are a financial data analyst assistant. Answer the user's question based on the retrieved data.

**User Question:**
{question}

**Data Retrieved:**
{result_json}

**Instructions:**
1. Provide a clear, direct answer to the question
2. Be conversational and friendly
3. Highlight key insights and patterns
4. Use formatting (bold, bullets) for readability
5. For comparisons, clearly show changes and trends
6. Include percentages and dollar amounts when relevant
7. Keep it concise but informative
8. Don't mention the code, data structures, or technical process
9. If comparing multiple dates, show the progression/trend
10. DO NOT add disclaimers, warnings, or investment advice notes
11. DO NOT mention "limited dataset" or "not investment advice"
12. Simply answer the question directly based on the data provided

**Answer:**"""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            # Fallback to simple formatting
            return f"Based on the data: {result}"

    def _get_dataframe_info(self, df: pd.DataFrame) -> str:
        """
        Get DataFrame structure information
        """
        info = []
        info.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        info.append(f"Columns: {', '.join(df.columns.tolist())}")

        # Show data types
        dtypes = df.dtypes.to_dict()
        info.append("Data types:")
        for col, dtype in dtypes.items():
            info.append(f"  - {col}: {dtype}")

        return "\n".join(info)


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
                # Keep as string for easier matching
                pass
            except:
                pass

    return df


def pandas_agent_query(question: str, path: str, llm) -> str:
    """
    Main entry point for dynamic pandas-based queries

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
        agent = DynamicPandasAgent(llm)

        # Process query
        answer = agent.process_query(question, df)

        return answer

    except Exception as e:
        return f"Error: {str(e)}"
