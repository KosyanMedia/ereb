class TaskList
  defaultSchedule: '* */1 * * *'
  defaultCmd: 'echo'

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./task_list.monk'))
    @template = monkberry.render('task_list')
    @initEvents()

  render: (taskId, taskRunId) ->
    @fetch taskId, taskRunId, (tasks) =>
      for task in tasks
        task.barPoints = @taskBarPoints(task.runs.slice(-20))
        task.statistics = @taskStatistics(task.runs.slice(-20))

      @template.appendTo(@wrapper)
      @template.update
        tasks: tasks

  taskBarPoints: (task_runs) =>
    task_runs = task_runs.slice(-20)
    width = 100 / task_runs.length
    task_runs.map (task_run) ->
      width: width
      exit_code: task_run.state.exit_code

  taskStatistics: (task_runs) =>
    statistics =
      success: 0
      error: 0
    for task_run in task_runs
      if task_run.state.exit_code == 0
        statistics.success += 1
      else
        statistics.error += 1
    statistics

  initEvents: ->
    @template.on 'click', '#new_task_form__submit', (e) =>
      e.preventDefault()
      newTaskName = $('#new_task_name').val().replace(/ /g, '_')
      unless newTaskName == ''
        @createTask newTaskName, =>
          document.location.hash = ['#/tasks', newTaskName].join('/')

  fetch: (taskId, taskRunId, callback, useStub=false) ->
    if useStub
      stub = require('./stub.coffee')
      callback(stub)
    else
      url = [window.SERVER_HOST, 'tasks'].join('/')
      promise = $.get url

      promise.done (response) ->
        callback JSON.parse(response)

      promise.fail (response) ->
        callback []

  createTask: (name, callback) ->
    url = [window.SERVER_HOST, 'tasks'].join('/')
    promise = $.post url, JSON.stringify
      task_id: name
      cmd: [@defaultCmd, name].join(' ')
      cron_schedule: @defaultSchedule
      enabled: false
      description: ''

    promise.done (response) ->
      callback()


module.exports = TaskList
