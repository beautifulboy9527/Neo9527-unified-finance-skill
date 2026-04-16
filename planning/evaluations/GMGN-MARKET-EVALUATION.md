# daily-gmgn-market Skill 评估报告

**评估时间**: 2026-04-16 05:42
**来源**: https://skills.yangsir.net/skill/daily-gmgn-market
**类型**: 加密货币市场数据工具

---

## 📊 整合价值评估: ⭐⭐⭐⭐ (高 - 补充增强)

### 为什么对金融 Skills 有帮助？

| 维度 | gmgn-market 能力 | 对我们的价值 |
|------|-----------------|-------------|
| **多链支持** | SOL/BSC/BASE | ⭐⭐⭐⭐ 补充增强 |
| **热门代币** | trending 数据 | ⭐⭐⭐⭐⭐ 新能力 |
| **K线数据** | 多时间框架 | ⭐⭐⭐ 已有类似 |
| **智能钱包追踪** | smart_degen_count | ⭐⭐⭐⭐⭐ 新能力 |
| **安全过滤** | honeypot检测 | ⭐⭐⭐⭐⭐ 新能力 |

---

## 🔍 核心能力分析

### 1. 支持的区块链

```
✅ Solana (SOL)
✅ BSC (BSC)
✅ Base (BASE)
```

**我们的现状**:
- ✅ 已有加密货币模块 (ccxt)
- ✅ 支持 Binance/Kraken 等交易所
- ❌ 缺少链上数据
- ❌ 缺少 DEX 数据

### 2. 核心功能

#### 2.1 K线数据查询

```bash
# 查询最近1小时的1分钟K线
gmgn-cli market kline \
  --chain sol \
  --address <token_address> \
  --resolution 1m \
  --from $(date -v-1H +%s) \
  --to $(date +%s)

# 支持的分辨率
1m / 5m / 15m / 1h / 4h / 1d
```

**对比我们的 crypto.py**:
- ✅ 我们已有 `get_ohlcv()` 函数
- ⚠️ 我们用的是交易所数据 (CEX)
- ✅ gmgn 提供的是 DEX 数据
- 🎯 可以补充增强

#### 2.2 热门代币查询

```bash
# 查询SOL链上最近1小时的热门代币
gmgn-cli market trending \
  --chain sol \
  --interval 1h \
  --order-by volume \
  --limit 20

# 排序字段
volume / swaps / marketcap / liquidity / holder_count
smart_degen_count / renowned_count / change1h / change5m
```

**我们的现状**:
- ✅ 有 `get_trending()` 函数
- ⚠️ 仅限交易所数据
- ❌ 缺少链上热门代币
- ❌ 缺少智能钱包追踪

#### 2.3 安全过滤

```bash
# 过滤安全代币
--filter not_honeypot    # 非蜜罐
--filter verified        # 已验证
--filter renounced       # 已弃权
--filter locked          # 已锁定
--filter has_social      # 有社交链接
```

**我们的现状**:
- ❌ 完全缺少安全检测
- ⭐⭐⭐⭐⭐ 这是重大缺失

#### 2.4 平台过滤

```bash
# 按平台过滤
SOL: Pump.fun / Moonshot / Raydium
BSC: fourmeme / PancakeSwap
BASE: clanker / virtuals_v2
```

**我们的现状**:
- ❌ 没有 DEX 平台数据
- 🎯 新能力补充

### 3. 智能分析信号

**gmgn 提供的分析框架**:

| 信号 | 字段 | 权重 | 说明 |
|------|------|------|------|
| **智能钱包兴趣** | smart_degen_count, renowned_count | 高 | 关键信心指标 |
| **蓝筹持有** | bluechip_owner_percentage | 中 | 持有者质量 |
| **真实交易** | volume, swaps | 中 | 区分真实 vs 对敲 |
| **价格动能** | change1h, change5m | 中 | 偏好正向非抛物线 |
| **池安全** | liquidity | 中 | 低流动性=高滑点 |
| **代币成熟度** | creation_timestamp | 低 | 避免<1小时的新币 |

