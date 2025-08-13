# iOS 自定义键盘开发指南

本指南将带你从零开始，一步步创建一个基础的 iOS 自定义键盘扩展。

## 简介

iOS 自定义键盘是在 iOS 8 中引入的一项功能，允许开发者创建系统级的替代键盘，用户可以在任何支持文本输入的应用中使用。

一个键盘项目通常包含两个主要部分：
1.  **Container App (容器应用)**: 一个普通的 iOS 应用。它的主要作用是提供键盘的设置界面、使用说明，并引导用户在系统中启用该键盘。键盘本身不能独立存在，必须依附于一个容器应用。
2.  **Keyboard Extension (键盘扩展)**: 这才是键盘的核心。它是一个独立运行的进程，负责处理 UI 显示和用户输入。

## 1. 准备工作

在开始之前，请确保你已准备好：
*   一台运行 macOS 的 Mac 电脑。
*   最新版本的 [Xcode](https://developer.apple.com/xcode/)。
*   一个 [Apple Developer](https://developer.apple.com/cn/) 账户（如果需要真机调试或发布到 App Store）。
*   具备 Swift 和 SwiftUI (或 UIKit) 的基础知识。本指南将优先使用 SwiftUI。

## 2. 创建项目

### 第一步：创建容器应用
1.  打开 Xcode，选择 **File > New > Project...**。
2.  在模板选择器中，选择 **iOS > App**，然后点击 **Next**。
3.  填写项目信息：
    *   **Product Name**: `MyKeyboardApp` (或你喜欢的名字)
    *   **Interface**: `SwiftUI`
    *   **Language**: `Swift`
4.  点击 **Next**，选择一个位置保存你的项目，然后点击 **Create**。

### 第二步：添加键盘扩展 Target
1.  在 Xcode 中，保持你的项目打开状态，选择 **File > New > Target...**。
2.  在模板选择器中，选择 **iOS > Custom Keyboard Extension**，然后点击 **Next**。
3.  填写扩展信息：
    *   **Product Name**: `MyKeyboard` (建议使用与主应用相关的名字)
    *   **Included in Application**: 确保这里选择了你刚刚创建的容器应用 `MyKeyboardApp`。
4.  点击 **Finish**。Xcode 会弹出一个窗口询问是否要激活 `MyKeyboard` scheme，点击 **Activate**。

现在，你的项目导航器中应该有两个 Target：`MyKeyboardApp` 和 `MyKeyboard`。

## 3. 核心概念

在编写代码之前，理解以下几个核心概念至关重要：

*   **`UIInputViewController`**: 这是键盘扩展的主视图控制器，相当于键盘的入口。我们所有的键盘 UI 和逻辑都将从这里开始。它位于 `MyKeyboard` Target 下的 `KeyboardViewController.swift` 文件中。

*   **`textDocumentProxy`**: 这是一个至关重要的对象，它充当你的键盘和当前输入框（例如备忘录、聊天窗口）之间的桥梁。通过它，你可以：
    *   `insertText(_:)`: 插入文本。
    *   `deleteBackward()`: 删除光标前的字符。
    *   `documentContextBeforeInput`: 获取光标前的文本内容。
    *   `adjustTextPosition(byCharacterOffset:)`: 移动光标。

*   **Open Access (开放访问权限)**: 默认情况下，键盘扩展在一个高度隔离的沙箱中运行，无法访问网络、文件系统，也无法与容器应用共享数据。如果你需要实现联想词、云同步等高级功能，就必须请求“开放访问权限”。但请注意，这会向用户显示一个关于隐私的警告。

*   **App Groups**: 如果你需要在容器应用和键盘扩展之间共享数据（例如自定义设置、词库），最标准的方式是使用 App Groups。它能创建一个共享的数据容器。

## 4. 基础实现步骤

我们将使用 SwiftUI 来构建键盘界面，因为它更现代、更简洁。

### 第一步：设计键盘 UI (SwiftUI)

在 `MyKeyboard` Target 中，创建一个新的 SwiftUI View 文件，命名为 `KeyboardView.swift`。

```swift
// MyKeyboard/KeyboardView.swift
import SwiftUI

// 定义一个回调，用于通知控制器按下了哪个键
typealias KeyPressAction = (String) -> Void

struct KeyboardView: View {
    var onKeyPress: KeyPressAction

    // 定义键盘按键布局
    let rows = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M", "delete"]
    ]

    var body: some View {
        VStack(spacing: 8) {
            // 字母按键
            ForEach(rows, id: \.self) { row in
                HStack(spacing: 4) {
                    ForEach(row, id: \.self) { key in
                        Button(action: {
                            onKeyPress(key)
                        }) {
                            Text(key == "delete" ? "⌫" : key)
                                .font(.system(size: 20))
                                .frame(maxWidth: .infinity, minHeight: 44)
                                .background(Color.gray.opacity(0.5))
                                .foregroundColor(.white)
                                .cornerRadius(5)
                        }
                    }
                }
            }

            // 功能按键 (地球、空格、换行)
            HStack(spacing: 4) {
                // “下一个键盘”按钮，这个功能由 KeyboardViewController 处理
                KeyButton(label: "🌐", value: "nextKeyboard", onKeyPress: onKeyPress)
                
                // 空格键
                KeyButton(label: "space", value: " ", onKeyPress: onKeyPress, flex: 0.6)

                // 换行键
                KeyButton(label: "return", value: "\n", onKeyPress: onKeyPress)
            }
        }
        .padding(4)
        .background(Color.black.opacity(0.9))
    }
}

// 封装一个可复用的按键组件
struct KeyButton: View {
    let label: String
    let value: String
    let onKeyPress: KeyPressAction
    var flex: CGFloat = 0.15 // 占用空间比例

    var body: some View {
        Button(action: {
            onKeyPress(value)
        }) {
            Text(label)
                .font(.system(size: 18))
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(Color.gray.opacity(0.8))
                .foregroundColor(.white)
                .cornerRadius(5)
        }
        .frame(maxWidth: .infinity, idealHeight: 44, maxHeight: 44, alignment: .center)
    }
}
```

### 第二步：集成 UI 到 `KeyboardViewController`

打开 `MyKeyboard/KeyboardViewController.swift`，修改它来加载我们的 SwiftUI 视图。

```swift
// MyKeyboard/KeyboardViewController.swift
import UIKit
import SwiftUI

class KeyboardViewController: UIInputViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        
        // 1. 创建 SwiftUI 视图
        let keyboardView = KeyboardView { [weak self] key in
            self?.handleKeyPress(key)
        }
        
        // 2. 使用 UIHostingController 将 SwiftUI 视图包装起来
        let hostingController = UIHostingController(rootView: keyboardView)
        
        // 3. 将 hostingController 添加到视图层级
        view.addSubview(hostingController.view)
        addChild(hostingController)
        hostingController.didMove(toParent: self)
        
        // 4. 设置约束
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            hostingController.view.leadingAnchor.constraint(equalTo: self.view.leadingAnchor),
            hostingController.view.trailingAnchor.constraint(equalTo: self.view.trailingAnchor),
            hostingController.view.topAnchor.constraint(equalTo: self.view.topAnchor),
            hostingController.view.bottomAnchor.constraint(equalTo: self.view.bottomAnchor)
        ])
        
        // 5. 为“下一个键盘”按钮添加功能
        // 注意：SwiftUI 视图中的 "🌐" 按钮只是触发一个标识符 "nextKeyboard"
        // 真正的切换逻辑在这里实现
    }

    // 处理按键逻辑
    func handleKeyPress(_ key: String) {
        let proxy = self.textDocumentProxy
        
        switch key {
        case "delete":
            proxy.deleteBackward()
        case " ":
            proxy.insertText(" ")
        case "\n":
            proxy.insertText("\n")
        case "nextKeyboard":
            // 调用系统方法切换到下一个键盘
            advanceToNextInputMode()
        default:
            // 插入普通字符
            proxy.insertText(key)
        }
    }
}
```

### 第三步：运行和测试
1.  在 Xcode 的 Scheme 选择器中，选择 `MyKeyboard` Target，并选择一个模拟器或连接的 iPhone 作为目标。
2.  点击 **Run** (▶️) 按钮。Xcode 会提示你选择一个应用来运行键盘扩展，选择一个内置应用，比如 **Notes (备忘录)** 或 **Safari**，然后点击 **Run**。
3.  应用启动后，键盘不会立即出现。你需要手动启用它：
    *   **模拟器**: 按下 `Cmd + Shift + H` 返回主屏幕，打开 **Settings > General > Keyboard > Keyboards > Add New Keyboard...**。在列表中找到你的应用名 `MyKeyboardApp`，然后选择 `MyKeyboard`。
    *   **真机**: 操作路径相同。
4.  启用后，回到备忘录应用，点击输入框，长按左下角的地球图标 (🌐)，在弹出的菜单中选择 `MyKeyboard`。
5.  现在你应该能看到并使用你刚刚创建的键盘了！

## 5. 配置与调试

### 启用 App Groups (可选)
如果需要与容器应用共享数据：
1.  在项目导航器中选择你的项目文件。
2.  选择 `MyKeyboardApp` Target，然后进入 **Signing & Capabilities** 标签页。
3.  点击 **+ Capability**，选择 **App Groups**。
4.  点击 `+` 号，创建一个新的 App Group，命名格式通常是 `group.com.yourcompany.appname`。
5.  **重复以上步骤**，为 `MyKeyboard` Target 添加完全相同的 App Group。

### 请求 Open Access (可选)
1.  在 `MyKeyboard` Target 中，打开 `Info.plist` 文件。
2.  展开 `NSExtension` > `NSExtensionAttributes` 字典。
3.  将 `RequestsOpenAccess` 的布尔值设置为 `YES`。

### 调试
调试键盘扩展比调试普通应用稍微复杂，因为它运行在其他应用的进程中。
1.  像之前一样运行 `MyKeyboard` Target。
2.  在 Xcode 中，选择 **Debug > Attach to Process...**。
3.  在弹出的列表中，找到你的键盘扩展名（例如 `MyKeyboard`），然后附加调试器。现在你可以在 `KeyboardViewController.swift` 中设置断点进行调试了。

## 6. 进阶功能建议

有了基础框架后，你可以探索更多高级功能：
*   **按键音效和振动反馈**: 使用 `UIDevice.current.playInputClick()` 来播放系统默认的按键音。
*   **自动大写和句号快捷键**: 通过分析 `textDocumentProxy.documentContextBeforeInput` 来实现。
*   **联想词/自动纠错**: 这需要更复杂的算法和词典，并且通常需要 Open Access。
*   **主题切换**: 在容器应用中设置主题，通过 App Groups 共享配置，然后在 `KeyboardView` 中动态加载。
*   **更复杂的布局**: 支持数字和符号切换。

## 总结

你已经成功创建了一个功能性的 iOS 自定义键盘。虽然它还很简单，但你已经掌握了最核心的开发流程。从这里开始，你可以不断迭代，添加更多个性化和高级的功能，打造出色的输入体验。祝你开发顺利！
