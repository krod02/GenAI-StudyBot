from dotenv import dotenv_values
from owlmind.discord import DiscordBot
from owlmind.botengine import SimpleBrain
from owlmind.llama_interface import run_llama_task



if __name__ == '__main__':

    # load token from .env
    config = dotenv_values(".env")
    TOKEN = config['TOKEN']
    ## Alternative: Hard-code your TOKEN here and remote the comment:
    # TOKEN={My Token} 

    # Load Simples Bot Brain loading rules from a CSV
    brain = SimpleBrain(id='bot-1')
    brain.load('rules/genAi.csv')

    # Kick start the Bot Runner process
    bot = DiscordBot(token=TOKEN, brain=brain, debug=True)
    bot.run()