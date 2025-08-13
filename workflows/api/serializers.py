from rest_framework import serializers  # 导入Django REST framework的序列化器模块
from workflows.models import Workflow, Edge  # 导入工作流相关的模型
from components.models import Node # 导入节点模型

# 边的序列化器，用于将Edge模型对象转换为JSON等格式，或反序列化
class EdgeSerializer(serializers.ModelSerializer):
    class Meta:  # Meta是Django中用于配置序列化器行为的内部类
        model = Edge  # 指定序列化的模型为Edge
        fields = '__all__'  # 序列化模型的所有字段

# 节点的序列化器，用于将Node模型对象转换为JSON等格式，或反序列化
class NodeSerializer(serializers.ModelSerializer):
    class Meta:  # 内部类Meta用于配置序列化器
        model = Node  # 指定序列化的模型为Node
        fields = '__all__'  # 序列化模型的所有字段

# 工作流的序列化器，用于将Workflow模型对象及其关联的节点和边序列化
class WorkflowSerializer(serializers.ModelSerializer):
    # 定义nodes字段，使用NodeSerializer进行序列化，many=True表示是多个节点，read_only=True表示只读
    nodes = NodeSerializer(many=True, read_only=True)
    # 定义edges字段，使用EdgeSerializer进行序列化，many=True表示是多条边，read_only=True表示只读
    edges = EdgeSerializer(many=True, read_only=True)

    class Meta:  # 内部类Meta用于配置序列化器
        model = Workflow  # 指定序列化的模型为Workflow
        # 指定需要序列化的字段，包括基本信息和关联的nodes、edges
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'nodes', 'edges']

# 解释说明：
# 1. 这些序列化器的作用是将Django模型对象（如Workflow、Node、Edge）转换为前端或API可以识别的格式（如JSON），
#    也可以将前端传来的数据反序列化为模型对象，便于数据库操作。
# 2. 在每个序列化器类中定义的内部类Meta，是Django和DRF的标准写法，用于配置序列化器的行为，比如指定模型和字段。
#    这不是在“类里面定义另一个类”的通用做法，而是Django/DRF的约定俗成，Meta类不会实例化，只是用来存储配置信息。
# 3. 从项目运行的角度看，这些序列化器是API接口和数据库之间的数据桥梁。前端请求API时，后端用这些序列化器将数据库对象转为JSON返回；
#    前端提交数据时，后端用这些序列化器校验和保存数据到数据库。
# 4. 通过嵌套NodeSerializer和EdgeSerializer，WorkflowSerializers可以一次性返回一个工作流及其所有节点和边的信息，方便前端展示和操作。