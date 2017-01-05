stub =
  state: 'running'
  next_run: 4345.1007
  next_tasks: [
    cron_schedule: '* * * * *'
    name: 'bar'
    cmd: 'echo bar'
  ,
    cron_schedule: '* * * * *'
    name: 'foo'
    cmd: 'echo foo'
  ,
    cron_schedule: '* * * * *'
    name: 'baz'
    cmd: 'echo baz'
  ]
  planned_task_run_uuids: [
    "1a282d86-2b37-4332-a781-38b24eefc8e9"
  ]

module.exports = stub
