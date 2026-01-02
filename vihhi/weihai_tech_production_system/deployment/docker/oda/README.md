# ODA File Converter 安装包目录

## 📦 安装包准备

### 步骤1：下载安装包

1. 访问 ODA 官网：https://www.opendesign.com/guestfiles
2. 注册账号并登录
3. 下载 Linux 版本的 ODA File Converter
4. 文件格式：`ODAFileConverter_*.tar.gz`（例如：`ODAFileConverter_24.12.0_Linux.tar.gz`）

### 步骤2：放置安装包

将下载的安装包文件放置在此目录下：

```bash
# 将下载的安装包复制到此目录
cp ~/Downloads/ODAFileConverter_*.tar.gz vihhi/weihai_tech_production_system/deployment/docker/oda/
```

### 步骤3：验证文件

确保文件存在：

```bash
ls -lh vihhi/weihai_tech_production_system/deployment/docker/oda/
```

应该能看到类似 `ODAFileConverter_24.12.0_Linux.tar.gz` 的文件。

## ⚠️ 注意事项

1. **文件大小**：安装包通常为 100-200MB，已添加到 `.gitignore`，不会提交到代码仓库
2. **版本更新**：更新 ODA File Converter 时，需要替换此目录下的安装包文件
3. **许可证**：确保遵守 ODA File Converter 的使用许可协议

## 🔧 构建镜像

安装包准备好后，构建 Docker 镜像：

```bash
cd vihhi/weihai_tech_production_system
docker build -f deployment/docker/Dockerfile.backend -t your-registry/backend:latest .
```

## 📝 相关文档

详细安装说明请参考：
- `backend/apps/production_management/services/SEALOS_DEPLOYMENT.md`
