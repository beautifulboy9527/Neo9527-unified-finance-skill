# 综合结论生成逻辑（临时文件）

## 需要实现的功能

### 1. 分析维度
- 技术面分析
- 链上数据（如果有）
- 多空因素对比

### 2. 时间窗口分析
- 短期（1-7天）：基于RSI超买超卖
- 中期（1-4周）：基于ADX趋势强度
- 长期（1-3月）：基于DI方向指标

### 3. 概率分析
根据总强度计算：
- 上涨概率
- 震荡概率  
- 下跌概率

### 4. 应对方案（场景化）
场景1: 上涨突破
- 条件：突破阻力位
- 操作：加仓追涨
- 止损：跌破关键位

场景2: 回调买入
- 条件：回调至支撑位
- 操作：逢低建仓
- 止损：跌破支撑位

场景3: 震荡观望
- 条件：区间震荡
- 操作：高抛低吸
- 止损：不适用

### 5. 风险提示
- RSI超买/超卖风险
- 鲸鱼派发风险
- 涨幅过大风险

## HTML结构

```html
<div class="card p-8 mb-8 fade-in">
    <h2>综合分析</h2>
    
    <!-- 分析维度 -->
    <div>
        <h3>分析维度</h3>
        <tags>技术面偏多 | 链上鲸鱼吸筹</tags>
    </div>
    
    <!-- 时间窗口分析 -->
    <div>
        <h3>时间窗口分析</h3>
        <grid>
            <card>短期(1-7日): 超买回调</card>
            <card>中期(1-4周): 趋势延续</card>
            <card>长期(1-3月): 上涨趋势</card>
        </grid>
    </div>
    
    <!-- 概率分析 -->
    <div>
        <h3>后续走势概率</h3>
        <progress bars>
            上涨: 60%
            震荡: 20%
            下跌: 20%
        </progress bars>
    </div>
    
    <!-- 应对方案 -->
    <div>
        <h3>应对方案</h3>
        <grid>
            <scenario card>
                <name>上涨突破</name>
                <condition>突破阻力位 $X,XXX</condition>
                <action>加仓追涨，目标下一阻力位</action>
                <stop_loss>跌破 $X,XXX (-3%)</stop_loss>
            </scenario card>
            <scenario card>
                <name>回调买入</name>
                <condition>回调至支撑位 $X,XXX</condition>
                <action>逢低建仓，分批买入</action>
                <stop_loss>跌破 $X,XXX (-3%)</stop_loss>
            </scenario card>
            <scenario card>
                <name>震荡观望</name>
                <condition>在 $X,XXX - $X,XXX 区间震荡</condition>
                <action>区间操作，高抛低吸</action>
                <stop_loss>不适用</stop_loss>
            </scenario card>
        </grid>
    </div>
    
    <!-- 风险提示 -->
    <div>
        <h3>风险提示</h3>
        <list>
            • RSI超买，短期回调风险较高
            • 链上鲸鱼派发，大资金流出
        </list>
    </div>
    
    <!-- 最终建议 -->
    <div class="highlight">
        <h3>最终建议</h3>
        <p>综合所有维度分析，建议逢低买入。</p>
        <p>关注支撑位 $X,XXX，跌破则止损观望。</p>
    </div>
</div>
```
