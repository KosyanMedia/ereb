$ = jQuery = require("jquery");
moment = require("moment");
moment_range = require("./js/readable_range.coffee");
director = require("director");
prettyCron = require("prettycron");
require("bootstrap-webpack");
require("./css/main.scss");
monkberry = require('monkberry');
require('monkberry-events');
require('./js/monkberry_filters.coffee');

Cookies = require("./js/cookies.coffee");
require("./js/main.coffee");

Header = require("./js/blocks/header/header.coffee");
Dashboard = require("./js/blocks/dashboard/dashboard.coffee");
TaskList = require("./js/blocks/task_list/task_list.coffee");
TaskRun = require("./js/task_run.coffee");
TaskForm = require("./js/task_form.coffee");
