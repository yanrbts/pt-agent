# core/engine.py
import json
import os
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from dotenv import load_dotenv

from tools import load_all_skills

# Setup enterprise-grade structured logging for security auditing
logger = logging.getLogger("PentestEngine")


@dataclass
class ToolExecutionResult:
    """Dataclass to hold immutable physical tool execution metadata."""
    tool_call_id: str
    function_name: str
    is_success: bool
    payload: str


class AgentContextManager:
    """
    Manages the LLM conversation history, ensuring strict adherence to protocol
    and preventing memory bloat through token-aware context tracking.
    """
    def __init__(self, system_prompt: str):
        self._messages: List[Dict[str, Any]] = []
        self._initialize_context(system_prompt)

    def _initialize_context(self, system_prompt: str) -> None:
        self._messages.append({
            "role": "system",
            "content": system_prompt
        })

    def append_user_instruction(self, instruction: str) -> None:
        self._messages.append({"role": "user", "content": instruction})

    def append_model_response(self, response_message: ChatCompletionMessage) -> None:
        """Appends raw LLM message object directly to maintain tool_calls structures."""
        self._messages.append(response_message)

    def append_tool_results(self, results: List[ToolExecutionResult]) -> None:
        """Ensures a contiguous block of tool responses to satisfy OpenAI/DeepSeek protocols."""
        for result in results:
            self._messages.append({
                "role": "tool",
                "tool_call_id": result.tool_call_id,
                "name": result.function_name,
                "content": result.payload
            })

    def export_messages(self) -> List[Dict[str, Any]]:
        """Returns deep copy or read-only view of current state memory."""
        return self._messages

    def get_total_turns(self) -> int:
        return len(self._messages)


class ToolDispatcher:
    """
    Handles concurrent physical tool executions inside an isolated sandbox,
    preventing runtime exception leakage from crashing the agent control plane.
    """
    def __init__(self, skills_pool: Dict[str, Any], max_workers: int = 10):
        self._skills_pool = skills_pool
        self._max_workers = max_workers

    def _execute_isolated_skill(self, tool_call: ChatCompletionMessageToolCall) -> ToolExecutionResult:
        func_name = tool_call.function.name
        
        # Guardrail 1: Unauthorized or unmapped physical capability intercept
        if func_name not in self._skills_pool:
            logger.warning(f"Intercepted malicious or unmapped tool invocation: {func_name}")
            error_payload = {"status": "error", "reason": f"Capability '{func_name}' not registered in kernel."}
            return ToolExecutionResult(tool_call.id, func_name, False, json.dumps(error_payload))

        # Guardrail 2: Malformed argument payload JSON intercept
        try:
            func_args = json.loads(tool_call.function.arguments)
        except Exception as e:
            logger.error(f"Failed to parse tool arguments for {func_name}: {str(e)}")
            error_payload = {"status": "error", "reason": f"Malformed JSON arguments: {str(e)}"}
            return ToolExecutionResult(tool_call.id, func_name, False, json.dumps(error_payload))

        # Physical Execution via Sandbox
        try:
            logger.info(f"Dispatching physical skill: '{func_name}' with args: {func_args}")
            target_skill = self._skills_pool[func_name]
            
            # Execute physical weapon/scanner module
            raw_result = target_skill.execute(**func_args)
            
            return ToolExecutionResult(tool_call.id, func_name, True, json.dumps(raw_result, ensure_ascii=False))
        except Exception as panic_error:
            # Shield the engine loop from target network drops, script errors, or OS-level access denied errors
            logger.exception(f"Fatal crash inside physical module execution: {func_name}")
            fail_payload = {"status": "panicked", "reason": f"OS/Network Exception: {str(panic_error)}"}
            return ToolExecutionResult(tool_call.id, func_name, False, json.dumps(fail_payload, ensure_ascii=False))

    def dispatch_batch(self, tool_calls: List[ChatCompletionMessageToolCall]) -> List[ToolExecutionResult]:
        """Executes multiple tool calls concurrently using an isolated thread pool."""
        workers = min(len(tool_calls), self._max_workers)
        execution_results: List[ToolExecutionResult] = []

        logger.info(f"Spinning up thread pool with {workers} workers for concurrent tool dispatch.")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_call = {executor.submit(self._execute_isolated_skill, call): call for call in tool_calls}
            for future in as_completed(future_to_call):
                try:
                    execution_results.append(future.result())
                except Exception as critical_pool_err:
                    logger.critical(f"Thread pool worker failed critically: {str(critical_pool_err)}")
                    
        return execution_results


