import yfinance as yf

t = yf.Ticker('688295.SS')
info = t.info

print("=== 股本数据 ===")
print(f"sharesOutstanding (总股本): {info.get('sharesOutstanding'):,} = {info.get('sharesOutstanding')/1e8:.2f}亿股")
print(f"floatShares (流通股): {info.get('floatShares'):,} = {info.get('floatShares')/1e8:.2f}亿股" if info.get('floatShares') else "无数据")

# 如果流通股是9亿股
if info.get('floatShares'):
    float_shares = info.get('floatShares')
    price = 52.10
    float_market_cap = price * float_shares / 1e8
    print(f"\n流通市值计算:")
    print(f"  {price:.2f} × {float_shares/1e8:.2f}亿 = {float_market_cap:.2f} 亿元")

print("\n=== 结论 ===")
print(f"股票APP显示46.89亿元，可能是:")
print(f"  1. 流通市值（而非总市值）")
print(f"  2. 或者数据源不同")
