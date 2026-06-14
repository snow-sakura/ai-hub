export default {
  // Page titles
  title: 'Execution Records',
  testPlan: 'Test Plan',
  planDetail: 'Plan Details',
  executionHistory: 'Execution History',
  inDevelopment: 'Execution records feature under development...',

  // Actions
  newPlan: 'New Test Plan',
  batchDelete: 'Batch Delete',
  viewExecution: 'View Execution',
  createPlan: 'Create',
  updatePlan: 'Save',
  closePlan: 'Close',
  activatePlan: 'Activate',
  viewHistory: 'History',

  // Table columns
  serialNumber: 'No.',
  planName: 'Plan Name',
  project: 'Project',
  projects: 'Projects',
  version: 'Version',
  creator: 'Creator',
  status: 'Status',
  createdAt: 'Created At',
  actions: 'Actions',
  testCase: 'Test Case',
  executionStatus: 'Execution Status',
  comments: 'Comments',
  executedBy: 'Executed By',
  executedAt: 'Executed At',

  // Status
  active: 'Active',
  closed: 'Closed',
  untested: 'Untested',
  passed: 'Passed',
  failed: 'Failed',
  blocked: 'Blocked',
  retest: 'Retest',
  completed: 'Completed',
  notStarted: 'Not Started',
  inProgress: 'In Progress',

  // Statistics
  total: 'Total',
  progressRate: 'Progress',

  // Dialog titles
  createPlanDialog: 'New Test Plan',
  editPlanDialog: 'Edit Test Plan',

  // Form labels
  planDescription: 'Plan Description',
  relatedProjects: 'Related Projects',
  relatedVersion: 'Related Version',
  testCases: 'Test Cases',
  assignees: 'Assignees',
  planStatus: 'Status',
  activeText: 'Active',
  inactiveText: 'Closed',

  // Placeholders
  planNamePlaceholder: 'Enter plan_bak name',
  planDescriptionPlaceholder: 'Enter plan_bak description',
  selectProjects: 'Select projects',
  selectVersion: 'Select version',
  selectTestcases: 'Select test cases',
  selectTestcasesDisabled: 'Please select project first',
  loadingTestcases: 'Loading...',
  selectAssignees: 'Select assignees',
  commentsPlaceholder: 'Enter comments',

  // Filters
  selectProject: 'Select Project',
  selectStatus: 'Select Status',
  filterActive: 'Active',
  filterClosed: 'Closed',

  // Messages
  fetchListFailed: 'Failed to fetch test plans',
  fetchDetailFailed: 'Failed to fetch test plan_bak details',
  fetchBasicDataFailed: 'Failed to fetch basic data',
  fetchTestcasesFailed: 'Failed to fetch test cases',
  fetchHistoryFailed: 'Failed to fetch execution history',
  createSuccess: 'Test plan_bak created successfully',
  createFailed: 'Failed to create test plan_bak',
  updateSuccess: 'Test plan_bak updated successfully',
  updateFailed: 'Failed to update test plan_bak',
  statusUpdateSuccess: 'Status updated successfully',
  statusUpdateFailed: 'Failed to update status',
  detailsUpdateSuccess: 'Details updated successfully',
  detailsUpdateFailed: 'Failed to update details',
  selectFirst: 'Please select test plans to delete first',
  selectCasesFirst: 'Please select cases to delete first',
  selectProjectFirst: 'Please select project first',
  batchDeleteConfirm: 'Are you sure to delete selected {count} test plans? This action cannot be undone.',
  batchDeleteCasesConfirm: 'Are you sure to delete selected {count} cases? This action cannot be undone.',
  batchDeleteSuccess: 'Successfully deleted {successCount} test plans',
  batchDeleteCasesSuccess: 'Successfully deleted {successCount} cases',
  batchDeletePartialSuccess: 'Successfully deleted {successCount} test plans, {failCount} failed',
  batchDeleteCasesPartialSuccess: 'Successfully deleted {successCount} cases, {failCount} failed',
  batchDeleteFailed: 'Delete failed',
  toggleStatusConfirm: 'Are you sure to {action} this test plan_bak?',
  toggleStatusSuccess: '{action} successful',
  toggleStatusFailed: 'Operation failed',

  // Other
  noProject: 'No Project',
  noData: '-',

  // Validation
  planNameRequired: 'Please enter plan_bak name',
  projectsRequired: 'Please select project',
  testcasesRequired: 'Please select at least one test case',
  selectProjectBeforeTestcases: 'Please select project first'
}
