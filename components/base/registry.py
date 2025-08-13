from typing import Dict, List, Type, Any
# 用于函数参数和返回值的类型提示，提升代码可读性和类型安全，方便IDE和静态检查工具进行类型检查。
import importlib    
# 这个模块用于在运行时动态导入模块或类，比如根据字符串名称加载某个组件类，实现插件式的自动发现和注册机制，是实现组件自动加载的关键。
import inspect      
# inspect模块用于检查对象的类型、获取类的成员、判断某个对象是否为类、函数等。这里主要用于遍历模块中的所有类，筛选出继承自BaseComponent的组件类，实现自动注册。
import logging      
# logging模块是Python标准库的日志系统，用于记录系统运行过程中的调试信息、警告、错误等。这里用于输出组件注册、加载等过程中的日志，方便开发和排查问题。
from .component import BaseComponent

logger = logging.getLogger(__name__)

class ComponentRegistry:
    """
    组件注册表：用于管理系统里所有可用的组件

    常见疑问解答：

    1. 为什么 _instance = None 和 _components = {} 不是写成 cls._instance = None 或 cls._components = {}？
       - _instance = None 和 _components = {} 写在类体内（即class定义的缩进块里），这就是“类变量”的标准声明方式。
       - 这样写，Python会在类定义时自动把它们绑定到类对象上，等价于 ComponentRegistry._instance = None。
       - 如果你在类体外部写 cls._instance = None，cls 其实是未定义的（只有在方法体里才有cls），而且那样写法不规范。
       - 在类体内部直接写 _instance = None，所有实例和类方法都能通过 cls._instance 访问和修改，符合单例和全局注册表的需求。

    2. 为什么不是实例变量？
       - 如果写成 self._instance = None，就是每个实例各有一份，无法实现全局唯一的单例和组件注册表。
       - 类变量保证所有实例共享同一份数据。
    
    3. 类的实例化
        类的实例化通常有两种方式：
        1. 直接用 类名()，如 a = 类名()，这会自动调用__new__和__init__，生成一个新实例。
        2. 通过重写__new__方法，可以自定义实例的创建过程，比如实现单例模式（只允许创建一个实例）

        在这里，__new__方法的cls参数代表“类对象”，而self只在实例方法（如__init__）中出现，代表“实例对象”。
        只有通过a = 类名()这种方式创建出来的对象，self才有意义。
        
        通过重写__new__，我们可以控制：无论你写多少次 a = ComponentRegistry()，得到的都是同一个实例（单例）。
        这就是为什么要用cls（类对象）来做判断和保存实例的原因。
        
        这样做的好处是：全局只有一个组件注册表，所有地方用的都是同一个对象，方便统一管理组件。
        
        注意：即使你在文件开头或结尾写 a = 类名()，只要__new__实现了单例，a始终指向同一个实例，没有区别。
    
    4. 实际运行流程
        当你执行 a = ComponentRegistry() 时，Python 会自动调用 ComponentRegistry 类中的 __new__ 方法。
        由于我们重写了 __new__ 并实现了单例模式，所以无论你后续再执行多少次 a = ComponentRegistry()，返回的都是同一个实例（即 cls._instance）。
        由于类中没有定义 __init__ 方法，所以不会有额外的初始化逻辑，每次实例化都只是简单返回同一个对象。
        这意味着 self._components（实际上是类变量 _components）会一直保留之前所有注册过的组件信息，不会因为多次实例化而丢失或重置。
        换句话说，所有通过 ComponentRegistry() 得到的对象，访问 self._components 时，看到的都是同一份全局组件注册表数据。
        
        当你执行 a = ComponentRegistry() 时，会自动调用_new__方法。
        如果 _instance 还没有创建，则创建一个新的实例并赋值给 cls._instance。
        # 如果已经创建过，则直接返回之前创建的实例，实现单例模式。

    5. 总结：
       - 类变量（写在class体内）用于全局共享，适合单例、注册表等场景。
       - 实例变量（self.xxx）用于每个对象独立的数据。
       - cls.xxx 只是访问类变量的方式，定义时要写在类体内。
    """

    # _xxx这种写法就是告诉开发人员这是类对象的变量，别擅自改
    _instance = None 
    _components = {}

    def __new__(cls):
        # 实现单例模式，具体实现见上文多段注释
        if cls._instance is None:
            cls._instance = super(ComponentRegistry, cls).__new__(cls)
        return cls._instance
    
    def register_component(self, component_class: Type[BaseComponent]) -> None:
        """
        注册组件到系统

        Args：
            component_class: 组件类，必须继承自BaseComponent
        """
        # issubclass() 是Python内置函数，用于判断第一个参数（类）是否为第二个参数（类或元组）的子类。
        # 语法：issubclass(A, B) 如果A是B的子类（或A就是B本身），返回True，否则返回False。
        # 这里用issubclass(component_class, BaseComponent)判断传入的component_class是否继承自BaseComponent。
        # 这样可以保证只有符合规范的组件类才能被注册，防止类型错误。
        if not issubclass(component_class, BaseComponent):
            # 如果不是BaseComponent的子类，抛出类型错误（注意应为TypeError而不是TyperError）
            raise TypeError(f"{component_class.__name__} 不是BaseComponent的子类")
        
        # 调用组件类的get_metadata方法，获取组件的元数据信息（如类型、名称等）
        metadata = component_class.get_metadata()
        # 生成组件唯一ID，格式为“类型.名称”，如"llm.ChatOpenAI"
        component_id = f"{metadata.get('type')}.{metadata.get('name')}"
        # 将组件类注册到全局组件字典中，key为component_id，value为组件类本身
        self._components[component_id] = component_class
        # 记录日志，提示已注册该组件
        logger.info(f"已注册插件：{component_id}")

    def get_component_class(self, component_id: str) -> Type[BaseComponent]:
        """
        获取指定ID的组件类

        Args：
            component_id: 组件ID（格式为type.name）

        Returns:
            Type[BaseComponent]: 组件类对象

        Raises：
            ValueError: 如果组件未注册则抛出异常
        """
        # 检查组件ID是否已注册
        if component_id not in self._components:
            # 如果未注册，抛出异常并提示未注册的组件ID
            raise ValueError(f"组件'{component_id}' 未注册")
        # 返回对应的组件类对象
        return self._components[component_id]
    
    def get_all_components(self) -> Dict[str, Type[BaseComponent]]:
        """
        获取所有注册的组件

        Return
            Dict[str, Type[BaseComponent]]: 组件ID到组件类的映射
        """
        return self._components
    
    def get_components_metadata(self) -> List[Dict]:
        """
        获取所有组件的元数据

        Return
            List[Dict]: 组件元数据列表,一个Dict就是一个组件，Dict里的内容就是元数据的键值对
        """
        return [component.get_metadata() for component in self._components.values()]
    
    def auto_discover(self, package_name: str = "components.implementations") -> None:
        """
        自动发现和注册指定包中的组件

        主要作用：
            该方法用于自动发现并注册指定包（及其所有子包、子模块）中的所有组件类（即BaseComponent的子类）。
            这样开发者只需将自定义组件放在指定包下，无需手动注册，系统即可自动识别并完成注册，极大提升了组件扩展和维护的便利性。

        参数说明：
            package_name: str = "components.implementations"
                这里的 package_name 是一个带有默认值的参数，默认值为 "components.implementations"。
                这样写的作用是：如果调用 auto_discover() 时没有传入 package_name 参数，则会自动使用 "components.implementations" 作为要搜索的包名。
                这样可以让函数在大多数情况下自动扫描默认的实现包，也允许用户自定义要扫描的包名，提升了灵活性和可扩展性。

        主要用途：
            1. 方便调用：调用 auto_discover() 时可以不传参数，直接扫描默认包。
            2. 灵活扩展：如需扫描其他包，只需传入新的包名即可，无需修改函数内部代码。
            3. 便于维护：默认包名集中管理，减少硬编码。
        
        实现思路：
            1. 首先通过importlib.import_module动态导入指定的包。
            2. 定义一个递归函数explore_package，用于遍历包下的所有子模块和子包。
            3. 对于每一个子包，递归调用explore_package继续深入遍历。
            4. 对于每一个子模块，导入模块后遍历其所有属性，查找是否有BaseComponent的子类（且不是BaseComponent本身）。
            5. 如果找到合格的组件类，则调用register_component方法进行注册。
            6. 整个过程中如遇导入异常，会记录警告日志，最终输出注册组件的总数。
            7. 如果最外层包导入失败，则记录错误日志。
            

        Args:
            package_name: 要搜索的包名
        """
        try:
            package = importlib.import_module(package_name)

            # 递归遍历所有子模块
            def explore_package(pkg_name):
                package = importlib.import_module(pkg_name)

                # 获取包的__path__属性
                if hasattr(package, "__path__"):
                    # 导入子模块
                    from pkgutil import iter_modules

                    for _, name, is_pkg in iter_modules(package.__path__, package.__name__ + "."):
                        if is_pkg:
                            # 如果是包，递归搜索
                            explore_package(name)
                        else:
                            # 如果是模块，导入并检查组件类
                            try:
                                module = importlib.import_module(name)
                                for attr_name in dir(module):
                                    attr = getattr(module, attr_name)
                                    if (inspect.isclass(attr) and 
                                        issubclass(attr, BaseComponent) and
                                        attr != BaseComponent):
                                        self.register_component(attr)
                            except (ImportError, AttributeError) as e:
                                logger.warning(f"导入模块 {name} 时出错：{str(e)}")
            explore_package(package_name)
            logger.info(f"自动发现完成， 共注册 {len(self._components)} 个组件")
        except ImportError as e:
            logger.error(f"无法导入包 {package_name}: {str(e)}")

# 全局组件注册表实例
component_registry = ComponentRegistry()