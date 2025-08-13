"""
本文件为 FlowisePy 的组件开发提供了统一的结构、类型和接口规范，是组件系统的基础支撑代码。

【前后端数据交互与校验流程说明】

1. 前端根据组件的输入（ComponentInput）和输出（ComponentOutput）规范，动态渲染参数表单，用户填写参数后将数据以结构化 JSON 格式提交给后端。
2. 后端接收到前端提交的数据后，首先根据组件定义的参数类型（ParamType）进行类型校验和必填校验，确保数据格式和内容的正确性。
3. 校验通过后，后端将参数传递给对应的组件实例，执行组件的核心逻辑（如模型推理、数据处理等）。
4. 组件执行完毕后，将输出结果按照 ComponentOutput 规范进行结构化封装，再以 JSON 格式返回给前端。
5. 前端根据输出规范展示结果，或将结果作为下一个节点的输入，实现工作流的数据流转。

开发者只需继承 `BaseComponent` 并实现必要方法，即可快速开发自定义组件，系统会自动适配上述前后端数据交互和校验流程，保证组件的可用性和一致性。
"""
from enum import Enum
from abc import ABC,abstractmethod
from typing import Any,Dict,List,Optional,Type

class ComponentInput:
    """组件所需的输入的格式规范（定义）类，方便前端展示"""
    def __init__(
            self,
            name: str,
            type: str,
            label: str,
            description: str = '',
            required: bool = True,
            default: Any = None,
            options: Optional[List[Dict[str, Any]]] = None,
            placeholder: str = '',
            validation: Optional[Dict[str, Any]] = None,
            ui_hidden: bool = False # 是否在ui中隐藏输入框
    ):
        self.name = name
        self.type = type
        self.label = label
        self.description = description
        self.required = required
        self.default = default
        self.options = options or []
        self.placeholder = placeholder
        self.validation = validation or {}
        self.ui_hidden = ui_hidden
    
    def to_dict(self) -> Dict[str, Any]:  # -> 只是一个提醒，提醒这个方法最终的输出是字典
        # 这个to_dict方法，可以把已经定义好的组件（ComponentInput）的属性和值转换成字典格式，进而可以很方便地序列化为JSON，存储到数据库、文件，或者通过接口传递给前端等。
        # 让组件的结构化信息可以标准化存储和传输，便于后续的读取、展示和使用。
        return {
            'name':self.name,
            'type':self.type,
            'label': self.label,
            'description':self.description,
            'required': self.required,
            'default': self.default,
            'options': self.options,
            'placeholder': self.placeholder,
            'validation': self.validation,
            'ui_hidden': self.ui_hidden
        }
    
class ComponentOutput:
    """组件的输出的格式规范（定义）类，方便前端展示"""
    def __init__(self,name: str, type: str, description: str = "") :
        self.name = name
        self.type = type
        self.description = description
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description
        }
    
class ParamType(str, Enum):
    """
    参数类型常量类。
    主要用于标明组件参数的数据类型，便于前端渲染表单、后端校验参数类型，
    以及将参数结构化存储到数据库时，明确每个参数的类型。
    """
    STRING = 'string'         # 字符串类型
    NUMBER = 'number'         # 数值类型
    BOOLEAN = 'boolean'       # 布尔类型
    SELECT = 'select'         # 单选下拉
    MULTISELECT = 'multiselect' # 多选下拉
    JSON = 'json'             # JSON对象
    FILE = 'file'             # 文件类型
    CODE = 'code'             # 代码片段
    PASSWORD = 'password'     # 密码/密钥类型
    ARRAY = 'array'          # 数组类型
    OBJECT = 'object'        # 对象类型

