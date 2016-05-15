class FailedTasks

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./failed_tasks.monk'))
    @template = monkberry.render('failed_tasks')

  render: () ->
    @fetch (data) =>
      @template.appendTo(@wrapper)
      @template.update
        rows: data

  fetch: (callback, useStub=false) ->
    if useStub
      stub = require('./stub.coffee')
      callback(stub)
    else
      url = [window.SERVER_HOST, 'status', 'recent_failed_tasks'].join('/')
      promise = $.get url

      promise.done (response) ->

        callback JSON.parse(response)

      promise.fail (response) ->
        callback []



module.exports = FailedTasks
