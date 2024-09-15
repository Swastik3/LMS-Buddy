from uagents import Agent, Bureau, Context, Model
 

study_plan = Agent(name="flux", seed="flux")

# Define the message structure
class Message(Model):
    message: str
 
# Create agents
emma = Agent(name="Emma", seed="emma_seed")
liam = Agent(name="Liam", seed="liam_seed")
 
# Define behaviour for Emma
@emma.on_interval(period=3.0)
async def send_message(ctx: Context):
    # Create an instance of the Message class with the desired content
    message_to_liam = Message(message="Hey Liam, how's it going?")
    # Send the message to Liam
    await ctx.send(liam.address, message_to_liam)
 
# Define behavior for handling messages received by Emma
@emma.on_message(model=Message)
async def emma_message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
 
# Define behavior for handling messages received by Liam
@liam.on_message(model=Message)
async def liam_message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(emma.address, Message(message="Hello Emma! Great and you?"))
 
# Create a bureau and add agents
bureau = Bureau()
bureau.add(emma)
bureau.add(liam)
 
# Run the bureau
if __name__ == "__main__":
    bureau.run()