class ComponentParam:
    """
    这个类就是对组件本身参数的类型、结构做统一的定义和规范。不是组件框架
    主要作用：
    1. 前端可以根据这个类的结构，自动生成参数填写表单，并对用户输入做类型和必填校验，提升交互体验。
    2. 后端可以用这个结构化信息，方便地把参数存到数据库，并且能标注每个参数的类型、默认值、可选项等，便于后续读取、校验和处理。
    3. 通过标准化参数定义，组件的扩展、维护和自动化识别都更方便。
    """
    def __init__(
            self,
            name: str,                      # 参数名称（唯一标识）
            type: str,                      # 参数类型（如string/number/boolean等，参考ParamType）
            label: str,                     # 参数在前端展示的标签
            description: str = "",          # 参数描述，前端可用于提示
            required: bool = False,         # 是否必填
            default: Any = None,            # 默认值，类型不限
            options: Optional[List[Dict[str, Any]]] = None, # 可选项（如下拉框），每项为{"label":..., "value":...}
            **kwargs                        # 额外自定义属性，便于扩展
    ):
        """
        例子：
        ComponentParam(
            name="temperature",
            type="number",
            label="温度",
            description="控制生成文本的随机性",
            required=False,
            default=0.7,
            foo="自定义参数"
        )
        # 其中 foo 会被收集到 self.extra_props 里
        """
        self.name = name
        self.type = type
        self.label = label
        self.description = description
        self.required = required
        self.default = default
        self.options = options or []
        self.extra_props = kwargs

    def to_dict(self) -> Dict:
        """
        转换为字典，方便序列化、存储和前后端传递。
        """
        result = {
            'name': self.name,
            'type': self.type,
            'label': self.label,
            'description': self.description,
            'required': self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.options:
            result["options"] = self.options
        result.update(self.extra_props)
        return result

class ComponentMetadata:
    """组件元数据类，用于规范化组件的元数据结构"""

    REQUIRED_FIELDS = ["name", "type", "category", "description"]

    def __init__(self,
                 name: str,
                 type: str,
                 category: str,
                 description: str,
                 icon: str = '',
                 version: str = '1.0.0',
                 inputs: Optional[List[Dict]] = None,
                 outputs: Optional[List[Dict]] = None,
                 params: Optional[List[Dict]] = None,
                 tags: Optional[List[str]] = None,
                 examples: Optional[List[Dict]] = None):
        self.name = name
        self.type = type
        self.category = category
        self.description = description
        self.icon = icon
        self.version = version
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.params = params or []
        self.tags = tags or []
        self.examples = examples or []
        
    
    def to_dict(self) -> Dict[str, Any]:
        """将元数据转换为字典，方便序列化、存储和前后端传递"""
        return {
            'name': self.name,
            'type': self.type,
            'category': self.category,
            'description': self.description,
            'icon': self.icon,
            'version': self.version,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'params': self.params,
            'tags': self.tags,
            'examples': self.examples
        }
    
    """
    @staticmethod装饰器将一个普通方法转换为静态方法。静态方法与普通实例方法的主要区别在于：
    - 不会自动接收self参数（实例引用）或cls参数（类引用）
    - 可以直接通过类名调用，无需创建类的实例
    - 无法访问实例属性或类属性（除非显式传递）

    “无法访问实例属性或类属性（除非显式传递）”的意思是：
        - 静态方法内部没有self（实例）或cls（类）参数，因此不能直接访问或修改实例的属性（如self.xxx）或类的属性（如cls.xxx）。
        - 如果你确实需要在静态方法里用到某个实例或类的属性，必须把实例或类对象作为参数显式传递进去，然后通过参数访问。
        - 具体做法举例：
            1. 访问类属性时，可以将类对象作为参数传入：
                @staticmethod
                def foo(cls, ...):
                    print(cls.SOME_CLASS_VAR)
                # 调用时：MyClass.foo(MyClass, ...)
            2. 访问实例属性时，可以将实例对象作为参数传入：
                @staticmethod
                def bar(instance, ...):
                    print(instance.some_instance_var)
                # 调用时：MyClass.bar(obj, ...)
        - 这样做可以让静态方法更独立、通用，不依赖于具体的对象状态。
    
    另外一个方法上有多个演示器，则依据自下而上的顺序执行，即：
    @装饰器1
    @装饰器2
    @装饰器3
    def 函数():
        print("函数执行")
    
    则是：装饰器1（装饰器2（装饰器3（函数）））
    """
    @staticmethod
    def validate(metadata: Dict, required_fields: Optional[list] = None) -> bool:
        """验证元数据是否符合要求，可通过参数传入需要的字段列表"""
        fields = required_fields or ComponentMetadata.REQUIRED_FIELDS
        for field in fields:
            if field not in metadata or not metadata[field]:
                return False
        return True
# 基类定义
class BaseComponent(ABC):
    """
    组件基础抽象类 - 所有组件必须继承此类
    是组件的框架，规定了组件必须实现的核心方法
    即get_metadata()获取组件元数据和execute()执行组件核心逻辑，验证参数和输入是否有效
    """
    
    @classmethod #表明这个是类方法，第一个参数是cls
    @abstractmethod #表明这个是抽象方法，子类不用这个方法，就无法实例化
    def get_metadata(cls) -> Dict:
        """
        获取组件元数据

        返回值必须包含以下字段：
        - name: 组件名称
        - type: 组件类型
        - category: 组件类别
        - description: 组件描述
        - 可选字段: icon, version, inputs, outputs, params, tags, examples

        return：
            Dict: 包括组件名称、类型、类别、描述、输入、输出和参数定义的字典
        """
        pass  # 基类不实现，子类必须重写（即子类自己要写一个方法实现）
    
    
    @abstractmethod
    # async是Python 3.5及以上引入的异步编程关键字，表示该函数是一个“协程函数”，可以被异步调度器（如asyncio）并发执行。
    # 使用async定义的函数，返回的是一个协程对象（coroutine），需要用await关键字等待其执行结果，或者由事件循环调度。
    # 这样可以在遇到IO操作（如网络请求、磁盘读写等）时不阻塞主线程，提高程序并发性能。
    async def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行组件的核心处理逻辑（异步方法）

        用法说明：
            该方法由每个具体组件子类实现，负责根据输入(inputs)和参数(params)进行实际的数据处理、API调用或业务逻辑，并返回结果字典。
            在工作流执行引擎中，会自动调用每个节点（组件）的execute方法，传入上游节点的输出和当前节点的参数配置。

        为什么要用async：
            很多AI组件（如调用OpenAI、HuggingFace等API，或数据库、网络IO操作）都涉及耗时的异步IO。
            如果用同步方法，遇到慢的网络请求会阻塞整个进程，导致系统吞吐量低、响应慢。
            使用async/await可以让Python在等待IO时切换去执行其他任务，实现高并发和非阻塞，极大提升系统性能。
            例如：多个节点并行调用API时，主线程不会被某个慢请求卡住。

        当某个组件需要调用API或者从数据库获取数据时，
        这个方法会被“暂停”执行（即遇到await时挂起），
        等待API调用完成或数据获取到之后，才会继续执行后续代码。
        这样不会阻塞主线程，系统可以同时处理更多任务。

        标准如下：
        Args:
            inputs: 输入数据，键为输入名称，值为输入值
            params: 参数数据，键为参数名称，值为参数值

        Returns:
            Dict[str, Any]: 输出数据，键为输出名称，值为输出值

        注意：
            子类实现时，遇到异步操作（如API请求）应使用await等待结果。
            该方法必须为异步，否则无法在异步工作流调度器中并发执行。
        """
        pass

    @classmethod
    def validate_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证参数是否有效

        Args：
            params：被验证的参数字典
        
        Rerurns:
            Dict[str， Any]：验证后的参数字典
        
        Raises：
            ValueError：参数验证失败
        """
        metadata = cls.get_metadata()
        param_defs = {p["name"]: p for p in metadata.get("params", [])}
        
        for name,param_def in param_defs.items():
            if param_def.get("required", False) and name not in params:
                raise ValueError(f"必须参数 '{name}' 未被提供")        
        return params

    # 在项目运行时，@classmethod 的作用是让该方法可以通过类本身直接调用，而不需要实例化对象。
    # 这样可以在不创建组件实例的情况下，直接用类名访问和校验参数/输入等逻辑，便于元数据管理、参数校验等全局操作。
    @classmethod
    def validate_inputs(cls,inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证输入是否有效
        
        Arags:
            inputs；被验证的字典类型的输入
            
        Returns：
            Dict[str, Any]: 验证后的字典类型的输入
        
        Raises：
            ValueError：输入验证失败
        """
        metadata = cls.get_metadata()
        """这句代码是一个字典推导式（dict comprehension），其详细含义如下：
        1. metadata.get("inputs", [])：从 metadata 这个字典中获取 "inputs" 这个键对应的值，如果没有则返回空列表 []。
        通常 "inputs" 是一个列表，列表中的每个元素 i 是一个输入定义的字典，例如 {"name": "text", "type": "str"}。
        2. for i in ...：遍历 "inputs" 列表中的每一个输入定义字典 i。
        3. i["name"]: i：以每个输入定义字典 i 中的 "name" 字段作为 key，整个输入定义字典 i 作为 value。
        4. 组合成一个新的字典 input_defs，其结构为 {输入名称: 输入定义字典, ...}。
        这样做的目的是：将输入定义列表转化为以输入名称为键、输入定义为值的字典，方便后续通过名称快速查找输入定义。
        举例说明：
        假设 metadata.get("inputs", []) 返回 [
            {"name": "text", "type": "str", "required": True},
            {"name": "lang", "type": "str", "required": False}
        ]
        则 input_defs 结果为：
        {
            "text": {"name": "text", "type": "str", "required": True},
            "lang": {"name": "lang", "type": "str", "required": False}
        }
        """
        
        input_defs = {i["name"]: i for i in metadata.get("inputs", [])}

        for name, input_def in input_defs.items():
            # 检查必填项是否存在
            if input_def.get("required", True) and (name not in inputs or inputs[name] is None):
                raise ValueError(f"必须输入的 '{name}' 未被提供")
            
            # 如果输入存在，检查类型是否匹配
            if name in inputs and inputs[name] is not None:
                input_type = input_def.get("type")
                value = inputs[name]

                # 简单类型检查
                if input_type == "string" and not isinstance(value, str):
                    raise TypeError(f"输入'{name}'期望字符串类型，但是收到了{type(value).__name__}")        
                elif input_type == "number" and not isinstance(value, (int,float)):
                    raise TypeError(f"输入'{name}'期望数字类型，但是收到了{type(value).__name__}")
                elif input_type == "boolean" and not isinstance(value, bool):
                    raise TypeError(f"输入'{name}'期望布尔类型，但是收到了{type(value).__name__}")
                
        return inputs
    
@classmethod
def map_output_to_input(cls, output: Dict[str, Any], input_name: str) -> Any:
    """
    将上游组件的输出映射到当前的组件的输入

    Args:
        output: 上游组件的输出字典
        input_name: 当前组件要接受的输入名称
    
    Returns:
        适合当前组件输入的值
    """
    # 默认实现，直接查找同名的键
    if input_name in output:
        return output[input_name]
    
    # 如果没有同名键，但只有一个输出值，可以直接使用
    if len(output) == 1:
        return next(iter(output.values()))
    
    # 找不到合适的映射
    raise ValueError(f"无法将输出映射到输入'{input_name}'")