class RecentHistory

  constructor: (wrapper) ->
    @wrapper = wrapper

  render: () ->
    @fetch ((data) =>
      @updateTemplate data
    ), false

  updateTemplate: (data) ->
    rows = data.map (run) =>
      """
        <tr>
          <td> <a href="#/tasks/#{run.task_id}"> #{run.task_id} </a> </td>
          <td> #{run.started_at} </td>
          <td> #{ if run.finished_at? then run.finished_at else run.current } </td>
          <td> #{ helpers.task_state_for_exit_code(run.exit_code) } </td>
          <td> <a href="#/tasks/#{run.task_id}/runs/#{run.task_run_id}"> More </a> </td>
        <tr>
      """

    html = [
      "<div class='row'>",
      "<div class='col-md-6 col-md-offset-3'>",
      "<table class='table'>",
      rows.join(''),
      "</table>",
      "</div>",
      "</div>"
    ].join('')

    $(@wrapper).html html

  fetch: (callback, useStub=false) ->
    if useStub
      stub =
        [
          task_id: 'bar'
          exit_code: 0
          started_at: '2015-07-11 20:05:00'
          finished_at: '2015-07-11 20:10:00'
          current: 'finished'
        ,
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
      callback(stub)
    else
      url = [window.SERVER_HOST, 'status', 'recent_history'].join('/')
      promise = $.get url

      promise.done (response) ->

        callback JSON.parse(response)

      promise.fail (response) ->
        callback []



module.exports = RecentHistory
