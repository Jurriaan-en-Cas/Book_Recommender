import boto3
from os import environ
import database.database_handler as database
import xmltodict

MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

mturk = boto3.client('mturk',
                     aws_access_key_id=environ["AWS_ACCESS_KEY"],
                     aws_secret_access_key=environ["AWS_ACCESS_SECRET"],
                     region_name='us-east-1',
                     endpoint_url=MTURK_SANDBOX
                     )


def print_account_balance():
    print("I have $" + mturk.get_account_balance()['AvailableBalance'] + " in my Sandbox account")


def create_recommendation(user_name, genre, read_book):
    question = open('question.xml', mode='r').read().format(read_book, genre)
    new_hit = mturk.create_hit(
        Title='Recommend two books',
        Description='Recommend two books based on a given book and genre',
        Keywords='book, recommendation',
        Reward='0.15',
        MaxAssignments=5,
        LifetimeInSeconds=172800,
        AssignmentDurationInSeconds=180,
        AutoApprovalDelayInSeconds=14400,
        Question=question
    )
    print("A new HIT has been created. You can preview it here:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
    database.register_hit(new_hit['HIT']['HITId'], user_name)


def retrieve_recommendation_hit(user_name):
    hit_id = database.get_hit(user_name)
    if len(hit_id) == 0:
        return database.get_all_recommended_books_for_user(user_name)
    hit_id = hit_id[0]
    worker_results = mturk.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])
    print(worker_results)
    result = []
    for assignment in worker_results['Assignments']:
        xml_doc = xmltodict.parse(assignment['Answer'])
        answer_fields = xml_doc['QuestionFormAnswers']['Answer']
        result.append(answer_fields[0]['FreeText'])
        result.append(answer_fields[1]['FreeText'])
    if worker_results['NumResults'] == 5:
        for item in result:
            database.create_book(item, 0)
            database.add_recommended_book(user_name, item)
        database.delete_hit(user_name)
    return result
