class Header
  constructor: (wrapper) ->
    @wrapper = wrapper
    @state =
      state: 'no_connection'
      info: @version()
      next_run: -1
      next_tasks: []

    monkberry.mount(require('./header.monk'))
    @template = monkberry.render('header')
    @template.appendTo(@wrapper)
    @update @state

    @getStatus @update
    @initEvents()
    @initWebsocket()
    @initTimer()

  initEvents: =>
    @template.on 'click', '#running_button', (e) =>
      url = if @state.state == 'stopped'
        [window.SERVER_HOST, 'status', 'start'].join('/')
      else
        [window.SERVER_HOST, 'status', 'stop'].join('/')
      $(@).attr('disabled', true)
      $.get url, (success) =>
        @getStatus(@update)

  initTimer: =>
    @timer = setInterval =>
      @state.next_run -= 1 if @state.next_run > 0
      @update @state
    , 1000


  initWebsocket: =>
    websocket_host = window.SERVER_HOST.replace(/http:\/\/|http:\/\//, '')
    websocket = new WebSocket("ws://#{websocket_host}/ws")

    websocket.onmessage = (message) =>
      status_response = JSON.parse(message.data)
      @update(status_response)

    websocket.onclose = (event) =>
      @state.state = 'no_connection'
      @update @state
      setTimeout((=> @initWebsocket()), 2000)


  getStatus: (callback, useStub=false) =>
    if useStub
      stub = require('./stub.coffee')
      callback(stub)
    else
      url = [window.SERVER_HOST, 'status'].join('/')
      promise = $.get url

      promise.done (response) ->
        callback JSON.parse(response)

      promise.fail (response) ->
        callback
          state: 'no_connection'
          next_run: -1
          next_tasks: []

  version: =>
    "Ereb for great future! #{window.DEFAULT_CONFIG.version}"

  update: (state) =>
    @state.state = state.state
    @state.next_run = state.next_run
    @state.next_run_time = moment.preciseDiff(moment(), moment().add(state.next_run, 'seconds'))
    @state.next_tasks = state.next_tasks
    @template.update @state

module.exports = Header