**对我们的价值**:
- ⭐⭐⭐⭐⭐ 完整的分析框架
- ⭐⭐⭐⭐⭐ 我们完全缺少这些字段

---

## 🎯 对我们的价值

### 1. 补充我们的加密货币能力

| 能力 | 我们现有 | gmgn-market | 整合价值 |
|------|---------|------------|---------|
| **K线数据** | ✅ CEX | ✅ DEX | ⭐⭐⭐ 补充 |
| **热门代币** | ✅ CEX | ✅ DEX + 链上 | ⭐⭐⭐⭐⭐ 增强 |
| **智能钱包** | ❌ | ✅ smart_degen | ⭐⭐⭐⭐⭐ 新能力 |
| **安全检测** | ❌ | ✅ honeypot | ⭐⭐⭐⭐⭐ 新能力 |
| **平台过滤** | ❌ | ✅ Pump.fun等 | ⭐⭐⭐⭐ 新能力 |
| **多链支持** | ✅ | ✅ | - |

### 2. 独特价值

**gmgn 独有**:
1. **智能钱包追踪**
   - smart_degen_count: 聪明的Degen数量
   - renowned_count: 知名钱包数量
   - bluechip_owner_percentage: 蓝筹持有比例

2. **安全过滤**
   - not_honeypot: 非蜜罐检测
   - verified: 已验证合约
   - renounced: 所有权已弃权

3. **DEX 数据**
   - Pump.fun / Moonshot / Raydium
   - fourmeme / PancakeSwap
   - clanker / virtuals_v2

**我们独有**:
- ✅ 传统股票市场 (A股/港股/美股)
- ✅ 贵金属
- ✅ 期权分析
- ✅ 新闻聚合
- ✅ 完整分析框架

### 3. 可整合的工作流

**发现交易机会流程** (来自 gmgn):

```
Step 1: 获取热门代币
→ gmgn-cli market trending --chain sol --interval 1h --limit 50

Step 2: AI多因子分析
→ 智能钱包兴趣 (高权重)
→ 蓝筹持有 (中权重)
→ 真实交易 (中权重)
→ 价格动能 (中权重)
→ 池安全 (中权重)
→ 代币成熟度 (低权重)

Step 3: 展示Top 5
→ 表格 + 一句话理由

Step 4: 后续行动
→ 深入分析: token info + token security
→ 直接交易: swap
```

**我们可以集成到 Agent 协调器**:
```python
def discover_crypto_opportunities(chain: str = 'sol') -> Dict:
    """
    发现加密货币交易机会
    
    整合 gmgn 的 trending + 分析框架
    """
    # 1. 获取热门代币
    trending = get_gmgn_trending(chain, interval='1h', limit=50)
    
    # 2. 多因子评分
    scored_tokens = []
    for token in trending:
        score = calculate_opportunity_score(token)
        scored_tokens.append({
            'symbol': token['symbol'],
            'address': token['address'],
            'score': score,
            'signals': extract_signals(token)
        })
    
    # 3. 排序返回 Top 5
    scored_tokens.sort(key=lambda x: x['score'], reverse=True)
    return scored_tokens[:5]
```

---

## 📊 功能对比

### 完整对比矩阵

| 功能 | 我们 | gmgn-market | 建议 |
|------|------|------------|------|
| **CEX K线** | ✅ | - | 保留 |
| **DEX K线** | ❌ | ✅ | 整合 |
| **热门代币(CEX)** | ✅ | - | 保留 |
| **热门代币(DEX)** | ❌ | ✅ | 整合 |
| **智能钱包追踪** | ❌ | ✅ | 整合 ⭐ |
| **安全检测** | ❌ | ✅ | 整合 ⭐ |
| **平台过滤** | ❌ | ✅ | 整合 |
| **传统市场** | ✅ | ❌ | 保留 ⭐ |
| **贵金属** | ✅ | ❌ | 保留 ⭐ |
| **分析框架** | ✅ | ⚠️ | 我们更强 |
| **Agent协调** | ✅ | ❌ | 保留 ⭐ |

