# 基于Flowise构建LangChain应用指南
##本项目是作为我弟弟妹妹初步学习python的教程素材，代码里面有关于我觉得可能难理解的地方的注释，复刻的是flowise的开源项目

## 1. 项目概述

### 1.1 什么是Flowise
Flowise是一个基于LangChain的可视化AI工作流构建工具，允许用户通过拖拽方式创建AI应用，而无需编写大量代码。它的核心优势在于将复杂的LangChain组件图形化，让开发者可以直观地设计、测试和部署AI应用。

### 1.2 Flowise与LangChain的关系
Flowise实际上是LangChain的可视化封装层。LangChain提供了构建AI应用的各种组件和工具，而Flowise则提供了图形化界面来操作这些组件。在Python版复刻项目中，我们需要理解这种关系，并用Python实现类似的图形化界面来操作LangChain的Python库。

### 1.3 项目目标
通过Python语言复刻Flowise项目，实现一个可视化的LangChain应用构建工具，帮助用户快速创建、测试和部署基于大模型的AI应用。

## 2. 技术栈选择

### 2.1 后端技术
- Python 3.8+
- Django：用于构建Django RESTful framwork服务
- LangChain Python库：核心AI功能组件
- SQLAlchemy：数据库ORM
- SQLite/PostgreSQL：数据存储

### 2.2 前端技术
1. React - UI框架
特点与优势：
组件化架构，便于代码复用和维护
虚拟DOM机制，提供高效的渲染性能
单向数据流，使状态管理更可预测
丰富的生态系统和社区支持
选择理由：
对于工作流设计器这类复杂交互界面，React的组件化设计非常适合
支持动态UI渲染，适合工作流节点的动态加载和渲染
与其他库的兼容性好，便于集成第三方组件
2. React Router - 路由管理
特点与优势：
声明式路由定义，便于管理多页面应用
支持路由嵌套，适合复杂的应用结构
提供历史管理和参数传递机制
选择理由：
FlowisePy需要多个功能页面（Chatflows、Credentials等），需要良好的路由管理
支持URL参数，便于通过URL直接访问特定工作流
与React深度集成，提供一致的开发体验
3. Ant Design - UI组件库
特点与优势：
企业级设计语言和高质量组件
完整的设计系统，包括布局、导航、表单等
良好的主题定制能力
国际化支持（包括中文界面）
选择理由：
提供现成的高质量UI组件，加速开发
企业级设计风格适合专业工具类应用
完整的表单和数据展示组件，适合工作流配置界面
中文界面支持，符合项目需求（从截图可见界面是中文的）
4. React Flow - 工作流可视化
特点与优势：
专门为构建节点式工作流界面设计
支持自定义节点和边的样式与行为
提供拖拽、连接、缩放等核心交互
处理节点位置计算和布局管理
选择理由：
FlowisePy核心功能是工作流设计，需要专业的图形工作流引擎
提供完整的节点连接和管理能力，无需从零构建
性能优化良好，能处理复杂工作流图
API灵活，便于集成自定义组件系统
5. Axios - API请求
特点与优势：
基于Promise的HTTP客户端
拦截器机制，便于统一处理请求和响应
自动转换JSON数据
客户端支持防御XSRF
选择理由：
前后端分离架构需要可靠的API通信方案
比原生fetch提供更多功能和更好的错误处理
拦截器机制便于统一处理认证和错误情况
在React生态中使用广泛，有成熟的最佳实践
6. 状态管理：Zustand vs Redux
Zustand特点：
简洁的API，学习曲线平缓
基于hooks的使用方式
避免了Redux的模板代码
体积小巧
Redux特点：
严格的单向数据流
强大的中间件生态
时间旅行调试能力
适合大型、复杂应用
选择理由：
工作流平台需要全局状态管理（当前工作流、组件库等）
Zustand更轻量，适合中小型应用，上手更快
Redux更成熟，适合大型团队和复杂状态管理
推荐初期使用Zustand，若应用扩展可考虑Redux
### 2.3 开发工具
- VSCode/PyCharm：代码编辑器
- Git：版本控制
- Docker：容器化部署
- Pytest：测试框架

## 3. 系统架构设计

### 3.1 整体架构
整个系统采用前后端分离架构，分为三个主要模块：
- **前端模块**：负责可视化界面呈现和用户交互
- **后端API模块**：处理前端请求，管理工作流
- **组件库模块**：封装LangChain组件，提供标准接口

### 3.2 核心数据模型
- **工作流(Workflow)**：用户创建的AI流程
- **节点(Node)**：工作流中的基本组件
- **边(Edge)**：连接节点的线，表示数据流向
- **凭证(Credential)**：存储API密钥等敏感信息

