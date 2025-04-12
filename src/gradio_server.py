import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def add_subscription(repo):
    # 添加GitHub项目的订阅
    if subscription_manager.add_subscription(repo):
        subscriptions = subscription_manager.list_subscriptions()
        return gr.update(choices=subscriptions, value=repo), gr.update(choices=subscriptions), "项目已成功添加: " + repo
    else:
        subscriptions = subscription_manager.list_subscriptions()
        return gr.update(choices=subscriptions), gr.update(choices=subscriptions), "项目已存在: " + repo

def remove_subscription(repo):
    # 删除GitHub项目的订阅
    if subscription_manager.remove_subscription(repo):
        subscriptions = subscription_manager.list_subscriptions()
        return gr.update(choices=subscriptions), gr.update(choices=subscriptions), "项目已成功删除: " + repo
    else:
        subscriptions = subscription_manager.list_subscriptions()
        return gr.update(choices=subscriptions), gr.update(choices=subscriptions), "未找到该订阅: " + repo

# 创建Gradio界面
with gr.Blocks() as demo:
    gr.Markdown("# GitHubSentinel")
    
    with gr.Tab("生成报告"):
        repo_dropdown = gr.Dropdown(
            choices=subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目",allow_custom_value=True  # 添加此属性以允许自定义值
        )
        days_slider = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")
        report_button = gr.Button("生成报告")
        report_output = gr.Markdown()
        file_output = gr.File(label="下载报告")
        
        report_button.click(
            fn=export_progress_by_date_range,
            inputs=[repo_dropdown, days_slider],
            outputs=[report_output, file_output]
        )
    
    with gr.Tab("管理订阅"):
        add_repo_input = gr.Textbox(label="添加项目", placeholder="输入GitHub项目的完整路径，例如：username/repository")
        add_repo_button = gr.Button("添加订阅")
        add_result = gr.Markdown()
        remove_repo_input = gr.Textbox(label="删除项目", placeholder="输入GitHub项目的完整路径，例如：username/repository")
        remove_repo_button = gr.Button("删除订阅")
        remove_result = gr.Markdown()
        subscription_list_output = gr.Dropdown(
            choices=subscription_manager.list_subscriptions(), label="当前订阅列表", allow_custom_value=True
        )
        
        add_repo_button.click(
            fn=add_subscription,
            inputs=[add_repo_input],
            outputs=[repo_dropdown, subscription_list_output, add_result]
        )
        remove_repo_button.click(
            fn=remove_subscription,
            inputs=[remove_repo_input],
            outputs=[repo_dropdown, subscription_list_output, remove_result]
        )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
