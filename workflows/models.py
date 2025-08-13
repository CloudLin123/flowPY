from django.db import models

# 定义数据模型，继承models.Model这个基类，代表一个流程图，这个流程图是一个有向无环图
class Workflow(models.Model):
    """工作流模型：存储整个工作流的基本信息"""
    # CharField是Django模型中用于存储短字符串（如名称、标题等）的字段类型，对应数据库中的varchar类型，适合保存较短的字符串。
    name = models.CharField(max_length = 255) 
    # TextField是Django模型中用于存储大段文本（如描述、备注等）的字段类型，对应数据库中的text类型，适合保存长度较长的字符串。
    # blank=True 表示在Django的表单验证和后台管理界面中，该字段可以留空（即用户可以不填写）。
    # null=True 表示在数据库层面，该字段允许存储NULL值（即数据库中可以没有实际内容）。
    # 当同时设置blank=True和null=True时，既允许用户在表单中不填写该字段，也允许数据库中该字段为空，实现了“可选字段”的效果。
    description = models.TextField(blank=True, null=True)
    # auto_now_add=True：只在对象首次创建时自动设置当前时间（即“创建时间”），之后无论怎么修改对象，这个字段都不会再变，适合记录“创建时间”。
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now=True：每次保存对象（包括创建和更新）时都会自动更新为当前时间（即“最后更新时间”），适合记录“更新时间”。
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# 关系定义，用于定义节点之间的连接方式，定义了节点间的连接关系（数据流向）
class Edge(models.Model):
    """边模型：定义节点之间的连接方式"""
    # workflow字段是一个ForeignKey（外键），指向Workflow模型，表示每条边（Edge）都属于某一个具体的工作流实例。
    # 外键（ForeignKey）是关系型数据库中用于建立两个表之间关联关系的字段。在Django模型中，ForeignKey用于定义“一对多”关系：
    #   - 即一个工作流（Workflow）可以有多条边（Edge），但每条边只属于一个工作流。
    #   - 外键字段在当前表中存储的是被关联表（这里是Workflow）的主键值，实现表与表之间的连接。
    #   - 通过外键，可以方便地在代码中通过对象属性访问关联的对象。
    # 类似的还有：
    #   - OneToOneField（一对一关系）：比如用户和用户详情表，一对一绑定。
    #   - ManyToManyField（多对多关系）：比如学生和课程，一个学生可以选多门课，一门课也可以有多个学生。
    # on_delete=models.CASCADE表示如果关联的工作流被删除，这条边也会自动被删除，保证数据一致性。
    # related_name='edges'让你可以通过workflow.edges来反向获取该工作流下的所有边。

    workflow = models.ForeignKey(Workflow, on_delete = models.CASCADE, related_name = 'edges')

    # source_node和target_node分别表示边的起点和终点节点的id（字符串类型）。
    source_node = models.CharField(max_length = 255) # 源节点id
    target_node = models.CharField(max_length = 255) # 目标节点id

    # source_handle和target_handle分别表示连接时的“输出点”和“输入点”。
    # 输出点（source_handle）：指的是源节点上用于输出数据的具体端口或接口（比如某个参数、某个输出口），通常用于区分节点有多个输出的情况。
    # 输入点（target_handle）：指的是目标节点上用于接收数据的具体端口或接口（比如某个参数、某个输入口），通常用于区分节点有多个输入的情况。
    # 这两个字段可以为空（blank=True），如果节点只有一个输入/输出点时可以不填。
    
    # 输出点（source_handle）和输入点（target_handle）在一个节点上可以存在多个，通常用于区分节点有多个输入/输出端口的情况。
    # 但一条边（Edge）只能连接一个源节点的一个输出点到一个目标节点的一个输入点。
    # 如果需要多个节点通过多条边输入到同一个节点，或者一个节点的多个输出流向不同节点，需要建立多条Edge记录，每条边分别指定source_node/source_handle和target_node/target_handle。
    source_handle = models.CharField(max_length = 255, blank = True) # 源节点的输出点（一个边只对应一个输出点，但节点可有多个输出点）
    target_handle = models.CharField(max_length = 255, blank = True) # 目标节点的输入点（一个边只对应一个输入点，但节点可有多个输入点）

    def __str__(self):
        return f"{self.source_node} -> {self.target_node}"

