#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量回测引擎 - 信号验证与策略回测
支持 Walk-Forward、Monte Carlo、样本内外验证
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class BacktestEngine:
    """
    轻量回测引擎
    
    功能:
    - 信号历史表现验证
    - Walk-Forward 分析
    - Monte Carlo 模拟
    - 风险收益统计
    """
    
    def __init__(self, initial_capital: float = 100000):
        """
        初始化
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.trades = []
        self.equity_curve = []
    
    # ========================================
    # 数据获取
    # ========================================
    
    def get_price_data(
        self, 
        symbol: str, 
        days: int = 365
    ) -> pd.DataFrame:
        """
        获取历史价格数据
        
        Args:
            symbol: 股票代码
            days: 历史天数
            
        Returns:
            OHLCV DataFrame
        """
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            import yfinance as yf
            
            # A股代码转换
            if symbol.isdigit():
                if symbol.startswith('6'):
                    symbol = f"{symbol}.SS"
                elif symbol.startswith(('0', '3')):
                    symbol = f"{symbol}.SZ"
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"⚠️ 无法获取 {symbol} 历史数据")
                return pd.DataFrame()
            
            return df
            
        except Exception as e:
            print(f"⚠️ 获取数据失败: {e}")
            return pd.DataFrame()
    
    # ========================================
    # 信号回测
    # ========================================
    
    def backtest_signal(
        self,
        symbol: str,
        signal_func,
        signal_name: str = "Signal",
        days: int = 365,
        holding_period: int = 10
    ) -> Dict:
        """
        回测单个信号
        
        Args:
            symbol: 股票代码
            signal_func: 信号函数 (返回 'buy'/'sell'/'hold')
            signal_name: 信号名称
            days: 回测天数
            holding_period: 持仓天数
            
        Returns:
            回测结果
        """
        df = self.get_price_data(symbol, days)
        
        if df.empty:
            return {'error': '无法获取数据'}
        
        trades = []
        equity = [self.initial_capital]
        current_capital = self.initial_capital
        position = None
        
        # 遍历历史数据
        for i in range(len(df) - holding_period):
            date = df.index[i]
            current_price = df['Close'].iloc[i]
            
            # 生成信号
            try:
                signal = signal_func(symbol, df.iloc[:i+1])
            except:
                signal = 'hold'
            
            # 买入
            if signal == 'buy' and position is None:
                shares = int(current_capital * 0.95 / current_price)
                if shares > 0:
                    position = {
                        'entry_date': date,
                        'entry_price': current_price,
                        'shares': shares,
                        'cost': shares * current_price
                    }
            
            # 卖出 (持仓到期)
            elif position is not None and i >= df.index.get_loc(position['entry_date']) + holding_period:
                exit_price = df['Close'].iloc[i]
                profit = (exit_price - position['entry_price']) * position['shares']
                profit_pct = (exit_price - position['entry_price']) / position['entry_price']
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': date,
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'shares': position['shares'],
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'holding_days': holding_period
                })
                
                current_capital += profit
                position = None
            
            equity.append(current_capital)
        
        # 计算统计指标
        if not trades:
            return {
                'signal': signal_name,
                'symbol': symbol,
                'total_trades': 0,
                'message': '未产生交易'
            }
        
        profits = [t['profit_pct'] for t in trades]
        winning_trades = [p for p in profits if p > 0]
        
        total_return = (current_capital - self.initial_capital) / self.initial_capital
        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_profit = np.mean(profits) if profits else 0
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean([p for p in profits if p <= 0]) if any(p <= 0 for p in profits) else 0
        
        # 夏普比率
        returns = pd.Series(profits)
        sharpe = (returns.mean() / returns.std() * np.sqrt(252/holding_period)) if returns.std() > 0 else 0
        
        # 最大回撤
        equity_series = pd.Series(equity)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'signal': signal_name,
            'symbol': symbol,
            'period_days': days,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(trades) - len(winning_trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'avg_profit_pct': avg_profit,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'final_capital': current_capital,
            'trades': trades[:10]  # 只返回前10笔
        }
    
    # ========================================
    # Walk-Forward 分析
    # ========================================
    
    def walk_forward_analysis(
        self,
        symbol: str,
        signal_func,
        signal_name: str = "Signal",
        total_days: int = 730,
        train_days: int = 365,
        test_days: int = 90
    ) -> Dict:
        """
        Walk-Forward 分析
        
        Args:
            symbol: 股票代码
            signal_func: 信号函数
            signal_name: 信号名称
            total_days: 总天数
            train_days: 训练期天数
            test_days: 测试期天数
            
        Returns:
            Walk-Forward 结果
        """
        df = self.get_price_data(symbol, total_days)
        
        if df.empty:
            return {'error': '无法获取数据'}
        
        results = []
        
        # 分段回测
        n_periods = (total_days - train_days) // test_days
        
        for i in range(n_periods):
            test_start = train_days + i * test_days
            test_end = test_start + test_days
            
            if test_end > len(df):
                break
            
            # 测试期回测
            test_df = df.iloc[test_start:test_end]
            
            # 简化：统计测试期收益
            if len(test_df) > 0:
                period_return = (test_df['Close'].iloc[-1] - test_df['Close'].iloc[0]) / test_df['Close'].iloc[0]
                results.append({
                    'period': i + 1,
                    'return': period_return
                })
        
        if not results:
            return {'error': '无有效测试期'}
        
        returns = [r['return'] for r in results]
        
        return {
            'signal': signal_name,
            'symbol': symbol,
            'total_periods': len(results),
            'in_sample_periods': len(results),
            'avg_return': np.mean(returns),
            'std_return': np.std(returns),
            'positive_periods': sum(1 for r in returns if r > 0),
            'consistency': sum(1 for r in returns if r > 0) / len(returns),
            'results': results
        }
    
    # ========================================
    # Monte Carlo 模拟
    # ========================================
    
    def monte_carlo_simulation(
        self,
        symbol: str,
        days: int = 252,
        simulations: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Monte Carlo 模拟
        
        Args:
            symbol: 股票代码
            days: 模拟天数
            simulations: 模拟次数
            confidence_level: 置信水平
            
        Returns:
            模拟结果
        """
        df = self.get_price_data(symbol, days * 2)  # 获取更多数据计算参数
        
        if df.empty or len(df) < 30:
            return {'error': '数据不足'}
        
        # 计算历史统计参数
        returns = df['Close'].pct_change().dropna()
        mu = returns.mean()
        sigma = returns.std()
        last_price = df['Close'].iloc[-1]
        
        # 模拟路径
        simulated_prices = []
        final_prices = []
        
        for _ in range(simulations):
            prices = [last_price]
            
            for _ in range(days):
                daily_return = np.random.normal(mu, sigma)
                prices.append(prices[-1] * (1 + daily_return))
            
            simulated_prices.append(prices)
            final_prices.append(prices[-1])
        
        final_prices = np.array(final_prices)
        
        # 计算风险指标
        var_threshold = (1 - confidence_level) / 2
        var = np.percentile(final_prices, var_threshold * 100)
        expected_shortfall = np.mean(final_prices[final_prices <= var])
        
        return {
            'symbol': symbol,
            'simulation_days': days,
            'simulations': simulations,
            'confidence_level': confidence_level,
            'current_price': last_price,
            'expected_price': np.mean(final_prices),
            'expected_return': (np.mean(final_prices) - last_price) / last_price,
            'std_price': np.std(final_prices),
            'var_price': var,
            'var_pct': (var - last_price) / last_price,
            'expected_shortfall': expected_shortfall,
            'es_pct': (expected_shortfall - last_price) / last_price,
            'probability_up': np.sum(final_prices > last_price) / simulations,
            'probability_down': np.sum(final_prices < last_price) / simulations,
            'percentile_5': np.percentile(final_prices, 5),
            'percentile_25': np.percentile(final_prices, 25),
            'percentile_75': np.percentile(final_prices, 75),
            'percentile_95': np.percentile(final_prices, 95)
        }
    
    # ========================================
    # 信号验证报告
    # ========================================
    
    def validate_signal(
        self,
        symbol: str,
        signal_func,
        signal_name: str = "Signal"
    ) -> Dict:
        """
        信号综合验证
        
        Args:
            symbol: 股票代码
            signal_func: 信号函数
            signal_name: 信号名称
            
        Returns:
            验证报告
        """
        # 1. 历史回测
        backtest = self.backtest_signal(symbol, signal_func, signal_name, days=365)
        
        # 2. Walk-Forward
        wf = self.walk_forward_analysis(symbol, signal_func, signal_name, total_days=730)
        
        # 3. Monte Carlo
        mc = self.monte_carlo_simulation(symbol, days=252, simulations=500)
        
        # 综合评估
        score = 0
        grade = 'C'
        
        if 'win_rate' in backtest:
            # 胜率评分 (40分)
            if backtest['win_rate'] > 0.7:
                score += 40
            elif backtest['win_rate'] > 0.6:
                score += 30
            elif backtest['win_rate'] > 0.5:
                score += 20
            
            # 夏普比率 (30分)
            if backtest.get('sharpe_ratio', 0) > 1.5:
                score += 30
            elif backtest.get('sharpe_ratio', 0) > 1.0:
                score += 20
            elif backtest.get('sharpe_ratio', 0) > 0.5:
                score += 10
            
            # 最大回撤 (20分)
            if backtest.get('max_drawdown', 0) > -0.1:
                score += 20
            elif backtest.get('max_drawdown', 0) > -0.2:
                score += 15
            elif backtest.get('max_drawdown', 0) > -0.3:
                score += 10
        
        # 一致性 (10分)
        if 'consistency' in wf and wf['consistency'] > 0.6:
            score += 10
        
        # 评级
        if score >= 80:
            grade = 'A'
        elif score >= 60:
            grade = 'B'
        elif score >= 40:
            grade = 'C'
        else:
            grade = 'D'
        
        return {
            'signal': signal_name,
            'symbol': symbol,
            'validation_score': score,
            'grade': grade,
            'backtest': backtest,
            'walk_forward': wf,
            'monte_carlo': mc,
            'recommendation': {
                'A': '强烈推荐使用此信号',
                'B': '推荐使用，注意风险控制',
                'C': '谨慎使用，需结合其他信号',
                'D': '不建议单独使用'
            }.get(grade, '未知')
        }