### 3.3 工作流程
1. 用户在前端界面通过拖拽方式创建工作流
2. 系统将工作流保存到数据库中
3. 用户执行工作流时，系统按照节点之间的连接顺序执行组件
4. 执行结果实时返回给前端展示

## 4. 环境准备

### 4.1 Python环境配置
在开发环境中，我们需要创建虚拟环境并安装必要的依赖。主要包括LangChain、FastAPI、SQLAlchemy等核心库。

以下命令是在任意目录下运行：

1、使用miniconda来创建虚拟环境

    conda create -n flowpy python=3.10  创建虚拟环境
    conda env list  查看所有的虚拟环境

tips:不建议用python来创建新的虚拟环境，要是喜欢以下是方法

    python -m venv <环境名称>  创建环境
    <环境名称>/Scripts/activate   激活环境
    python --version    查看版本，默认是你下载的python版本，改不了，所以建议用miniconda或者Anaconda

这里最容易出现的问题如下：

    1、conda创建好了虚拟环境，但是activate后没有显示“（环境名称）”
    	那就执行以下指令：conda init powershell，然后重启终端，再activate



2、使用以下命令安装依赖

```
pip install django==4.2.10 djangorestframework==3.14.0 langchain==0.3.26 langchain-community==0.3.27 langchain-openai==0.3.27 sqlalchemy==1.4.50 pydantic==2.5.2 python-dotenv==1.0.0 django==4.2.10 
```

ps：从0开始的项目在下载依赖的时候，建议一个个下载，遇到兼容问题好一个个解决。



### 4.2 项目初始化
创建项目目录结构，初始化Git仓库，以及创建基础配置文件。

#### 1、利用Django来初始化项目
```
django-admin startproject <项目名称>    初始化项目，这个命令会初始化好这个项目的框架，本项目名称是flowisePy
cd <项目名称>

python manage.py startapp <文件名称>    初始化主要应用模块的文件结构
本项目现阶段需要执行以下命令创建核心应用模块：
python manage.py startapp core  		核心功能
python manage.py startapp components    LangChain组件封装
python manage.py startapp workflows     工作流管理与执行
```
#### 2、配置REST Framework
##### 1、在......\flowisePy\flowisePy下编辑settings.py
       INSTALLED_APPS = [
       # Django默认应用
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       
       # 第三方应用(你要手动加的)
       'rest_framework',
       
       # 自定义应用(你要手动加的)
       'core',
       'components',
       'workflows',
    ]
这是Django的核心配置，告诉Django哪些应用应该被加载
Django默认应用：框架自带的系统功能（管理后台、认证系统等）
rest_framework：你安装的Django REST Framework库，用于构建API
自定义应用：你通过python manage.py startapp创建的三个应用模块，Django需要知道它们的存在才能使用它们的功能

##### 2、初始化数据库、超级用户
    # 初始化数据库
    python manage.py makemigrations
    # 初次执行No changes detected会出现这个，属于正常，以后创建了数据类型后还得运行这个命令
    python manage.py migrate
    # 与上同理
    tips：以上初始化操作切记在各个app里，只要定义或者完成了关于初始化某些表的代码编程后，确定没问题了就得执行一次，这很重要
    
    超级用户（可选）
    python manage.py createsuperuser


##### 3、运行开发服务器测试
    验证服务器是否正常运行：访问 http://127.0.0.1:8000/
    python manage.py runserver

##### 4、常见问题的解决
    1、忘记在./components/base/registry.py完成后却没有初始化数据库的操作，出现django.db.utils.OperationalError: no such table: components_component报错。(这里提一嘴，记得注意)
    
    问题解释：registry.py里面利用了单表模式创建了一个数据表，代码完成了就需要进行初始化数据库的操作，这在上面的tips里有提到。结合下面的情景就不难知道，其实就是我在后续想起并开始初始化数据库的时候，Django框架接收到初始化指令开始按照规矩启动整个框架及其app，执行到apps.py的ready方法时就找不到所谓的组件表，找不到组件表就无法同步组件表，无法同步组件表就启动不了，启动不了初始化不了数据库，初始化不了数据库就会牵扯到这句报错上方诸多文件，最后发现是组件表不存在就告诉你了，先有鸡还是先有蛋的问题，哈哈哈哈哈哈哈哈哈。或者说你就看models.py文件有没有修改，有就得更新，没有就老老实实根据文档错误举一反三吧。
    
    情景介绍：我是写完这个文件后没更新数据库，然后往下继续写apps.py文件里面的ready方法（里面有自动注册组件表和自动同步到数据库的内容）后，还完成了一些组件的实现后才想起初始化的，执行命令就报出这个错误。
    
    解决方法：注释掉ready方法，然后老老实实在项目根目录下（你执行完ls指令后能看见manage.py的地方）执行以下命令
        python manage.py makemigrations
        python manage.py migrate
        python manage.py runserver
        python manage.py showmigrations # 查看哪些应用的数据库的迁移（初始化）被应用了，有[X]就是被用了



