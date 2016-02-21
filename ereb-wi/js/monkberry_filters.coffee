monkberry.filters.humanize_exit_code = (exit_code) =>
  return 'Running' unless exit_code?
  return 'Success' if exit_code == 0
  'Fail'

monkberry.filters.enabled_icon = (enabled) =>
  if enabled then 'ok' else 'remove'

monkberry.filters.task_exit_code_to_class = (exit_code) =>
  if exit_code == 0
    'progress-bar-success'
  else
    'progress-bar-danger'
