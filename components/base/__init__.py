# 为什么这里需要导入component和registry这两个文件的所有方法？
# 
# 1. from .component import * 的作用：
#    这样写会把 component.py 文件中所有没有以下划线“_”开头的类、函数、变量都导入到当前 base 包的命名空间。
#    这样做的好处是：其他地方只需要 from components.base import 类名，就能直接用到所有基础组件相关的类型和基类（如 BaseComponent、ComponentInput 等），
#    方便开发者快速继承和扩展，不用每次都写 from components.base.component import BaseComponent 这样冗长的路径。
#
# 2. from .registry import component_registry 的作用：
#    registry.py 里实现了组件注册表（单例模式），component_registry 是全局唯一的注册表实例。
#    导入它后，其他模块可以直接通过 component_registry 进行组件的注册、查询、自动发现等操作，实现组件的统一管理和动态加载。
#    这样做可以让整个系统的组件注册和发现机制变得非常简洁和集中，所有组件相关的注册、获取都通过这个全局对象完成。
from .component import *
from .registry import component_registry