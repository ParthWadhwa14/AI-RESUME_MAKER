# from crewai import Agent, Crew, Process, Task
# from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
# from crewai.agents.agent_builder.base_agent import BaseAgent
# import json
# import re
# import logging
# from typing import List
# from pathlib import Path

# logger = logging.getLogger(__name__)

# try:
#     from crewai_tools import SerperDevTool, ScrapeWebsiteTool  # type: ignore
# except Exception:  # pragma: no cover - depends on runtime extras
#     SerperDevTool = None
#     ScrapeWebsiteTool = None

# # --- Emergency fallback search tool (DuckDuckGo HTML) ---
# try:
#     import requests  # type: ignore
# except Exception:  # pragma: no cover
#     requests = None

# try:
#     from bs4 import BeautifulSoup  # type: ignore
# except Exception:  # pragma: no cover
#     BeautifulSoup = None


# def _duckduckgo_search(query: str, *, max_results: int = 5) -> str:
#     """Very small emergency search fallback.

#     Returns a plain-text list of result titles + URLs. Used when Serper isn't available.
#     """
#     if requests is None or BeautifulSoup is None:
#         return "DuckDuckGo fallback unavailable (missing requests/bs4)."

#     url = "https://duckduckgo.com/html/"
#     try:
#         resp = requests.post(url, data={"q": query}, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
#         resp.raise_for_status()
#         soup = BeautifulSoup(resp.text, "html.parser")
#         links = soup.select("a.result__a")
#         out_lines: list[str] = []
#         for a in links[:max_results]:
#             title = (a.get_text() or "").strip()
#             href = (a.get("href") or "").strip()
#             if title and href:
#                 out_lines.append(f"- {title} — {href}")
#         return "\n".join(out_lines) if out_lines else "No DuckDuckGo results."
#     except Exception as exc:
#         return f"DuckDuckGo search failed: {exc}"


# class _DuckDuckGoSearchTool:
#     """CrewAI-compatible wrapper with a tool name used in YAML."""

#     name = "search_the_internet_with_serper"  # alias expected by YAML
#     description = "Web search tool. Uses Serper when available; falls back to DuckDuckGo."

#     def __call__(self, search_query: str) -> str:  # matches SerperDevToolSchema
#         # Prefer Serper if installed
#         if SerperDevTool is not None:
#             try:
#                 return SerperDevTool().run(search_query=search_query)
#             except Exception as exc:
#                 logger.warning("Serper failed, falling back to DuckDuckGo: %s", exc)
#         return _duckduckgo_search(search_query)


# class _ReadWebsiteContentTool:
#     name = "read_website_content"  # alias expected by YAML
#     description = "Scrape/read a website URL and return main content."

#     def __call__(self, website_url: str) -> str:  # matches ScrapeWebsiteToolSchema
#         if ScrapeWebsiteTool is not None:
#             try:
#                 return ScrapeWebsiteTool().run(website_url=website_url)
#             except Exception as exc:
#                 logger.warning("ScrapeWebsiteTool failed: %s", exc)
#                 return f"Scrape failed: {exc}"
#         return "Scrape tool unavailable."

# @CrewBase
# class ResumeGalaCrew():
#     """Resume Gala - Core Frontend Generation Crew"""

#     # Point these to where your yaml files are stored
#     agents_config = 'config/agents.yaml'
#     tasks_config = 'config/tasks.yaml'
#     template_path = Path(__file__).resolve().parent / "config" / "react_template.json"

#     def _research_tools(self) -> List:
#         tools: List = []
#         # Use alias tools with stable names expected by agents.yaml
#         tools.append(_DuckDuckGoSearchTool())
#         tools.append(_ReadWebsiteContentTool())
#         return tools

#     def _asset_tools(self) -> List:
#         tools: List = []
#         tools.append(_DuckDuckGoSearchTool())
#         tools.append(_ReadWebsiteContentTool())
#         return tools

#     @before_kickoff
#     def prepare_inputs(self, inputs):
#         """Validate and normalize inputs before kickoff."""
#         if not isinstance(inputs, dict):
#             raise ValueError("Inputs must be a dictionary.")
#         if not inputs.get("user_prompt"):
#             raise ValueError("Missing required field: user_prompt")
#         if not inputs.get("resume_input"):
#             raise ValueError("Missing required field: resume_input")

