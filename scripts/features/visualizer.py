#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逻辑可视化模块 - 饕餮整合自 alphaear-logic-visualizer
传导链路图、信号雷达图、情绪趋势图
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = Path(r'D:\OpenClaw\outputs')


class LogicVisualizer:
    """
    逻辑可视化器 - 饕餮整合自 alphaear-logic-visualizer
    
    能力:
    - 传导链路图 (Graph)
    - 信号质量雷达图
    - 情绪趋势图
    - Draw.io XML 生成
    """
    
    def __init__(self):
        self.charts_dir = OUTPUT_DIR / 'charts'
        self.charts_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_transmission_chain(
        self,
        nodes: List[Dict],
        title: str = "投资逻辑传导链条"
    ) -> Dict:
        """
        生成传导链路图
        
        Args:
            nodes: 节点列表 [{"name": "事件", "logic": "逻辑", "impact": "利好/利空"}]
            title: 图表标题
            
        Returns:
            图表数据和文件路径
        """
        result = {
            'nodes': nodes,
            'links': [],
            'chart_file': None,
            'drawio_xml': None,
            'error': None
        }
        
        try:
            # 构建节点数据
            chart_nodes = []
            links = []
            
            for i, node in enumerate(nodes):
                node_name = node.get('name', f'节点{i+1}')
                impact = node.get('impact', '中性')
                
                # 颜色
                if '利好' in impact or '正面' in impact:
                    color = '#22c55e'
                elif '利空' in impact or '负面' in impact:
                    color = '#ef4444'
                else:
                    color = '#6b7280'
                
                chart_nodes.append({
                    'name': node_name,
                    'value': node.get('logic', ''),
                    'color': color,
                    'size': 60 if i == 0 else 50
                })
                
                # 构建链接
                if i > 0:
                    links.append({
                        'source': chart_nodes[i-1]['name'],
                        'target': node_name
                    })
            
            result['nodes'] = chart_nodes
            result['links'] = links
            
            # 生成 Draw.io XML
            result['drawio_xml'] = self._generate_drawio_xml(nodes, title)
            
            # 生成 HTML
            html_file = self.charts_dir / f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            result['chart_file'] = self._render_graph_html(chart_nodes, links, title, html_file)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _generate_drawio_xml(self, nodes: List[Dict], title: str) -> str:
        """生成 Draw.io XML"""
        xml_parts = ['<mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">']
        xml_parts.append('<root><mxCell id="0"/><mxCell id="1" parent="0"/>')
        
        y_offset = 50
        prev_id = None
        
        for i, node in enumerate(nodes):
            node_id = str(i + 2)
            node_name = node.get('name', f'节点{i+1}')
            impact = node.get('impact', '中性')
            
            # 颜色
            if '利好' in impact or '正面' in impact:
                fill_color = '#d4edda'
                stroke_color = '#28a745'
            elif '利空' in impact or '负面' in impact:
                fill_color = '#f8d7da'
                stroke_color = '#dc3545'
            else:
                fill_color = '#e2e3e5'
                stroke_color = '#6c757d'
            
            # 节点
            xml_parts.append(f'''<mxCell id="{node_id}" value="{node_name}" style="rounded=1;whiteSpace=wrap;html=1;fillColor={fill_color};strokeColor={stroke_color};" vertex="1" parent="1">
<mxGeometry x="300" y="{y_offset}" width="200" height="60" as="geometry"/>
</mxCell>''')
            
            # 链接
            if prev_id:
                edge_id = str(i + 100)
                xml_parts.append(f'''<mxCell id="{edge_id}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="{prev_id}" target="{node_id}">
<mxGeometry relative="1" as="geometry"/>
</mxCell>''')
            
            prev_id = node_id
            y_offset += 100
        
        xml_parts.append('</root></mxGraphModel>')
        
        return ''.join(xml_parts)
    
    def _render_graph_html(self, nodes: List[Dict], links: List[Dict], title: str, filename: Path) -> str:
        """渲染图形 HTML"""
        try:
            import json
            
            # 构建 ECharts Graph 数据
            echarts_nodes = []
            for node in nodes:
                echarts_nodes.append({
                    'name': node['name'],
                    'symbolSize': node['size'],
                    'value': node['value'],
                    'itemStyle': {'color': node['color']}
                })
            
            echarts_links = []
            for link in links:
                echarts_links.append({
                    'source': link['source'],
                    'target': link['target']
                })
            
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 20px; }}
        #chart {{ width: 100%; height: 600px; }}
    </style>
</head>
<body>
    <h2>{title}</h2>
    <div id="chart"></div>
    <script>
        var chart = echarts.init(document.getElementById('chart'));
        var option = {{
            title: {{ text: '', left: 'center' }},
            tooltip: {{ formatter: '{{b}}: {{c}}' }},
            series: [{{
                type: 'graph',
                layout: 'force',
                data: {json.dumps(echarts_nodes, ensure_ascii=False)},
                links: {json.dumps(echarts_links, ensure_ascii=False)},
                roam: true,
                draggable: true,
                label: {{ show: true, position: 'inside', color: 'white' }},
                force: {{ repulsion: 5000, edgeLength: 100 }},
                edgeSymbol: ['circle', 'arrow'],
                edgeSymbolSize: [4, 10],
                lineStyle: {{ width: 2, curveness: 0.2 }}
            }}]
        }};
        chart.setOption(option);
    </script>