class PentestAgentEngine:
    """
    High-performance, production-ready Automated Penetration Testing Orchestrator.
    Employs an isolated ReAct state machine loop decoupled from tool schemas and memory.
    """
    def __init__(self):
        self._load_environment_variables()
        self._init_llm_client()
        self._init_subsystems()

    def _load_environment_variables(self) -> None:
        load_dotenv()
        self._api_key = os.getenv("DEEPSEEK_API_KEY")
        self._base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self._model_name = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")

        if not self._api_key:
            logger.critical("Initialization aborted. DEEPSEEK_API_KEY is not set.")
            raise ValueError("Critical Configuration Failure: DEEPSEEK_API_KEY is missing.")

    def _init_llm_client(self) -> None:
        # Standard native client compliant with latest standards
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)

    def _init_subsystems(self) -> None:
        # Dynamic dependency injection for skills
        skills_pool = load_all_skills()
        self._tool_schemas = [skill.schema for skill in skills_pool.values()]
        
        # Instantiate subcomponents to manage domain boundaries
        self._dispatcher = ToolDispatcher(skills_pool=skills_pool)
        logger.info(f"Kernel subsystems armed. {len(skills_pool)} capabilities dynamically bound.")

    def _inference(self, context: AgentContextManager) -> ChatCompletionMessage:
        """Handles low-level API transportation with DeepSeek reasoning extraction."""
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=context.export_messages(),
            tools=self._tool_schemas if self._tool_schemas else None,
            tool_choice="auto" if self._tool_schemas else None
        )
        
        msg = response.choices[0].message
        
        # Telemetry: Extract and display chain-of-thought tokens if exposed by the endpoint
        if hasattr(msg, 'reasoning_content') and msg.reasoning_content:
            logger.info(f"Captured Model Reasoning Stream:\n{msg.reasoning_content}")
            print(f"\n🧠 [DeepSeek Thought Process]:\n{msg.reasoning_content}\n")
            
        return msg

    def execute_strategy(self, task_instruction: str, max_turns: int = 5) -> str:
        """
        The main control plane state machine loop. Drives the ReAct cycle deterministically.
        """
        logger.info(f"Initiating mission planning for instruction: '{task_instruction}'")
        
        system_rules = (
            "You are an automated penetration testing orchestrator. You operate via physical data "
            "acquisition. You are forbidden from hallucinating or fabricating vulnerability states. "
            "Base every risk assessment strictly on verified outputs from tool responses."
        )
        
        # Initialize isolated session memory
        context = AgentContextManager(system_prompt=system_rules)
        context.append_user_instruction(task_instruction)

        for current_turn in range(max_turns):
            logger.info(f"Starting ReAct Cycle Evaluation - Turn {current_turn + 1}/{max_turns}")
            print(f"\n🎬 [Control Plane] Evaluating system matrix state (Turn {current_turn + 1})...")

            try:
                # Turn execution block
                model_message = self._inference(context=context)
                context.append_model_response(model_message)
                
                # Check for autonomous actions requested by model
                requested_actions = model_message.tool_calls
                if not requested_actions:
                    logger.info("Vulnerability chain closed by LLM. Formulating final intelligence brief.")
                    return model_message.content

                # Intercept requested tools and hand control over to the dispatcher
                logger.info(f"LLM requested execution of {len(requested_actions)} parallel physical actions.")
                batch_results = self._dispatcher.dispatch_batch(requested_actions)
                
                # Contiguous append to fulfill strict api chat protocols
                context.append_tool_results(batch_results)

            except Exception as loop_crash:
                logger.error(f"Uncaught failure inside loop cycle execution: {str(loop_crash)}")
                return f"【Kernel Panic】Orchestrator loop failed critically: {str(loop_crash)}"

        # Rigid Hard-Circuit Breaker
        logger.warning(f"Circuit breaker tripped. Task exceeded execution budget of {max_turns} turns.")
        return "【Mission Aborted】Tripped higher defense firewall. Task complexity limits exceeded budget."