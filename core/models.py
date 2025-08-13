from django.db import models
from django.contrib.auth.models import User

# 凭证模型
class Credential(models.Model):
    """凭证模型：安全存储API密钥等敏感信息"""
    # name字段表示“凭证的名称”，即用户为每一条凭证自定义的标识名（如“我的OpenAI Key”、“公司Huggingface凭证”等）。
    # 一个用户可以拥有多个凭证，每个凭证都可以有不同的name，方便区分和管理。
    # 这里的“凭证列表”其实就是指用户拥有的多条凭证记录，每条记录有自己的name。
    name = models.CharField(max_length=255, help_text="凭证名称，用于区分和标识不同的凭证（如‘OpenAI Key1’）")
    credential_type = models.CharField(max_length = 255) # 例如：‘openai’、‘huggingface’
    data = models.JSONField(default = dict) # 加密存储的凭证依据
    # user字段用于关联Django自带的User模型，实现凭证与具体用户的绑定关系。
    # related_name只是给反向查询起名字，不会影响任何用户的一对多的关系。
    # 你这个系统每个用户都可以有多个凭证（即一对多），只要用ForeignKey就对了，不管related_name写不写，都是一对多。
    # related_name的作用只是让你可以通过user.credentials.all()来获取该用户的所有凭证，更方便而已。
    # 如果不写related_name，默认就是user.credential_set.all()。
    # user字段用于将凭证与Django自带的User模型（即真实用户账号）建立外键关联。
    # 这样，用户通过账号密码登录系统后，可以通过user.credentials.all()（如果设置了related_name='credentials'）或user.credential_set.all()（默认）来管理和访问自己所有的凭证，实现“每个用户拥有自己的凭证列表”。
    # 只要用户登录，系统就能识别其身份并只允许其操作自己的凭证，保证凭证的私密性和安全性。
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='credentials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