---

## 🔧 整合方案

### 方案: 补充增强我们的加密货币模块

**Phase 1: DEX 数据集成** (立即)

```python
# 增强 features/crypto.py

class GmgnMarketClient:
    """gmgn-market API 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = os.getenv('GMGN_HOST', 'https://api.gmgn.ai')
    
    def get_trending(
        self,
        chain: str = 'sol',
        interval: str = '1h',
        limit: int = 20,
        order_by: str = 'volume',
        filters: List[str] = None
    ) -> List[Dict]:
        """
        获取热门代币
        
        Args:
            chain: sol / bsc / base
            interval: 1h / 3h / 6h / 24h
            limit: 数量 (max 100)
            order_by: 排序字段
            filters: 过滤条件 ['not_honeypot', 'verified', 'has_social']
        """
        params = {
            'chain': chain,
            'interval': interval,
            'limit': limit,
            'order_by': order_by
        }
        
        if filters:
            params['filter'] = filters
        
        response = requests.get(
            f"{self.base_url}/market/trending",
            params=params,
            headers={'X-API-Key': self.api_key}
        )
        
        return response.json()
    
    def get_kline(
        self,
        chain: str,
        address: str,
        resolution: str = '1h',
        from_ts: int = None,
        to_ts: int = None
    ) -> List[Dict]:
        """
        获取K线数据
        
        Args:
            chain: sol / bsc / base
            address: 代币合约地址
            resolution: 1m / 5m / 15m / 1h / 4h / 1d
        """
        params = {
            'chain': chain,
            'address': address,
            'resolution': resolution
        }
        
        if from_ts:
            params['from'] = from_ts
        if to_ts:
            params['to'] = to_ts
        
        response = requests.get(
            f"{self.base_url}/market/kline",
            params=params,
            headers={'X-API-Key': self.api_key}
        )
        
        return response.json()
```

**Phase 2: 智能分析模块** (本周)

