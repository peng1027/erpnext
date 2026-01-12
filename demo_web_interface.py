#!/usr/bin/env python3
"""
Construction Inspection Module Web 演示界面
簡單的 Flask Web 應用程序來展示系統運行
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Construction Inspection Module - 演示系統</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .nav-tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .nav-tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .nav-tab:hover {
            background: #e9ecef;
        }
        
        .nav-tab.active {
            background: #007bff;
            color: white;
        }
        
        .tab-content {
            padding: 30px;
            min-height: 500px;
        }
        
        .tab-pane {
            display: none;
        }
        
        .tab-pane.active {
            display: block;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stat-card p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .data-table th {
            background: #343a40;
            color: white;
            padding: 15px;
            text-align: left;
        }
        
        .data-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .data-table tr:hover {
            background: #f8f9fa;
        }
        
        .status-badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status-completed { background: #d4edda; color: #155724; }
        .status-progress { background: #d1ecf1; color: #0c5460; }
        .status-draft { background: #f8d7da; color: #721c24; }
        .status-review { background: #fff3cd; color: #856404; }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            margin: 5px;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0056b3;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #1e7e34;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
            color: #6c757d;
        }
        
        .test-result {
            background: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        
        .test-result.failed {
            border-left-color: #dc3545;
        }
        
        .footer {
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Construction Inspection Module</h1>
            <p>建築檢查模組演示系統 - 實時運行狀態</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">儀表板</button>
            <button class="nav-tab" onclick="showTab('sites')">工地管理</button>
            <button class="nav-tab" onclick="showTab('inspections')">檢查記錄</button>
            <button class="nav-tab" onclick="showTab('tests')">系統測試</button>
        </div>
        
        <div class="tab-content">
            <!-- 儀表板 -->
            <div id="dashboard" class="tab-pane active">
                <h2>📊 系統概覽</h2>
                <div class="stats-grid" id="stats-grid">
                    <div class="loading">載入統計數據中...</div>
                </div>
                
                <h3>📈 最近活動</h3>
                <div id="recent-activity">
                    <div class="loading">載入活動記錄中...</div>
                </div>
            </div>
            
            <!-- 工地管理 -->
            <div id="sites" class="tab-pane">
                <h2>🏗️ 工地管理</h2>
                <button class="btn btn-primary" onclick="refreshSites()">🔄 刷新數據</button>
                <div id="sites-content">
                    <div class="loading">載入工地數據中...</div>
                </div>
            </div>
            
            <!-- 檢查記錄 -->
            <div id="inspections" class="tab-pane">
                <h2>📋 檢查記錄</h2>
                <button class="btn btn-primary" onclick="refreshInspections()">🔄 刷新數據</button>
                <div id="inspections-content">
                    <div class="loading">載入檢查記錄中...</div>
                </div>
            </div>
            
            <!-- 系統測試 -->
            <div id="tests" class="tab-pane">
                <h2>🧪 系統測試</h2>
                <button class="btn btn-success" onclick="runSystemTest()">▶️ 運行系統測試</button>
                <div id="test-results">
                    <div class="loading">點擊上方按鈕開始測試...</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 Construction Inspection Module - 演示版本</p>
            <p>最後更新: <span id="last-update">{{ current_time }}</span></p>
        </div>
    </div>

    <script>
        // 標籤切換
        function showTab(tabName) {
            // 隱藏所有標籤內容
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            
            // 移除所有標籤的活動狀態
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 顯示選中的標籤
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // 載入對應數據
            if (tabName === 'dashboard') {
                loadDashboard();
            } else if (tabName === 'sites') {
                loadSites();
            } else if (tabName === 'inspections') {
                loadInspections();
            }
        }
        
        // 載入儀表板數據
        async function loadDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                // 更新統計卡片
                const statsGrid = document.getElementById('stats-grid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <h3>${data.stats.total_sites}</h3>
                        <p>總工地數</p>
                    </div>
                    <div class="stat-card">
                        <h3>${data.stats.total_inspections}</h3>
                        <p>總檢查數</p>
                    </div>
                    <div class="stat-card">
                        <h3>${data.stats.completed_inspections}</h3>
                        <p>已完成檢查</p>
                    </div>
                    <div class="stat-card">
                        <h3>${Math.round(data.stats.completion_rate)}%</h3>
                        <p>完成率</p>
                    </div>
                `;
                
                // 更新最近活動
                const recentActivity = document.getElementById('recent-activity');
                recentActivity.innerHTML = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>時間</th>
                                <th>活動</th>
                                <th>狀態</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.recent_activities.map(activity => `
                                <tr>
                                    <td>${activity.time}</td>
                                    <td>${activity.description}</td>
                                    <td><span class="status-badge status-${activity.status.toLowerCase()}">${activity.status}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } catch (error) {
                console.error('載入儀表板數據失敗:', error);
            }
        }
        
        // 載入工地數據
        async function loadSites() {
            try {
                const response = await fetch('/api/sites');
                const data = await response.json();
                
                const sitesContent = document.getElementById('sites-content');
                sitesContent.innerHTML = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>工地名稱</th>
                                <th>供應商</th>
                                <th>狀態</th>
                                <th>創建時間</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.sites.slice(0, 20).map(site => `
                                <tr>
                                    <td>${site.site_name}</td>
                                    <td>${site.supplier}</td>
                                    <td><span class="status-badge status-${site.site_status.toLowerCase().replace(' ', '')}">${site.site_status}</span></td>
                                    <td>${new Date(site.creation).toLocaleString('zh-TW')}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } catch (error) {
                console.error('載入工地數據失敗:', error);
            }
        }
        
        // 載入檢查記錄
        async function loadInspections() {
            try {
                const response = await fetch('/api/inspections');
                const data = await response.json();
                
                const inspectionsContent = document.getElementById('inspections-content');
                inspectionsContent.innerHTML = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>檢查標題</th>
                                <th>工地</th>
                                <th>檢查員</th>
                                <th>狀態</th>
                                <th>檢查日期</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.inspections.slice(0, 20).map(inspection => `
                                <tr>
                                    <td>${inspection.inspection_title}</td>
                                    <td>${inspection.construction_site}</td>
                                    <td>${inspection.inspector_name}</td>
                                    <td><span class="status-badge status-${inspection.inspection_status.toLowerCase().replace(' ', '')}">${inspection.inspection_status}</span></td>
                                    <td>${new Date(inspection.inspection_date).toLocaleDateString('zh-TW')}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } catch (error) {
                console.error('載入檢查記錄失敗:', error);
            }
        }
        
        // 運行系統測試
        async function runSystemTest() {
            const testResults = document.getElementById('test-results');
            testResults.innerHTML = '<div class="loading">正在運行系統測試...</div>';
            
            try {
                const response = await fetch('/api/run-test', { method: 'POST' });
                const data = await response.json();
                
                testResults.innerHTML = `
                    <h3>測試結果 (${data.timestamp})</h3>
                    <div class="test-result">
                        <strong>總體結果:</strong> ${data.overall_result} 
                        (${data.passed_tests}/${data.total_tests} 通過, 成功率: ${data.success_rate}%)
                    </div>
                    ${data.test_details.map(test => `
                        <div class="test-result ${test.status === 'passed' ? '' : 'failed'}">
                            <strong>${test.name}:</strong> 
                            <span class="status-badge status-${test.status}">${test.status}</span>
                            ${test.error ? `<br><small>錯誤: ${test.error}</small>` : ''}
                        </div>
                    `).join('')}
                `;
            } catch (error) {
                testResults.innerHTML = `<div class="test-result failed">測試運行失敗: ${error.message}</div>`;
            }
        }
        
        // 刷新函數
        function refreshSites() {
            document.getElementById('sites-content').innerHTML = '<div class="loading">載入工地數據中...</div>';
            loadSites();
        }
        
        function refreshInspections() {
            document.getElementById('inspections-content').innerHTML = '<div class="loading">載入檢查記錄中...</div>';
            loadInspections();
        }
        
        // 頁面載入時初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            
            // 每30秒自動刷新儀表板
            setInterval(function() {
                if (document.getElementById('dashboard').classList.contains('active')) {
                    loadDashboard();
                }
            }, 30000);
        });
    </script>
</body>
</html>
"""

