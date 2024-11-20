import boto3
import os


BUCKET = 'lmx-file'
MODEL = ['conf/earth_latest_high_prec.bpc', 'conf/naif0012.tls', 'conf/matrix.json']

AWS_ACCESS_KEY_ID = 'admin'
AWS_SECRET_ACCESS_KEY = 'admin123'
AWS_STORAGE_BUCKET_NAME = 'test'
AWS_S3_ENDPOINT_URL = 'http://192.168.128.225:7000'
AWS_S3_USE_SSL = False
client = boto3.client(
    's3',
    endpoint_url=AWS_S3_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    use_ssl=AWS_S3_USE_SSL,
)


def get_model(bucket: str, name: str, local_dir: str = './conf/'):
    model_key = f'/{name}'
    # 从OSS获取文件对象
    # ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html
    response = client.get_object(Bucket=bucket, Key=model_key)
    
    # 确定本地文件名
    local_filename = os.path.join(local_dir, name.split('/')[-1])
    
    # 确保本地目录存在
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # 将S3对象的内容写入到本地文件
    with open(local_filename, 'wb') as file:
        file.write(response['Body'].read())
    


if __name__ == '__main__':
    for model in MODEL:
        get_model(BUCKET, model)






