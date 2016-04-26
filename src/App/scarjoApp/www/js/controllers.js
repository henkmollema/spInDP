angular.module('starter.controllers', [])

.controller('SpiderCtrl', function($scope, SpiderService) {
	$scope.testConnection = function()
	{
		SpiderService.getFromSpider();
	}
	
	
})

.controller('GraphsCtrl', function($scope, SpiderService) {
  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //
  //$scope.$on('$ionicView.enter', function(e) {
  //});
  
	$scope.labels = ["January", "February", "March", "April", "May", "June", "July"];
    $scope.series = ['Series A', 'Series B'];
    $scope.data = [
        [65, 59, 80, 81, 56, 55, 40],
        [28, 48, 40, 19, 86, 27, 90]
    ];
	
})

.controller('DebugCtrl', function($scope, $stateParams, SpiderService) {
  
})

.controller('AccountCtrl', function($scope) {
  $scope.settings = {
    enableFriends: true
  };
});
