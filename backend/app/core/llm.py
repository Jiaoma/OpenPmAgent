"""LLM service for AI-powered features."""
import os
from typing import Optional, List
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from app.config import settings


class LLMService:
    """Service for LLM integration."""

    def __init__(self):
        """Initialize LLM service based on configuration."""
        self.llm = self._create_llm()
        self.enabled = self.llm is not None

    def _create_llm(self) -> Optional[ChatOpenAI]:
        """Create LLM instance based on configuration."""
        llm_type = settings.llm_type.lower()

        if llm_type == "openai":
            if settings.llm_api_url and settings.llm_api_key:
                return ChatOpenAI(
                    base_url=settings.llm_api_url,
                    api_key=settings.llm_api_key,
                    model="gpt-3.5-turbo",
                    temperature=0.7,
                )
        elif llm_type == "local":
            if settings.llm_api_url:
                return ChatOpenAI(
                    base_url=settings.llm_api_url,
                    model="llama-2",
                    temperature=0.7,
                )

        return None

    async def recommend_task_assignment(
        self,
        task_name: str,
        task_description: str,
        candidates: List[dict]
    ) -> Optional[dict]:
        """
        Recommend best person for task assignment.

        Args:
            task_name: Name of the task
            task_description: Description of the task
            candidates: List of candidate persons with their capabilities

        Returns:
            Dictionary with recommendation or None if LLM is disabled
        """
        if not self.enabled:
            return None

        try:
            # Format candidates for prompt
            candidates_str = "\n".join([
                f"- {c['name']} (工号: {c['emp_id']}): "
                f"能力: {c.get('capabilities', 'N/A')}, "
                f"当前负载: {c.get('workload', 'N/A')}"
                for c in candidates
            ])

            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="你是项目管理专家，根据人员能力和当前负载推荐最佳的任务分配。"),
                HumanMessage(content=f"""
任务名称: {task_name}
任务描述: {task_description}

候选人列表:
{candidates_str}

请从候选人中选择最合适的人员，并给出以下格式的回答：
推荐人员: [姓名]
工号: [工号]
理由: [详细解释推荐理由]
                """)
            ])

            messages = prompt.format_messages(
                task_name=task_name,
                task_description=task_description,
                candidates=candidates_str
            )

            response = await self.llm.ainvoke(messages)
            return {"recommendation": response.content}

        except Exception as e:
            print(f"LLM recommendation error: {e}")
            return None

    async def analyze_task_risk(
        self,
        tasks: List[dict]
    ) -> Optional[dict]:
        """
        Analyze project task risks.

        Args:
            tasks: List of tasks with schedules and dependencies

        Returns:
            Risk analysis result or None if LLM is disabled
        """
        if not self.enabled:
            return None

        try:
            tasks_str = "\n".join([
                f"- {t['name']}: 起止时间 {t['start_date']} - {t['end_date']}, "
                f"工作量 {t['man_months']} 人月, 负责人 {t.get('developer', 'N/A')}"
                for t in tasks
            ])

            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="你是项目管理专家，分析项目任务风险并提供预警建议。"),
                HumanMessage(content=f"""
任务列表:
{tasks_str}

请分析这些任务可能存在的风险，并给出以下格式的回答：
高风险任务: [任务名称列表]
中风险任务: [任务名称列表]
风险原因: [详细分析原因]
建议措施: [具体建议]
                """)
            ])

            messages = prompt.format_messages(tasks=tasks_str)
            response = await self.llm.ainvoke(messages)
            return {"risk_analysis": response.content}

        except Exception as e:
            print(f"LLM risk analysis error: {e}")
            return None

    async def generate_report(
        self,
        report_type: str,
        data: dict
    ) -> Optional[str]:
        """
        Generate natural language report.

        Args:
            report_type: Type of report (weekly, monthly, etc.)
            data: Report data

        Returns:
            Generated report text or None if LLM is disabled
        """
        if not self.enabled:
            return None

        try:
            prompt_map = {
                "weekly": "生成一份项目周报",
                "monthly": "生成一份项目月报",
                "iteration": "生成一份迭代总结报告",
            }

            system_msg = f"你是项目管理专家，{prompt_map.get(report_type, '生成项目报告')}。"
            human_msg = f"""
报告数据:
{data}

请生成一份清晰的报告，包含以下部分：
1. 概述
2. 完成情况
3. 风险和问题
4. 下一步计划
            """

            messages = [
                SystemMessage(content=system_msg),
                HumanMessage(content=human_msg)
            ]

            response = await self.llm.ainvoke(messages)
            return response.content

        except Exception as e:
            print(f"LLM report generation error: {e}")
            return None


# Global LLM service instance
llm_service = LLMService()
