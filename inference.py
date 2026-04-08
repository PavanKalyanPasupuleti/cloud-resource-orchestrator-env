import os, textwrap
from openai import OpenAI
from client import OrchestratorClient
from models import OrchestratorAction

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-70B-Instruct")

SYSTEM_PROMPT = textwrap.dedent("""
    You are an Expert Cloud Capacity Manager.
    Your goal is to solve the current task based on metrics.
    
    RULES:
    1. If Users are very low (less than 100), use: scale_down
    2. If Status says 'Servers reduced', use: switch_to_spot
    3. If Users are massive (100,000), FIRST use: enable_cdn
    4. If Status says 'CDN enabled', use: scale_up
    5. ONLY if none of the above apply and Latency is high, use: scale_up
    
    Respond ONLY with the command string. No extra text.
""")

def main():
    if not API_KEY:
        print("Error: HF_TOKEN or OPENAI_API_KEY not set.")
        return

    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=API_KEY)
    
    for task_id in [0, 1, 2]:
        print(f"\n--- Task {task_id} ---")
        # FIXED: Changed port 8000 to 7860
        env_url = os.getenv("ENV_URL", "http://localhost:7860")
        
        with OrchestratorClient(base_url=env_url).sync() as env:
            obs = env.reset(task_id=task_id).observation
            for step in range(1, 5):
                resp = client.chat.completions.create(model=MODEL_NAME, messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Users: {obs.active_users}, Latency: {obs.latency_ms}ms, Status: {obs.message}"}
                ])
                action = resp.choices[0].message.content.strip()
                print(f"Action: {action}")
                res = env.step(OrchestratorAction(command=action))
                obs = res.observation
                print(f"Score: {res.reward}")
                if res.done: break

if __name__ == "__main__":
    main()
