angular.module('ipcaApp', [])
.controller('MainCtrl', [function(g) {
  this.dataset_names = GLOBALS.dataset_names;
  this.dataset = GLOBALS.dataset;
}]);

// DEBUGGING
// https://www.ng-book.com/p/Debugging-AngularJS/
var rootEle, 
    ele, 
    scope, 
    ctrl;