#         if isinstance(inputs.get('resume_input'), dict):
#             inputs['resume_input'] = json.dumps(inputs['resume_input'], indent=2)
#         if not isinstance(inputs.get('user_prompt'), str):
#             inputs['user_prompt'] = str(inputs.get('user_prompt'))
#         if len(inputs['user_prompt'].strip()) < 5:
#             raise ValueError("user_prompt is too short. Provide a meaningful design prompt.")

#         # Inject a stable React/Vite scaffold so coding is template-first, not free-form.
#         try:
#             if self.template_path.is_file():
#                 with open(self.template_path, "r", encoding="utf-8") as f:
#                     template_map = json.load(f)
#                 inputs["react_template"] = json.dumps(template_map, indent=2)
#         except Exception as exc:
#             logger.warning("Could not load react template scaffold: %s", exc)
#         return inputs

#     @after_kickoff
#     def parse_output(self, result):
#         """Parse the raw crew output into a clean file-mapping dictionary."""
#         raw = result.raw if hasattr(result, 'raw') else str(result)

#         def _extract_file_map(parsed_obj):
#             if not isinstance(parsed_obj, dict):
#                 return None
#             # Feedback gate format
#             if "verdict" in parsed_obj:
#                 verdict = str(parsed_obj.get("verdict", "")).strip().lower()
#                 final_files = parsed_obj.get("final_files")
#                 feedback = parsed_obj.get("feedback", []) or []
#                 if verdict == "needs_changes":
#                     # Minor/configuration warnings should not hard-fail generation if final_files exist.
#                     feedback_text = " ".join(str(item).lower() for item in feedback)
#                     minor_markers = [
#                         "placeholder",
#                         "emailjs",
#                         "service id",
#                         "template id",
#                         "user id",
#                         "public key",
#                         "environment variable",
#                     ]
#                     if isinstance(final_files, dict) and any(m in feedback_text for m in minor_markers):
#                         logger.warning("Feedback gate returned minor warnings; proceeding with final_files.")
#                         return final_files
#                     raise ValueError(f"Feedback gate rejected output: {feedback}")
#                 if isinstance(final_files, dict):
#                     return final_files
#             # Direct file map format
#             if all(isinstance(v, str) for v in parsed_obj.values()):
#                 return parsed_obj
#             return None
        
#         # Try to extract JSON from the output (may be wrapped in markdown code fences)
#         json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw)
#         if json_match:
#             try:
#                 parsed = json.loads(json_match.group(1))
#                 extracted = _extract_file_map(parsed)
#                 if isinstance(extracted, dict):
#                     result._parsed_files = extracted
#                     logger.info(f"Successfully parsed {len(extracted)} files from crew output")
#                     return result
#             except json.JSONDecodeError:
#                 pass
        
#         # Try to parse the entire output as JSON
#         try:
#             parsed = json.loads(raw)
#             extracted = _extract_file_map(parsed)
#             if isinstance(extracted, dict):
#                 result._parsed_files = extracted
#                 logger.info(f"Successfully parsed {len(extracted)} files from crew output")
#                 return result
#         except (json.JSONDecodeError, TypeError):
#             pass
        
#         # Fallback: wrap the raw output
#         logger.warning("Could not parse crew output as JSON file mapping. Wrapping as raw output.")
#         result._parsed_files = {"src/App.jsx": raw}
#         return result

#     # ==========================================
#     # AGENTS
#     # ==========================================
    
#     @agent
#     def planning_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['planning_agent'], # type: ignore[index]
#             verbose=True,
#             max_iter=4,
#         )

#     @agent
#     def design_theme_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['design_theme_agent'], # type: ignore[index]
#             verbose=True,
#             max_iter=4,
#         )

#     @agent
#     def research_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['research_agent'], # type: ignore[index]
#             verbose=True,
#             tools=self._research_tools(),
#             max_iter=3,
#         )

#     @agent
#     def asset_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['asset_agent'], # type: ignore[index]
#             verbose=True,
#             tools=self._asset_tools(),
#             max_iter=3,
#         )

