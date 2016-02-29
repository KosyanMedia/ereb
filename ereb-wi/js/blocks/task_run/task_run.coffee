class TaskRun

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./task_run.monk'))
    @template = monkberry.render('task_run')

  render: (taskId, taskRunId) ->
    @fetch taskId, taskRunId, (data) =>
      console.log(data)
      @template.appendTo(@wrapper)
      @template.update data
      @initCodeMirror()

  initCodeMirror: ->
    for textarea_id in ['stdout', 'stderr']
      textarea = document.getElementById(textarea_id)
      if textarea
        CodeMirror.fromTextArea textarea,
          mode: 'shell'
          theme: '3024-night'
          readOnly: "nocursor"

  fetch: (taskId, taskRunId, callback, useStub=false) ->
    if useStub
      stub = require('./stub.coffee')
      callback(stub)
    else
      url = [
        window.SERVER_HOST,
        'tasks',
        taskId,
        'task_runs',
        taskRunId
      ].join('/')
      promise = $.get url

      promise.done (response) ->

        callback JSON.parse(response)

      promise.fail (response) ->
        callback []

module.exports = TaskRun
