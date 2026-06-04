import yfinance as yf

t = yf.Ticker('688295.SS')
info = t.info

market_cap = info.get('marketCap', 0)
long_name = info.get('longName', '')

print(f"marketCap: {market_cap:,.0f}")
print(f"marketCap (billion): {market_cap/1e9:.2f}")
print(f"longName: {long_name}")
print(f"trailingPE: {info.get('trailingPE')}")