#     @agent
#     def coding_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['coding_agent'], # type: ignore[index]
#             verbose=True,
#             allow_delegation=False,
#             max_iter=6,
#         )

#     @agent
#     def checking_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['checking_agent'], # type: ignore[index]
#             verbose=True,
#             max_iter=3,
#         )

#     @agent
#     def testing_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['testing_agent'], # type: ignore[index]
#             verbose=True,
#             max_iter=3,
#         )

#     @agent
#     def feedback_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['feedback_agent'], # type: ignore[index]
#             verbose=True,
#             max_iter=3,
#         )

#     @agent
#     def editing_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['editing_agent'], # type: ignore[index]
#             verbose=True
#         )

#     # ==========================================
#     # TASKS (With Context Passing)
#     # ==========================================
    
#     @task
#     def planning_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['planning_task'], # type: ignore[index]
#         )

#     @task
#     def design_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['design_task'], # type: ignore[index]
#             context=[self.planning_task()] # Depends on the layout blueprint
#         )

#     @task
#     def research_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['research_task'], # type: ignore[index]
#             context=[self.planning_task()] # Needs the blueprint to know what stats to fetch
#         )

#     @task
#     def asset_collection_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['asset_collection_task'], # type: ignore[index]
#             context=[self.planning_task()] # Needs the blueprint to know what icons/logos to fetch
#         )

#     @task
#     def coding_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['coding_task'], # type: ignore[index]
#             # CRITICAL: The coding agent receives the outputs from all 4 previous tasks simultaneously!
#             context=[
#                 self.planning_task(), 
#                 self.design_task(), 
#                 self.research_task(), 
#                 self.asset_collection_task()
#             ]
#         )

#     @task
#     def checking_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['checking_task'], # type: ignore[index]
#             context=[self.coding_task()]
#         )

#     @task
#     def testing_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['testing_task'], # type: ignore[index]
#             context=[self.checking_task()]
#         )

#     @task
#     def feedback_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['feedback_task'], # type: ignore[index]
#             context=[
#                 self.planning_task(),
#                 self.design_task(),
#                 self.research_task(),
#                 self.asset_collection_task(),
#                 self.coding_task(),
#                 self.checking_task(),
#                 self.testing_task(),
#             ],
#         )

#     @task
#     def editing_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['editing_task'], # type: ignore[index]
#             # No context passed here initially. This is meant to be run in isolation later.
#         )

#     # ==========================================
#     # CREW ORCHESTRATION
#     # ==========================================

#     @crew
#     def generation_crew(self) -> Crew:
#         """Creates the main Resume Gala crew for initial website generation."""
        
#         # We explicitly define the task list here to EXCLUDE the editing_task 
#         # because conversational editing happens AFTER the website is built.
#         generation_tasks = [
#             self.planning_task(),
#             self.design_task(),
#             self.research_task(),
#             self.asset_collection_task(),
#             self.coding_task(),
#             self.checking_task(),
#             self.testing_task(),
#             self.feedback_task(),
#         ]

#         return Crew(
#             agents=self.agents, # type: ignore
#             tasks=generation_tasks, 
#             process=Process.sequential,
#             verbose=True,
#             max_rpm=15,
#         )


from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

from crewai.tools import BaseTool

import json
import re
import logging

from typing import List, Type
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ==========================================
# OPTIONAL TOOL IMPORTS
# ==========================================

try:
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool
except Exception:
    SerperDevTool = None
    ScrapeWebsiteTool = None

# ==========================================
# FALLBACK IMPORTS
# ==========================================

try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


# ==========================================
# DUCKDUCKGO FALLBACK SEARCH
# ==========================================

def _duckduckgo_search(query: str, *, max_results: int = 5) -> str:
    """
    Emergency DuckDuckGo fallback search.
    """

    if requests is None or BeautifulSoup is None:
        return "DuckDuckGo fallback unavailable."

    url = "https://duckduckgo.com/html/"

    try:
        resp = requests.post(
            url,
            data={"q": query},
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )

        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        links = soup.select("a.result__a")

        out_lines = []

        for a in links[:max_results]:
            title = (a.get_text() or "").strip()
            href = (a.get("href") or "").strip()

            if title and href:
                out_lines.append(f"- {title} — {href}")

        return "\n".join(out_lines) if out_lines else "No results found."

    except Exception as exc:
        return f"DuckDuckGo search failed: {exc}"


