# src/command_handler.py

import argparse

import argparse  # 导入argparse库，用于处理命令行参数解析

class CommandHandler:
    def __init__(self, github_client, subscription_manager, report_generator):
        # 初始化CommandHandler，接收GitHub客户端、订阅管理器和报告生成器
        self.github_client = github_client
        self.subscription_manager = subscription_manager
        self.report_generator = report_generator
        self.parser = self.create_parser()  # 创建命令行解析器

    def create_parser(self):
        # 创建并配置命令行解析器
        parser = argparse.ArgumentParser(
            description='GitHub Sentinel Command Line Interface',
            formatter_class=argparse.RawTextHelpFormatter
        )
        subparsers = parser.add_subparsers(title='Commands', dest='command')

        # 添加订阅命令
        parser_add = subparsers.add_parser('add', help='Add a subscription')
        parser_add.add_argument('repo', type=str, help='The repository to subscribe to (e.g., owner/repo)')
        parser_add.set_defaults(func=self.add_subscription)

        # 删除订阅命令
        parser_remove = subparsers.add_parser('remove', help='Remove a subscription')
        parser_remove.add_argument('repo', type=str, help='The repository to unsubscribe from (e.g., owner/repo)')
        parser_remove.set_defaults(func=self.remove_subscription)

        # 列出所有订阅命令
        parser_list = subparsers.add_parser('list', help='List all subscriptions')
        parser_list.set_defaults(func=self.list_subscriptions)

        # 导出每日进展命令
        parser_export = subparsers.add_parser('export', help='Export daily progress')
        parser_export.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        parser_export.set_defaults(func=self.export_daily_progress)

        # 导出特定日期范围进展命令
        parser_export_range = subparsers.add_parser('export-range', help='Export progress over a range of dates')
        parser_export_range.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        parser_export_range.add_argument('days', type=int, help='The number of days to export progress for')
        parser_export_range.set_defaults(func=self.export_progress_by_date_range)

        # 生成日报命令
        parser_generate = subparsers.add_parser('generate', help='Generate daily report from markdown file')
        parser_generate.add_argument('file', type=str, help='The markdown file to generate report from')
        parser_generate.set_defaults(func=self.generate_daily_report)
        
        # 帮助命令
        parser_help = subparsers.add_parser('help', help='Show help message')
        parser_help.set_defaults(func=self.print_help)
        # 在 create_parser() 中添加以下命令
        # 在 create_parser() 中添加以下命令
        parser_hn = subparsers.add_parser('hn', help='Fetch Hacker News top stories')
        parser_hn.add_argument('--limit', type=int, default=10, help='Number of stories to fetch (default=10)')
        parser_hn.set_defaults(func=self.fetch_hackernews)
        # 在 create_parser() 中添加以下命令：
        parser_task_add = subparsers.add_parser('task-add', help='Add a custom crawling task')
        parser_task_add.add_argument('name', type=str, help='Task name')
        parser_task_add.add_argument('url', type=str, help='Target URL')
        parser_task_add.add_argument('interval', type=int, help='Crawl interval in seconds')
        parser_task_add.set_defaults(func=self.add_custom_task)

        parser_task_remove = subparsers.add_parser('task-remove', help='Remove a custom task')
        parser_task_remove.add_argument('name', type=str, help='Task name')
        parser_task_remove.set_defaults(func=self.remove_custom_task)

        parser_task_list = subparsers.add_parser('task-list', help='List all custom tasks')
        parser_task_list.set_defaults(func=self.list_custom_tasks)

        parser_task_run = subparsers.add_parser('task-run', help='Run a specific custom task once')
        parser_task_run.add_argument('name', type=str, help='Task name')
        parser_task_run.set_defaults(func=self.run_custom_task_once)


# 添加对应方法
    def fetch_hackernews(self, args):
        from hacker_news_client import HackerNewsClient
        hn_client = HackerNewsClient()
        stories = hn_client.fetch_top_stories(limit=args.limit)
        if not stories:
            print("⚠️  No stories found.")
            return
        report_path = self.report_generator.generate_hackernews_report(stories)
        print(f"✅ Hacker News report generated: {report_path}")

# 添加对应方法
    def fetch_hackernews(self, args):
        from hacker_news_client import HackerNewsClient
        hn_client = HackerNewsClient()
        stories = hn_client.fetch_top_stories(limit=args.limit)
        if not stories:
            print("⚠️  No stories found.")
            return
        report_path = self.report_generator.generate_hackernews_report(stories)
        print(f"✅ Hacker News report generated: {report_path}")
            return parser  # 返回配置好的解析器

    def add_custom_task(self, args):
        from custom_agent import CustomAgent
        agent = CustomAgent(self.github_client.config, self.report_generator)
        agent.add_task(args.name, args.url, args.interval)
        print(f"✅ Added custom task '{args.name}' for {args.url} every {args.interval}s")

    def remove_custom_task(self, args):
        from custom_agent import CustomAgent
        agent = CustomAgent(self.github_client.config, self.report_generator)
        agent.remove_task(args.name)
        print(f"🗑️ Removed task '{args.name}'")
    
    def list_custom_tasks(self, args):
        from custom_agent import CustomAgent
        agent = CustomAgent(self.github_client.config, self.report_generator)
        tasks = agent.list_tasks()
        if tasks:
            print("📋 Current tasks:")
            for name, t in tasks.items():
                print(f" - {name}: {t['url']} (interval={t['interval']}s)")
        else:
            print("⚠️ No tasks configured.")
    
    def run_custom_task_once(self, args):
        from custom_agent import CustomAgent
        agent = CustomAgent(self.github_client.config, self.report_generator)
        tasks = agent.list_tasks()
        if args.name not in tasks:
            print(f"❌ Task '{args.name}' not found.")
            return
        task = tasks[args.name]
        agent.run_task_once(args.name, task["url"])


    # 下面是各种命令对应的方法实现，每个方法都使用了相应的管理器来执行实际操作，并输出结果信息
    def add_subscription(self, args):
        self.subscription_manager.add_subscription(args.repo)
        print(f"Added subscription for repository: {args.repo}")

    def remove_subscription(self, args):
        self.subscription_manager.remove_subscription(args.repo)
        print(f"Removed subscription for repository: {args.repo}")

    def list_subscriptions(self, args):
        subscriptions = self.subscription_manager.list_subscriptions()
        print("Current subscriptions:")
        for sub in subscriptions:
            print(f"  - {sub}")

    def export_daily_progress(self, args):
        self.github_client.export_daily_progress(args.repo)
        print(f"Exported daily progress for repository: {args.repo}")

    def export_progress_by_date_range(self, args):
        self.github_client.export_progress_by_date_range(args.repo, days=args.days)
        print(f"Exported progress for the last {args.days} days for repository: {args.repo}")

    def generate_daily_report(self, args):
        self.report_generator.generate_daily_report(args.file)
        print(f"Generated daily report from file: {args.file}")

    def print_help(self, args=None):
        self.parser.print_help()  # 输出帮助信息
