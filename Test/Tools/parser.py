#!/usr/bin/env python3
"""
Message parser and formatter for LangGraph agent outputs
"""
import json
import re


def format_json_content(content):
    """Format JSON content nicely - show only the latest JSON"""
    if isinstance(content, list):
        content = "".join(content)

    content = content.replace('```json\n', '').replace('```', '').strip()

    if '{' in content and '}' in content:
        json_objects = re.findall(r'\{[^}]*\}', content)
        if json_objects:
            latest_json = json_objects[-1]
            try:
                parsed = json.loads(latest_json)
                formatted = json.dumps(parsed, indent=2)
                print(f"📋 JSON:")
                print(f"   {formatted}")
            except:
                print(f"📋 JSON: {latest_json}")
        else:
            print(f"🧠 THINKING: {content}")
    else:
        print(f"🧠 THINKING: {content}")


def print_stream(stream):
    """Helper function to format streaming output nicely"""
    for s in stream:
        message = s["messages"][-1]
        if hasattr(message, 'type'):
            if message.type == "ai":
                if message.content:
                    format_json_content(message.content)

                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        args_str = ", ".join([f"{k}={v}" for k, v in tool_call['args'].items()])
                        print(f"🔧 TOOL: {tool_call['name']}({args_str})")

            elif message.type == "tool":
                print(f"📊 RESULT: {message.content}")
                print()


def get_user_choice(questions):
    """Get user's problem choice"""
    print("\nAvailable Problems:")
    for i, q in enumerate(questions, 1):
        title = q.split(':')[0] + ":"
        print(f"{i}) {title}")

    try:
        choice = input("\nChoose (1 or 2): ").strip()
        problem_num = int(choice)

        if problem_num not in [1, 2]:
            print("❌ Please choose 1 or 2")
            return None

        return problem_num

    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid choice")
        return None


def create_prompt(question):
    """Create formatted prompt for the agent"""
    return f"""{question}

INSTRUCTIONS:
Solve each sub-question step by step using tools.
Provide JSON for each sub-question:

{{"sub_question": 1, "description": "what you calculated", "result": number, "unit": "units"}}

Work systematically through all sub-questions."""