</body>
</html>'''
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return str(filename)
            
        except Exception as e:
            return None
    
    def generate_signal_radar(
        self,
        sentiment: float,
        confidence: float,
        intensity: int,
        expectation_gap: float = 0.5,
        timeliness: float = 0.8
    ) -> Dict:
        """
        生成信号质量雷达图
        
        Args:
            sentiment: 情绪分数 (-1 到 1)
            confidence: 置信度 (0 到 1)
            intensity: 强度 (1 到 5)
            expectation_gap: 预期差 (0 到 1)
            timeliness: 时效性 (0 到 1)
            
        Returns:
            雷达图数据
        """
        result = {
            'data': {
                'sentiment_strength': abs(sentiment),
                'confidence': confidence,
                'intensity': intensity / 5,
                'expectation_gap': expectation_gap,
                'timeliness': timeliness
            },
            'chart_file': None,
            'error': None
        }
        
        try:
            html_file = self.charts_dir / f"radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            result['chart_file'] = self._render_radar_html(result['data'], html_file)
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _render_radar_html(self, data: Dict, filename: Path) -> str:
        """渲染雷达图 HTML"""
        try:
            import json
            
            values = [
                data['sentiment_strength'] * 100,
                data['confidence'] * 100,
                data['intensity'] * 100,
                data['expectation_gap'] * 100,
                data['timeliness'] * 100
            ]
            
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>信号质量雷达图</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 20px; }}
        #chart {{ width: 100%; height: 500px; }}
    </style>
</head>
<body>
    <h2>信号质量 ISQ 评估</h2>
    <div id="chart"></div>
    <script>
        var chart = echarts.init(document.getElementById('chart'));
        var option = {{
            title: {{ text: '', left: 'center' }},
            radar: {{
                indicator: [
                    {{ name: '情绪强度', max: 100 }},
                    {{ name: '确定性', max: 100 }},
                    {{ name: '影响力', max: 100 }},
                    {{ name: '预期差', max: 100 }},
                    {{ name: '时效性', max: 100 }}
                ]
            }},
            series: [{{
                type: 'radar',
                data: [{{
                    value: {json.dumps(values)},
                    name: '信号特征',
                    areaStyle: {{ color: 'rgba(249, 115, 22, 0.3)' }},
                    lineStyle: {{ color: '#f97316' }}
                }}]
            }}]
        }};
        chart.setOption(option);
    </script>
</body>
</html>'''
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return str(filename)
            
        except Exception as e:
            return None
    
    def generate_sentiment_trend(
        self,
        sentiment_history: List[Dict]
    ) -> Dict:
        """
        生成情绪趋势图
        
        Args:
            sentiment_history: [{"date": "2024-01-01", "score": 0.8}, ...]
            
        Returns:
            趋势图数据
        """
        result = {
            'data': sentiment_history,
            'chart_file': None,
            'error': None
        }
        
        try:
            html_file = self.charts_dir / f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            result['chart_file'] = self._render_sentiment_html(sentiment_history, html_file)
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _render_sentiment_html(self, data: List[Dict], filename: Path) -> str:
        """渲染情绪趋势图 HTML"""
        try:
            import json
            
            dates = [d['date'] for d in data]
            scores = [d['score'] for d in data]
            
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>情绪趋势图</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 20px; }}
        #chart {{ width: 100%; height: 400px; }}
    </style>
</head>
<body>
    <h2>舆情情绪趋势</h2>
    <div id="chart"></div>
    <script>
        var chart = echarts.init(document.getElementById('chart'));
        var option = {{
            title: {{ text: '', left: 'center' }},
            xAxis: {{ type: 'category', data: {json.dumps(dates)} }},
            yAxis: {{ type: 'value', min: -1, max: 1, name: 'Sentiment' }},
            series: [{{
                type: 'line',
                data: {json.dumps(scores)},
                smooth: true,
                markLine: {{ data: [{{ yAxis: 0, name: '中性线' }}] }},
                areaStyle: {{ color: 'rgba(84, 112, 198, 0.3)' }},
                lineStyle: {{ color: '#5470c6', width: 2 }}
            }}],
            tooltip: {{ trigger: 'axis' }}
        }};
        chart.setOption(option);
    </script>
</body>
</html>'''
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return str(filename)
            
        except Exception as e:
            return None


def generate_transmission_chain(nodes: List[Dict], title: str = "投资逻辑传导链条") -> Dict:
    """生成传导链路图"""
    visualizer = LogicVisualizer()
    return visualizer.generate_transmission_chain(nodes, title)


def generate_signal_radar(sentiment: float, confidence: float, intensity: int, **kwargs) -> Dict:
    """生成信号雷达图"""
    visualizer = LogicVisualizer()
    return visualizer.generate_signal_radar(sentiment, confidence, intensity, **kwargs)


def generate_sentiment_trend(sentiment_history: List[Dict]) -> Dict:
    """生成情绪趋势图"""
    visualizer = LogicVisualizer()
    return visualizer.generate_sentiment_trend(sentiment_history)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='逻辑可视化 - 饕餮整合自 alphaear-logic-visualizer')
    parser.add_argument('--demo', action='store_true', help='生成演示图表')
    
    args = parser.parse_args()
    
    visualizer = LogicVisualizer()
    
    if args.demo:
        # 演示传导链路
        nodes = [
            {'name': '美联储加息', 'logic': '货币政策收紧', 'impact': '利空'},
            {'name': '美元走强', 'logic': '汇率上升', 'impact': '利空'},
            {'name': '黄金下跌', 'logic': '避险需求下降', 'impact': '利空'},
            {'name': 'A股承压', 'logic': '外资流出', 'impact': '利空'}
        ]
        result = visualizer.generate_transmission_chain(nodes, "加息传导链路")
        
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print("使用 --demo 生成演示图表")