```python
# 新增 features/crypto_analysis.py

class CryptoOpportunityScorer:
    """
    加密货币机会评分器
    
    基于 gmgn 的分析框架
    """
    
    # 信号权重
    WEIGHTS = {
        'smart_money_interest': 0.30,      # 高权重
        'bluechip_ownership': 0.15,        # 中权重
        'real_trading_activity': 0.15,     # 中权重
        'price_momentum': 0.15,            # 中权重
        'pool_safety': 0.15,               # 中权重
        'token_maturity': 0.10             # 低权重
    }
    
    def score_opportunity(self, token: Dict) -> Dict:
        """
        评分交易机会
        
        Returns:
            {
                'symbol': 'PEPE',
                'total_score': 85,
                'signals': {
                    'smart_money': {'score': 90, 'weight': 0.30},
                    'bluechip': {'score': 80, 'weight': 0.15},
                    ...
                },
                'recommendation': 'strong_buy'
            }
        """
        signals = {}
        
        # 1. 智能钱包兴趣 (高权重)
        smart_money_score = self._score_smart_money(token)
        signals['smart_money'] = {
            'score': smart_money_score,
            'weight': self.WEIGHTS['smart_money_interest'],
            'details': {
                'smart_degen_count': token.get('smart_degen_count', 0),
                'renowned_count': token.get('renowned_count', 0)
            }
        }
        
        # 2. 蓝筹持有 (中权重)
        bluechip_score = self._score_bluechip(token)
        signals['bluechip'] = {
            'score': bluechip_score,
            'weight': self.WEIGHTS['bluechip_ownership'],
            'details': {
                'bluechip_owner_percentage': token.get('bluechip_owner_percentage', 0)
            }
        }
        
        # 3. 真实交易 (中权重)
        trading_score = self._score_trading(token)
        signals['trading'] = {
            'score': trading_score,
            'weight': self.WEIGHTS['real_trading_activity'],
            'details': {
                'volume': token.get('volume', 0),
                'swaps': token.get('swaps', 0)
            }
        }
        
        # 4. 价格动能 (中权重)
        momentum_score = self._score_momentum(token)
        signals['momentum'] = {
            'score': momentum_score,
            'weight': self.WEIGHTS['price_momentum'],
            'details': {
                'change_1h': token.get('change1h', 0),
                'change_5m': token.get('change5m', 0)
            }
        }
        
        # 5. 池安全 (中权重)
        safety_score = self._score_safety(token)
        signals['safety'] = {
            'score': safety_score,
            'weight': self.WEIGHTS['pool_safety'],
            'details': {
                'liquidity': token.get('liquidity', 0)
            }
        }
        
        # 6. 代币成熟度 (低权重)
        maturity_score = self._score_maturity(token)
        signals['maturity'] = {
            'score': maturity_score,
            'weight': self.WEIGHTS['token_maturity'],
            'details': {
                'creation_timestamp': token.get('creation_timestamp')
            }
        }
        
        # 计算总分
        total_score = sum(
            s['score'] * s['weight'] 
            for s in signals.values()
        )
        
        # 确定建议
        if total_score >= 80:
            recommendation = 'strong_buy'
        elif total_score >= 65:
            recommendation = 'buy'
        elif total_score >= 50:
            recommendation = 'watch'
        else:
            recommendation = 'avoid'
        
        return {
            'symbol': token.get('symbol'),
            'address': token.get('address'),
            'total_score': round(total_score, 2),
            'signals': signals,
            'recommendation': recommendation
        }
    
    def _score_smart_money(self, token: Dict) -> float:
        """智能钱包评分"""
        smart_degen = token.get('smart_degen_count', 0)
        renowned = token.get('renowned_count', 0)
        
        # 简单评分逻辑
        if smart_degen >= 10 or renowned >= 5:
            return 90
        elif smart_degen >= 5 or renowned >= 2:
            return 75
        elif smart_degen >= 1 or renowned >= 1:
            return 60
        else:
            return 30
    
    def _score_bluechip(self, token: Dict) -> float:
        """蓝筹持有评分"""
        percentage = token.get('bluechip_owner_percentage', 0)
        
        if percentage >= 20:
            return 90
        elif percentage >= 10:
            return 75
        elif percentage >= 5:
            return 60
        else:
            return 40
    
    def _score_trading(self, token: Dict) -> float:
        """真实交易评分"""
        volume = token.get('volume', 0)
        swaps = token.get('swaps', 0)
        
        # 简单评分
        if volume >= 100000 and swaps >= 1000:
            return 85
        elif volume >= 50000 and swaps >= 500:
            return 70
        elif volume >= 10000 and swaps >= 100:
            return 55
        else:
            return 35
    
    def _score_momentum(self, token: Dict) -> float:
        """价格动能评分"""
        change_1h = token.get('change1h', 0)
        change_5m = token.get('change5m', 0)
        
        # 偏好正向但非抛物线
        if 5 <= change_1h <= 50:
            return 85
        elif 0 < change_1h < 5:
            return 70
        elif change_1h > 50:
            return 50  # 太激进
        else:
            return 40
    
    def _score_safety(self, token: Dict) -> float:
        """池安全评分"""
        liquidity = token.get('liquidity', 0)
        
        if liquidity >= 100000:
            return 90
        elif liquidity >= 50000:
            return 75
        elif liquidity >= 10000:
            return 60
        else:
            return 35
    
    def _score_maturity(self, token: Dict) -> float:
        """代币成熟度评分"""
        import time
        creation_ts = token.get('creation_timestamp', 0)
        
        if not creation_ts:
            return 50
        
        age_hours = (time.time() - creation_ts) / 3600
        
        if age_hours >= 24:
            return 90
        elif age_hours >= 6:
            return 70
        elif age_hours >= 1:
            return 50
        else:
            return 20  # 太新
```

