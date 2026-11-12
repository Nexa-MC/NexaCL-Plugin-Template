# NexaCL 插件模板

[English](README.md) · [开发文档](https://docs.pcln.top/plugin-sdk/) · [SDK 源码](https://github.com/Nexa-MC/NexaCL-Plugin-SDK)

该模板包含可运行的 Wasm 插件、宿主渲染页面、按钮与确认动作，以及打包脚本和 CI。
SDK 从公开发行版下载并校验，不需要访问私有 Sidecar 仓库。

## 构建与安装

1. 安装 Python 3.12、Clang 和 wasm-ld。Debian/Ubuntu 可安装 `clang`、`lld`。
2. 修改 `plugin.config.json` 中的插件 ID、版本和标题，使用自己的唯一 ID。
3. 执行：

   ```sh
   python eng/build.py --clang clang
   python eng/verify_package.py
   ```

4. 在支持该契约的 NexaCL 开发版本中启用开发者模式，通过插件管理页选择
   `artifacts/plugin.zip` 并审阅权限。
5. 打开插件页面，点击按钮并确认，动作返回 `Desktop action completed`。

首次构建按 `sdk.lock.json` 下载固定版本 SDK，之后复核本地缓存；缓存完整且已安装编译器时，
Wasm 项目可离线构建。运行时离线准入仍由宿主控制。

## 开发入口

- `wasm/plugin.c`：初始化、页面/动作注册、按钮回调。
- `wasm/page.nxml`：布局与动作绑定。
- `plugin.config.json`：身份、版本、权限。ID 会同时用于 C 注册项和 NXML 绑定。
- `sdk.lock.json`：SDK 版本、提交、大小和 SHA-256。
- `managed-contract/`：可选 C# 契约示例，不打进插件 ZIP，不代表可直接安装 CLR DLL。

默认权限仅覆盖示例所需的页面、包内文件、动作和任务观察，不读取账户或实例。
新增功能时按需声明权限，并处理拒绝、取消、过期句柄和宿主尚未支持的接口。

升级 SDK 时同步更新锁文件和 C# PackageReference。除 CI 外，还应在启动器中验证拒绝确认、
停止、重载和权限不足等路径；编译通过不等于功能已经在宿主中完成。
