#!/usr/bin/env python
import sys
import warnings
import json
from datetime import datetime

# Import your custom crew architecture
from website_maker.crew import ResumeGalaCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Define a robust, high-fidelity sample payload for local testing and validation
DEFAULT_TESTING_INPUTS = {
    'user_prompt': (
        "Create a premium, dark-minimal portfolio website with modern glassmorphism elements. "
        "The projects section must look like a high-end Bento Grid with subtle interactive hover scale animations. "
        "Include a working contact form connected via client-side EmailJS."
    ),
    'resume_input': {
        "name": "Parth Wadhwa",
        "title": "Consultant & Frontend Architect",
        "education": [
            {
                "institution": "Indian Institute of Technology (IIT) Delhi",
                "degree": "Bachelor of Technology",
                "timeline": "2024 - Present"
            }
        ],
        "skills": [
            "React", "Next.js", "Tailwind CSS", "Framer Motion", 
            "FastAPI", "Python", "Docker", "OpenCV", "SQL"
        ],
        "projects": [
            {
                "title": "ResearchSync",
                "description": "An AI-powered collaborative research engine built for distributed research teams.",
                "technologies": ["React", "FastAPI", "Tailwind CSS"]
            },
            {
                "title": "Cyber Warriors Platform",
                "description": "A collaborative secure portal developed for regional digital safety initiatives.",
                "technologies": ["Next.js", "TypeScript", "Docker"]
            }
        ],
        "experience": [
            {
                "company": "Fumind.ai",
                "role": "AI Engineering Intern",
                "timeline": "Feb 2026 - Present",
                "highlights": ["Designed one-shot segmentation solutions in a highly unified monorepo frontend architecture."]
            },
            {
                "company": "Design Club (BRCA IIT Delhi)",
                "role": "Club Representative",
                "timeline": "2025 - 2026",
                "highlights": ["Orchestrated visual frameworks, design collateral, and interface layouts for major campus milestones."]
            }
        ]
    }
}


def _load_runtime_inputs() -> dict:
    """
    Load dynamic inputs from one of:
    1) CLI JSON string argument
    2) CLI path to JSON file
    3) stdin JSON payload
    Falls back to DEFAULT_TESTING_INPUTS for local smoke tests.
    """
    # Pattern: python main.py run '{"user_prompt":"...","resume_input":{...}}'
    if len(sys.argv) > 1:
        candidate = sys.argv[1]
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass

        # Pattern: python main.py run inputs.json
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass

    # Pattern: echo '{"user_prompt":"...","resume_input":{...}}' | python main.py run
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            try:
                payload = json.loads(raw)
                if isinstance(payload, dict):
                    return payload
            except json.JSONDecodeError:
                pass

    return DEFAULT_TESTING_INPUTS

def run():
    """
    Run the crew to generate the production-ready React codebase.
    """
    try:
        runtime_inputs = _load_runtime_inputs()
        if "user_prompt" not in runtime_inputs:
            runtime_inputs["user_prompt"] = DEFAULT_TESTING_INPUTS["user_prompt"]
        if "resume_input" not in runtime_inputs:
            runtime_inputs["resume_input"] = DEFAULT_TESTING_INPUTS["resume_input"]

        ResumeGalaCrew().generation_crew().kickoff(inputs=runtime_inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the generation crew: {e}")


def train():
    """
    Train the crew for a given number of iterations to optimize prompt alignments.
    """
    if len(sys.argv) < 3:
        raise Exception("Training requires iteration count and output filename. Usage: python main.py train <iterations> <filename.pkl>")
        
    try:
        ResumeGalaCrew().generation_crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=DEFAULT_TESTING_INPUTS
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task state for targeted debugging.
    """
    if len(sys.argv) < 2:
        raise Exception("Replay requires a valid Task ID string. Usage: python main.py replay <task_id>")
        
    try:
        ResumeGalaCrew().generation_crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution pipeline and output qualitative performance evaluations.
    """
    if len(sys.argv) < 3:
        raise Exception("Testing requires iteration count and evaluation LLM model name. Usage: python main.py test <iterations> <model_name>")

    try:
        ResumeGalaCrew().generation_crew().test(
            n_iterations=int(sys.argv[1]), 
            eval_llm=sys.argv[2], 
            inputs=DEFAULT_TESTING_INPUTS
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew dynamically using a production webhook or API trigger payload.
    """
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please pass raw JSON string as an argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Provided argument is not a valid JSON structure.")

    # Format the external trigger variables safely to decouple from the schema
    inputs = {
        "user_prompt": trigger_payload.get("user_prompt", DEFAULT_TESTING_INPUTS["user_prompt"]),
        "resume_input": trigger_payload.get("resume_input", DEFAULT_TESTING_INPUTS["resume_input"])
    }

    try:
        result = ResumeGalaCrew().generation_crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while executing the triggered crew runner: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        # Shift arguments past command keyword for internal parsing compatibility
        sys.argv = sys.argv[1:]
        
        if command == "run":
            run()
        elif command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        else:
            print(f"Unknown command: {command}. Available commands: run, train, replay, test")
    else:
        # Default behavior: run generation pipeline
        run()
