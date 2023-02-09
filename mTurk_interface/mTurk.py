from collections import Counter

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
    hit = database.get_hit(user_name)
    if hit is not None:
        return

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


def create_verification_task(user_name, genre, read_book, recommendations):
    recommendation_string = parse_recommendations(recommendations)
    question = open('verification_question.xml', mode='r').read().format(read_book, genre, recommendation_string)
    new_hit = mturk.create_hit(
        Title='Verify book recommendation',
        Description='Verify a book recommendation based on a read book and genre',
        Keywords='book, recommendation, verification',
        Reward='0.15',
        MaxAssignments=2,
        LifetimeInSeconds=172800,
        AssignmentDurationInSeconds=180,
        AutoApprovalDelayInSeconds=14400,
        Question=question
    )
    print("A new HIT has been created. You can preview it here:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
    database.register_hit(new_hit['HIT']['HITId'], user_name, True)


def parse_recommendations(recommendations):
    result = "<div><ul>"
    i = 0
    for recommendation in recommendations:
        result += '<li><input type="checkbox" name={}>{}</li>'.format(recommendation, recommendation)
    result += "</ul></div>"
    return result


def retrieve_recommendation_hit(user_name):
    ## Only show stuff when in DB or show temp results?
    hit_id = database.get_hit(user_name)
    if hit_id is None:
        return database.get_all_recommended_books_for_user(user_name)
    hit_id = hit_id[0]
    worker_results = mturk.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted', 'Approved'])
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
    result.sort(key=Counter(result).get, reverse=True)
    return result

def generate_verification_tasks():
    ## Recommendation based on this book
    ## Workers came up with this result
    ## Is this a good result
    ## 2 tasks?
    saved_hits = database.get_all_hits(verification=False)
    for hit in saved_hits:
        hit_id = hit[0]
        worker_results = mturk.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted', 'Approved'])
        # if worker_results['NumResults'] == 5:
            ## TODO Generate verification task and delete hit from db.


def retrieve_verification_tasks():
    saved_hits = database.get_all_hits(verification=True)
    for hit in saved_hits:
        hit_id = hit[0]
        user_id = hit[1]
        worker_results = mturk.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted', 'Approved'])
        if worker_results['NumResults'] == 1:
            # Hit is completed, so we can parse the results and add them to the database.
            user_name = database.get_user_by_id(user_id)[1]
            for assignment in worker_results["Assignments"]:
                xml_doc = xmltodict.parse(assignment['Answer'])
                answer_fields = xml_doc['QuestionFormAnswers']['Answer']
                if len(answer_fields) == 0:
                    answer_fields = [answer_fields]
                for answer in answer_fields:
                    item = answer['QuestionIdentifier']

                    database.create_book(item, 0)
                    database.add_recommended_book(user_name, item)
            database.delete_hit(user_name, verification=True)


