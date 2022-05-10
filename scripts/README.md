# OpenCore AMD 5900X-X570-6800xt配置自动化脚本

*important*: 此脚本编写，基于OpenCore 0.8.0版本文档.

此脚本目标: 执行脚本后，会从网络获取最新的OpenCore版本，及和硬件对应的最新稳定版本驱动文件(.kext)  
获取完毕后, 执行操作:

| 特性                           | 当前状态 |
|------------------------------|------|
| 更新OpenCore基础文件               | DONE |
| 更新OpenCore DSDT              | DONE |
| 更新OpenCore driver文件          | DONE |
| 更新OpenCore kext文件            | DONE |
| 更新OpenCore resources文件       | TODO |
| 调用ProperTree生成基本config.plist | DONE |
| 根据OpenCore文档定制配置文件           | DONE |
| Gen SMBIOS, add to config    | TODO |
| 执行AMD CPU内核补丁脚本              | DONE |

***注意:*** 目前请不要更改config/packages.toml文件中Basic项的fresh_update值，因为目前只支持完整更新功能


## Post Install:

重要的可选配置节点:

| 名称          | 状态   |
|-------------|------|
| GUI配置       | TODO |
| Windows启动配置 | TODO |
| Linux启动配置   | TODO |

## OpenCore GUI配置

### 图形

*wiki*: https://dortania.github.io/OpenCore-Post-Install/cosmetic/gui.html

- Binary Resources, add the Resources folder to ```EFI/OC```
- Copy OpenCanopy.efi to ```EFI/OC/Drivers```

### 声音