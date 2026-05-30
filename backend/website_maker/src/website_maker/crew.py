from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
import json
import re
import logging
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool  # type: ignore
except Exception:  # pragma: no cover - depends on runtime extras
    SerperDevTool = None
    ScrapeWebsiteTool = None

@CrewBase
class ResumeGalaCrew():
    """Resume Gala - Core Frontend Generation Crew"""

    # Point these to where your yaml files are stored
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    template_path = Path(__file__).resolve().parent / "config" / "react_template.json"

    def _research_tools(self) -> List:
        tools: List = []
        if SerperDevTool is not None:
            tools.append(SerperDevTool())
        if ScrapeWebsiteTool is not None:
            tools.append(ScrapeWebsiteTool())
        return tools

    def _asset_tools(self) -> List:
        tools: List = []
        if SerperDevTool is not None:
            tools.append(SerperDevTool())
        if ScrapeWebsiteTool is not None:
            tools.append(ScrapeWebsiteTool())
        return tools

    @before_kickoff
    def prepare_inputs(self, inputs):
        """Validate and normalize inputs before kickoff."""
        if not isinstance(inputs, dict):
            raise ValueError("Inputs must be a dictionary.")
        if not inputs.get("user_prompt"):
            raise ValueError("Missing required field: user_prompt")
        if not inputs.get("resume_input"):
            raise ValueError("Missing required field: resume_input")

        if isinstance(inputs.get('resume_input'), dict):
            inputs['resume_input'] = json.dumps(inputs['resume_input'], indent=2)
        if not isinstance(inputs.get('user_prompt'), str):
            inputs['user_prompt'] = str(inputs.get('user_prompt'))
        if len(inputs['user_prompt'].strip()) < 5:
            raise ValueError("user_prompt is too short. Provide a meaningful design prompt.")

        # Inject a stable React/Vite scaffold so coding is template-first, not free-form.
        try:
            if self.template_path.is_file():
                with open(self.template_path, "r", encoding="utf-8") as f:
                    template_map = json.load(f)
                inputs["react_template"] = json.dumps(template_map, indent=2)
        except Exception as exc:
            logger.warning("Could not load react template scaffold: %s", exc)
        return inputs

    @after_kickoff
    def parse_output(self, result):
        """Parse the raw crew output into a clean file-mapping dictionary."""
        raw = result.raw if hasattr(result, 'raw') else str(result)

        def _extract_file_map(parsed_obj):
            if not isinstance(parsed_obj, dict):
                return None
            # Feedback gate format
            if "verdict" in parsed_obj:
                verdict = str(parsed_obj.get("verdict", "")).strip().lower()
                final_files = parsed_obj.get("final_files")
                feedback = parsed_obj.get("feedback", []) or []
                if verdict == "needs_changes":
                    # Minor/configuration warnings should not hard-fail generation if final_files exist.
                    feedback_text = " ".join(str(item).lower() for item in feedback)
                    minor_markers = [
                        "placeholder",
                        "emailjs",
                        "service id",
                        "template id",
                        "user id",
                        "public key",
                        "environment variable",
                    ]
                    if isinstance(final_files, dict) and any(m in feedback_text for m in minor_markers):
                        logger.warning("Feedback gate returned minor warnings; proceeding with final_files.")
                        return final_files
                    raise ValueError(f"Feedback gate rejected output: {feedback}")
                if isinstance(final_files, dict):
                    return final_files
            # Direct file map format
            if all(isinstance(v, str) for v in parsed_obj.values()):
                return parsed_obj
            return None
        
        # Try to extract JSON from the output (may be wrapped in markdown code fences)
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                extracted = _extract_file_map(parsed)
                if isinstance(extracted, dict):
                    result._parsed_files = extracted
                    logger.info(f"Successfully parsed {len(extracted)} files from crew output")
                    return result
            except json.JSONDecodeError:
                pass
        
        # Try to parse the entire output as JSON
        try:
            parsed = json.loads(raw)
            extracted = _extract_file_map(parsed)
            if isinstance(extracted, dict):
                result._parsed_files = extracted
                logger.info(f"Successfully parsed {len(extracted)} files from crew output")
                return result
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Fallback: wrap the raw output
        logger.warning("Could not parse crew output as JSON file mapping. Wrapping as raw output.")
        result._parsed_files = {"src/App.jsx": raw}
        return result

    # ==========================================
    # AGENTS
    # ==========================================
    
    @agent
    def planning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['planning_agent'], # type: ignore[index]
            verbose=True,
            max_iter=8,
        )

    @agent
    def design_theme_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['design_theme_agent'], # type: ignore[index]
            verbose=True,
            max_iter=8,
        )

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'], # type: ignore[index]
            verbose=True,
            tools=self._research_tools(),
            max_iter=10,
        )

    @agent
    def asset_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['asset_agent'], # type: ignore[index]
            verbose=True,
            tools=self._asset_tools(),
            max_iter=10,
        )

    @agent
    def coding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['coding_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=True, # Allows the coding agent to query the checking agent if it gets stuck
            max_iter=14,
        )

    @agent
    def checking_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['checking_agent'], # type: ignore[index]
            verbose=True,
            max_iter=8,
        )

    @agent
    def testing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['testing_agent'], # type: ignore[index]
            verbose=True,
            max_iter=8,
        )

    @agent
    def feedback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['feedback_agent'], # type: ignore[index]
            verbose=True,
            max_iter=8,
        )

    @agent
    def editing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['editing_agent'], # type: ignore[index]
            verbose=True
        )

    # ==========================================
    # TASKS (With Context Passing)
    # ==========================================
    
    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['planning_task'], # type: ignore[index]
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'], # type: ignore[index]
            context=[self.planning_task()] # Depends on the layout blueprint
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            context=[self.planning_task()] # Needs the blueprint to know what stats to fetch
        )

    @task
    def asset_collection_task(self) -> Task:
        return Task(
            config=self.tasks_config['asset_collection_task'], # type: ignore[index]
            context=[self.planning_task()] # Needs the blueprint to know what icons/logos to fetch
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'], # type: ignore[index]
            # CRITICAL: The coding agent receives the outputs from all 4 previous tasks simultaneously!
            context=[
                self.planning_task(), 
                self.design_task(), 
                self.research_task(), 
                self.asset_collection_task()
            ]
        )

    @task
    def checking_task(self) -> Task:
        return Task(
            config=self.tasks_config['checking_task'], # type: ignore[index]
            context=[self.coding_task()]
        )

    @task
    def testing_task(self) -> Task:
        return Task(
            config=self.tasks_config['testing_task'], # type: ignore[index]
            context=[self.checking_task()]
        )

    @task
    def feedback_task(self) -> Task:
        return Task(
            config=self.tasks_config['feedback_task'], # type: ignore[index]
            context=[
                self.planning_task(),
                self.design_task(),
                self.research_task(),
                self.asset_collection_task(),
                self.coding_task(),
                self.checking_task(),
                self.testing_task(),
            ],
        )

    @task
    def editing_task(self) -> Task:
        return Task(
            config=self.tasks_config['editing_task'], # type: ignore[index]
            # No context passed here initially. This is meant to be run in isolation later.
        )

    # ==========================================
    # CREW ORCHESTRATION
    # ==========================================

    @crew
    def generation_crew(self) -> Crew:
        """Creates the main Resume Gala crew for initial website generation."""
        
        # We explicitly define the task list here to EXCLUDE the editing_task 
        # because conversational editing happens AFTER the website is built.
        generation_tasks = [
            self.planning_task(),
            self.design_task(),
            self.research_task(),
            self.asset_collection_task(),
            self.coding_task(),
            self.checking_task(),
            self.testing_task(),
            self.feedback_task(),
        ]

        return Crew(
            agents=self.agents, # type: ignore
            tasks=generation_tasks, 
            process=Process.sequential,
            verbose=True,
            max_rpm=40,
        )
