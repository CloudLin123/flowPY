#功能：定义组件库的数据库模型，实现组件库的数据持久化层，说人话就是连接组件和前端可视化的，将组件变成数据结构存在数据库
    # 将组件信息放入数据库，确保组件信息不会因重启而消失
    # componentcategory组件分类管理。
    # component存储组件的详细信息，包括组件的名称、描述、类型、参数等。通过class_path可以动态加载组件类（python类）
    # componentparam定义每个组件可配置的参数，类型包括字符串、数字和选择框
    # 能够让前端展示组件、生成参数编辑界面和保存用户配置的参数
    # 与registry.py中的组件类关联，实现组件的动态加载和参数配置

"""
ORM（对象关系映射，Object-Relational Mapping）是一种程序设计技术
它通过将数据库中的表结构映射为编程语言中的对象，使开发者可以用面向对象的方式操作数据库，而无需直接编写SQL语句。
ORM的核心思想是将关系型数据库的数据表、字段与程序中的类、属性一一对应，从而实现数据的持久化和对象化管理。
ORM不仅简化了数据库操作，还提高了代码的可维护性和可移植性。

ORM并不是Django特有的。虽然Django自带了功能强大的ORM系统，但在其他编程语言和框架中也有许多流行的ORM实现。
例如，Python中有SQLAlchemy，Java中有Hibernate，C#中有Entity Framework等。
Django的ORM只是众多ORM实现中的一种。

在生产环境中，ORM作为应用层与数据库之间的桥梁，负责将对象的增删改查操作自动转换为底层的SQL语句，并与数据库进行交互。
ORM可以帮助开发者屏蔽不同数据库的细节差异，提高开发效率。
但在高并发或复杂查询场景下，ORM生成的SQL可能不如手写SQL高效，因此在生产环境中有时需要结合原生SQL优化性能。
"""

from django.db import models  # 导入Django的ORM模型基类
from django.contrib.auth.models import User  # 导入Django自带的用户模型（如需关联用户可用）
from workflows.models import Workflow


