import json
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import os
import re
import sys
import time


def get_message_for_slack(event_details, event_type, affected_accounts, affected_entities, slack_webhook):
    message = ""
    summary = ""
    if slack_webhook == "webhook":
        if len(affected_entities) >= 1:
            affected_entities = "\n".join(affected_entities)
            if affected_entities == "UNKNOWN":
                affected_entities = "All resources\nin region"
        else:
            affected_entities = "All resources\nin region"
        if len(affected_accounts) >= 1:
            affected_accounts = "\n".join(affected_accounts)
        else:
            affected_accounts = "All accounts\nin region"      
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "danger",
                            "fields": [
                                { "title": "Account(s)", "value": affected_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                          
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "00ff00",
                            "fields": [
                                { "title": "Account(s)", "value": affected_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                                
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }
    else:
        if len(affected_entities) >= 1:
            affected_entities = "\n".join(affected_entities)
            if affected_entities == "UNKNOWN":
                affected_entities = "All resources\nin region"
        else:
            affected_entities = "All resources in region"
        if len(affected_accounts) >= 1:
            affected_accounts = "\n".join(affected_accounts)
        else:
            affected_accounts = "All accounts in region"      
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
               "text": summary,
                "accounts": affected_accounts,
                "resources": affected_entities,
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "accounts": affected_accounts,
                "resources": affected_entities,                
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            }
    
    print("Message sent to Slack: ", message)
    return message


def get_org_message_for_slack(event_details, event_type, affected_org_accounts, affected_org_entities, slack_webhook):
    message = ""
    summary = ""
    if slack_webhook == "webhook":
        if len(affected_org_entities) >= 1:
            affected_org_entities = "\n".join(affected_org_entities)
        else:
            affected_org_entities = "All resources\nin region"
        if len(affected_org_accounts) >= 1:
            affected_org_accounts = "\n".join(affected_org_accounts)
        else:
            affected_org_accounts = "All accounts\nin region"        
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "danger",
                            "fields": [
                                { "title": "Account(s)", "value": affected_org_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_org_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                                  
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "00ff00",
                            "fields": [
                                { "title": "Account(s)", "value": affected_org_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_org_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                                
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }
    else:
        if len(affected_org_entities) >= 1:
            affected_org_entities = "\n".join(affected_org_entities)
        else:
            affected_org_entities = "All resources in region"
        if len(affected_org_accounts) >= 1:
            affected_org_accounts = "\n".join(affected_org_accounts)
        else:
            affected_org_accounts = "All accounts in region"        
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
               "text": summary,
                "accounts": affected_org_accounts,
                "resources": affected_org_entities,
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "accounts": affected_org_accounts,
                "resources": affected_org_entities,                
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            } 
    json.dumps(message)
    print("Message sent to Slack: ", message)
    return message


def cleanup_time(event_time):
    """
    Takes as input a datetime string as received from The AWS Health event_detail call.  It converts this string to a
    datetime object, changes the timezone to EST and then formats it into a readable string to display in Slack.

    :param event_time: datetime string
    :type event_time: str
    :return: A formatted string that includes the month, date, year and 12-hour time.
    :rtype: str
    """
    event_time = datetime.strptime(event_time[:16], '%Y-%m-%d %H:%M')
    return event_time.strftime("%Y-%m-%d %H:%M:%S")


def get_last_aws_update(event_details):
    """
    Takes as input the event_details and returns the last update from AWS (instead of the entire timeline)

    :param event_details: Detailed information about a specific AWS health event.
    :type event_details: dict
    :return: the last update message from AWS
    :rtype: str
    """
    aws_message = event_details['successfulSet'][0]['eventDescription']['latestDescription']
    return aws_message


def format_date(event_time):
    """
    Takes as input a datetime string as received from The AWS Health event_detail call.  It converts this string to a
    datetime object, changes the timezone to EST and then formats it into a readable string to display in Slack.

    :param event_time: datetime string
    :type event_time: str
    :return: A formatted string that includes the month, date, year and 12-hour time.
    :rtype: str
    """
    event_time = datetime.strptime(event_time[:16], '%Y-%m-%d %H:%M')
    return event_time.strftime('%B %d, %Y at %I:%M %p')
