$ = jQuery = require("jquery");
HightlighJS = require("highlight.js");
Cookies = require("./js/vendor/cookies.coffee");
moment = require("moment");
moment_range = require("./js/vendor/readable_range.coffee");
director = require("director");
prettyCron = require("prettycron");
require("bootstrap-webpack");
monkberry = require('monkberry');
require('monkberry-events');

require("./css/main.scss");
require("./css/highlightjs_tomorrow_night.css");
require('./js/monkberry_filters.coffee');
require("./js/main.coffee");

Header = require("./js/blocks/header/header.coffee");
Dashboard = require("./js/blocks/dashboard/dashboard.coffee");
TaskList = require("./js/blocks/task_list/task_list.coffee");
TaskForm = require("./js/blocks/task_form/task_form.coffee");
TaskRun = require("./js/blocks/task_run/task_run.coffee");
