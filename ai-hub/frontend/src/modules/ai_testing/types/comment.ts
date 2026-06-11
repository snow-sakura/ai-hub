/** AI Testing 用例评论类型 */

export interface CaseComment {
  id: string
  case_id: string
  content: string
  author: string
  created_at: string
  updated_at: string
}

export interface CommentCreate {
  content: string
  author?: string
}

export interface CommentUpdate {
  content: string
}
