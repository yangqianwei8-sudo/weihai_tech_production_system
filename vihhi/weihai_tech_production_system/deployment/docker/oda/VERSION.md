# ODA File Converter 版本说明

## 📌 版本选择

**项目未指定特定版本要求，建议使用最新稳定版本。**

## 🔍 如何选择版本

### 1. 查看可用版本

访问 ODA 官网下载页面：https://www.opendesign.com/guestfiles

在下载页面可以看到所有可用的版本，通常包括：
- 最新版本（Latest）
- 历史版本（Previous Versions）

### 2. 版本命名规则

ODA File Converter 的版本命名格式：
```
ODAFileConverter_<主版本>.<次版本>.<修订版本>_Linux.tar.gz
```

例如：
- `ODAFileConverter_24.12.0_Linux.tar.gz` - 版本 24.12.0
- `ODAFileConverter_25.1.0_Linux.tar.gz` - 版本 25.1.0

### 3. 平台选择

**必须选择：Linux x64 (64位)**

⚠️ **不要选择以下版本：**
- Windows 版本
- macOS 版本
- Linux 32位版本

### 4. 推荐版本策略

1. **生产环境**：使用最新稳定版本（Latest Stable）
2. **测试环境**：可以使用最新版本进行测试
3. **兼容性要求**：如果项目有特定的 DWG/DXF 文件格式要求，请查看 ODA 的版本说明文档

## 📋 当前推荐版本

**建议下载最新版本**，因为：
- 包含最新的 bug 修复
- 支持更多文件格式
- 性能优化
- 安全性更新

## 🔄 版本更新

如果需要更新版本：

1. 下载新版本的安装包
2. 替换 `deployment/docker/oda/` 目录下的旧文件
3. 重新构建 Docker 镜像
4. 测试验证新版本是否正常工作

## ⚠️ 注意事项

1. **向后兼容性**：新版本通常向后兼容，但建议在测试环境先验证
2. **许可证**：确保新版本的许可证与您的使用场景兼容
3. **依赖关系**：某些 Python 库（如 ezdxf）可能与特定版本的 ODA File Converter 配合更好

## 📞 获取帮助

如果对版本选择有疑问：
- 查看 ODA 官方文档：https://www.opendesign.com/docs
- 联系 ODA 技术支持
- 查看项目的其他相关文档
