import yfinance as yf

t = yf.Ticker('688295.SS')
info = t.info

print("=== yfinance 数据 ===")
print(f"marketCap: {info.get('marketCap'):,}")
print(f"marketCap (billion USD): {info.get('marketCap')/1e9:.2f}")
print(f"trailingPE: {info.get('trailingPE')}")
print(f"forwardPE: {info.get('forwardPE')}")
print(f"priceToBook: {info.get('priceToBook')}")
print(f"longName: {info.get('longName')}")
print(f"sharesOutstanding: {info.get('sharesOutstanding'):,}")

# 计算市值
hist = t.history(period='1d')
if not hist.empty:
    latest = hist.iloc[-1]
    close = latest['Close']
    shares = info.get('sharesOutstanding', 0)
    calc_market_cap = close * shares
    print(f"\n=== 计算市值 ===")
    print(f"最新价: {close:.2f}")
    print(f"总股本: {shares:,}")
    print(f"计算市值: {calc_market_cap:,.0f}")
    print(f"计算市值 (billion CNY): {calc_market_cap/1e9:.2f}")
