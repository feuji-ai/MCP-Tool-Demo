#!/usr/bin/env python3
import asyncio, sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from math_tools import AddTool, SubtractTool, MultiplyTool, DivideTool, PowerTool, SqrtTool
from langgraph.prebuilt import create_react_agent
from LLM.gemini_service import get_gemini_llm
from parser import print_stream, get_user_choice, create_prompt

async def main():
    print("📚 PHYSICS & CHEMISTRY PROBLEMS")

    # Setup
    tools = [AddTool(), SubtractTool(), MultiplyTool(), DivideTool(), PowerTool(), SqrtTool()]
    agent = create_react_agent(get_gemini_llm(), tools)

    questions = [
        """🚗 PHYSICS: A truck travels 75km at 45km/h, then 120km at 80km/h.

        Sub-questions: 
        1) Time for first segment?
        2) Average speed for entire journey?""",

        """🔬 CHEMISTRY: Mix Solution A (350ml at 18.5%) with Solution B (275ml at 22.8%).

        Sub-questions: 
        1) Pure acid in Solution A?
        2) Final concentration percentage?"""
    ]

    # Get user choice
    problem_num = get_user_choice(questions)
    if not problem_num:
        return

    # Solve chosen problem
    question = questions[problem_num - 1]
    print(f"\n{'=' * 60}")
    print(f"💭 SOLVING PROBLEM {problem_num}:")
    print(f"{question}")
    print('=' * 60)

    # Create and run agent
    prompt = create_prompt(question)
    inputs = {"messages": [{"role": "user", "content": prompt}]}
    config = {"configurable": {"thread_id": f"problem_{problem_num}"}, "recursion_limit": 15}

    print("\n🔄 AGENT PROCESS:")
    print("-" * 30)

    try:
        print_stream(agent.stream(inputs, config, stream_mode="values"))
        print(f"\n✅ COMPLETED")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())