var myApp = angular.module('myApp', ['ngRoute']);

myApp.config(function($routeProvider) {
  $routeProvider
   .when('/room', {
    templateUrl: './subviews/room.html'
  })
  .otherwise('/', {
    templateUrl: 'index.html',
    controller: 'mainController'
  });

});

myApp.controller('mainController', function($scope, $timeout){
	$timeout(function() {
		$scope.testing = "hi";
	});
	
});