import pandas as pd
import pdfplumber
def extract_tables(path):
    all_tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            all_tables.extend(tables)
    return all_tables
def pdf_to_dataframe(path):
    rows = []
    tables = extract_tables(path)
    for table in tables:
        rows.extend(table)
    if rows:
        df = pd.DataFrame(
            rows[1:],
            columns=rows[0]
        )
        return df
    return None
def load_dataframe(path):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(
        df['Date'],
        dayfirst=True
    )
    df['Date'] = df['Date'].dt.strftime("%d-%m-%Y")
    return df
def calculate_profit_loss(path,
                          buy_date,
                          sell_date,
                          shares):
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".pdf"):
        df = pdf_to_dataframe(path)
    else:
        return None
    buy_row = df[df['Date'] == buy_date]
    sell_row = df[df['Date'] == sell_date]
    if buy_row.empty or sell_row.empty:
        return None
    buy_price = float(
        buy_row.iloc[0]['Price']
    )
    sell_price = float(
        sell_row.iloc[0]['Price']
    )
    profit_loss = (
        sell_price-buy_price
    )*shares
    return {
        'buy_price':buy_price,
        'sell_price':sell_price,
        'shares':shares,
        'profit_loss':profit_loss
    }