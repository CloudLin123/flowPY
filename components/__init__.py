# 在 __init__.py 里通过 default_app_config 指定apps.py中的ComponentsConfig为默认 app 配置入口。
default_app_config = 'components.apps.ComponentsConfig' 

# 导入组件注册表，方便其他模块使用
"""
以下两种方式都能实现单例模式的效果，最终得到的是同一个对象，区别只在于使用方式：
1. `from .base.registry import component_registry`：
   - 直接获取现成的单例实例，立即可用
   - 代码更简洁，无需再实例化

2. `from .base.registry import ComponentRegistry`：
   - 获取类定义后，还需自己实例化：`my_registry = ComponentRegistry()`
   - 虽然多了一步，但因为`__new__`方法的实现，创建的仍然是同一个实例
   - `my_registry`和全局的`component_registry`是同一个对象的引用

无论使用哪种方式，由于ComponentRegistry类的`__new__`方法实现了单例模式，确保了全局只有一个组件注册表实例存在。
这两种方式都能保证在整个应用程序中使用的是同一个组件注册表对象。
"""
from .base.registry import component_registry
