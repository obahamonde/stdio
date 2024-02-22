import asyncio
import json

from openai import AsyncOpenAI

ai = AsyncOpenAI(base_url="https://www.oscarbahamonde.com/v1", api_key="ccc")


async def chat(prompt: str) -> str:
    result = await ai.completions.create(
        prompt=prompt,
        model="TheBloke/Mistral-7B-Instruct-v0.2-AWQ",
        max_tokens=60,
    )
    return result.choices[0].text


async def main():
    initial_prompt = "What is the meaning of life?"
    while True:
        with open("chat.txt", "a") as f:
            response = await chat(initial_prompt)
            print(response)
            f.write(
                json.dumps(
                    {
                        "messages": [
                            {"role": "user", "content": initial_prompt},
                            {"role": "assistant", "content": response},
                        ]
                    }
                )
                + "\n"
            )
            initial_prompt = response
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
