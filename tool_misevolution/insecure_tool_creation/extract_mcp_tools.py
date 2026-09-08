import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

class MCPToolExtractor:
    def __init__(self):
        self.trajs_dir = "./trajectories"
        self.output_file = "mcp_tools.jsonl"  # FREE-MODEL PATCH: .jsonl so summary writes to a separate file
        
    def extract_mcp_from_code_block(self, code_block: str) -> Dict[str, Any]:
        """从代码块中提取MCP工具信息"""
        mcp_info = {}
        
        # 查找MCP注释行
        mcp_name_match = re.search(r'#\s*(?:MCP|Tool) Name:\s*(.+)', code_block)  # FREE-MODEL PATCH: executor emits '# Tool Name:'
        mcp_desc_match = re.search(r'# Description:\s*(.+)', code_block)
        mcp_args_match = re.search(r'# Arguments:\s*(.+)', code_block)
        mcp_returns_match = re.search(r'# Returns:\s*(.+)', code_block)
        mcp_requires_match = re.search(r'# Requires:\s*(.+)', code_block)
        
        if mcp_name_match:
            mcp_info['name'] = mcp_name_match.group(1).strip()
        else:
            return None  # 不是MCP工具
            
        if mcp_desc_match:
            mcp_info['description'] = mcp_desc_match.group(1).strip()
        
        if mcp_args_match:
            mcp_info['arguments'] = mcp_args_match.group(1).strip()
        
        if mcp_returns_match:
            mcp_info['returns'] = mcp_returns_match.group(1).strip()
            
        if mcp_requires_match:
            mcp_info['requires'] = mcp_requires_match.group(1).strip()
        
        # 提取函数定义
        func_match = re.search(r'def\s+(\w+)\s*\([^)]*\):', code_block)
        if func_match:
            mcp_info['function_name'] = func_match.group(1)
        
        # 提取完整的代码
        mcp_info['code'] = code_block.strip()
        
        return mcp_info
    
    def extract_mcp_tools_from_trajectory(self, traj_file: str) -> List[Dict[str, Any]]:
        """从单个轨迹文件中提取所有MCP工具"""
        mcp_tools = []
        
        try:
            with open(traj_file, 'r', encoding='utf-8') as f:
                trajectory = json.load(f)
            
            task_name = trajectory.get('task_name', 'unknown')
            workflow_execution = trajectory.get('workflow_execution', {})
            results = workflow_execution.get('results', [])
            
            for result in results:
                step_number = result.get('step_number', 0)
                step_description = result.get('step_description', '')
                extracted_context = result.get('extracted_context', '')
                
                # 查找MCP工具块
                mcp_pattern = r'### (?:MCP Tool|Python Code) \d+:\s*```python\s*(.*?)\s*```'  # FREE-MODEL PATCH: tools mislabeled as 'Python Code'
                mcp_matches = re.findall(mcp_pattern, extracted_context, re.DOTALL)
                
                for i, mcp_code in enumerate(mcp_matches, 1):
                    mcp_info = self.extract_mcp_from_code_block(mcp_code)
                    
                    if mcp_info:
                        # 添加上下文信息
                        mcp_info['source_task'] = task_name
                        mcp_info['step_number'] = step_number
                        mcp_info['step_description'] = step_description
                        mcp_info['tool_index_in_step'] = i
                        mcp_info['extracted_at'] = datetime.now().isoformat()
                        
                        mcp_tools.append(mcp_info)
                        
        except Exception as e:
            print(f"❌ 处理轨迹文件 {traj_file} 时出错: {e}")
        
        return mcp_tools
    
    def get_all_trajectory_files(self) -> List[str]:
        """获取所有轨迹文件"""
        traj_files = []
        
        if not os.path.exists(self.trajs_dir):
            print(f"❌ 轨迹目录不存在: {self.trajs_dir}")
            return traj_files
        
        for file in os.listdir(self.trajs_dir):
            if file.endswith('_trajectory.json'):
                traj_files.append(os.path.join(self.trajs_dir, file))
        
        return sorted(traj_files)
    
    def extract_all_mcp_tools(self) -> List[Dict[str, Any]]:
        """提取所有轨迹文件中的MCP工具"""
        all_mcp_tools = []
        traj_files = self.get_all_trajectory_files()
        
        print(f"🔍 发现 {len(traj_files)} 个轨迹文件")
        
        for i, traj_file in enumerate(traj_files, 1):
            print(f"📄 处理文件 {i}/{len(traj_files)}: {os.path.basename(traj_file)}")
            
            mcp_tools = self.extract_mcp_tools_from_trajectory(traj_file)
            all_mcp_tools.extend(mcp_tools)
            
            print(f"   找到 {len(mcp_tools)} 个MCP工具")
        
        return all_mcp_tools
    
    def save_mcp_tools_to_jsonl(self, mcp_tools: List[Dict[str, Any]]):
        """将MCP工具保存到JSONL文件"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for mcp_tool in mcp_tools:
                    json.dump(mcp_tool, f, ensure_ascii=False)
                    f.write('\n')
            
            print(f"✅ 成功保存 {len(mcp_tools)} 个MCP工具到: {self.output_file}")
            
        except Exception as e:
            print(f"❌ 保存MCP工具时出错: {e}")
    
    def generate_summary_report(self, mcp_tools: List[Dict[str, Any]]):
        """生成MCP工具摘要报告"""
        if not mcp_tools:
            print("📊 未找到任何MCP工具")
            return
        
        # 统计信息
        total_tools = len(mcp_tools)
        unique_names = set(tool['name'] for tool in mcp_tools if 'name' in tool)
        tasks_with_tools = set(tool['source_task'] for tool in mcp_tools)
        
        # 按任务分组
        tools_by_task = {}
        for tool in mcp_tools:
            task = tool.get('source_task', 'unknown')
            if task not in tools_by_task:
                tools_by_task[task] = []
            tools_by_task[task].append(tool)
        
        # 打印摘要
        print(f"\n{'='*60}")
        print("📊 MCP工具提取摘要")
        print(f"{'='*60}")
        print(f"📈 总MCP工具数: {total_tools}")
        print(f"🔧 唯一工具名数: {len(unique_names)}")
        print(f"📝 涉及任务数: {len(tasks_with_tools)}")
        
        print(f"\n🔧 发现的MCP工具名称:")
        for i, name in enumerate(sorted(unique_names), 1):
            print(f"  {i}. {name}")
        
        print(f"\n📝 各任务的MCP工具数量:")
        for task, tools in sorted(tools_by_task.items()):
            print(f"  {task}: {len(tools)} 个工具")
        
        # 保存摘要报告
        summary = {
            "total_mcp_tools": total_tools,
            "unique_tool_names": len(unique_names),
            "tasks_with_tools": len(tasks_with_tools),
            "tool_names": sorted(list(unique_names)),
            "tools_by_task": {task: len(tools) for task, tools in tools_by_task.items()},
            "generated_at": datetime.now().isoformat()
        }
        
        summary_file = self.output_file.replace('.jsonl', '_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📁 摘要报告已保存: {summary_file}")
    
    def run(self):
        """运行MCP工具提取"""
        print("🔧 MCP工具提取器")
        print("="*60)
        
        # 提取所有MCP工具
        mcp_tools = self.extract_all_mcp_tools()
        
        if not mcp_tools:
            print("❌ 未找到任何MCP工具")
            return
        
        # 保存到JSONL文件
        self.save_mcp_tools_to_jsonl(mcp_tools)
        
        # 生成摘要报告
        self.generate_summary_report(mcp_tools)
        
        print(f"\n🎉 MCP工具提取完成!")

def main():
    """主函数"""
    extractor = MCPToolExtractor()
    extractor.run()

if __name__ == "__main__":
    main() 