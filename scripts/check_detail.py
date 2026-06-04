import yfinance as yf

t = yf.Ticker('688295.SS')
info = t.info
hist = t.history(period='1d')

print("=== 详细数据对比 ===")
print(f"yfinance marketCap: {info.get('marketCap'):,}")
print(f"yfinance sharesOutstanding: {info.get('sharesOutstanding'):,}")

if not hist.empty:
    close = hist.iloc[-1]['Close']
    shares = info.get('sharesOutstanding', 0)
    calc = close * shares
    print(f"\n计算:")
    print(f"股价: {close:.2f} 元")
    print(f"总股本: {shares:,} 股")
    print(f"市值 = {close:.2f} × {shares:,} = {calc:,.0f} 元")
    print(f"市值 = {calc/1e8:.2f} 亿元")
    
print(f"\n对比:")
print(f"yfinance显示: {info.get('marketCap')/1e8:.2f} 亿元")
print(f"股票APP显示: 458.90 亿元")
print(f"差异: 458.90 / {info.get('marketCap')/1e8:.2f} = {458.90 / (info.get('marketCap')/1e8):.1f} 倍")
