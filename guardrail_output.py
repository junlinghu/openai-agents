import asyncio

from pydantic import BaseModel
from agents import Agent,GuardrailFunctionOutput,OutputGuardrailTripwireTriggered, RunContextWrapper,Runner,output_guardrail

class MessageOutput(BaseModel): 
    response: str

class MathOutput(BaseModel): 
    reasoning: str
    is_math: bool

guardrail_agent = Agent(name="Guardrail check", instructions="Check if the output includes any math.",
                        output_type=MathOutput,)

@output_guardrail
async def math_guardrail(ctx: RunContextWrapper, agent: Agent, output: MessageOutput) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)
    final_out= result.final_output
    return GuardrailFunctionOutput(output_info=final_out,tripwire_triggered=final_out.is_math,)

customer_agent = Agent(name="Customer support agent",
            instructions="You are a customer support agent. You help customers with their questions.",
            output_guardrails=[math_guardrail], output_type=MessageOutput,)

async def main():
    userInput="Hello, can you help me solve for x: 2x + 3 = 11?"# This should trip the guardrail
    while True:
        userInput = input("Enter your request: ")
        if userInput.lower() == 'quit':
            print("Goodbye!")
            break
        
        try:
            await Runner.run(customer_agent,userInput)
            print("Guardrail didn't trip")
        except OutputGuardrailTripwireTriggered:
            print("Math output guardrail tripped")

if __name__ == "__main__":
    asyncio.run(main())