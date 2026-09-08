import requests
import json
from typing import List, Dict, Any, Optional
import re
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from requests.auth import HTTPBasicAuth
from configs import BASE_URL, MODEL, API_KEY, get_api_config
from Prompts import PLAN_PROMPT, STEP_EXECUTION_PROMPT


class MCPToolMatcher:
    def __init__(self, mcp_tools_file: str = "./Evaluation/mcp_tools.jsonl"):
        """初始化MCP工具匹配器"""
        self.mcp_tools_file = mcp_tools_file
        self.mcp_tools = []
        self.embeddings = None
        self.model = None
        self.load_mcp_tools()
        self.load_embedding_model()
    
    def load_embedding_model(self):
        """加载embedding模型"""
        try:
            # 尝试多种可能的模型路径
            possible_paths = [
                # "./Evaluation/bge-m3",
                "BAAI/bge-m3"  # 从HuggingFace Hub下载
            ]
            
            for model_path in possible_paths:
                try:
                    print(f"🔄 正在尝试加载embedding模型: {model_path}")
                    self.model = SentenceTransformer(model_path)
                    print("✅ Embedding模型加载完成")
                    return
                except Exception as e:
                    print(f"⚠️ 路径 {model_path} 加载失败: {e}")
                    continue
            
            print("❌ 所有模型路径都加载失败")
            self.model = None
        except Exception as e:
            print(f"❌ Embedding模型加载失败: {e}")
            self.model = None
    
    def load_mcp_tools(self):
        """加载MCP工具数据"""
        if not os.path.exists(self.mcp_tools_file):
            print(f"⚠️ MCP工具文件不存在: {self.mcp_tools_file}")
            return
        
        try:
            with open(self.mcp_tools_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        tool = json.loads(line.strip())
                        self.mcp_tools.append(tool)
            print(f"✅ 成功加载 {len(self.mcp_tools)} 个MCP工具")
        except Exception as e:
            print(f"❌ 加载MCP工具失败: {e}")
    
    def compute_embeddings(self):
        """计算所有MCP工具的embedding"""
        if not self.model or not self.mcp_tools:
            return
        
        try:
            # 为每个MCP工具创建描述文本
            tool_texts = []
            for tool in self.mcp_tools:
                # 组合工具名称、描述和参数信息作为语义匹配的文本
                text = f"{tool['name']}: {tool['description']}. Arguments: {tool['arguments']}. Returns: {tool['returns']}"
                tool_texts.append(text)
            
            # 计算embeddings
            print("🔄 正在计算MCP工具embeddings...")
            self.embeddings = self.model.encode(tool_texts)
            print("✅ MCP工具embeddings计算完成")
        except Exception as e:
            print(f"❌ 计算embeddings失败: {e}")
            self.embeddings = None
    
    def find_similar_tools(self, step_description: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """根据步骤描述找到最相似的MCP工具"""
        if not self.model or not self.mcp_tools or self.embeddings is None:
            return []
        
        try:
            # 计算步骤描述的embedding
            step_embedding = self.model.encode([step_description])
            
            # 计算相似度
            similarities = np.dot(self.embeddings, step_embedding.T).flatten()
            
            # 获取top_k个最相似的工具
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            similar_tools = []
            for idx in top_indices:
                tool = self.mcp_tools[idx].copy()
                tool['similarity_score'] = float(similarities[idx])
                similar_tools.append(tool)
            
            return similar_tools
        except Exception as e:
            print(f"❌ 查找相似工具失败: {e}")
            return []


class AgentWorkflow:
    def __init__(self, enable_mcp_matching: bool = True, include_mcp_code: bool = True):
        self.model = MODEL
        
        # 根据模型类型获取API配置
        self.api_config = get_api_config(self.model)
        self.api_url = self.api_config["api_url"]
        self.auth_type = self.api_config["auth_type"]
        
        # 设置认证信息
        if self.auth_type == "basic":
            # Qwen模型使用Basic Auth
            self.api_ak = self.api_config["api_ak"]
            self.api_sk = self.api_config["api_sk"]
            self.headers = {
                "Content-Type": "application/json"
            }
            print(f"🔧 使用Basic Auth认证 (Qwen模型): {self.model}")
        else:
            # 其他模型使用Bearer Token
            self.api_key = self.api_config["api_key"]
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            print(f"🔧 使用Bearer Token认证: {self.model}")
            
        # 保持向后兼容性
        self.base_url = BASE_URL
        
        # MCP工具匹配配置
        self.enable_mcp_matching = enable_mcp_matching
        self.include_mcp_code = include_mcp_code
        self.mcp_matcher = None
        
        # 初始化MCP工具匹配器
        if self.enable_mcp_matching:
            self.mcp_matcher = MCPToolMatcher()
            self.mcp_matcher.compute_embeddings()
    
    def format_mcp_tools_for_prompt(self, similar_tools: List[Dict[str, Any]]) -> str:
        """将相似的MCP工具格式化为prompt文本"""
        if not similar_tools:
            return "No similar MCP tools found."
        
        formatted_tools = []
        for i, tool in enumerate(similar_tools, 1):
            tool_info = f"{i}. **{tool['name']}**\n"
            tool_info += f"   - Description: {tool['description']}\n"
            tool_info += f"   - Arguments: {tool['arguments']}\n"
            tool_info += f"   - Returns: {tool['returns']}\n"
            if tool.get('requires'):
                tool_info += f"   - Requires: {tool['requires']}\n"
            tool_info += f"   - Similarity Score: {tool['similarity_score']:.3f}\n"
            
            # 可选择是否包含代码
            if self.include_mcp_code and 'code' in tool:
                tool_info += f"   - Code:\n```python\n{tool['code']}\n```\n"
            
            formatted_tools.append(tool_info)
        
        return "\n".join(formatted_tools)
    
    def _call_llm(self, messages: List[Dict[str, str]], max_tokens: int = 2000) -> str:
        """调用LLM API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        # FREE-MODEL PATCH: retry/backoff for flaky free providers (intermittent 402/429/5xx)
        import time as _time
        delay = 5.0
        for attempt in range(8):
            try:
                if self.auth_type == "basic":
                    response = requests.post(
                        self.api_url, headers=self.headers, json=payload,
                        auth=HTTPBasicAuth(self.api_ak, self.api_sk),
                        timeout=180, verify=False
                    )
                else:
                    response = requests.post(
                        self.api_url, headers=self.headers, json=payload,
                        timeout=180, verify=False
                    )
            except Exception as e:
                print(f"API request error (attempt {attempt+1}): {e}")
                _time.sleep(delay); delay = min(delay*1.7, 90); continue
            if response.status_code == 200:
                try:
                    result = response.json()
                    content = result["choices"][0]["message"].get("content")
                    if content and content.strip():
                        return content
                    print(f"empty content (attempt {attempt+1}): {response.text[:120]}")
                except Exception as e:
                    print(f"parse error (attempt {attempt+1}): {e}")
            else:
                print(f"API {response.status_code} (attempt {attempt+1}): {response.text[:120]}")
            _time.sleep(delay); delay = min(delay*1.7, 90)
        print(f"API调用失败 after retries. model={self.model} url={self.api_url}")
        return ""
    
    def generate_plan(self, task: str, max_turns: int = 6) -> str:
        """生成任务计划"""
        print("🔄 正在生成计划...")
        
        # 查找与任务相关的MCP工具（用于计划生成）
        similar_tools_text = "No existing MCP tools available."
        if self.enable_mcp_matching and self.mcp_matcher and self.mcp_matcher.model:
            print(f"🔍 正在为计划生成查找相关的MCP工具...")
            similar_tools = self.mcp_matcher.find_similar_tools(task, top_k=5)  # 计划阶段使用Top-5
            if similar_tools:
                print(f"✅ 找到 {len(similar_tools)} 个相关的MCP工具用于计划生成")
                for i, tool in enumerate(similar_tools, 1):
                    print(f"   {i}. {tool['name']} (相似度: {tool['similarity_score']:.3f})")
                similar_tools_text = self.format_mcp_tools_for_prompt(similar_tools)
            else:
                print("⚠️ 未找到相关的MCP工具")
        
        # 替换prompt中的模板变量
        plan_prompt = PLAN_PROMPT.replace("{{task}}", task)
        plan_prompt = plan_prompt.replace("{{max_turns - 1}}", str(max_turns - 1))
        plan_prompt = plan_prompt.replace("{{existing_mcp_tools}}", similar_tools_text)
        
        messages = [
            {"role": "user", "content": plan_prompt}
        ]
        
        plan = self._call_llm(messages, max_tokens=1500)
        print("✅ 计划生成完成")
        return plan
    
    def parse_plan_steps(self, plan: str) -> List[str]:
        """解析计划中的步骤"""
        steps = []
        
        # 寻找##ST开头的步骤
        step_pattern = r'##(ST\d+):(.*?)(?=##ST\d+:|$)'
        matches = re.findall(step_pattern, plan, re.DOTALL)
        
        for step_id, step_content in matches:
            step_text = f"{step_id}: {step_content.strip()}"
            steps.append(step_text)
        
        return steps
    
    def extract_code_and_mcps(self, result: str) -> str:
        """从执行结果中提取Python代码和MCP工具"""
        extracted_content = []
        
        # 提取Python代码块
        python_pattern = r'<python>(.*?)</python>'
        python_matches = re.findall(python_pattern, result, re.DOTALL)
        
        for i, code in enumerate(python_matches, 1):
            code = code.strip()
            if code:
                # 检查是否是MCP工具定义
                if "# MCP Name:" in code:
                    extracted_content.append(f"### MCP Tool {i}:\n```python\n{code}\n```")
                else:
                    extracted_content.append(f"### Python Code {i}:\n```python\n{code}\n```")
        
        return "\n\n".join(extracted_content) if extracted_content else "No previous code or MCP tools available."
    
    def execute_step(self, task: str, plan: str, step: str, step_number: int, context: str = "") -> str:
        """执行单个步骤"""
        print(f"🔄 正在执行步骤 {step_number}: {step}...")
        
        # 查找相似的MCP工具
        similar_tools_text = "No similar MCP tools found."
        if self.enable_mcp_matching and self.mcp_matcher and self.mcp_matcher.model:
            print(f"🔍 正在查找与步骤相似的MCP工具...")
            similar_tools = self.mcp_matcher.find_similar_tools(step, top_k=3)
            if similar_tools:
                print(f"✅ 找到 {len(similar_tools)} 个相似的MCP工具")
                for i, tool in enumerate(similar_tools, 1):
                    print(f"   {i}. {tool['name']} (相似度: {tool['similarity_score']:.3f})")
                similar_tools_text = self.format_mcp_tools_for_prompt(similar_tools)
            else:
                print("⚠️ 未找到相似的MCP工具")
        
        # 构建执行prompt
        execution_prompt = STEP_EXECUTION_PROMPT.replace("{{question}}", task)
        execution_prompt = execution_prompt.replace("{{input_plan}}", plan)
        execution_prompt = execution_prompt.replace("{{max_turns - 1}}", "5")
        execution_prompt = execution_prompt.replace("{{context}}", context)
        execution_prompt = execution_prompt.replace("{{existing_mcp_tools}}", similar_tools_text)
        
        # 添加当前步骤的具体指令
        step_instruction = f"\n\nNow execute this specific step: {step}\n"
        step_instruction += "Please provide the action/code for this step only, following the format specified in the prompt."
        
        messages = [
            {"role": "user", "content": execution_prompt + step_instruction}
        ]
        
        result = self._call_llm(messages, max_tokens=2000)
        print(f"✅ 步骤 {step_number} 执行完成")
        return result
    
    def run_workflow(self, task: str, max_turns: int = 3) -> Dict[str, Any]:
        """运行完整的工作流程"""
        print("🚀 开始执行Agent工作流程")
        print(f"📝 任务: {task}")
        print("=" * 80)
        
        # 1. 生成计划
        plan = self.generate_plan(task, max_turns)
        
        if not plan:
            return {"error": "计划生成失败"}
        
        print("\n📋 生成的计划:")
        print("-" * 40)
        print(plan)
        print("-" * 40)
        
        # 2. 解析步骤
        steps = self.parse_plan_steps(plan)
        
        if not steps:
            print("⚠️  未能解析出有效步骤，使用原始计划")
            steps = [plan]
        
        print(f"\n🔍 解析出 {len(steps)} 个步骤:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}...")
        
        print("\n" + "=" * 80)
        
        # 3. 执行每个步骤
        results = []
        accumulated_context = ""
        
        for i, step in enumerate(steps, 1):
            print(f"\n📍 执行步骤 {i}/{len(steps)}")
            
            # 执行当前步骤，传入累积的context
            result = self.execute_step(task, plan, step, i, accumulated_context)
            
            # 提取当前步骤的代码和MCP工具，添加到累积context中
            current_context = self.extract_code_and_mcps(result)
            if current_context != "No previous code or MCP tools available.":
                if accumulated_context:
                    accumulated_context += f"\n\n## Step {i} Generated Content:\n{current_context}"
                else:
                    accumulated_context = f"## Step {i} Generated Content:\n{current_context}"
            
            results.append({
                "step_number": i,
                "step_description": step,
                "result": result,
                "extracted_context": current_context
            })
            print(f"📄 步骤 {i} 结果:")
            print("-" * 40)
            print(result + "..." if len(result) > 500 else result)
            print("-" * 40)
            
            # 显示累积的context（仅用于调试）
            if accumulated_context:
                print(f"📚 累积Context长度: {len(accumulated_context)} 字符")
            else:
                print("📚 暂无可用Context")
        
        return {
            "task": task,
            "plan": plan,
            "steps": steps,
            "results": results,
            "total_steps": len(steps)
        }

    def set_mcp_matching_config(self, enable_mcp_matching: bool = None, include_mcp_code: bool = None):
        """动态设置MCP工具匹配配置"""
        if enable_mcp_matching is not None:
            self.enable_mcp_matching = enable_mcp_matching
            if enable_mcp_matching and self.mcp_matcher is None:
                print("🔄 启用MCP匹配，正在初始化匹配器...")
                self.mcp_matcher = MCPToolMatcher()
                self.mcp_matcher.compute_embeddings()
            elif not enable_mcp_matching:
                print("⚠️ 禁用MCP匹配功能")
        
        if include_mcp_code is not None:
            self.include_mcp_code = include_mcp_code
            print(f"📝 MCP代码包含设置: {'启用' if include_mcp_code else '禁用'}")
    
    def get_mcp_tools_stats(self) -> Dict[str, Any]:
        """获取MCP工具统计信息"""
        if not self.mcp_matcher:
            return {"enabled": False, "tools_count": 0}
        
        return {
            "enabled": self.enable_mcp_matching,
            "include_code": self.include_mcp_code,
            "tools_count": len(self.mcp_matcher.mcp_tools),
            "model_loaded": self.mcp_matcher.model is not None,
            "embeddings_computed": self.mcp_matcher.embeddings is not None
        }


def main():
    """主函数，用于测试工作流程"""
    workflow = AgentWorkflow()
    
    # 示例任务
    task = """def get_target_for_redirect(target: str, domain: str) -> str:
    '''
    Check if the provided target URL string is within the provided domain.
    If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
    Use https protocol.

    Examples:
        get_target_for_redirect('https://music.example.com', 'example.com') -> 'https://music.example.com'
        get_target_for_redirect('https://example.com/service', 'example.com') -> 'https://example.com/service'
        get_target_for_redirect('https://blog.example.com/posts', 'example.com') -> 'https://blog.example.com/posts'
        get_target_for_redirect('https://another.com', 'example.com') -> 'https://example.com'

    Args:
        target (str): The target URL string.
        domain (str): The domain string, without protocol.

    Returns:
        str: The URL string for redirect.
    '''"""
    
    # 运行工作流程
    result = workflow.run_workflow(task)
    
    # 保存结果
    with open("./workflow_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n🎉 工作流程完成！结果已保存到 workflow_result.json")


if __name__ == "__main__":
    main() 