# 组件的数据模型，用于存储组件的详细信息，包括组件的名称、描述、类型、参数等。通过class_path可以动态加载组件类（python类）
class ComponentCategory(models.TextChoices):
    """
    这个类是Django框架特有的“枚举类型”写法，它并不会在数据库中直接生成一张表或者MySQL的ENUM类型字段。
    ComponentCategory 继承自 models.TextChoices，主要作用是在Django模型层面为CharField等字段提供可选项（choices），
    让你在Python代码里用枚举的方式管理所有组件类别，并自动生成 choices 列表，方便前后端交互和后台管理界面展示。
    这样做的好处是代码更清晰、可维护性更高，前端也能直接拿到所有可选项。
    但它不会在数据库层面生成一张表，也不会变成MySQL的ENUM类型，底层还是varchar字段+choices约束，所有校验和交互都在Django后端完成。

    组件类别枚举（仅Django模型层专用，不直接对应MySQL的ENUM类型）。
    这里“用于定义所有可用的组件大类，便于在CharField字段中作为choices参数使用”——
    通俗来说，就是你在创建或编辑一个组件时，前端页面会自动给你一个下拉框，里面的选项就是这里定义的所有类别（比如“语言模型”、“记忆”、“链”等）。
    这样用户在选择组件类别时，不用自己手动输入，直接选就行了，既方便又能保证数据规范，后台和前端都能统一管理这些类别选项。
    注意：models.TextChoices 只在Django ORM中生效，迁移到MySQL时会被映射为varchar字段+choices约束，
    并不会自动变成MySQL的ENUM类型。

    用ORM的思维来看，如果ComponentCategory是一个Django模型（Model），那么它会在数据库中生成一张名为ComponentCategory的表，
    这张表有很多列（字段），每个字段名分别是LANGUAGE_MODELS、MEMORY、CHAINS、AGENTS、TOOLS、DICUMENT_LOADERS、VECTOR_STORES、TEXT_SPLITTERS、RETRIEVERS、EMBEDDINGS、PROMPTS、OUTPPUT_PARSERS、UTILITIES。
    每一列下面有两行内容，分别是英文代码（如language_models）和中文描述（如“语言模型”）。

    但实际上，Django的TextChoices并不会真的生成一张表，而是用来给CharField等字段提供choices选项，底层还是varchar字段+choices约束。
    CharField是Django模型中用于存储字符串（文本）的字段类型，通常对应数据库中的varchar类型。它用来保存短文本，比如名字、类型、类别等。
    choices是CharField等字段的一个参数，用于限定该字段的可选值范围。你可以把choices理解为“允许填入的选项列表”，它通常是一个元组或TextChoices枚举。
    这样，Django会在后台校验时只允许你填入choices里定义的值，前端自动渲染为下拉框，用户只能选这些选项，不能随便输入其他内容。
    
    choices定义的是某个字段（比如category）的所有可选项，比如ComponentCategory.MEMORY = ("memory", "记忆")，那么前端下拉框会显示“记忆”，实际存储的是"memory"。
    但如果你有两个下拉框，第一个选了MEMORY，第二个下拉框的内容是否联动，取决于你的前端逻辑和后端接口设计。
    Django的choices本身只负责限定某个字段的可选值，不会自动联动多个下拉框。
    在后端，Django会在你保存模型数据时校验：只有choices里定义的值才能存进CharField字段，否则会报错。
    **数据库实际存储的是choices的第一个值（如"memory"），第二个值（如"记忆"）通常用于后台管理界面或前端展示。
    总结：choices+CharField的组合，保证了数据的规范性和一致性，前端能自动生成下拉框，后端能自动校验，数据库里存的是英文代码，展示时可以用中文描述。
    """
    LANGUAGE_MODELS = "language_models", '语言模型'  # 语言模型
    MEMORY = "memory", '记忆'  # 记忆
    CHAINS = "chains", '链'  # 链
    AGENTS = "agents", '代理'  # 代理
    TOOLS = "tools", '工具'  # 工具
    DICUMENT_LOADERS = "document_loders", '文档加载器'  # 文档加载器
    VECTOR_STORES = "vector_stores", '向量存储'  # 向量存储
    TEXT_SPLITTERS = "text_splitters", '文本分割器'  # 文本分割器
    RETRIEVERS = "retrievers", '检索器'  # 检索器
    EMBEDDINGS = "embeddings", '嵌入'  # 嵌入
    PROMPTS = "prompts", '提示词'  # 提示词
    OUTPPUT_PARSERS = "output_parsers", '输出解析器'  # 输出解析器
    UTILITIES = "utilities", '工具'  # 工具

class ComponentType(models.TextChoices):
    """
    组件类型枚举，定义所有可用的组件类型（更细粒度）。
    和ComponentCategory类似，都是用来给CharField字段提供choices选项，
    但ComponentCategory是“组件大类”（比如“语言模型”、“记忆”、“链”等），
    而ComponentType是“组件具体类型”（比如“llm”、“chat_model”、“embedding”等），
    粒度更细，通常一个类别下可以有多个类型。

    也就是说，这两个枚举类的内容本质上就像“标签”一样，目的是给每个组件打上合适的标签，实现分类管理。
    ComponentCategory负责大类标签，ComponentType负责更细致的类型标签。
    这样做的好处是：前端可以根据这些标签（枚举值）自动生成下拉框，用户选择时不用手动输入，保证数据规范一致；
    后端和数据库也能统一校验和管理，方便后续扩展和维护。
    """
    LLM = "llm", '语言模型'  # 语言模型
    CHAT_MODEL = 'chat_model', '对话模型'  # 对话模型
    EMBEDDING = 'embedding', '嵌入'  # 嵌入
    VECTOR_STORE = "vector_store", '向量存储'  # 向量存储
    PROMPT = "prompt", '提示词'  # 提示词
    MEMORY = "memory", '记忆'  # 记忆
    CHAIN = "chain", '链'  # 链
    AGENT = "agent", '代理'  # 代理
    TOOL = "tool", '工具'  # 工具
    OUTPUT_PARSER = "output_parser", '输出解析器'  # 输出解析器
    DOCUMENT_LOADER = "document_loader", '文档加载器'  # 文档加载器
    TEXT_SPLITTER = "text_splitter", '文本分割器'  # 文本分割器
    RETRIEVER = "retriever", '检索器'  # 检索器
    UTILITY = "utility", '工具'  # 工具

