# 服务信息功能删除备份说明

## 备份时间
2025年12月19日 12:10:13

## 备份内容
本目录包含删除服务信息功能前的完整代码备份。

## 删除范围

### 1. 前端模板
- `contract_form.html`: 删除服务信息section及相关JavaScript代码

### 2. 后端视图
- `views_pages.py`: 删除contract_create和contract_edit中的服务信息处理代码

### 3. 数据库模型
- `models.py`: 注释ContractServiceContent模型定义

### 4. 数据库
- **注意**: 数据库表 `contract_service_content` **保留**（作为备份），只删除代码层面的引用

## 相关文件

### 已备份的文件
1. `views_pages.py` - 后端视图处理逻辑
2. `contract_form.html` - 前端模板
3. `models.py` - 数据库模型定义

### 涉及的数据库表
- `contract_service_content` - 合同服务内容表（保留，未删除）

### 涉及的模型
- `ContractServiceContent` - 合同服务内容模型（代码中已注释）

### 涉及的字段
- `service_contents` - 在BusinessContract中的related_name

## 恢复方法

如果需要恢复服务信息功能，请：

1. 从本备份目录恢复相关文件
2. 取消models.py中ContractServiceContent模型的注释
3. 确保数据库表contract_service_content存在
4. 运行数据库迁移（如果需要）

## 删除的代码位置

### views_pages.py
- contract_create函数: 4957-5013行（服务内容处理）
- contract_create函数: 5112-5167行（服务内容上下文）
- contract_edit函数: 5221-5269行（服务内容处理）
- contract_edit函数: 5347-5366行（服务内容上下文）

### contract_form.html
- HTML: 服务信息section（约395-410行）
- JavaScript: serviceProfessionsData, resultFileTypesData定义
- JavaScript: serviceContentsTableManager相关代码

### models.py
- ContractServiceContent模型: 1939-1964行（已注释）

## 注意事项
- 数据库表和数据**未删除**，仅删除代码引用
- 如需完全清理，需要手动执行SQL删除表和数据
