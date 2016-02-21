class Dashboard

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./dashboard.monk'))
    require('./dashboard.monk')
    @template = monkberry.render('dashboard')

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
      url = [window.SERVER_HOST, 'status', 'recent_history'].join('/')
      promise = $.get url

      promise.done (response) ->

        callback JSON.parse(response)

      promise.fail (response) ->
        callback []



module.exports = Dashboard
