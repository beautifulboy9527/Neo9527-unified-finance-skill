import yfinance as yf

t = yf.Ticker('000651.SZ')
info = t.info

print("=== 格力电器数据 ===")
print(f"longName: {info.get('longName')}")
print(f"shortName: {info.get('shortName')}")
print(f"industry: {info.get('industry')}")
print(f"sector: {info.get('sector')}")
