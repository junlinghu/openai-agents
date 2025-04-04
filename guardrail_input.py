import asyncio

from pydantic import BaseModel
from agents import Agent,GuardrailFunctionOutput,InputGuardrailTripwireTriggered,RunContextWrapper,Runner,TResponseInputItem,input_guardrail

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent(name="Guardrail check", instructions="Check if the user is asking you to do their math homework.",
                        output_type=MathHomeworkOutput,)


@input_guardrail
async def math_guardrail(ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    final_out= result.final_output
    return GuardrailFunctionOutput(output_info=final_out, tripwire_triggered=final_out.is_math_homework,)


agent = Agent(name="Customer support agent",instructions="You are a customer support agent. You help customers with their questions.",
              input_guardrails=[math_guardrail],)

async def main():
    userInput="Hello, can you help me solve for x: 2x + 3 = 11?"# This should trip the guardrail
    while True:
        userInput = input("Enter your request: ")
        if userInput.lower() == 'quit':
            print("Goodbye!")
            break

        try:
            await Runner.run(agent, userInput)
            print("Guardrail didn't trip")
        except InputGuardrailTripwireTriggered:
            print("Math homework guardrail tripped")

if __name__ == "__main__":
    asyncio.run(main())