### 4.3 配置文件准备（暂时，后续步骤有需要再加）
准备环境变量配置文件，存储API密钥、数据库连接信息等敏感配置。

#### 现在是开发环境，所以用以下方法：

```
创建.env文件，复制以下内容：
# 数据库配置
DATABASE_URL=sqlite:///db.sqlite3
# 或者PostgreSQL配置
# DATABASE_URL=postgresql://user:password@localhost:5432/flowisepy

# API密钥（自己有什么api自己加）
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here

# 安全设置（自己随机生成一个SECRET_KEY，其他的不变）
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```


## 5.数据库模型设计

### 5.1在相应的应用中定义Django模型
介绍：Django模型这里指的是数据模型，而且这是langchain框架在Django后端框架实现时的数据模型。因为langchain的数据模型的数据在数据库中的映射的实现所用的方法是Django的，所以这里说的笼统了点就是Django模型。并且下面提到的模型的类(class)是以其功能作用为依据分别在component、core、workflow这三个文件夹的models.py里面。也就是说你直接点开这三个文件夹看到的models.py无一例外全是放Django模型。

#### 5.1.1工作流（workflow）模型

工作流模型是存储工作流基本信息的，也就是说整个模型抽象点来讲就是一个有向无环图(DAG),整个图就是一个工作流模型，其结构定义如下：

```
class Workflow(models.Model):
    args：
        name: 工作流的名称
        description：描述
        created_at: 创建时间戳
        update_at：修改时间戳
    
    function：
        __str__ -> return: 返回名字
    
```

#### 5.1.2边（edge）模型

边模型是和工作流模型放一个models.py里，用于定义节点之间的连接方式，定义了节点间的连接关系（数据流向）。其中涉及到外键的概念，外键是指关系型数据库中用于建立两个表之间的关联关系的字段，有ForeignKey(一对多)、OneToOneField(一对一)和ManyToManyField(多对多)。这里用的是用来描述工作流个边的数量关系的，即一对多，也就是说一个工作流可以无数条边；而N条边可以同时独属于某个工作流。其结构定义如下：

```
class Edge(models.Model):
    args:
        workflow: 建立“边”和“工作流”之间的关系。
        source_node: 源节点
        target_node: 目标节点
        source_handle: 源节点的输出点
        target_handle: 目标节点的输出点
    
    function：
        __str__ -> return: 返回这条边所连接的两个节点
```

#### 5.1.3节点（node）模型

节点模型位于componnets文件夹下的models.py里，用于存储节点信息，包括节点名称、类型、参数等，是工作流中的组件实例。与边模型同理，它与工作流也是存在一对多的关系。其结构定义如下：

```
class Node(models.Model):
    args:
        workflow: 与上同理
        node_id: 节点的唯一标识
        component_type: 该组件实例的类型
        data: 节点的配置参数内容
        position_x: 在画布上的横坐标
        position_y: 在画布上的纵坐标

    function：
        __str__ -> return: 返回组件实例的类型和id
```

#### 5.1.4凭证（credential）模型

凭证模型位于core文件夹下的models.py里，用于加密存储API密钥，类似的，在凭证模型里也存在一对多的情况，不过是用户和凭证的一对多关系。其结构定义如下：

```
class Credential(models.Model):
    args:
        name: 凭证的名称，区分不同的凭证的
        credential_type: 凭证类型
        data: 加密存储的凭证依据
        user: 建立与用户（Django关联的）的一对多的关系
        created_at: 创建时间
        updated_at: 更新时间

    function：
        __str__ -> return: 返回凭证名称
```

### 5.2迁移数据库模型

```
python manage.py makemigrations

python manage.py migrate
```

## 6. 组件库开发

### 6.1 组件接口定义

组件库是系统的核心，首先需要定义清晰的接口，包括节点参数类型、节点接口、输出接口等。

#### 创建基础抽象类定义节点接口

文件结构

```
components/
├── __init__.py
├── models.py          # 所有数据库模型
├── views.py           # 基础视图
├── urls.py            # URL路由
├── api/               # API相关
│   ├── __init__.py
│   ├── views.py       # API视图
│   ├── serializers.py # 序列化器
│   └── permissions.py # 权限控制
├── base/              # 核心接口定义
│   ├── __init__.py
│   ├── component.py   # 组件基类
│   └── registry.py    # 注册机制
└── implementations/   # 具体组件实现
    ├── __init__.py
    ├── llms/          # 语言模型组件
    │   ├── __init__.py
    │   └── openai.py
    ├── memory/        # 记忆组件
    └── chains/        # 链组件
```

