class TaskRun

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./task_run.monk'))
    @template = monkberry.render('task_run')

  render: (taskId, taskRunId) ->
    @fetch taskId, taskRunId, (data) =>
      @template.appendTo(@wrapper)
      @template.update data
      @highlight()

  highlight: ->
    for block_id in ['stdout', 'stderr']      
      HightlighJS.highlightBlock(document.getElementById(block_id));

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