# ==========================================
# TOOL INPUT SCHEMAS
# ==========================================

class SearchToolInput(BaseModel):
    search_query: str = Field(
        ...,
        description="Search query for internet search",
    )


class WebsiteToolInput(BaseModel):
    website_url: str = Field(
        ...,
        description="Website URL to scrape",
    )


# ==========================================
# SEARCH TOOL
# ==========================================

class DuckDuckGoSearchTool(BaseTool):
    name: str = "search_the_internet_with_serper"

    description: str = (
        "Search the internet using Serper or DuckDuckGo fallback."
    )

    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, search_query: str) -> str:

        # Prefer Serper if available
        if SerperDevTool is not None:
            try:
                tool = SerperDevTool()

                return tool.run(search_query)

            except Exception as exc:
                logger.warning(
                    "Serper failed, falling back to DuckDuckGo: %s",
                    exc,
                )

        return _duckduckgo_search(search_query)


# ==========================================
# WEBSITE SCRAPER TOOL
# ==========================================

class ReadWebsiteContentTool(BaseTool):
    name: str = "read_website_content"

    description: str = (
        "Read and scrape website content from a URL."
    )

    args_schema: Type[BaseModel] = WebsiteToolInput

    def _run(self, website_url: str) -> str:

        if ScrapeWebsiteTool is not None:
            try:
                tool = ScrapeWebsiteTool(website_url=website_url)

                return tool.run()

            except Exception as exc:
                logger.warning(
                    "ScrapeWebsiteTool failed: %s",
                    exc,
                )

                return f"Scrape failed: {exc}"

        return "Scrape tool unavailable."


# ==========================================
# CREW
# ==========================================

