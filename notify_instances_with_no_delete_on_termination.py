#!/usr/bin/env python3.6

"""
If an EC2 instance is started with any EBS volume that has
deleteOnTermination set to False, notify us via SMS.

In future we may want to do other things, such as
terminate the instance and delete the volume.
"""

import json

import boto3


def lambda_handler(event, context):  # pylint: disable=unused-argument
    """
    This function is the lambda entry point.
    """
    if not "items" in event["detail"]["requestParameters"]["blockDeviceMapping"]:
        print("No volumes attached to this instance. Exiting.")
        return    
    bdm = event["detail"]["requestParameters"]["blockDeviceMapping"]["items"]
    bad = [x for x in bdm if x["ebs"]["deleteOnTermination"] is False]
    if bad:
        print("Found a volume with deleteOnTermination set to False!")
        sns = boto3.client("sns")
        resp = sns.publish(
            TopicArn="arn:aws:sns:us-west-2:064561331775:non-deleted-volume",
            Subject="Instance started with volume with deleteOnTermination=False!",
            Message=json.dumps(event),
        )
        print("Sent MessageId {} to SNS topic.".format(resp["MessageId"]))

    else:
        print("No volumes have deleteOnTermination set to False, we are ok.")


if __name__ == "__main__":
    with open("example-event.json") as filehandle:
        lambda_handler(json.load(filehandle), None)
