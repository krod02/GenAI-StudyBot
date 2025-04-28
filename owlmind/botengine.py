from .agent import Agent, Plan
from .context import Context
from .llama_interface import run_llama_task  

##
## BASE CLASS FOR BOTMESSAGE
## This is the class received through BotBrain.process()

class BotMessage(Context):
    BASE_STANDARD = '.;'
    """
    Message format being passed to/from BotBrain logic
    """
    def __init__(self, **kwargs):
        
        # Load default fields and update with parameters
        default_fields = {
            'layer1': 0,
            'layer2': 0,
            'layer3': 0,
            'layer4': None,
            'server_name': '',
            'channel_name': '',
            'thread_name': '',
            'author_name': '',
            'author_fullname': '',
            'message': '',
            'attachments': None,
            'reactions': None
        }

        default_fields.update(kwargs)
        
        # Initialize Context
        super().__init__(facts=default_fields)
        return 

##
## BASE CLASS FOR BOTBRAIN
##

class BotBrain(Agent):
    """
    BotBrain logic
    """  
    def __init__(self, id):
        self.debug = False
        self.announcement = None
        super().__init__(id)

    def process(self, context:BotMessage):
        super().process(context=context)

##
## SIMPLEBRAIN
##

import csv

class SimpleBrain(BotBrain):
    """
    SimpleBrain provides a very simple Rule-based + AI-driven message processor.
    """
        
    def __init__(self, id):
        super().__init__(id)
        self += Plan(condition={'message':'_'}, action='I have no idea how to respond!')
        return 

    def load(self, file_name):
        """
        Load plans from a CSV file.
        """
        row_count = 0
        try:
            with open(file_name, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(row for row in file if row.strip() and not row.strip().startswith('#'))
                for row in reader:
                    condition = {key.strip(): value.strip() for key, value in row.items() if key and value and key.strip().lower() != 'response'}
                    response = row.get(next((k for k in row.keys() if k.strip().lower() == 'response'), ''), '').strip()
                    self += Plan(condition=condition, action=response)
                    row_count += 1
        except FileNotFoundError:
            if self.debug: print(f'SimpleBrain.load(.): ERROR, file {file_name} not found.')

        ## Update announcement
        self.announcement = f'SimpleBrain {self.id} loaded {row_count} Rules from {file_name}.'
        return 

    def process(self, context:BotMessage):
        """
        Expanded logic: first check for AI tasks, then fallback to rule-based matching.
        """
        text = context['message'].lower()   # ✅ CORRECTED HERE

        # ===> New Llama AI triggers
        if text.startswith("summarize"):
            input_text = text.replace("summarize", "", 1).strip()
            context.response = run_llama_task("summarization", input_text)

        elif text.startswith("flashcards"):
            input_text = text.replace("flashcards", "", 1).strip()
            context.response = run_llama_task("flashcards", input_text)

        elif text.startswith("quiz"):
            input_text = text.replace("quiz", "", 1).strip()
            context.response = run_llama_task("quiz", input_text)

        else:
            # Fallback to RULE-BASED matching
            if context in self.plans:
                if self.debug: print(f'SimpleBrain: response={context.best_result}, alternatives={len(context.all_results)}, score={context.match_score}')

                if self.is_action(context.best_result):
                    context.response = f'it should be an action here: {context.best_result[0], context.best_result[1]}'
                else: 
                    context.response = context.best_result
            else:
                # No rule matched and no Llama task triggered
                context.response = "I have no idea how to respond!"
        return