@CrewBase
class ResumeGalaCrew:
    """Resume Gala - Core Frontend Generation Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    template_path = (
        Path(__file__).resolve().parent
        / "config"
        / "react_template.json"
    )

    # ==========================================
    # TOOL HELPERS
    # ==========================================

    def _research_tools(self) -> List:
        return [
            DuckDuckGoSearchTool(),
            ReadWebsiteContentTool(),
        ]

    def _asset_tools(self) -> List:
        return [
            DuckDuckGoSearchTool(),
            ReadWebsiteContentTool(),
        ]

    # ==========================================
    # INPUT PREPARATION
    # ==========================================

    @before_kickoff
    def prepare_inputs(self, inputs):

        if not isinstance(inputs, dict):
            raise ValueError("Inputs must be a dictionary.")

        if not inputs.get("user_prompt"):
            raise ValueError("Missing required field: user_prompt")

        if not inputs.get("resume_input"):
            raise ValueError("Missing required field: resume_input")

        if isinstance(inputs.get("resume_input"), dict):
            inputs["resume_input"] = json.dumps(
                inputs["resume_input"],
                indent=2,
            )

        if not isinstance(inputs.get("user_prompt"), str):
            inputs["user_prompt"] = str(
                inputs.get("user_prompt")
            )

        if len(inputs["user_prompt"].strip()) < 5:
            raise ValueError(
                "user_prompt is too short."
            )

        try:
            if self.template_path.is_file():

                with open(
                    self.template_path,
                    "r",
                    encoding="utf-8",
                ) as f:
                    template_map = json.load(f)

                inputs["react_template"] = json.dumps(
                    template_map,
                    indent=2,
                )

        except Exception as exc:
            logger.warning(
                "Could not load react template scaffold: %s",
                exc,
            )

        return inputs

    # ==========================================
    # OUTPUT PARSER
    # ==========================================

    @after_kickoff
    def parse_output(self, result):

        raw = (
            result.raw
            if hasattr(result, "raw")
            else str(result)
        )

        def _extract_file_map(parsed_obj):

            if not isinstance(parsed_obj, dict):
                return None

            if "verdict" in parsed_obj:

                verdict = str(
                    parsed_obj.get("verdict", "")
                ).strip().lower()

                final_files = parsed_obj.get("final_files")

                feedback = (
                    parsed_obj.get("feedback", [])
                    or []
                )

                if verdict == "needs_changes":

                    feedback_text = " ".join(
                        str(item).lower()
                        for item in feedback
                    )

                    minor_markers = [
                        "placeholder",
                        "emailjs",
                        "service id",
                        "template id",
                        "user id",
                        "public key",
                        "environment variable",
                    ]

                    if (
                        isinstance(final_files, dict)
                        and any(
                            m in feedback_text
                            for m in minor_markers
                        )
                    ):
                        logger.warning(
                            "Minor warnings only."
                        )

                        return final_files

                    raise ValueError(
                        f"Feedback rejected: {feedback}"
                    )

                if isinstance(final_files, dict):
                    return final_files

            if all(
                isinstance(v, str)
                for v in parsed_obj.values()
            ):
                return parsed_obj

            return None

        json_match = re.search(
            r"```(?:json)?\s*(\{[\s\S]*?\})\s*```",
            raw,
        )

        if json_match:
            try:
                parsed = json.loads(
                    json_match.group(1)
                )

                extracted = _extract_file_map(parsed)

                if isinstance(extracted, dict):

                    result._parsed_files = extracted

                    logger.info(
                        f"Parsed {len(extracted)} files."
                    )

                    return result

            except json.JSONDecodeError:
                pass

        try:
            parsed = json.loads(raw)

            extracted = _extract_file_map(parsed)

            if isinstance(extracted, dict):

                result._parsed_files = extracted

                logger.info(
                    f"Parsed {len(extracted)} files."
                )

                return result

        except (json.JSONDecodeError, TypeError):
            pass

        logger.warning(
            "Could not parse JSON output."
        )

        result._parsed_files = {
            "src/App.jsx": raw
        }

        return result

    # ==========================================
    # AGENTS
    # ==========================================

    @agent
    def planning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["planning_agent"],
            verbose=True,
            max_iter=4,
        )

    @agent
    def design_theme_agent(self) -> Agent:
        return Agent(
            config=self.agents_config[
                "design_theme_agent"
            ],
            verbose=True,
            max_iter=4,
        )

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_agent"],
            verbose=True,
            tools=self._research_tools(),
            max_iter=3,
        )

    @agent
    def asset_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["asset_agent"],
            verbose=True,
            tools=self._asset_tools(),
            max_iter=3,
        )

    @agent
    def coding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["coding_agent"],
            verbose=True,
            allow_delegation=False,
            max_iter=6,
        )

    @agent
    def checking_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["checking_agent"],
            verbose=True,
            max_iter=3,
        )

    @agent
    def testing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["testing_agent"],
            verbose=True,
            max_iter=3,
        )

    @agent
    def feedback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["feedback_agent"],
            verbose=True,
            max_iter=3,
        )

    @agent
    def editing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["editing_agent"],
            verbose=True,
        )

    # ==========================================
    # TASKS
    # ==========================================

    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["planning_task"]
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config["design_task"],
            context=[self.planning_task()],
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            context=[self.planning_task()],
        )

    @task
    def asset_collection_task(self) -> Task:
        return Task(
            config=self.tasks_config[
                "asset_collection_task"
            ],
            context=[self.planning_task()],
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config["coding_task"],
            context=[
                self.planning_task(),
                self.design_task(),
                self.research_task(),
                self.asset_collection_task(),
            ],
        )

    @task
    def checking_task(self) -> Task:
        return Task(
            config=self.tasks_config["checking_task"],
            context=[self.coding_task()],
        )

    @task
    def testing_task(self) -> Task:
        return Task(
            config=self.tasks_config["testing_task"],
            context=[self.checking_task()],
        )

    @task
    def feedback_task(self) -> Task:
        return Task(
            config=self.tasks_config["feedback_task"],
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
            config=self.tasks_config["editing_task"]
        )

    # ==========================================
    # CREW
    # ==========================================

    @crew
    def generation_crew(self) -> Crew:

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
            agents=self.agents,
            tasks=generation_tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=15,
        )
