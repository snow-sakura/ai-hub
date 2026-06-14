"""自定义业务异常 - 避免暴露底层技术细节"""

from fastapi import HTTPException, status


class AppException(HTTPException):
  """应用基础异常"""

  def __init__(self, message: str, code: str = "APP_ERROR",
               status_code: int = 500):
    super().__init__(status_code=status_code, detail={"code": code, "message": message})
    self.code = code


class ConversationNotFoundError(AppException):
  """会话未找到异常"""

  def __init__(self, conversation_id: str):
    super().__init__(
      message="会话不存在",
      code="CONVERSATION_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class KnowledgeDocNotFoundError(AppException):
  """知识库文档未找到异常"""

  def __init__(self, doc_id: str):
    super().__init__(
      message="文档不存在",
      code="KNOWLEDGE_DOC_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class ModelProviderError(AppException):
  """模型调用异常"""

  def __init__(self, provider: str, detail: str = ""):
    super().__init__(
      message="模型调用失败",
      code="MODEL_ERROR",
      status_code=status.HTTP_502_BAD_GATEWAY,
    )


class FileParseError(AppException):
  """文件解析异常"""

  def __init__(self, filename: str, detail: str = ""):
    super().__init__(
      message=f"文件 {filename} 解析失败: {detail}",
      code="FILE_PARSE_ERROR",
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


class ToolExecutionError(AppException):
  """工具执行异常"""

  def __init__(self, tool_name: str, detail: str = ""):
    super().__init__(
      message=f"工具 {tool_name} 执行失败: {detail}",
      code="TOOL_EXECUTION_ERROR",
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class ComfortSceneNotFoundError(AppException):
  """场景未找到异常"""

  def __init__(self, scene_id: str):
    super().__init__(
      message="场景不存在",
      code="COMFORT_SCENE_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class ComfortCharacterNotFoundError(AppException):
  """角色未找到异常"""

  def __init__(self, character_id: str):
    super().__init__(
      message="角色不存在",
      code="COMFORT_CHARACTER_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class ComfortMemoryNotFoundError(AppException):
  """记忆未找到异常"""

  def __init__(self, memory_id: str):
    super().__init__(
      message="记忆不存在",
      code="COMFORT_MEMORY_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class TestingProjectNotFoundError(AppException):
  """测试项目未找到异常"""

  def __init__(self, project_id: str):
    super().__init__(
      message="测试项目不存在",
      code="TESTING_PROJECT_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class TestingCaseNotFoundError(AppException):
  """测试用例未找到异常"""

  def __init__(self, case_id: str):
    super().__init__(
      message="测试用例不存在",
      code="TESTING_CASE_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class GenerationTaskNotFoundError(AppException):
  """生成任务未找到异常"""

  def __init__(self, task_id: str):
    super().__init__(
      message="生成任务不存在",
      code="GENERATION_TASK_NOT_FOUND",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class ReviewNotFoundError(AppException):
  """评审未找到异常"""
  def __init__(self, review_id: str):
    super().__init__(message="评审不存在", code="REVIEW_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
