##
## OwlMind - Platform for Education and Experimentation with Generative Intelligent Systems
## discord.py :: Bot Runner for Discord
##

import re
import discord
from .botengine import BotMessage, BotBrain
from .llama_interface import run_llama_task


class DiscordBot(discord.Client):
    """
    DiscordBot provides logic to connect the Discord Runner with OwlMind's BotMind, 
    forming a multi-layered context in BotMessage by collecting elements of the Discord conversation
    (layer1=user, layer2=thread, layer3=channel, layer4=guild), and aggregating attachments, reactions, and other elements.
    """
    def __init__(self, token, brain:BotBrain, promiscous:bool=False, debug:bool=False):
        self.token = token
        self.promiscous = promiscous
        self.debug = debug
        self.brain = brain
        if self.brain:
            self.brain.debug = debug

        ## Discord attributes
        intents = discord.Intents.default()
        intents.messages = True
        intents.reactions = True
        intents.message_content = True
        #intents.guilds = True
        #intents.members = True

        super().__init__(intents=intents)
        return 

    async def on_ready(self):
        print(f'Bot is running as: {self.user.name}.')
        if self.debug:
            print(f'Debug is on!')
        if self.brain: 
            print(f'Bot is connected to {self.brain.__class__.__name__}({self.brain.id}).') 
            if self.brain.announcement:
                print(self.brain.announcement)
            self.brain.debug = self.debug
        
    async def on_message(self, message):
        # CUT-SHORT conditions
        if message.author == self.user or \
            (not self.promiscous and not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))):
            if self.debug:
                print(f'IGNORING: orig={message.author.name}, dest={self.user}') 
            return

        # Remove calling @Mention if in the message
        text = re.sub(r"<@\d+>", "", message.content,).strip()

        # === C&R Bot: Handle LLaMA Special Commands ===
        if text.startswith('!summarize'):
            prompt = text[len('!summarize'):].strip()
            await message.channel.send("Generating summary, please wait...")
            try:
                response = run_llama_task(task_type="summarization", user_input=prompt)
                await message.channel.send(response)
            except Exception as e:
                await message.channel.send(f"Error: {str(e)}")
            return

        if text.startswith('!flashcards'):
            prompt = text[len('!flashcards'):].strip()
            await message.channel.send("Generating flashcards, please wait...")
            try:
                response = run_llama_task(task_type="flashcards", user_input=prompt)
                await message.channel.send(response)
            except Exception as e:
                await message.channel.send(f"Error: {str(e)}")
            return

        if text.startswith('!quiz'):
            prompt = text[len('!quiz'):].strip()
            await message.channel.send("Generating quiz, please wait...")
            try:
                response = run_llama_task(task_type="quiz", user_input=prompt)
                await message.channel.send(response)
            except Exception as e:
                await message.channel.send(f"Error: {str(e)}")
            return

        # === Normal processing: Collect attachments, reactions, etc ===
        attachments = None
        reactions = None

        context = BotMessage(
                layer1       = message.guild.id if message.guild else 0,
                layer2       = message.channel.id if hasattr(message.channel, 'id') else 0,
                layer3       = message.channel.id if isinstance(message.channel, discord.Thread) else 0,
                layer4       = message.author.id,
                server_name  = message.guild.name if message.guild else '#dm',
                channel_name = message.channel.name if hasattr(message.channel, 'name') else '#dm',
                thread_name  = message.channel.name if isinstance(message.channel, discord.Thread) else '',
                author_name  = message.author.name,
                author_fullname = message.author.global_name,
                message      = text,
                attachments  = attachments,
                reactions    = reactions)

        if self.debug:
            print(f'PROCESSING: ctx={context}')
                              
        # Process through Brain
        if self.brain:
            self.brain.process(context)

        # Return any generated response
        if context.response:
            await message.channel.send(context.response)
        return

    def run(self):
        super().run(self.token)