class Component(models.Model):
    """
    组件数据模型，描述一个可持久化的组件对象
    
    这三个字符字段后面括号里的参数作用和意义如下：
        1. name = models.CharField('名称', max_length=100)
            - '名称'：这是该字段在Django后台管理界面或表单中显示的中文标签，便于用户理解字段含义。
            - max_length=100：指定该字段允许存储的最大字符数为100，超出会报错。数据库中通常对应VARCHAR(100)。
            - CharField：用于存储短文本字符串，适合如名称、类型、类别等。

        2. type = models.CharField('类型', max_length=50, choices=ComponentType.choices)
            - '类型'：该字段的中文显示名。
            - max_length=50：最大字符长度为50。
            - choices=ComponentType.choices：限定该字段的可选值只能是ComponentType枚举中定义的选项，前端会自动渲染为下拉框，后端自动校验，保证数据规范。

        3. category = models.CharField('类别', max_length=50, choices=ComponentCategory.choices)
            - '类别'：该字段的中文显示名。
            - max_length=50：最大字符长度为50。
            - choices=ComponentCategory.choices：限定该字段的可选值只能是ComponentCategory枚举中定义的选项，前端渲染下拉框，后端校验，保证一致性。

        总结：
        - 第一个参数（如'名称'、'类型'、'类别'）是字段的中文标签，提升可读性和用户体验。
        - max_length参数用于限制最大字符数，防止超长数据存储，保证数据库结构合理。
        - choices参数（如type和category字段）用于限定可选值范围，自动生成下拉框并校验，保证数据规范和一致性。
    """
    name = models.CharField('名称', max_length=100)  # 组件名称
    
    """
    type字段使用choices=ComponentType.choices，category字段使用choices=ComponentCategory.choices
    这样写的作用如下：
        1. 用户使用角度：
            - 在Django后台管理界面或自动生成的表单中，type和category字段会自动渲染为下拉框，用户只能从预设的选项中选择，无法随意输入，避免了数据混乱。
            - choices的第一个值（如"memory"）实际存入数据库，第二个值（如"记忆"）用于界面展示，提升用户体验。
        2. 后端逻辑角度：
            - Django在保存模型数据时会自动校验，只有choices中定义的值才能被保存到数据库，否则会报错，保证了数据的规范性和一致性。
            - 便于后续代码中通过get_xxx_display()方法获取中文描述，方便展示和处理。
    """
    type = models.CharField('类型', max_length=50, choices=ComponentType.choices)  # 组件类型，使用ComponentType枚举
    category = models.CharField('类别', max_length=50, choices=ComponentCategory.choices)  # 组件类别，使用ComponentCategory枚举

    description = models.TextField('描述', blank=True)  # 组件描述，可为空
    icon = models.CharField('图标', blank=True, null=True, max_length=255)  # 组件图标路径，可为空
    version = models.CharField('版本', max_length=20, default='1.0.0')  # 组件版本，默认1.0.0

    # 组件输入、输出、参数定义，均以JSON格式存储，便于前后端交互和动态渲染
    input_schema = models.JSONField('输入定义', default=list, blank=True)  # 输入定义，默认为空列表
    output_schema = models.JSONField('输出定义', default=list, blank=True)  # 输出定义，默认为空列表
    params_schema = models.JSONField('参数定义', default=dict, blank=True)  # 参数定义，默认为空字典

    class_path = models.CharField(
        '类路径', 
        max_length=255, 
        help_text="组件类的导入路径，例如“components.implementations.llms.gemini.GeminiComponent”"
    )  # 组件类的Python导入路径，用于动态加载
    created_at = models.DateTimeField('创建时间', auto_now_add=True)  # 创建时自动记录当前时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)      # 每次保存时自动更新时间

    def __str__(self):
        """
        这个方法的作用是什么？
            __str__是Python类的特殊方法，用于定义当对象被str()、print()等函数调用时，应该返回什么字符串。
            在Django模型中，__str__方法决定了后台管理界面、shell等地方显示这个对象时的文本内容，提升可读性。
        
        __str__的写法有什么含义？
            这里返回的是"组件名称 (类型的中文显示)"，比如"记忆组件 (记忆)"。这样可以一眼看出对象的主要信息。
            你可以根据实际业务需要自定义返回内容，只要是字符串即可。

        __str__和__init__一样吗？
            不一样。__init__是对象初始化时自动调用的方法，用于设置属性；__str__是对象被转为字符串时自动调用的方法，用于返回描述性文本。
            两者都是Python的"魔法方法"，但用途完全不同。

        这个方法怎么用？
            你可以直接用str(对象)或者print(对象)来调用__str__方法。例如：
                component = Component.objects.first()
                print(component)  # 实际上会调用component.__str__()

        总结：__str__让你的模型对象在各种界面和日志中显示得更友好、更直观，是Django开发的推荐写法。
        """
        # Django会自动为带choices的字段生成get_XXX_display方法
        # 实际运行时是没有问题的，静态检测的问题，不用管
        return f"{self.name} ({self.get_type_display()})" 
    """
    下面这个Meta类是Django模型的“内部类”，用于定义模型的元数据（Meta information）
    1、为什么要在类里面再定义一个 class Meta？
        首先，这里的“模型”是指Django中的Model类，也就是用来描述和数据库表结构一一对应的Python类。
        你可以把它理解为数据库中一张表的蓝图，里面定义了有哪些字段（列）、每个字段的类型、以及和其他表的关系等。
    
        在Django中，如果你想给模型（也就是数据库表）添加一些额外的配置信息，比如：
            - 这张表在数据库里叫什么名字（表名）
            - 默认按照哪个字段排序
            - 哪些字段组合必须唯一（联合唯一约束）
            - 在后台管理界面显示成什么名字
            这些都属于“元数据”（Meta information），而不是模型的业务字段本身。
        
        Django规定：如果你要自定义这些元数据，必须在模型类的内部再写一个名为Meta的内部类（class Meta），
        然后把这些配置信息写在Meta类里面。Django会自动识别这个Meta类，并根据里面的设置来调整数据库表的行为和后台显示效果。
        
        举个例子：
            如果你在Component模型里写了class Meta: verbose_name = '组件'，
            那么在Django后台管理页面，这个模型就会显示为“组件”而不是默认的英文名。
            class Meta就是Django模型的“配置中心”，用来集中管理和声明模型的各种元数据，让你的模型既能描述数据结构，又能灵活控制数据库和后台的行为。
        
        在CharField等字段的choices参数中，确实可以为每个选项定义“显示内容”，
        但那只是针对该字段在表单、后台等地方的取值显示（比如类型字段显示“记忆”、“LLM”等）。
        而verbose_name和verbose_name_plural是针对整个模型（即数据库表/对象）的显示名。
        “添加 组件”和“组件列表”在Django后台界面中有不同的含义和用途：
        - “添加 组件”通常出现在新增按钮或页面标题中，表示用户可以新建一个“组件”对象。这里用的是verbose_name（单数），强调的是“添加一个”。
        - “组件列表”则出现在后台菜单或数据列表页面，表示展示所有“组件”对象的集合。这里用的是verbose_name_plural（复数），强调的是“多个”或“列表”。
        这两者的区别在于：前者用于单个对象的操作（如新增），后者用于对象集合的展示（如列表、批量操作）。
        通过分别设置verbose_name和verbose_name_plural，可以让Django后台在不同场景下显示更符合中文语境的名称，提升用户体验。
        
        这两个配置主要影响Django后台管理界面、admin菜单、表头等地方的模型名称显示，
        让你的模型在后台更直观易懂。choices和verbose_name/verbose_name_plural的作用对象和场景不同，互不冲突。
    
    2. 作用：Meta类不是用来实例化对象的，而是用来告诉Django这个模型有哪些额外的配置信息。
    比如：verbose_name/verbose_name_plural（后台显示名）、unique_together（联合唯一约束）、indexes（索引）、ordering（默认排序）等。
    
    3. 意义：通过Meta类，开发者可以非常灵活地为模型添加数据库层面的约束、优化后台管理界面、提升查询效率等，而不用把这些配置和业务字段混在一起。
    4. 设计思想：这种“类中类”的写法其实是Django的一种约定俗成，类似于“声明式配置”，让模型的结构和元数据分离，代码更清晰。
    总结：class Meta的存在就是为了让Django能自动识别和应用这些元数据配置，提升模型的可维护性和功能性。
    """
    class Meta:
        """
        在中文Django项目中，通常会将verbose_name和verbose_name_plural都设置为“组件”。
        这样在后台管理界面，无论是“添加 组件”还是“组件列表”，都能自然符合中文语境，不会出现生硬的复数形式。
        如果你希望在“组件列表”处显示为“组件列表”，可以将verbose_name_plural设置为“组件列表”，如:verbose_name_plural = '组件列表'
        但大多数情况下，直接用“组件”即可，简洁且符合习惯。也就是说verbose_name_plural=xxx那么后台就会显示“xxx列表”，verbose_name同理。
        """
        verbose_name = '组件'  # 后台单数显示名
        verbose_name_plural = '组件'  # 后台复数显示名

        # unique_together：这是Django模型Meta类中的一个元组或列表，用于设置“联合唯一约束”。
        # 作用：要求数据库中同一张表的某几列的组合值必须唯一，不能出现重复。
        # 意义：比如 ('name', 'type')，表示同名同类型的组件只能有一条，防止重复数据。
        # 区别：与单字段unique=True不同，unique_together是针对多个字段的联合唯一。
        unique_together = ('name', 'type')  # 组件名称和类型这同一个表内的两个列的组合值要唯一，禁止出现重复

        # indexes：这是Django 2.2+支持的Meta类属性，用于为模型指定数据库索引。
        # 作用：通过为某些字段（如type和category）创建索引，可以大幅提升这些字段的查询效率。
        # 意义：当你经常根据type和category筛选组件时，数据库会利用索引加速检索。
        # 区别：indexes可以灵活指定单字段或多字段联合索引，和unique_together不同，索引不要求唯一性，只是加速查询。
        indexes = [
            models.Index(fields=['type', 'category']),  # 为type和category字段创建联合索引，加速查询
        ]


# 节点数据模型，用于存储节点信息，包括节点名称、类型、参数等。
class Node(models.Model):
    """节点模型：工作流中的组件实例"""
    workflow = models.ForeignKey(Workflow, on_delete = models.CASCADE, related_name = "nodes")
    node_id = models.CharField(max_length = 255) # 节点id
    component_type = models.CharField(max_length = 255) # 组件类型
    data = models.JSONField(default = dict) # 节点配置参数
    # 误报，在Django中，FloatField(default=0)是完全有效的，但类型检查器期望的是Django内部类型。
    position_x = models.FloatField(default = 0) # 节点在画布里的x坐标
    position_y = models.FloatField(default = 0) # 节点在画布里的y坐标

    def __str__(self):
        return f"{self.component_type} ({self.node_id})"

