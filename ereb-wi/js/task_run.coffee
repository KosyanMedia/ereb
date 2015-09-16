class TaskRun

  constructor: (wrapper) ->
    @wrapper = wrapper

  render: (taskId, taskRunId) ->
    @fetch taskId, taskRunId, (data) =>
      @updateTemplate data

  updateTemplate: (data) ->
    formatted_stdout = data.stdout
    formatted_stderr = data.stderr

    html =
      """
        <div class="row">
          <div class="col-md-6 col-md-offset-3">
            <h3> Task run #{data.id} </h3>
            <p> <b> Started at: </b> #{data.state.started_at} </p>
            <p> <b> Finished at: </b> #{data.state.finished_at} </p>
            <p> <b> Exit code: </b> #{data.state.exit_code} </p>
            <p> <b> Current state: </b> #{data.state.current} </p>
          </div>

        </div>

        <div class="row">
          <div class="col-md-6 col-md-offset-3">
            <h4> STDOUT </h4>
            <pre class="wi__formatted_stdout">#{formatted_stdout}</pre>

            <h4> STDERR </h4>
            <pre class="wi__formatted_stderr">#{formatted_stderr}</pre>
          </div>
        </div>
      """

    $(@wrapper).html html

  fetch: (taskId, taskRunId, callback, useStub=false) ->
    if useStub
      stub =
        id: '2015_07_14_11_13_00_014547'
        pid: '9519'
        state:
          finished_at: "2015-07-14 11:13:00"
          started_at: "2015-07-14 11:13:00"
          exit_code: 0
          current: "finished"
        stdout: 'blablfadllfas lsdfl asldf lasdf stdout\n
        END'
        stderr: 'whoop whoop stderr'
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