class DatabaseManager:
    def __init__(self, db_path="test_construction_inspection.db"):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_dashboard_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 基本統計
        cursor.execute("SELECT COUNT(*) as total FROM tabconstruction_site")
        total_sites = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM tabsupplier_inspection")
        total_inspections = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM tabsupplier_inspection WHERE inspection_status = 'Completed'")
        completed_inspections = cursor.fetchone()['total']
        
        completion_rate = (completed_inspections / max(total_inspections, 1)) * 100
        
        # 最近活動
        cursor.execute('''
            SELECT inspection_title, inspection_status, modified
            FROM tabsupplier_inspection
            ORDER BY modified DESC
            LIMIT 10
        ''')
        
        recent_activities = []
        for row in cursor.fetchall():
            recent_activities.append({
                'time': row['modified'][:19],
                'description': f"檢查: {row['inspection_title']}",
                'status': row['inspection_status']
            })
        
        conn.close()
        
        return {
            'stats': {
                'total_sites': total_sites,
                'total_inspections': total_inspections,
                'completed_inspections': completed_inspections,
                'completion_rate': completion_rate
            },
            'recent_activities': recent_activities
        }
    
    def get_sites(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, site_name, supplier, site_status, creation
            FROM tabconstruction_site
            ORDER BY creation DESC
        ''')
        
        sites = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {'sites': sites}
    
    def get_inspections(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT inspection_title, construction_site, inspector_name, 
                   inspection_status, inspection_date
            FROM tabsupplier_inspection
            ORDER BY inspection_date DESC
        ''')
        
        inspections = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {'inspections': inspections}

# 初始化數據庫管理器
db_manager = DatabaseManager()

@app.route('/')
def index():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE, current_time=current_time)

@app.route('/api/dashboard')
def api_dashboard():
    try:
        return jsonify(db_manager.get_dashboard_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sites')
def api_sites():
    try:
        return jsonify(db_manager.get_sites())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inspections')
def api_inspections():
    try:
        return jsonify(db_manager.get_inspections())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-test', methods=['POST'])
def api_run_test():
    try:
        # 運行系統測試
        import subprocess
        result = subprocess.run(['python', 'test_system_runner.py'], 
                              capture_output=True, text=True, cwd='.')
        
        # 讀取測試結果
        if os.path.exists('system_test_report.json'):
            with open('system_test_report.json', 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            passed_tests = sum(1 for test in test_data['test_results'] if test['status'] == 'passed')
            total_tests = len(test_data['test_results'])
            success_rate = (passed_tests / total_tests) * 100
            
            return jsonify({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'overall_result': '通過' if passed_tests == total_tests else '部分通過',
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'success_rate': round(success_rate, 1),
                'test_details': test_data['test_results']
            })
        else:
            return jsonify({'error': '測試報告文件不存在'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 啟動 Construction Inspection Module 演示界面...")
    print("📱 訪問地址: http://localhost:8080")
    print("🔄 系統將在 8080 端口運行")
    app.run(debug=True, host='0.0.0.0', port=8080)