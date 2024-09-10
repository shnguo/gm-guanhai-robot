# -*- coding: utf-8 -*-

import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests
from alibabacloud_openapi_util.client import Client as util
from Tea.request import TeaRequest
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=False, verbose=True)
accessKeyId = os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID']
accessKeySecret = os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
securityToken = os.environ.get('ALIBABA_CLOUD_SECURITY_TOKEN', '')   # 可选，使用STS时需要提供
print(accessKeyId)
print(accessKeySecret)
method = 'POST'
body = 'hello world'
url = 'http://gm-guanhai-robot-online.vevor.net/health'   # 你的HTTP触发器地址
date = datetime.utcnow().isoformat('T')[:19]+'Z'
headers = {
    'x-acs-date': date,
    # 'x-acs-security-token': securityToken
}

parsedUrl = urlparse(url)
authRequest = TeaRequest()
authRequest.method = method
authRequest.pathname = parsedUrl.path.replace('$', '%24')
authRequest.headers = headers
authRequest.query = {k: v[0] for k, v in parse_qs(parsedUrl.query).items()}

auth = util.get_authorization(authRequest, 'ACS3-HMAC-SHA256', '', accessKeyId, accessKeySecret)
headers['authorization'] = auth
print(auth)

resp = requests.get(url, body, headers=headers)

print(resp.text)