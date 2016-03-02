class TaskList
  defaultSchedule: '* * * * *'
  defaultCmd: 'echo'

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./task_list.monk'))
    @template = monkberry.render('task_list')
    @initEvents()

  render: (taskId, taskRunId) ->
    @fetch taskId, taskRunId, (tasks) =>
      for task in tasks
        if task.stats
          task.bar_points = @taskBarPoints(task.stats.exit_codes)

      @template.appendTo(@wrapper)
      @template.update
        tasks: tasks

  taskBarPoints: (exit_codes) =>
    width = 100 / exit_codes.length
    exit_codes.map (exit_code) ->
      width: width
      exit_code: parseInt(exit_code)

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