**Phase 3: CLI 命令集成** (本周)

```python
# 增强 finance.py

# gmgn commands
gmgn_parser = subparsers.add_parser('gmgn', help='gmgn市场数据')
gmgn_sub = gmgn_parser.add_subparsers(dest='gmgn_type')

# trending
trending_parser = gmgn_sub.add_parser('trending', help='热门代币')
trending_parser.add_argument('--chain', default='sol', help='链 (sol/bsc/base)')
trending_parser.add_argument('--interval', default='1h', help='时间间隔')
trending_parser.add_argument('--limit', type=int, default=20, help='数量')
trending_parser.add_argument('--order-by', default='volume', help='排序字段')
trending_parser.add_argument('--safe', action='store_true', help='仅安全代币')

# kline
kline_parser = gmgn_sub.add_parser('kline', help='K线数据')
kline_parser.add_argument('address', help='代币地址')
kline_parser.add_argument('--chain', default='sol', help='链')
kline_parser.add_argument('--resolution', default='1h', help='分辨率')
kline_parser.add_argument('--hours', type=int, default=24, help='小时数')

# discover
discover_parser = gmgn_sub.add_parser('discover', help='发现机会')
discover_parser.add_argument('--chain', default='sol', help='链')
discover_parser.add_argument('--top', type=int, default=5, help='返回数量')
```

---

## 💡 核心启发

### 1. DEX vs CEX 数据

**gmgn 启示**:
- DEX 数据包含智能钱包行为
- CEX 数据缺少链上透明度
- 两者结合才是完整画面

**我们的行动**:
- 保留 CEX 数据 (我们的优势)
- 补充 DEX 数据 (gmgn)
- 提供完整的市场视图

### 2. 安全过滤的重要性

**gmgn 启示**:
- honeypot 检测是刚需
- verified/renounced 是基础安全
- 社交链接验证真实性

**我们的行动**:
- 立即增加安全过滤模块
- 整合到发现流程
- 提供安全评分

### 3. 智能钱包追踪

**gmgn 启示**:
- smart_degen 是关键信心指标
- renowned 钱包增加可信度
- bluechip 持有提升质量

**我们的行动**:
- 这是我们的重大缺失
- 立即整合到评分系统
- 作为高权重信号

---

## 🏆 最终结论

### 是否需要整合？

**✅ 推荐整合作为补充增强**

| 理由 | 说明 |
|------|------|
| **补充能力** | DEX数据 + 智能钱包 + 安全检测 |
| **我们的缺失** | 完全缺少这些能力 |
| **独特价值** | gmgn 在加密领域专业 |
| **互补关系** | 我们的传统市场 + gmgn的加密 |
| **完整视图** | CEX + DEX = 完整市场 |

### 整合优先级

```
P0: DEX trending 集成 (本周)
P1: 智能钱包分析模块 (本周)
P2: 安全检测模块 (下周)
P3: K线数据补充 (下周)
```

### 前提条件

```
需要配置:
1. GMGN_API_KEY (环境变量)
2. gmgn-cli 安装: npm install -g gmgn-cli@1.0.1
3. 或者直接使用 API (推荐)
```

---

## 📊 整合后能力矩阵

| 市场 | CEX数据 | DEX数据 | 智能钱包 | 安全检测 | 完整度 |
|------|---------|---------|---------|---------|--------|
| **SOL** | ❌ | ✅ | ✅ | ✅ | 完整 |
| **BSC** | ⚠️ | ✅ | ✅ | ✅ | 完整 |
| **BASE** | ❌ | ✅ | ✅ | ✅ | 完整 |
| **BTC/ETH** | ✅ | - | - | - | 完整 |
| **A股/港股/美股** | ✅ | - | - | - | 完整 |
| **贵金属** | ✅ | - | - | - | 完整 |

---

**gmgn-market 提供了我们完全缺少的 DEX 数据、智能钱包追踪和安全检测能力，强烈推荐作为补充增强整合！** 🎯
