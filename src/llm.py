import os
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self):
         # 将这里换成你在便携AI聚合API后台生成的令牌
        os.environ	[	"OPENAI_API_KEY"	] = "sk-Y9P2ZYbyYK0HNbjBjj5s6yddubVCZ36WqCbXEVcYXSQMiaEm"
        # 这里将官方的接口访问地址替换成便携AI聚合API的入口地址
        os.environ	[	"OPENAI_BASE_URL"	] = "https://www.dmxapi.com/v1"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # 创建一个OpenAI客户端实例
        #self.client = OpenAI()
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 构建一个用于生成报告的提示文本，要求生成的报告包含新增功能、主要改进和问题修复
        prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报。请确保报告的格式清晰、语言准确、条理分明。简报至少包含以下三个部分：\n\n1. 新增功能：列出所有新添加的功能及其简要描述。\n2. 主要改进：总结所有重要的代码改进和优化措施。\n3. 修复问题：详细描述已解决的问题及其修复方法。\n\n{markdown_content}"
        
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个专业的技术文档编写助手，精通 Markdown 格式和项目管理。"},
                    {"role": "user", "content": prompt}
                ]
            )
            LOG.debug("GPT response: {}", response)
            LOG.debug("Daily report generated.")
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
