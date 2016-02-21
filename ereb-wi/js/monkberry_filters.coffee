monkberry.filters.humanize_exit_code = (exit_code) =>
  return 'Running' unless exit_code?
  return 'Success' if exit_code == 0
  'Fail'
