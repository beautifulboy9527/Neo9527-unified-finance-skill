#!/usr/bin/env python3
"""
Portfolio Manager - 投资组合管理
支持持仓记录、盈亏计算、组合分析
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# 配置文件路径 - 统一输出目录
PORTFOLIO_FILE = os.path.join(
    r'D:\OpenClaw\outputs\data',
    'portfolio.json'
)


class PortfolioManager:
    """投资组合管理器"""
    
    def __init__(self):
        self.portfolio_file = PORTFOLIO_FILE
        self._ensure_config_dir()
        self.portfolio = self._load_portfolio()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.portfolio_file)
        os.makedirs(config_dir, exist_ok=True)
    
    def _load_portfolio(self) -> Dict:
        """加载持仓数据"""
        if os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'positions': [], 'cash': 1000000, 'created_at': datetime.now().isoformat()}
    
    def _save_portfolio(self):
        """保存持仓数据"""
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, ensure_ascii=False, indent=2)
    
    def add_position(self, symbol: str, quantity: float, cost_price: float, 
                     position_type: str = 'stock'):
        """
        添加持仓
        
        Args:
            symbol: 股票代码
            quantity: 数量
            cost_price: 成本价
            position_type: 类型 (stock/crypto/cash)
        """
        position = {
            'id': len(self.portfolio['positions']) + 1,
            'symbol': symbol.upper(),
            'quantity': quantity,
            'cost_price': cost_price,
            'cost_basis': quantity * cost_price,
            'type': position_type,
            'created_at': datetime.now().isoformat()
        }
        
        self.portfolio['positions'].append(position)
        self.portfolio['cash'] -= position['cost_basis']
        self._save_portfolio()
        
        print(f"[OK] 已添加持仓：{symbol} x {quantity} @ {cost_price}")
    
    def remove_position(self, position_id: int):
        """移除持仓"""
        for i, pos in enumerate(self.portfolio['positions']):
            if pos['id'] == position_id:
                self.portfolio['cash'] += pos['cost_basis']
                removed = self.portfolio['positions'].pop(i)
                self._save_portfolio()
                print(f"[OK] 已移除持仓：{removed['symbol']}")
                return
        print(f"[FAIL] 未找到持仓 ID: {position_id}")
    
    def update_price(self, symbol: str, current_price: float):
        """更新股票当前价（用于计算盈亏）"""
        for pos in self.portfolio['positions']:
            if pos['symbol'] == symbol.upper():
                pos['current_price'] = current_price
                pos['market_value'] = pos['quantity'] * current_price
                pos['unrealized_pnl'] = pos['market_value'] - pos['cost_basis']
                pos['unrealized_pnl_pct'] = (pos['unrealized_pnl'] / pos['cost_basis']) * 100
                pos['last_updated'] = datetime.now().isoformat()
    
    def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        return self.portfolio['positions']
    
    def get_summary(self) -> Dict:
        """获取组合摘要"""
        import yfinance as yf
        
        total_cost = sum(pos['cost_basis'] for pos in self.portfolio['positions'])
        total_market_value = 0
        total_pnl = 0
        
        positions_data = []
        
        for pos in self.portfolio['positions']:
            # 获取当前价格
            try:
                ticker = yf.Ticker(pos['symbol'])
                info = ticker.info
                current_price = info.get('regularMarketPrice') or info.get('currentPrice')
                
                if current_price:
                    self.update_price(pos['symbol'], current_price)
                    
                    market_value = pos.get('market_value', pos['cost_basis'])
                    pnl = pos.get('unrealized_pnl', 0)
                    pnl_pct = pos.get('unrealized_pnl_pct', 0)
                    
                    total_market_value += market_value
                    total_pnl += pnl
                    
                    positions_data.append({
                        'symbol': pos['symbol'],
                        'quantity': pos['quantity'],
                        'cost_price': pos['cost_price'],
                        'current_price': current_price,
                        'market_value': market_value,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct
                    })
            except Exception:
                positions_data.append({
                    'symbol': pos['symbol'],
                    'quantity': pos['quantity'],
                    'cost_price': pos['cost_price'],
                    'current_price': None,
                    'market_value': pos['cost_basis'],
                    'pnl': 0,
                    'pnl_pct': 0
                })
        
        return {
            'cash': self.portfolio['cash'],
            'total_cost': total_cost,
            'total_market_value': total_market_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / total_cost * 100) if total_cost else 0,
            'positions': positions_data,
            'position_count': len(positions_data)
        }
    
    def analyze_allocation(self) -> Dict:
        """分析持仓配置"""
        summary = self.get_summary()
        positions = summary['positions']
        
        if not positions:
            return {'allocation': [], 'concentration': {}}
        
        total_value = summary['total_market_value']
        
        allocation = []
        for pos in positions:
            weight = (pos['market_value'] / total_value * 100) if total_value else 0
            allocation.append({
                'symbol': pos['symbol'],
                'weight': round(weight, 2),
                'market_value': pos['market_value']
            })
        
        # 按权重排序
        allocation = sorted(allocation, key=lambda x: x['weight'], reverse=True)
        
        # 集中度分析
        top_3_weight = sum(a['weight'] for a in allocation[:3])
        top_5_weight = sum(a['weight'] for a in allocation[:5])
        
        return {
            'allocation': allocation,
            'concentration': {
                'top_3': round(top_3_weight, 2),
                'top_5': round(top_5_weight, 2),
                'total_positions': len(allocation)
            }
        }


def format_portfolio_summary(summary: Dict) -> str:
    """格式化组合摘要"""
    lines = [
        "=" * 60,
        "  投资组合摘要",
        "=" * 60,
        "",
        f"现金：{summary['cash']:,.2f}",
        f"总成本：{summary['total_cost']:,.2f}",
        f"总市值：{summary['total_market_value']:,.2f}",
        f"总盈亏：{summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.2f}%)",
        f"持仓数：{summary['position_count']}",
        "",
        "-" * 60,
        "  持仓明细",
        "-" * 60,
    ]
    
    for pos in summary['positions']:
        pnl_color = "green" if pos['pnl'] >= 0 else "red"
        lines.append(
            f"{pos['symbol']:10} | {pos['quantity']:>10} | "
            f"成本：{pos['cost_price']:>8.2f} | "
            f"现价：{str(pos['current_price']):>8} | "
            f"盈亏：{pos['pnl']:>+10,.2f} ({pos['pnl_pct']:+.2f}%)"
        )
    
    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == '__main__':
    pm = PortfolioManager()
    
    if len(sys.argv) < 2:
        print("用法：python portfolio_manager.py <命令> [参数]")
        print("\n命令:")
        print("  add <symbol> <quantity> <cost_price>  # 添加持仓")
        print("  remove <id>                            # 移除持仓")
        print("  list                                   # 列出持仓")
        print("  summary                                # 组合摘要")
        print("  analyze                                # 配置分析")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'add' and len(sys.argv) >= 5:
        symbol = sys.argv[2]
        quantity = float(sys.argv[3])
        cost_price = float(sys.argv[4])
        pm.add_position(symbol, quantity, cost_price)
    
    elif command == 'remove' and len(sys.argv) >= 3:
        position_id = int(sys.argv[2])
        pm.remove_position(position_id)
    
    elif command == 'list':
        positions = pm.get_positions()
        if positions:
            print("\n当前持仓:")
            for pos in positions:
                print(f"  {pos['id']}. {pos['symbol']} x {pos['quantity']} @ {pos['cost_price']}")
        else:
            print("无持仓")
    
    elif command == 'summary':
        summary = pm.get_summary()
        print(format_portfolio_summary(summary))
    
    elif command == 'analyze':
        allocation = pm.analyze_allocation()
        print("\n持仓配置分析:")
        for alloc in allocation['allocation']:
            print(f"  {alloc['symbol']:10} {alloc['weight']:>6.2f}%  ({alloc['market_value']:,.0f})")
        print(f"\n集中度:")
        print(f"  前 3 大：{allocation['concentration']['top_3']}%")
        print(f"  前 5 大：{allocation['concentration']['top_5']}%")
    
    else:
        print(f"未知命令：{command}")
