import gradio as gr

from config import Config
from github_client import GitHubClient
from hacker_news_client import HackerNewsClient
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG

# 创建各个组件实例
config = Config()
github_client = GitHubClient(config.github_token)
hacker_news_client = HackerNewsClient()
subscription_manager = SubscriptionManager(config.subscriptions_file)

# --- 功能函数定义 ---
def generate_github_report(model_type, model_name, repo, days):
    config.llm_model_type = model_type
    if model_type == "openai":
        config.openai_model_name = model_name
    else:
        config.ollama_model_name = model_name

    llm = LLM(config)
    report_generator = ReportGenerator(llm, config.report_types)
    raw_file_path = github_client.export_progress_by_date_range(repo, days)
    report, report_file_path = report_generator.generate_github_report(raw_file_path)
    return report, report_file_path

def generate_hn_hour_topic(model_type, model_name):
    config.llm_model_type = model_type
    if model_type == "openai":
        config.openai_model_name = model_name
    else:
        config.ollama_model_name = model_name

    llm = LLM(config)
    report_generator = ReportGenerator(llm, config.report_types)
    markdown_file_path = hacker_news_client.export_top_stories()
    report, report_file_path = report_generator.generate_hn_topic_report(markdown_file_path)
    return report, report_file_path

def update_model_list(model_type):
    if model_type == "openai":
        return gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型", interactive=True)
    else:
        return gr.Dropdown(choices=["llama3.1", "gemma2:2b", "qwen2:7b"], label="选择模型", interactive=True)

# --- 优化版 Gradio 界面 ---
custom_css = """
.gradio-container {max-width: 900px; margin: auto;}
.logo {text-align: center; margin-bottom: 20px;}
.progress-bar {height: 10px; background: linear-gradient(to right, #4CAF50, #81C784); border-radius: 5px; margin-top: 10px;}
.dark-theme {background-color: #121212; color: #f1f1f1;}
"""

with gr.Blocks(title="GitHub Sentinel", theme=gr.themes.Soft(primary_hue="blue", secondary_hue="green"), css=custom_css) as demo:
    gr.HTML('<div class="logo"><img src="https://raw.githubusercontent.com/github/explore/main/topics/github/github.png" width="80" style="border-radius:50%"/></div>')
    gr.Markdown("# 🚀 GitHub Sentinel\nAI 驱动的开源项目与技术趋势监控平台")

    with gr.Tab("📊 GitHub 项目进展"):
        with gr.Row():
            with gr.Column(scale=1):
                model_type = gr.Radio(["openai", "ollama"], label="模型类型", value="openai", info="选择语言模型服务类型")
                model_name = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型", value="gpt-4o")
                subscription_list = gr.Dropdown(subscription_manager.list_subscriptions(), label="订阅项目", info="选择需要分析的GitHub仓库")
                days = gr.Slider(value=3, minimum=1, maximum=7, step=1, label="报告周期 (天)")
                generate_button = gr.Button("📘 生成进展报告", variant="primary")
                progress_bar = gr.HTML('<div class="progress-bar" style="width:0%"></div>')
            with gr.Column(scale=2):
                markdown_output = gr.Markdown(label="报告预览", value="生成的项目进展将在此显示。")
                file_output = gr.File(label="下载报告")

        model_type.change(fn=update_model_list, inputs=model_type, outputs=model_name)
        generate_button.click(generate_github_report, inputs=[model_type, model_name, subscription_list, days], outputs=[markdown_output, file_output])

    with gr.Tab("🔥 Hacker News 热点话题"):
        with gr.Row():
            with gr.Column(scale=1):
                model_type_hn = gr.Radio(["openai", "ollama"], label="模型类型", value="openai")
                model_name_hn = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型", value="gpt-4o")
                hn_button = gr.Button("📰 获取最新热点话题", variant="primary")
                progress_bar_hn = gr.HTML('<div class="progress-bar" style="width:0%"></div>')
            with gr.Column(scale=2):
                hn_output = gr.Markdown(label="热点摘要")
                hn_file_output = gr.File(label="下载报告")

        model_type_hn.change(fn=update_model_list, inputs=model_type_hn, outputs=model_name_hn)
        hn_button.click(generate_hn_hour_topic, inputs=[model_type_hn, model_name_hn], outputs=[hn_output, hn_file_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=True)
