stub =
  config:
    cron_schedule: '* * * * *'
    cmd: 'echo foo'
    name: 'foo',
    enabled: false,
    description: ''
  runs: [
    task_id: 'bar'
    exit_code: 0
    started_at: '2015-07-11 20:05:00'
    finished_at: '2015-07-11 20:10:00'
    current: 'finished'
  ,
    task_id: 'baz'
    started_at: '2015-07-11 20:05:00'
    current: 'started'
  ,
    task_id: 'foo'
    exit_code: -1
    started_at: '2015-07-11 20:05:00'
    finished_at: '2015-07-11 20:10:00'
    current: 'finished'
  ]

module.exports = stub
