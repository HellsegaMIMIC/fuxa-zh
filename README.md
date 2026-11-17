# FUXA 中文版 · PLCdev 安装源码包

基于固定 `@frangoteam/fuxa@1.3.5`，使用原生简体中文并补充遗漏词条，包含 PLCdev 的原生画面集成源码。
Release 的 `fuxa-zh-patch-*.zip` 是**联网安装/补丁包，不含 FUXA 或 Node.js 二进制**。

## 安装

1. 安装 [Node.js](https://nodejs.org/en/download) 和 Python 3。PLCdev 当前已验证 Node 25.9.0；集成使用 `node:sqlite`，旧版 Node 不适用。
2. 完整解压后运行 `Install-FUXA-ZH.cmd`。按锁文件从 npm 下载 FUXA 1.3.5；首次需要联网。
3. 完成后运行 `Start-FUXA-ZH.cmd`。编辑器在本机 `http://127.0.0.1:18812/editor` 打开；按启动窗口提示退出。

安装目录：`.tools/fuxa/runtime/node_modules/@frangoteam/fuxa`；独立工程和设置位于 `outputs/fuxa-zh-standalone/profile`。
将前者作为 PLCdev 的 FUXA 工具目录。DSH 管理工程时使用自己的工程和 profile；不要把独立 profile 当作工程源文件。
包内独立启动器不读取或复用任何已有模型密钥，AI helper 默认未提供；工程 AI 修改从 DSH 主对话发起。
上游自带的语言设置优先于默认值；部分协议名、标识符和未国际化文字仍为英文。

## 范围

此包不是完整 PLCdev、PLC Runtime 或 OIP 安装包，不自动运行设备。安装脚本核对固定版本与补丁锚点，未知版本停止。
集成源码沿用本机已有实现；本 Release 的联网全新机器安装尚待独立验收。原配置和原安装不会被打包上传。

来源：[FUXA v1.3.5](https://github.com/frangoteam/FUXA/releases/tag/v1.3.5)。保留上游 MIT `LICENSE.FUXA`，PLCdev 补丁为 MIT。
清单与 SHA-256 见 `SOURCE-MANIFEST.json` 和 Release 附件。本项目为社区汉化适配。
