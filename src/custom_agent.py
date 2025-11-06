import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from logger import LOG

class CustomAgent:
    def __init__(self, config, report_generator):
        self.config = config
        self.report_generator = report_generator
        self.tasks_file = "custom_tasks.json"
        self.tasks = self._load_tasks()

    def _load_tasks(self):
        import json
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    LOG.error("任务文件解析失败，重新初始化。")
                    return {}
        return {}

    def _save_tasks(self):
        import json
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def add_task(self, name, url, interval):
        """
        添加一个定时爬取任务。
        :param name: 任务名称
        :param url: 目标URL
        :param interval: 爬取间隔（秒）
        """
        self.tasks[name] = {"url": url, "interval": interval}
        self._save_tasks()
        LOG.info(f"新增任务：{name} | URL: {url} | 每 {interval}s 爬取一次")

    def remove_task(self, name):
        if name in self.tasks:
            del self.tasks[name]
            self._save_tasks()
            LOG.info(f"已删除任务：{name}")
        else:
            LOG.warning(f"未找到任务：{name}")

    def list_tasks(self):
        return self.tasks

    def fetch_content(self, url):
        """通用网页抓取逻辑"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            # 仅保留文本
            text = soup.get_text(separator="\n", strip=True)
            return text[:5000]  # 防止过长
        except Exception as e:
            LOG.error(f"抓取失败 {url}：{e}")
            return ""

    def run_task_once(self, name, url):
        """执行单次任务并生成报告"""
        content = self.fetch_content(url)
        if content:
            report_path = self.report_generator.generate_custom_report(name, url, content)
            LOG.info(f"[{name}] 报告生成完成：{report_path}")
        else:
            LOG.warning(f"[{name}] 未获取到有效内容")

    def start_scheduler(self):
        """启动定时任务"""
        LOG.info("启动自定义URL Agent 调度器...")

        def worker():
            while True:
                for name, task in self.tasks.items():
                    LOG.info(f"[执行任务] {name}")
                    self.run_task_once(name, task["url"])
                    time.sleep(1)
                time.sleep(10)  # 每 10 秒检查一次任务列表是否更新

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
