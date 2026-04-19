import yfinance as yf

t = yf.Ticker('688295.SS')
info = t.info
hist = t.history(period='1d')

print("=== 数据对比 ===")
print(f"yfinance marketCap: {info.get('marketCap'):,}")
print(f"yfinance sharesOutstanding: {info.get('sharesOutstanding'):,}")

if not hist.empty:
    close = hist.iloc[-1]['Close']
    shares = info.get('sharesOutstanding', 0)
    
    print(f"\n股价: {close:.2f} 元")
    print(f"总股本: {shares:,} 股 = {shares/1e8:.2f} 亿股")
    
    # 正确计算
    market_cap_yuan = close * shares
    market_cap_yi = market_cap_yuan / 1e8
    
    print(f"\n市值计算:")
    print(f"  {close:.2f} × {shares/1e8:.2f}亿 = {market_cap_yi:.2f} 亿元")
    
    print(f"\n对比:")
    print(f"  yfinance返回: {info.get('marketCap')/1e8:.2f} 亿元")
    print(f"  计算结果: {market_cap_yi:.2f} 亿元")
    print(f"  股票APP显示: 46.89 亿元")
