# apps.py 是 Django 应用的配置文件，用于定义和配置该 app 的相关信息。
# 其中 ComponentsConfig 类继承自 AppConfig，是“components”这个 Django 应用的配置类。

from django.apps import AppConfig

class ComponentsConfig(AppConfig):
    """
    主要作用如下：
    1. 指定 app 的名称（name = 'components'），用于 Django 识别和管理该应用。
    2. 可以在该类中自定义 ready() 方法，实现 app 启动时的初始化逻辑（如信号注册、自动发现等）。
    3. default_auto_field 这个属性用于指定Django模型中主键字段（即每个表的唯一标识）的默认类型。
        设置为 'django.db.models.BigAutoField' 后，Django 在你新建模型且未显式声明主键时，
        会自动使用 BigAutoField（一个64位自增整型字段）作为主键类型。
        这样可以避免每次新建模型时都要手动指定主键类型，并且能支持更大的数据量，减少主键溢出的风险。
    4. 在 __init__.py 里通过 default_app_config 指定该配置类为默认 app 配置入口。
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'components'
    verbose_name = '组件系统'

    def ready(self):
        """当应用准备好启动时，自动发现和注册组件"""
        from .base.registry import component_registry

        # 自动发现和注册组件
        component_registry.auto_discover()
        # 同步组件到数据库
        self._sync_components_to_db()

    def _sync_components_to_db(self):
        """将组件注册表中的组件同步到数据库"""
        from .base.registry import component_registry  # 导入全局组件注册表实例
        from .models import Component  # 导入数据库模型Component

        # 遍历注册表中所有已注册的组件类
        for component_class in component_registry.get_all_components().values():
            metadata = component_class.get_metadata()  # 获取每个组件的元数据信息（如名称、类型、描述等）

            # 使用Django的update_or_create方法同步组件信息到数据库
            # 如果数据库中已存在同名同类型的组件，则更新其信息；否则新建一条记录
            Component.objects.update_or_create(
                name = metadata.get('name'),  # 组件名称，作为唯一标识之一
                type = metadata.get('type'),  # 组件类型，作为唯一标识之一
                defaults = {  # 其余字段作为默认值进行更新或创建
                    'category': metadata.get('category'),  # 组件类别
                    'description': metadata.get('description', ''),  # 组件描述，默认为空字符串
                    'icon': metadata.get('icon'),  # 组件图标
                    'version': metadata.get('version','1.0.0'),  # 组件版本，默认为1.0.0
                    'input_schema': metadata.get('inputs', []),  # 输入参数结构，默认为空列表
                    'output_schema': metadata.get('output', []),  # 输出参数结构，默认为空列表
                    # __module__ 和 __name__ 都是Python所有类对象自带的内置属性（不是BaseComponent自定义的），
                    # __module__ 表示该类定义所在的模块名（如 "components.implementations.xxx"），
                    # __name__ 表示类名本身（如 "MyComponent"）。
                    # 这两个属性任何Python类都有，返回的内容分别是字符串类型的模块路径和类名。
                    # 例如：MyComponent类定义在components.implementations.text模块下，则
                    # component_class.__module__ = "components.implementations.text"
                    # component_class.__name__ = "MyComponent"
                    # 所以拼接后可唯一定位到该类。
                    'class_path': f"{component_class.__module__}·{component_class.__name__}"  # 组件类的完整路径，便于后续动态加载
                }                
            )
