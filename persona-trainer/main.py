import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

client = openai.OpenAI()
model = 'gpt-4'

# persona_trainer_assist = client.beta.assistants.create(
#     name='Persona Trainer Assistant',
#     instructions="""You are the best personal trainer and nutritionist who knows how to get clients to build lean muscles. You've trained high-caliber athletes and movie stars. """,
#     model=model
# )
# assistent_id = persona_trainer_assist.id
# print(assistent_id)


# thread

# thread = client.beta.threads.create(
#     messages=[ 
#         {
#         "role":"user",
#         "content" : "How do i get started working out to lose weight?"
#         }
#     ]
# )
# thread_id = thread.id
# print(thread_id)

# hardcodeID
assistent_id = 'asst_ncdaN3oQu281DTCRV7pyNCpw'
thread_id = 'thread_dPeHHVxFc08McTwTuPzpg0sZ'

# create message
message = "how much calories should i eat in a day to lose weight"
message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role='user',
    content=message
)

#run assistant

run = client.beta.threads.runs.create(
    assistant_id=assistent_id,
    thread_id=thread_id,
    instructions='Please addres the user as james',
)

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """

    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)

#run
wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

#logs
run_step = client.beta.threads.runs.steps.list(
    thread_id=thread_id,
    run_id=run.id
)

print(f'step id: {run_step.data[0]}')