base文件夹的作用
```
1、./base/component.py: 这个文件为 FlowisePy 的组件开发提供了统一的结构、类型和接口规范，是组件系统的基础支撑代码。也就是说这个文件定义了所有组件的整体框架和内容组成结构，是所有的组建的父类。开发者只需继承 `BaseComponent` 并实现必要方法，即可快速开发自定义组件，且能自动适配前后端的数据交互和校验流程。

2、./base/registry.py：这个文件是实现组件注册功能，特点是单表模式，只有一个注册表。方法有：注册组件、获取指定id的组件、获取所有组件、获取组件的元数据和自动扫描并发现组件。

3、./base/__init__.py：负责初始化的文件，没多大作用，就是方便后续继承基类和导入自动发现方法的时候导入语句不用写那么长
```

implementations文件夹的作用
```

```

#### 定义输入/输出参数规范

#### 设计节点元数据结构



### 6.2 基础节点类型实现

实现基础的节点类型，例如LLM节点、Prompt节点等，这些是构建工作流的基本单元。

#### 封装LangChain基础组件(LLM, Prompt等)
要下载的组件如下:
langchain-ollama==0.3.4、langchain-google-genai==2.0.10
llama-cpp-python要么下cpu版本：
```pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu```

要么就下载预编译的wheel，然后在相应的环境里面安装：
```
wheel网址：https://github.com/JamePeng/llama-cpp-python/releases?page=1
pip install D:\llama_cpp_python-0.3.13-cp310-cp310-win_amd64.whl
```

#### 实现节点参数验证

#### 创建基本节点连接逻辑



### 6.3 组件注册机制
创建组件注册表，方便系统动态加载组件，为前端提供可用节点列表。

#### 实现组件自动发现与注册系统

#### 创建组件目录和分类管理

每次像在implementations文件夹中导入完了所有的组件之后，需要运行python manage.py runserver命令



## 6. 后端API开发

### 6.1 API路由设计与实现
#### 工作流CRUD接口

#### 节点和边管理接口

#### 凭证管理接口



### 6.2 工作流执行引擎

工作流执行是系统的核心功能，需要按照有向无环图的拓扑顺序执行节点。

#### 实现工作流拓扑排序

#### 节点按顺序执行机制

#### 数据流转机制

#### 错误处理与日志记录



### 6.3 API文档和测试

#### 使用Django REST框架工具生成

#### 简单的测试服务



## 7. 前端开发

### 7.1 用户界面设计
前端界面主要分为以下几部分：
1. 左侧组件面板：显示所有可用节点
2. 中央画布：用于拖拽组件构建工作流
3. 右侧属性面板：编辑选中节点的属性
4. 顶部工具栏：提供保存、运行等操作

### 7.2 工作流可视化
使用React Flow实现可视化的流程图编辑，支持拖拽、连线等交互操作。

### 7.3 组件面板
实现左侧组件面板，用于展示和拖拽组件到画布上。

## 8. 系统集成与测试

### 8.1 工作流保存和加载
实现工作流的保存和加载功能，确保用户可以保存工作进度并随时恢复。

### 8.2 系统启动
编写系统启动脚本，确保所有服务正确启动和初始化。

### 8.3 单元测试
编写单元测试，确保系统各个组件的功能正常运行。

## 9. 部署与扩展

### 9.1 Docker化部署
使用Docker和Docker Compose简化部署过程，确保系统可以在不同环境中一致运行。

### 9.2 功能扩展
系统可扩展的功能包括：
1. **用户认证**：添加用户注册、登录和权限管理
2. **多语言支持**：添加对不同语言模型的支持
3. **导入导出**：支持工作流的导入导出
4. **版本控制**：工作流的版本管理和回滚
5. **实时协作**：多用户同时编辑工作流

### 9.3 性能优化
性能优化措施包括：
1. **异步执行**：长时间运行的工作流使用异步队列
2. **缓存机制**：缓存常用组件实例和结果
3. **节点并行化**：支持并行执行独立节点
4. **流式响应**：实现流式输出，提升用户体验

## 10. 开发路线图

### 10.1 第一阶段：核心功能
- 基础组件库实现
- 工作流创建和执行
- 简单的用户界面

### 10.2 第二阶段：增强功能
- 更多LangChain组件集成
- 完善错误处理和日志
- 工作流调试和测试工具

### 10.3 第三阶段：高级功能
- 用户权限和团队协作
- 工作流模板和市场
- API集成和自动化