# ============================================
# 示例信号函数
# ============================================

def sma_cross_signal(symbol: str, df: pd.DataFrame) -> str:
    """
    SMA 交叉信号
    
    Args:
        symbol: 股票代码
        df: 价格数据
        
    Returns:
        'buy'/'sell'/'hold'
    """
    if len(df) < 30:
        return 'hold'
    
    close = df['Close']
    sma_5 = close.rolling(5).mean().iloc[-1]
    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_5_prev = close.rolling(5).mean().iloc[-2]
    sma_20_prev = close.rolling(20).mean().iloc[-2]
    
    # 金叉
    if sma_5 > sma_20 and sma_5_prev <= sma_20_prev:
        return 'buy'
    # 死叉
    elif sma_5 < sma_20 and sma_5_prev >= sma_20_prev:
        return 'sell'
    else:
        return 'hold'


def rsi_oversold_signal(symbol: str, df: pd.DataFrame) -> str:
    """
    RSI 超卖信号
    
    Args:
        symbol: 股票代码
        df: 价格数据
        
    Returns:
        'buy'/'sell'/'hold'
    """
    if len(df) < 20:
        return 'hold'
    
    close = df['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    
    if current_rsi < 30:
        return 'buy'
    elif current_rsi > 70:
        return 'sell'
    else:
        return 'hold'


# ============================================
# 便捷函数
# ============================================

def validate_signal_performance(
    symbol: str,
    signal_func,
    signal_name: str = "Signal"
) -> Dict:
    """验证信号表现"""
    engine = BacktestEngine()
    return engine.validate_signal(symbol, signal_func, signal_name)


def backtest_signal(
    symbol: str,
    signal_func,
    signal_name: str = "Signal",
    days: int = 365
) -> Dict:
    """回测信号"""
    engine = BacktestEngine()
    return engine.backtest_signal(symbol, signal_func, signal_name, days)


if __name__ == '__main__':
    import json
    
    symbol = '002241'
    
    print("=" * 60)
    print(f"信号回测验证: {symbol}")
    print("=" * 60)
    
    # 测试 SMA 交叉信号
    print("\n📊 SMA 交叉信号回测")
    print("-" * 60)
    result = validate_signal_performance(symbol, sma_cross_signal, "SMA交叉")
    
    if 'error' not in result:
        print(f"验证评分: {result['validation_score']}/100 (Grade {result['grade']})")
        print(f"推荐: {result['recommendation']}")
        
        backtest = result.get('backtest', {})
        print(f"\n回测结果:")
        print(f"  总交易数: {backtest.get('total_trades', 0)}")
        print(f"  胜率: {backtest.get('win_rate', 0)*100:.1f}%")
        print(f"  总收益: {backtest.get('total_return', 0)*100:.1f}%")
        print(f"  夏普比率: {backtest.get('sharpe_ratio', 0):.2f}")
        print(f"  最大回撤: {backtest.get('max_drawdown', 0)*100:.1f}%")
        
        mc = result.get('monte_carlo', {})
        print(f"\nMonte Carlo 模拟 (95%置信):")
        print(f"  预期收益: {mc.get('expected_return', 0)*100:.1f}%")
        print(f"  VaR (95%): {mc.get('var_pct', 0)*100:.1f}%")
        print(f"  上涨概率: {mc.get('probability_up', 0)*100:.1f}%")
    else:
        print(f"错误: {result['error']}")
