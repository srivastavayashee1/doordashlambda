import json
import pandas as pd
import boto3
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

def lambda_handler(event,context):
    print("Event is:", event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    s3_client=boto3.client('s3')
    response=s3_client.get_object(Bucket=bucket,Key=key)
    file_Content=response["Body"].read().decode('utf-8')
    lst=file_Content.split('\r\n')
    df=pd.DataFrame(columns=['id','status','amount','date'])
    for e in lst:
        dict=json.loads(e)
        if  dict['status']=="delivered":
            df.loc[dict['id']]=dict
    df.to_csv('/tmp/prcoesseddata.csv',sep=',')
    try:
        str_date=str(date.today())
        new_filename="processedfolder/{}_processedfile.csv".format(str_date)
    except:
        new_filename="processedfolder/processedfile.csv"
    
    upload_response=s3_client.upload_file('/tmp/prcoesseddata.csv',os.environ['targetbucket'],new_filename)

    sns_client=boto3.client('sns')
    sns_client.publish(TopicArn=os.environ['snstopicarn']
                       ,Message="file {} has been formated and Filter.Processed file is Placed in {} with Name {}".format(key,os.environ['targetbucket'],new_filename))



